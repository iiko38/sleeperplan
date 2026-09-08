"""Independent transcription/check of the pinned Sleeperplan offer geometry.

Not the repository's planner and not a connection-strength calculation.
This deliberately supports only the reviewed 2400 x 1400, long-through example.
All pilot and head-seat instructions remain UNCONFIRMED.
"""
from __future__ import annotations
import csv
import hashlib
import json
from itertools import combinations
from math import sqrt
from pathlib import Path

COMMIT = '37db13b378fc868f2d4e6b73f8ba19f6e5f4b526'
DATE = '2026-09-08'
MODEL = dict(length_mm=2400, width_mm=1400, thickness_mm=100, course_height_mm=200,
             freeboard_mm=50, corner_pattern='long_through', kerf_mm=3,
             source_commit=COMMIT, source_input='examples/first-model-2400x1400.json')
MODEL_HASH = hashlib.sha256(json.dumps(MODEL, sort_keys=True).encode()).hexdigest()


def make_plan(n: int) -> dict:
    if type(n) is not int or n not in (1, 2, 3):
        raise ValueError('This review model supports 1, 2 or 3 courses only.')
    pieces, fixings = [], []
    for course in range(1, n+1):
        z = 200*(course-1)
        for side, x, y, length, axis in [('S',0,0,2400,'X'),('N',0,1300,2400,'X'),
                                        ('W',0,100,1200,'Y'),('E',2300,100,1200,'Y')]:
            pid = f'first-bed-01-C{course}-{side}'
            dx, dy = (length,100) if axis == 'X' else (100,length)
            piece = dict(id=pid, course=course, side=side, axis=axis, x=x,y=y,z=z,
                         length=length, thickness=100, height=200,
                         box=[[x,x+dx],[y,y+dy],[z,z+200]])
            pieces.append(piece)
            seq=0
            if side in ('S','N'):
                for u in (50,2350):
                    for w in (50,150):
                        seq+=1
                        v=0 if side=='S' else 100
                        entry=[x+u,y+v,z+w]
                        direction=[0,1 if side=='S' else -1,0]
                        rec=f'first-bed-01-C{course}-'+('W' if u==50 else 'E')
                        fixings.append(dict(id=f'{pid}-F{seq:02}',piece_id=pid,receiver_id=rec,
                            course=course,side=side,kind='corner',face='OUTER',u=u,v=v,w=w,
                            screw_id='wickes-287686',screw_length=150,diameter=7,through=100,
                            penetration=50,entry=entry,direction=direction,
                            tip=[entry[i]+150*direction[i] for i in range(3)],
                            pilot_mode='unconfirmed',pilot_diameter_mm=None,pilot_depth_mm=None,
                            head_seat='unconfirmed'))
            if course>1:
                base=[200,700,1200,1700,2200] if axis=='X' else [200,600,1000]
                shift=40 if course==3 else 0
                for u0 in base:
                    seq+=1; u=u0+shift
                    entry=[x+u,y+50,z+200] if axis=='X' else [x+50,y+u,z+200]
                    fixings.append(dict(id=f'{pid}-F{seq:02}',piece_id=pid,
                        receiver_id=f'first-bed-01-C{course-1}-{side}',course=course,side=side,
                        kind='stack',face='TOP',u=u,v=50,w=200,
                        screw_id='wickes-287688',screw_length=250,diameter=7,through=200,
                        penetration=50,entry=entry,direction=[0,0,-1],
                        tip=[entry[0],entry[1],entry[2]-250],pilot_mode='unconfirmed',
                        pilot_diameter_mm=None,pilot_depth_mm=None,head_seat='unconfirmed'))
    fixings.sort(key=lambda f: f['id'])
    need_a,need_b=8*n,16*(n-1)
    def packs(need):
        return (((need*110+99)//100)+24)//25
    cost=10400*n+900*packs(need_a)+1230*packs(need_b)
    return dict(**MODEL,courses=n,height_mm=n*200,inside_length_mm=2200,inside_width_mm=1200,
                fill_litres=2200*1200*(n*200-50)/1_000_000,diagonal_mm=round(sqrt(2400**2+1400**2),1),
                status='DRAFT_MARK_OUT_ONLY',review_model_sha256=MODEL_HASH,
                pieces=pieces,fixings=fixings,need_a=need_a,need_b=need_b,
                packs_a=packs(need_a),packs_b=packs(need_b),purchased_sleepers=4*n,
                stock_2400=2*n,stock_1800=2*n,saw_cuts=2*n,timber_and_screws_pence=cost,
                cost_basis='Repository catalogue dated 2026-09-06; 10% screws allowance; not an installed price.')


def contains(box, pt):
    return all(a-1e-7<=v<=b+1e-7 for (a,b),v in zip(box,pt))


def segment_distance(a, b):
    squared=0
    for i in range(3):
        alo,ahi=sorted((a['entry'][i],a['tip'][i]))
        blo,bhi=sorted((b['entry'][i],b['tip'][i]))
        gap=max(0,blo-ahi,alo-bhi)
        squared+=gap*gap
    return sqrt(squared)


def verify(plan: dict) -> dict:
    ps={p['id']:p for p in plan['pieces']}
    checks=0
    def require(value, msg):
        nonlocal checks
        checks+=1
        if not value: raise AssertionError(msg)
    n=plan['courses']
    require(len(ps)==4*n,'Part count')
    require(len(plan['fixings'])==(8,32,56)[n-1],'Fixing count')
    for c in range(1,n+1):
        layer=[p for p in ps.values() if p['course']==c]
        require(sum(p['length']*100 for p in layer)==2400*1400-2200*1200,'Ring area')
        for a,b in combinations(layer,2):
            overlap=all(min(x[1],y[1])>max(x[0],y[0]) for x,y in zip(a['box'],b['box']))
            require(not overlap,'Timber overlap')
    for f in plan['fixings']:
        require(contains(ps[f['piece_id']]['box'],f['entry']),'Entry inside through-member')
        near=[f['entry'][i]+(f['through']-.01)*f['direction'][i] for i in range(3)]
        far=[f['entry'][i]+(f['through']+.01)*f['direction'][i] for i in range(3)]
        require(contains(ps[f['piece_id']]['box'],near),'Through-member path')
        require(contains(ps[f['receiver_id']]['box'],far),'Receiver begins at joint')
        require(contains(ps[f['receiver_id']]['box'],f['tip']),'Tip stays inside receiver')
        require(f['pilot_mode']=='unconfirmed','No invented drilling approval')
    distances=[segment_distance(a,b) for a,b in combinations(plan['fixings'],2)]
    for d in distances: require(d>=19-1e-7,'Modelled shaft clearance: 7 mm diameter + 12 mm extra')
    for p in ps.values():
        us=sorted(f['u'] for f in plan['fixings'] if f['piece_id']==p['id'] and f['kind']=='stack')
        for a,b in zip(us,us[1:]): require(b-a<=600,'Stack spacing')
    require(plan['fill_litres']==(396,924,1452)[n-1],'Fill volume')
    require(plan['timber_and_screws_pence']==(11300,22930,35460)[n-1],'Known material cost')
    require(1200+3+597==1800,'One cross-member stock conservation')
    require(2*1200+3>2400,'Two 1200 parts do not fit nominal 2400 with kerf')
    return dict(courses=n,assertions=checks,parts=len(ps),fixings=len(plan['fixings']),
                shaft_pairs=len(distances),minimum_centreline_distance_mm=min(distances),
                status='PASS',scope='Independent transcription checks; no upstream test run or physical validation.')


def export(folder: Path) -> list[dict]:
    folder.mkdir(parents=True,exist_ok=True)
    plans=[make_plan(n) for n in (1,2,3)]
    reports=[verify(p) for p in plans]
    (folder/'review_data.json').write_text(json.dumps(dict(model=MODEL,plans=plans,checks=reports),indent=2)+'\n')
    (folder/'independent_checks.json').write_text(json.dumps(reports,indent=2)+'\n')
    fields=['id','piece_id','receiver_id','course','side','kind','face','u','v','w',
            'screw_id','screw_length','diameter','through','penetration','pilot_mode',
            'pilot_diameter_mm','pilot_depth_mm','head_seat']
    with (folder/'mark_out_2400x1400_three_courses.csv').open('w',newline='') as fh:
        wr=csv.DictWriter(fh,fieldnames=fields,extrasaction='ignore');wr.writeheader();wr.writerows(plans[-1]['fixings'])
    return reports

if __name__=='__main__':
    print(json.dumps(export(Path(__file__).resolve().parents[1]),indent=2))
