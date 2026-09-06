import random
import unittest
from dataclasses import replace
from itertools import combinations
from sleeperplan.config import parse_job
from sleeperplan.geometry import bed_pieces,compile_geometry,contains,collide
from sleeperplan.model import Fixing,Piece,PlanError
from sleeperplan.planner import plan
from .helpers import job,inputs,TODAY

class GeometryTests(unittest.TestCase):
    def test_alternating_exact_lengths(self):
        j=job();_,ps,_=compile_geometry(j)
        self.assertEqual(sorted(p.length_mm for p in ps if p.course==1),[1000,1000,2400,2400])
        self.assertEqual(sorted(p.length_mm for p in ps if p.course==2),[1200,1200,2200,2200])
        self.assertEqual(sorted(p.length_mm for p in ps if p.course==3),[1000,1000,2400,2400])

    def test_all_sections_uniform(self):
        _,ps,_=compile_geometry(job())
        self.assertEqual({(p.thickness_mm,p.height_mm) for p in ps},{(100,200)})

    def test_cavity_and_fill(self):
        b=plan(job(),TODAY)['beds'][0]
        self.assertEqual((b['inside_length_mm'],b['inside_width_mm'],b['height_mm']),(2200,1000,600))
        self.assertEqual(b['fill_litres'],1210)
        self.assertEqual(b['diagonal_mm'],2683.3)

    def test_52_fixing_entries(self):
        _,_,fs=compile_geometry(job())
        self.assertEqual(len(fs),52)
        self.assertEqual(sum(f.kind=='corner' for f in fs),24)
        self.assertEqual(sum(f.kind=='stack' for f in fs),28)

    def test_first_course_never_screws_down_into_ground(self):
        _,_,fs=compile_geometry(job())
        self.assertFalse(any(f.kind=='stack' and f.course==1 for f in fs))

    def test_all_screw_tips_in_named_receiver(self):
        _,ps,fs=compile_geometry(job());by_id={p.id:p for p in ps}
        for f in fs:
            with self.subTest(f=f.id):
                self.assertTrue(contains(by_id[f.receiver_id],f.tip_mm))
                self.assertTrue(contains(by_id[f.piece_id],f.entry_mm))

    def test_screw_paths_are_pairwise_clear(self):
        j=job();_,_,fs=compile_geometry(j)
        for a,b in combinations(fs,2):
            self.assertFalse(collide(a,b,j.rules.metal_clearance_mm),(a.id,b.id))

    def test_local_world_roundtrip(self):
        _,ps,fs=compile_geometry(job());by_id={p.id:p for p in ps}
        for f in fs:
            self.assertEqual(by_id[f.piece_id].world(*f.local_mm),f.entry_mm)

    def test_corner_entry_faces_not_end_faces(self):
        _,ps,fs=compile_geometry(job());by_id={p.id:p for p in ps}
        for f in fs:
            if f.kind=='corner':
                p=by_id[f.piece_id]
                self.assertEqual(f.local_mm[1],0 if p.side in ('S','W') else p.thickness_mm)
                self.assertIn(f.local_mm[2],(50,150))

    def test_stack_fixings_stagger_between_courses(self):
        _,_,fs=compile_geometry(job())
        xy2={f.entry_mm[:2] for f in fs if f.kind=='stack' and f.course==2}
        xy3={f.entry_mm[:2] for f in fs if f.kind=='stack' and f.course==3}
        self.assertFalse(xy2 & xy3)

    def test_stack_screws_have_correct_penetration(self):
        _,_,fs=compile_geometry(job())
        for f in fs:
            self.assertEqual(f.penetration_mm,50)
            self.assertEqual(f.screw_length_mm,250 if f.kind=='stack' else 150)

    def test_flat_orientation_swaps_hardware_lengths(self):
        raw,cat=inputs();raw['orientation']='flat'
        j=parse_job(raw,cat);beds,_,fs=compile_geometry(j)
        self.assertEqual(beds[0]['height_mm'],300)
        self.assertEqual(beds[0]['inside_width_mm'],800)
        for f in fs:
            self.assertEqual(f.screw_length_mm,150 if f.kind=='stack' else 250)

    def test_multiple_beds_have_unique_parts_and_fixings(self):
        j=job();j=replace(j,beds=(replace(j.beds[0],quantity=3),))
        beds,ps,fs=compile_geometry(j)
        self.assertEqual(len(beds),3)
        self.assertEqual(len(ps),len({p.id for p in ps}))
        self.assertEqual(len(fs),len({f.id for f in fs}))

    def test_long_through_option_is_not_silently_interlocked(self):
        j=job();j=replace(j,beds=(replace(j.beds[0],corner_pattern='long_through'),))
        _,ps,_=compile_geometry(j)
        self.assertEqual({p.length_mm for p in ps if p.axis=='X'},{2400})
        self.assertIn('aligned_corners',{i['code'] for i in plan(j,TODAY)['issues']})

    def test_absent_long_screws_fail_not_shorten(self):
        j=job();j=replace(j,screws=tuple(s for s in j.screws if s.length_mm==150))
        with self.assertRaises(PlanError):compile_geometry(j)

    def test_seeded_ring_geometry_invariants_200_cases(self):
        rng=random.Random(3721);j=job()
        for _ in range(200):
            L,W=rng.randint(700,2400),rng.randint(600,1800)
            b=replace(j.beds[0],length_mm=L,width_mm=W,courses=rng.randint(1,6))
            ps=bed_pieces(b,'test',100,200)
            self.assertEqual(sum(p.length_mm*100*200 for p in ps),(L*W-(L-200)*(W-200))*200*b.courses)

    def test_seeded_fixing_geometry_40_cases(self):
        rng=random.Random(2391);base=job()
        for case in range(40):
            b=replace(base.beds[0],length_mm=rng.randint(1200,2400),width_mm=rng.randint(800,1600),courses=rng.randint(1,3))
            j=replace(base,beds=(b,));_,_,fs=compile_geometry(j)
            for a,c in combinations(fs,2):
                self.assertFalse(collide(a,c,j.rules.metal_clearance_mm),(case,a.id,c.id))

if __name__=='__main__':unittest.main()
