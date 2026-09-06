"""Portable CLI: python -m sleeperplan. No account, API key, server or LLM."""
from __future__ import annotations
import argparse
from dataclasses import replace
from datetime import date
from pathlib import Path
import shutil
import sys
import tempfile
from . import __version__
from .config import load_job
from .costing import pounds
from .drawing import comparison_scene
from .export import export_plan, write_json, csv_rows
from .model import PlanError
from .planner import plan


def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(prog='sleeperplan',description='Offline sleeper flower-bed workshop planner. Dimensions in mm; money in pence.')
    p.add_argument('--version',action='version',version=__version__)
    commands=p.add_subparsers(dest='command',required=True)
    for name in ('plan','check','compare'):
        sub=commands.add_parser(name)
        sub.add_argument('job',type=Path,help='JSON job file; catalogue path is relative to this file')
        sub.add_argument('--catalogue',type=Path,help='Optional catalogue override, relative to current directory')
        sub.add_argument('--as-of',type=date.fromisoformat,default=date.today(),help='YYYY-MM-DD for reproducible price-age checks')
        if name!='check':
            sub.add_argument('--out',required=True,type=Path,help='New output directory; existing directories are refused')
            sub.add_argument('--pdf',action='store_true',help='Also create optional PDF(s); requires ReportLab')
        if name=='compare':
            sub.add_argument('--courses',nargs='+',type=int,default=[2,3],help='Independent height alternatives, default: 2 3')
        else:
            sub.add_argument('--release',action='store_true',help='Require recorded site/fixing/measurement checks and confirmed pilot specs')
    return p


def summary(result: dict) -> str:
    cp=result['cut_plan'];cost=result['costs']
    return (f"{result['status']} | {len(result['beds'])} bed(s) | {len(result['pieces'])} pieces | {len(result['fixings'])} fixing entries\n"
            f"Buy {cp['purchased_sleepers']} sleepers; {cp['saw_cuts']} saw cuts; cutting={cp['algorithm']}\n"
            f"Timber + screws: {pounds(cost['timber_and_screw_purchase_pence'])}\n"
            f"Known subtotal: {pounds(cost['known_subtotal_pence'])}; complete cost: {pounds(cost['complete_cost_pence'])}\n"
            f"{sum(i['blocking'] for i in result['issues'])} review blocker(s); plan {result['input_sha256'][:16]}")


def compare(args,job):
    heights=list(dict.fromkeys(args.courses))
    if len(heights)<2 or len(heights)>4 or any(not 1<=n<=6 for n in heights):
        raise PlanError('Compare 2-4 distinct alternatives, each between 1 and 6 courses')
    if args.out.exists() or args.out.is_symlink():
        raise PlanError(f'Output already exists: {args.out}; use a new folder')
    variants=[]
    for n in heights:
        beds=tuple(replace(b,courses=n) for b in job.beds)
        if any(b.freeboard_mm>=n*job.profile.height_mm for b in beds):
            raise PlanError('Freeboard exceeds an alternative height')
        # Old sign-offs cannot silently authorise a modified geometry.
        modified=replace(job,beds=beds,review={})
        variants.append(plan(modified,args.as_of))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    tmp=Path(tempfile.mkdtemp(prefix='.sleeperplan-compare-',dir=args.out.parent))
    try:
        rows=[]
        for n,p in zip(heights,variants):
            export_plan(p,tmp/f'{n}-courses',pdf=args.pdf)
            rows.append({'courses':n,'height_mm':n*job.profile.height_mm,
                         'beds':len(p['beds']),'purchased_sleepers':p['cut_plan']['purchased_sleepers'],
                         'saw_cuts':p['cut_plan']['saw_cuts'],'fixing_entries':len(p['fixings']),
                         'timber_and_screws_pence':p['costs']['timber_and_screw_purchase_pence'],
                         'known_subtotal_pence':p['costs']['known_subtotal_pence'],
                         'complete_cost_pence':p['costs']['complete_cost_pence'],
                         'fill_litres':p['total_fill_litres'],'cutting_algorithm':p['cut_plan']['algorithm']})
        write_json(tmp/'comparison.json',{'note':'Independent alternative job totals, not cumulative purchases. Each reuses the same starting inventory without consuming it.', 'options':rows})
        csv_rows(tmp/'comparison.csv',rows,list(rows[0]))
        scenes=[]
        for b in job.beds:
            scene=comparison_scene(variants,b.id);scenes.append(scene)
            (tmp/f'{b.id}-height-comparison.svg').write_text(scene.svg(),encoding='utf-8')
        if args.pdf:
            from .pdf import write_scene_pdf
            write_scene_pdf(scenes,tmp/'height-comparison.pdf')
        if args.out.exists():raise PlanError('Output appeared during generation')
        tmp.rename(args.out)
    except Exception:
        shutil.rmtree(tmp,ignore_errors=True)
        raise
    for n,result in zip(heights,variants):
        print(f'\n{n} COURSES\n{summary(result)}')
    print(f'\nCreated {args.out}')


def main(argv: list[str] | None = None) -> int:
    args=parser().parse_args(argv)
    try:
        job=load_job(args.job,args.catalogue)
        if args.command=='compare':
            compare(args,job)
        else:
            result=plan(job,args.as_of,release=args.release)
            if args.command=='plan':
                export_plan(result,args.out,pdf=args.pdf)
            print(summary(result))
            if args.command=='check':
                for i in result['issues']:
                    print(f"{'BLOCKER' if i['blocking'] else 'NOTE'} {i['code']}: {i['message']}")
                if not result['review_gate_clear']:
                    return 3
            else:
                print(f'Created {args.out}')
        return 0
    except (PlanError,OSError) as exc:
        print(f'sleeperplan: {exc}',file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())
