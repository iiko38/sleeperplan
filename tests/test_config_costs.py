import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from sleeperplan.config import parse_job,load_job
from sleeperplan.costing import REQUIRED_EXTRAS,cost_job
from sleeperplan.model import PlanError
from sleeperplan.planner import physical_design_hash,plan
from .helpers import inputs,job,TODAY,ROOT

class ConfigTests(unittest.TestCase):
    def reject(self,mutate):
        raw,cat=inputs();mutate(raw,cat)
        with self.assertRaises(PlanError):parse_job(raw,cat)

    def test_unknown_fields_rejected(self):self.reject(lambda r,c:r['beds'][0].update(wdith_mm=1200))
    def test_mm_not_metres(self):self.reject(lambda r,c:r['beds'][0].update(length_mm=2.4))
    def test_bool_not_integer(self):self.reject(lambda r,c:r['beds'][0].update(courses=True))
    def test_negative_quantity(self):self.reject(lambda r,c:r['beds'][0].update(quantity=-1))
    def test_zero_cavity(self):self.reject(lambda r,c:r['beds'][0].update(width_mm=200))
    def test_negative_price(self):self.reject(lambda r,c:c['stocks'][0].update(price_pence=-1))
    def test_non_integer_pence(self):self.reject(lambda r,c:c['stocks'][0].update(price_pence=28.0))
    def test_bad_pilot_mode(self):self.reject(lambda r,c:c['screws'][0].update(pilot_mode='probably'))
    def test_pilot_needs_evidence(self):self.reject(lambda r,c:c['screws'][0].update(pilot_mode='none'))
    def test_pilot_needs_diameter_and_depth(self):self.reject(lambda r,c:c['screws'][0].update(pilot_mode='pilot',pilot_evidence='Recorded instruction'))
    def test_pilot_depth_not_beyond_screw_tip(self):self.reject(lambda r,c:c['screws'][0].update(pilot_mode='pilot',pilot_evidence='test only',pilot_diameter_mm=4,pilot_depth_mm=151))
    def test_no_unlimited_inventory(self):self.reject(lambda r,c:r.update(inventory=[{'id':'off','length_mm':1000,'quantity':None}]))
    def test_duplicate_stock_ids(self):self.reject(lambda r,c:c['stocks'].append(c['stocks'][0]))
    def test_missing_labour_rate(self):self.reject(lambda r,c:r['costs'].update(labour_minutes=120))
    def test_margin_less_than_100_percent(self):self.reject(lambda r,c:r['costs'].update(target_margin_bps=10000))
    def test_no_path_traversal_ids(self):self.reject(lambda r,c:r['beds'][0].update(id='../outside'))
    def test_trim_at_least_kerf(self):self.reject(lambda r,c:c['stocks'][0].update(trim_start_mm=1))
    def test_bad_date(self):self.reject(lambda r,c:c['stocks'][0].update(checked_on='yesterday'))
    def test_unknown_site_type(self):self.reject(lambda r,c:r['beds'][0].update(site_type='pond'))
    def test_quantity_limit(self):self.reject(lambda r,c:r['beds'][0].update(quantity=30))

    def test_bad_approval_hash_format_rejected(self):
        self.reject(lambda r,c:r['review'].update(approved_physical_design_hash='tooshort'))

    def test_all_examples_parse_and_plan(self):
        for p in sorted((ROOT/'examples').glob('*.json')):
            with self.subTest(path=p):self.assertTrue(plan(load_job(p),TODAY)['pieces'])

    def test_relative_catalogue_from_another_working_directory(self):
        self.assertTrue(load_job(ROOT/'examples/neighbour.json').stocks)

    def test_measured_section_override(self):
        raw,cat=inputs();raw['measured_section_mm']=[98,198]
        j=parse_job(raw,cat)
        self.assertEqual((j.profile.thickness_mm,j.profile.height_mm),(98,198))

class CostAndGateTests(unittest.TestCase):
    def test_unknowns_not_zero(self):
        p=plan(job(),TODAY)
        self.assertFalse(p['costs']['is_complete'])
        self.assertIsNone(p['costs']['complete_cost_pence'])
        self.assertEqual(set(p['costs']['unpriced_items']),set(REQUIRED_EXTRAS)|{'labour'})

    def test_pack_rounding_and_spares(self):
        p=plan(job(),TODAY);byid={r['id']:r for r in p['costs']['rows']}
        self.assertEqual(byid['wickes-287686']['needed'],24)
        self.assertEqual(byid['wickes-287686']['buy_quantity'],2)
        self.assertEqual(byid['wickes-287688']['needed'],28)
        self.assertEqual(byid['wickes-287688']['buy_quantity'],2)
        self.assertEqual(p['costs']['timber_and_screw_purchase_pence'],29460)

    def test_global_pack_rounding_not_one_pack_per_bed(self):
        j=job();b=replace(j.beds[0],courses=1,quantity=3);p=plan(replace(j,beds=(b,),rules=replace(j.rules,screw_spares_percent=0)),TODAY)
        screw=next(r for r in p['costs']['rows'] if r['category']=='screws')
        self.assertEqual(screw['needed'],24);self.assertEqual(screw['buy_quantity'],1)

    def test_unknown_cost_blocks_target_price(self):
        j=job();j=replace(j,costs=dict(j.costs,target_margin_bps=3000))
        self.assertIsNone(plan(j,TODAY)['costs']['internal_target_price_pence'])

    def test_margin_not_markup_and_labour_rounded(self):
        j=job();extras=[dict(id=i,description=d,quantity=1,unit='job',unit_price_pence=0) for i,d in REQUIRED_EXTRAS.items()]
        j=replace(j,costs={'extras':extras,'labour_minutes':1,'labour_rate_pence_per_hour':30,'target_margin_bps':2500})
        c=plan(j,TODAY)['costs'];self.assertTrue(c['is_complete'])
        self.assertEqual(c['known_subtotal_pence'],29461)
        self.assertEqual(c['internal_target_price_pence'],39282)

    def test_release_refuses_unreviewed_job(self):
        with self.assertRaisesRegex(PlanError,'release blocked'):plan(job(),TODAY,release=True)

    def reviewed(self):
        j=job()
        screws=tuple(replace(s,pilot_mode='none',pilot_evidence='Synthetic test record, not manufacturer advice',
                             pilot_evidence_kind='recorded_trial') for s in j.screws)
        j=replace(j,screws=screws)
        review={'timber_and_kerf_measured':True,'site_and_supports_reviewed':True,'fixing_schedule_reviewed':True,
                'reviewer':'TEST ONLY','reviewed_on':'2026-09-06','notes':'Synthetic test record, not build evidence.',
                'approved_physical_design_hash':physical_design_hash(j)}
        return replace(j,review=review)

    def test_release_requires_pilot_confirmation_even_if_other_flags_true(self):
        j=replace(self.reviewed(),screws=job().screws)
        with self.assertRaisesRegex(PlanError,'mark-out only'):plan(j,TODAY,release=True)

    def test_recorded_review_release(self):
        p=plan(self.reviewed(),TODAY,release=True)
        self.assertEqual(p['status'],'REVIEWED_WORKSHOP_PLAN')

    def test_out_of_scope_sites_block_release(self):
        for site in ('hard_surface','slope','retaining','roof_or_deck'):
            j=self.reviewed();j=replace(j,beds=(replace(j.beds[0],site_type=site),))
            with self.subTest(site=site),self.assertRaisesRegex(PlanError,'outside v1'):plan(j,TODAY,release=True)

    def test_height_limit_not_mislabeled_as_strength(self):
        j=self.reviewed();j=replace(j,beds=(replace(j.beds[0],courses=4),))
        with self.assertRaisesRegex(PlanError,'600 mm'):plan(j,TODAY,release=True)

    def test_release_requires_design_approval_hash(self):
        j=self.reviewed()
        j=replace(j,review={k:v for k,v in j.review.items() if k!='approved_physical_design_hash'})
        with self.assertRaisesRegex(PlanError,'approved_physical_design_hash'):plan(j,TODAY,release=True)

    def test_missing_approval_blocks_draft_and_check_not_just_release(self):
        j=self.reviewed()
        j=replace(j,review={k:v for k,v in j.review.items() if k!='approved_physical_design_hash'})
        p=plan(j,TODAY)
        self.assertFalse(p['release_ready'])
        self.assertFalse(p['review_gate_clear'])
        self.assertIn('approval_hash_required',{i['code'] for i in p['issues']})

    def test_fixture_evidence_cannot_issue_even_with_matching_hash(self):
        j=self.reviewed()
        screws=tuple(replace(s,pilot_mode='pilot',pilot_diameter_mm=5,pilot_depth_mm=100,
                             pilot_evidence='DEMONSTRATION PLACEHOLDER - NOT REAL EVIDENCE',
                             pilot_evidence_kind='fixture') for s in j.screws)
        j=replace(j,screws=screws,review=dict(j.review,approved_physical_design_hash=physical_design_hash(replace(j,screws=screws))))
        with self.assertRaisesRegex(PlanError,'DEMONSTRATION FIXTURE'):plan(j,TODAY,release=True)

    def test_recorded_trial_evidence_can_release(self):
        j=self.reviewed()
        screws=tuple(replace(s,pilot_mode='pilot',pilot_diameter_mm=5,pilot_depth_mm=100,
                             pilot_evidence='Recorded physical trial on scrap, 2026-09-06',
                             pilot_evidence_kind='recorded_trial') for s in j.screws)
        j=replace(j,screws=screws,review=dict(j.review,approved_physical_design_hash=physical_design_hash(replace(j,screws=screws))))
        p=plan(j,TODAY,release=True)
        self.assertEqual(p['status'],'REVIEWED_WORKSHOP_PLAN')

    def test_stale_approval_cannot_authorise_changed_design(self):
        j=self.reviewed()
        j=replace(j,beds=(replace(j.beds[0],length_mm=2200),))
        p=plan(j,TODAY)
        self.assertIn('stale_approval',{i['code'] for i in p['issues']})
        with self.assertRaisesRegex(PlanError,'does not match this physical design'):plan(j,TODAY,release=True)

    def test_price_only_change_keeps_physical_approval(self):
        j=self.reviewed()
        j=replace(j,stocks=tuple(replace(s,price_pence=s.price_pence+7) if not s.inventory else s for s in j.stocks))
        p=plan(j,TODAY,release=True)
        self.assertEqual(p['status'],'REVIEWED_WORKSHOP_PLAN')

    def test_machining_change_invalidates_approval(self):
        j=self.reviewed()
        j=replace(j,screws=tuple(replace(s,length_mm=s.length_mm+50) for s in j.screws))
        with self.assertRaisesRegex(PlanError,'does not match this physical design'):plan(j,TODAY,release=True)

    def test_repricing_cannot_swap_hardware_between_competing_screws(self):
        j=self.reviewed()
        base=next(s for s in j.screws if s.length_mm==150)
        rival=replace(base,id=base.id+'-rival',diameter_mm=9,pack_price_pence=base.pack_price_pence+1)
        j=replace(j,screws=tuple(sorted((*j.screws,rival),key=lambda s:s.id)))
        chosen_first=plan(j,TODAY)['fixings'][0]['screw_id']
        repriced=replace(j,screws=tuple(replace(s,pack_price_pence=s.pack_price_pence*4) if s.id==base.id else s for s in j.screws))
        chosen_after=plan(repriced,TODAY)['fixings'][0]['screw_id']
        self.assertEqual(chosen_first,chosen_after)
        self.assertEqual(plan(j,TODAY)['physical_design_hash'],plan(repriced,TODAY)['physical_design_hash'])

    def test_commercial_rules_do_not_change_physical_hash(self):
        j=self.reviewed()
        j2=replace(j,rules=replace(j.rules,screw_spares_percent=50,price_max_age_days=7))
        self.assertEqual(physical_design_hash(j),physical_design_hash(j2))
        self.assertNotEqual(plan(j,TODAY)['input_sha256'],plan(j2,TODAY)['input_sha256'])

    def test_head_seat_warning_present_when_stacked_absent_single_course(self):
        stacked=plan(job(),TODAY)
        self.assertIn('head_seat_unmodeled',{i['code'] for i in stacked['issues']})
        j=job();single=replace(j,beds=(replace(j.beds[0],courses=1),))
        self.assertNotIn('head_seat_unmodeled',{i['code'] for i in plan(single,TODAY)['issues']})

    def test_demo_fixtures_are_marked_as_demonstrations(self):
        import json
        catalogue=json.loads((ROOT/'catalogues/wickes-reviewed-2026-09-06.json').read_text(encoding='utf-8'))
        self.assertIn('DEMONSTRATION',catalogue['supplier_note'])
        for s in catalogue['screws']:
            if s.get('pilot_mode')=='pilot':
                self.assertIn('NOT REAL EVIDENCE',s['pilot_evidence'])
        example=json.loads((ROOT/'examples/reviewed-example.json').read_text(encoding='utf-8'))
        self.assertIn('DEMONSTRATION ONLY',example['review']['notes'])
        self.assertNotEqual(example['review']['reviewer'],'Jake')

    def test_hash_deterministic(self):
        self.assertEqual(plan(job(),TODAY),plan(job(),TODAY))

    def test_hash_changes_when_kerf_changes(self):
        j=job();j2=replace(j,rules=replace(j.rules,kerf_mm=4))
        self.assertNotEqual(plan(j,TODAY)['input_sha256'],plan(j2,TODAY)['input_sha256'])

    def test_stale_prices_visible(self):
        from datetime import date
        p=plan(job(),date(2026,12,1))
        self.assertIn('stale_price',{i['code'] for i in p['issues']})

    def test_inventory_proposal_never_mutates_input(self):
        j=load_job(ROOT/'examples/with-offcut.json');before=j.stocks
        p=plan(j,TODAY);self.assertEqual(before,j.stocks)
        self.assertTrue(p['inventory_proposal']['apply_only_after_job_completed'])
        self.assertIn('inventory_value',p['costs']['unpriced_items'])

if __name__=='__main__':unittest.main()
