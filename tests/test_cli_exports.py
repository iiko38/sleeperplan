import csv
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from sleeperplan.drawing import iso_scene,layer_scene,piece_scene,comparison_scene,scad_model
from sleeperplan.export import export_plan,csv_rows
from sleeperplan.model import PlanError
from sleeperplan.planner import plan
from .helpers import job,TODAY,ROOT

class PublicationTests(unittest.TestCase):
    """F01: the public tree must never distribute demonstration evidence as an
    issued plan, and every published bundle must carry a consistent identity."""

    PUBLIC_ROOTS=[ROOT/'published',ROOT/'site'/'demo']

    def plans(self):
        for root in self.PUBLIC_ROOTS:
            for p in sorted(root.rglob('plan.json')):
                yield p

    def test_public_tree_contains_no_issued_plans(self):
        for p in self.plans():
            with self.subTest(path=str(p)):
                d=json.loads(p.read_text(encoding='utf-8'))
                self.assertNotEqual(d.get('status'),'REVIEWED_WORKSHOP_PLAN',
                                    'demonstration/fixture-based outputs must stay drafts in the public tree')

    def test_published_manifest_matches_plan_identity(self):
        root=ROOT/'published'
        manifests=list(root.rglob('web-manifest.json'))
        self.assertTrue(manifests,'published/ must contain at least one tracked bundle')
        for m in manifests:
            with self.subTest(manifest=str(m)):
                d=json.loads(m.read_text(encoding='utf-8'))
                plan=json.loads((m.parent/d['artifacts']['plan']).read_text(encoding='utf-8'))
                self.assertEqual(d['plan_sha256'],plan['input_sha256'])

    def test_published_pack_has_operations_schedule(self):
        root=ROOT/'published'
        ops=list(root.rglob('operations.json'))
        self.assertTrue(ops,'published bundles must ship the compiled operation schedule')
        for o in ops:
            with self.subTest(ops=str(o)):
                d=json.loads(o.read_text(encoding='utf-8'))
                plan=json.loads((o.parent/'plan.json').read_text(encoding='utf-8'))
                self.assertEqual(d['schema'],'sleeperplan.operations.v1')
                self.assertEqual(d['plan_sha256'],plan['input_sha256'])
                self.assertGreaterEqual(len(d['operations']),1)


    @classmethod
    def setUpClass(cls):cls.p=plan(job(),TODAY)

    def test_svg_is_valid_xml(self):
        p=self.p;b=p['beds'][0]
        scenes=[iso_scene(p,b),layer_scene(p,b,2),piece_scene(p,p['pieces'][4]),comparison_scene([p,p],'front')]
        for s in scenes:self.assertEqual(ET.fromstring(s.svg()).tag,'{http://www.w3.org/2000/svg}svg')

    def test_export_complete_and_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/'a',Path(tmp)/'b';export_plan(self.p,a);export_plan(self.p,b)
            for f in a.rglob('*'):
                if f.is_file():self.assertEqual(f.read_bytes(),(b/f.relative_to(a)).read_bytes())
            self.assertTrue((a/'plan.json').exists());self.assertTrue((a/'model.scad').exists())
            self.assertTrue((a/'web-manifest.json').exists());self.assertTrue((a/'quality-report.json').exists())
            self.assertEqual(len(list((a/'drawings').glob('*fixings.svg'))),12)
            with (a/'parts.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
            self.assertEqual(len(rows),12);self.assertTrue(all(r['stock_board'] for r in rows))
            manifest=json.loads((a/'web-manifest.json').read_text(encoding='utf-8'))
            quality=json.loads((a/'quality-report.json').read_text(encoding='utf-8'))
            self.assertEqual(manifest['schema'],'sleeperplan.web_manifest.v1')
            self.assertEqual(quality['schema'],'sleeperplan.quality_report.v1')
            self.assertIn('viewer',manifest)
            self.assertIn('camera',manifest['viewer'])
            self.assertEqual(len(manifest['viewer']['camera']['target_mm']),3)
            self.assertEqual(len(manifest['viewer']['camera']['position_mm']),3)
            self.assertTrue(quality['checks']['manual_sections_complete'])
            self.assertTrue(quality['checks']['drawings_match_expected'])
            self.assertTrue(quality['checks']['piece_callouts_cover_all_fixing_pieces'])

    def test_existing_output_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(PlanError):export_plan(self.p,tmp)

    def test_csv_formula_injection_protection(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'data.csv';csv_rows(path,[{'label':'=2+2','number':-1}],['label','number'])
            with path.open(encoding='utf-8-sig',newline='') as f:r=next(csv.DictReader(f))
            self.assertEqual(r['label'],"'=2+2");self.assertEqual(r['number'],'-1')

    def test_scad_uses_model_dimensions(self):
        scad=scad_model(self.p)
        self.assertIn('cube([2400, 100, 200])',scad)
        self.assertIn('explode_mm = 0',scad)
        self.assertIn('front-01-C3-S',scad)

    @unittest.skipUnless(importlib.util.find_spec('reportlab'),'Optional PDF dependency absent')
    def test_optional_pdf_generation(self):
        from sleeperplan.pdf import write_workshop_pdf
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/'a.pdf',Path(tmp)/'b.pdf'
            write_workshop_pdf(self.p,a);write_workshop_pdf(self.p,b)
            self.assertTrue(a.read_bytes().startswith(b'%PDF'))
            self.assertEqual(a.read_bytes(),b.read_bytes())

    @unittest.skipUnless(importlib.util.find_spec('reportlab'),'Optional PDF dependency absent')
    def test_options_pdf_covers_each_height(self):
        from dataclasses import replace
        from sleeperplan.pdf import write_options_pdf
        base=job()
        heights=[1,3]
        variants=[plan(replace(base,beds=tuple(replace(b,courses=n) for b in base.beds)),TODAY) for n in heights]
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/'a.pdf',Path(tmp)/'b.pdf'
            write_options_pdf(variants,heights,a,job_name=base.name)
            write_options_pdf(variants,heights,b,job_name=base.name)
            self.assertTrue(a.read_bytes().startswith(b'%PDF'))
            self.assertEqual(a.read_bytes(),b.read_bytes())

class CLITests(unittest.TestCase):
    def run_cli(self,*args):
        return subprocess.run([sys.executable,'-m','sleeperplan',*map(str,args)],cwd=ROOT,capture_output=True,text=True,timeout=30)

    def test_help(self):self.assertEqual(self.run_cli('--help').returncode,0)
    def test_version(self):self.assertEqual(self.run_cli('--version').stdout.strip(),'0.3.0')
    def test_check_draft_has_distinct_exit_code(self):self.assertEqual(self.run_cli('check','examples/neighbour.json','--as-of','2026-09-06').returncode,3)

    def test_bad_job_returns_clean_error(self):
        r=self.run_cli('check','does-not-exist.json')
        self.assertEqual(r.returncode,2);self.assertNotIn('Traceback',r.stderr)

    def test_release_fails_without_leaving_partial_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'pack'
            r=self.run_cli('plan','examples/neighbour.json','--out',out,'--release')
            self.assertEqual(r.returncode,2);self.assertFalse(out.exists())

    def test_compare_generates_independent_alternatives(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'compare'
            r=self.run_cli('compare','examples/neighbour.json','--courses',2,3,'--out',out,'--as-of','2026-09-06')
            self.assertEqual(r.returncode,0,r.stderr)
            comp=json.loads((out/'comparison.json').read_text())['options']
            self.assertEqual([x['height_mm'] for x in comp],[400,600])
            self.assertEqual([x['purchased_sleepers'] for x in comp],[6,9])
            self.assertEqual([x['timber_and_screws_pence'] for x in comp],[18930,29460])
            self.assertTrue((out/'front-height-comparison.svg').exists())

if __name__=='__main__':unittest.main()
