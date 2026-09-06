import random
import unittest
from functools import lru_cache
from sleeperplan.cutting import solve,pattern_fits,layout_board
from sleeperplan.model import Rules,Stock,PlanError
from .helpers import piece,job,TODAY
from sleeperplan.planner import plan


def oracle(lengths,stocks,kerf=3):
    """Independent subset-partition oracle for small unlimited-supply cases."""
    @lru_cache(None)
    def go(mask):
        if not mask:return 0
        first=mask & -mask
        best=10**12
        subset=mask
        while subset:
            if subset & first:
                members=[lengths[i] for i in range(len(lengths)) if subset & (1<<i)]
                n=len(members);total=sum(members)
                for stock in stocks:
                    used_without_last_cut=total+(n-1)*kerf
                    if used_without_last_cut==stock.length_mm or used_without_last_cut+kerf<=stock.length_mm:
                        best=min(best,stock.price_pence+go(mask ^ subset))
            subset=(subset-1)&mask
        return best
    return go((1<<len(lengths))-1)


class CuttingTests(unittest.TestCase):
    def test_two_1200_do_not_fit_2400(self):
        stock=Stock('s',2400,2800)
        self.assertFalse(pattern_fits([1200,1200],stock,3))
        result=solve([piece(1200,1),piece(1200,2)],[stock],Rules())
        self.assertEqual(result['purchased_sleepers'],2)

    def test_full_uncut_stock_needs_zero_cuts(self):
        b=layout_board(Stock('s',2400,2800),[piece(2400)],Rules(),'B1')
        self.assertEqual(b['cuts'],[]);self.assertEqual(b['offcut_mm'],0)

    def test_exact_final_piece_does_not_need_phantom_cut(self):
        b=layout_board(Stock('s',2400,2800),[piece(1199,1),piece(1198,2)],Rules(),'B1')
        self.assertEqual(len(b['cuts']),1);self.assertEqual(b['offcut_mm'],0)
        self.assertEqual(b['cuts'][0]['kerf_start_mm'],1199)
        self.assertEqual(b['cuts'][0]['blade_centre_mm'],1200.5)

    def test_two_short_pieces_need_two_cuts_if_tail_remains(self):
        b=layout_board(Stock('s',2400,2800),[piece(1000,1),piece(1000,2)],Rules(),'B1')
        self.assertEqual(len(b['cuts']),2);self.assertEqual(b['offcut_mm'],394)
        self.assertEqual(b['parts'][1]['start_mm'],1003)

    def test_terminal_sliver_not_treated_as_full_kerf(self):
        self.assertFalse(pattern_fits([2399],Stock('s',2400,2800),3))
        self.assertTrue(pattern_fits([2397],Stock('s',2400,2800),3))

    def test_trim_includes_kerf_without_double_count(self):
        b=layout_board(Stock('s',2400,2800,trim_start_mm=5,trim_end_mm=5),[piece(1000)],Rules(),'B1')
        self.assertEqual(b['parts'][0]['start_mm'],5)
        self.assertEqual(b['cuts'][0]['kerf_start_mm'],2)
        self.assertEqual(b['cuts'][1]['kerf_start_mm'],2395)
        self.assertEqual(b['kerf_and_trim_loss_mm'],13)
        self.assertEqual(b['offcut_mm'],1387)

    def test_full_nominal_length_impossible_after_trim(self):
        with self.assertRaisesRegex(PlanError,'uninterrupted'):
            solve([piece(2400)],[Stock('s',2400,2800,trim_start_mm=5)],Rules())

    def test_unsupported_splice_is_not_invented(self):
        with self.assertRaisesRegex(PlanError,'splice'):
            solve([piece(3000)],[Stock('s',2400,2800)],Rules())

    def test_cheapest_purchase_not_fewest_boards(self):
        stocks=[Stock('cheap',1000,100),Stock('long',2100,1000)]
        r=solve([piece(1000,1),piece(1000,2)],stocks,Rules())
        self.assertEqual(r['timber_purchase_pence'],200)
        self.assertEqual(r['purchased_sleepers'],2)

    def test_mixed_lengths_and_finite_inventory(self):
        stocks=[Stock('new',2400,2800),Stock('old',1200,0,quantity=1,inventory=True)]
        r=solve([piece(1200,1),piece(1200,2)],stocks,Rules())
        self.assertEqual(r['inventory_pieces_used'],1)
        self.assertEqual(r['purchased_sleepers'],1)

    def test_finite_stock_infeasibility(self):
        with self.assertRaisesRegex(PlanError,'finite stock'):
            solve([piece(2000,1),piece(2000,2)],[Stock('s',2400,2800,quantity=1)],Rules())

    def test_exhausted_budget_labels_heuristic(self):
        r=solve([piece(1000,i) for i in range(4)],[Stock('s',2400,2800)],Rules(max_search_steps=1))
        self.assertEqual(r['algorithm'],'heuristic');self.assertFalse(r['optimality_proven'])
        self.assertEqual(r['purchased_sleepers'],2)

    def test_allocation_is_one_to_one(self):
        r=solve([piece(1000,i) for i in range(17)],[Stock('s',2400,2800)],Rules())
        ids=[p['piece_id'] for b in r['boards'] for p in b['parts']]
        self.assertEqual(sorted(ids),sorted(f'p{i}' for i in range(17)))

    def test_reusable_offcut_threshold(self):
        b=layout_board(Stock('s',2400,2800),[piece(1000)],Rules(reusable_offcut_min_mm=1500),'B1')
        self.assertFalse(b['keep_offcut'])

    def test_seeded_conservation_100_cases(self):
        rng=random.Random(73731)
        for _ in range(100):
            ps=[piece(rng.choice([400,700,1000,1200,1800,2400]),i) for i in range(rng.randint(1,12))]
            r=solve(ps,[Stock('s',2400,2800)],Rules())
            self.assertEqual(r['input_length_mm'],r['finished_length_mm']+r['offcut_length_mm']+r['kerf_and_trim_loss_mm'])
            for b in r['boards']:
                self.assertEqual(sum(p['length_mm'] for p in b['parts'])+b['offcut_mm']+b['kerf_and_trim_loss_mm'],b['gross_length_mm'])
                self.assertTrue(all(0<=c['kerf_start_mm']<c['kerf_end_mm']<=b['gross_length_mm'] for c in b['cuts']))

    def test_exact_cost_matches_independent_oracle_70_cases(self):
        rng=random.Random(12121)
        stocks=[Stock('short',1200,1400),Stock('long',2400,2300)]
        for case in range(70):
            lengths=[rng.choice([400,500,600,800,1000,1200]) for _ in range(rng.randint(1,6))]
            result=solve([piece(L,i) for i,L in enumerate(lengths)],stocks,Rules())
            self.assertTrue(result['optimality_proven'])
            self.assertEqual(result['timber_purchase_pence'],oracle(lengths,stocks),case)

    def test_default_job_golden_counts(self):
        p=plan(job(),TODAY)
        self.assertEqual(p['cut_plan']['purchased_sleepers'],9)
        self.assertEqual(p['cut_plan']['saw_cuts'],8)
        self.assertEqual(p['cut_plan']['timber_purchase_pence'],25200)

if __name__=='__main__':unittest.main()
