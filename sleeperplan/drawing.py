"""Small vector scene graph shared by SVG and PDF. Geometry is never re-invented here."""
from __future__ import annotations
from dataclasses import dataclass, field
from html import escape
from math import cos, pi
from .model import Piece

INK = "#183339"
MUTED = "#52666a"
ACCENT = "#147c80"
TIMBER = "#c69b6b"
PALE = "#edf3f1"
WARN = "#9d4e19"


@dataclass
class Scene:
    width: float
    height: float
    elements: list[dict] = field(default_factory=list)

    def text(self, x, y, value, size=15, colour=INK, anchor="start", bold=False, rotate=0):
        self.elements.append(dict(kind="text", x=x, y=y, value=str(value), size=size,
                                  colour=colour, anchor=anchor, bold=bold, rotate=rotate))

    def line(self, x1, y1, x2, y2, colour=INK, width=1, dash=False):
        self.elements.append(dict(kind="line", x1=x1, y1=y1, x2=x2, y2=y2,
                                  colour=colour, width=width, dash=dash))

    def rect(self, x, y, w, h, fill="none", stroke=INK, width=1):
        self.elements.append(dict(kind="rect", x=x, y=y, w=w, h=h, fill=fill, stroke=stroke, width=width))

    def polygon(self, points, fill=TIMBER, stroke=INK, width=1):
        self.elements.append(dict(kind="polygon", points=points, fill=fill, stroke=stroke, width=width))

    def circle(self, x, y, r=4, fill="white", stroke=ACCENT, width=2):
        self.elements.append(dict(kind="circle", x=x, y=y, r=r, fill=fill, stroke=stroke, width=width))

    def svg(self) -> str:
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width:g}" height="{self.height:g}" viewBox="0 0 {self.width:g} {self.height:g}">',
               '<rect width="100%" height="100%" fill="white"/>']
        for e in self.elements:
            kind = e["kind"]
            if kind == "text":
                weight = "700" if e["bold"] else "400"
                transform = f' transform="rotate({e["rotate"]} {e["x"]} {e["y"]})"' if e["rotate"] else ""
                out.append(f'<text x="{e["x"]}" y="{e["y"]}" font-family="Arial,Helvetica,sans-serif" '
                           f'font-size="{e["size"]}" font-weight="{weight}" fill="{e["colour"]}" '
                           f'text-anchor="{e["anchor"]}"{transform}>{escape(e["value"])}</text>')
            elif kind == "line":
                dash = ' stroke-dasharray="6 4"' if e["dash"] else ""
                out.append(f'<line x1="{e["x1"]}" y1="{e["y1"]}" x2="{e["x2"]}" y2="{e["y2"]}" stroke="{e["colour"]}" stroke-width="{e["width"]}"{dash}/>')
            elif kind == "rect":
                out.append(f'<rect x="{e["x"]}" y="{e["y"]}" width="{e["w"]}" height="{e["h"]}" fill="{e["fill"]}" stroke="{e["stroke"]}" stroke-width="{e["width"]}"/>')
            elif kind == "circle":
                out.append(f'<circle cx="{e["x"]}" cy="{e["y"]}" r="{e["r"]}" fill="{e["fill"]}" stroke="{e["stroke"]}" stroke-width="{e["width"]}"/>')
            else:
                pts = " ".join(f"{x:g},{y:g}" for x, y in e["points"])
                out.append(f'<polygon points="{pts}" fill="{e["fill"]}" stroke="{e["stroke"]}" stroke-width="{e["width"]}"/>')
        return "\n".join(out+["</svg>", ""])


def number(n: float) -> str:
    return f"{n:g}" if float(n).is_integer() else f"{n:.1f}"


def header(s: Scene, title: str, subtitle: str):
    s.rect(0, 0, s.width, 6, ACCENT, ACCENT)
    s.text(30, 43, title, min(25, (s.width-60)/max(1, len(title)*0.56)), bold=True)
    s.text(30, 69, subtitle, 14, MUTED)


def dimensions(s: Scene, x1, y1, x2, y2, label: str, vertical=False):
    s.line(x1, y1, x2, y2, MUTED)
    if vertical:
        s.line(x1-5,y1,x1+5,y1,MUTED)
        s.line(x2-5,y2,x2+5,y2,MUTED)
        s.text(x1-12, (y1+y2)/2, label, 15, MUTED, "middle", rotate=-90)
    else:
        s.line(x1,y1-5,x1,y1+5,MUTED)
        s.line(x2,y2-5,x2,y2+5,MUTED)
        s.text((x1+x2)/2, y1-9, label, 15, MUTED, "middle")


def layer_scene(plan: dict, bed: dict, course: int) -> Scene:
    s = Scene(1100, 710)
    header(s, f"{bed['id']} / course {course} / plan view",
           f"{plan['status']}  |  All dimensions mm  |  Origin O = outside S/W corner  |  NOT a 1:1 template")
    L,W = bed["length_mm"],bed["width_mm"]
    scale = min(910/L, 450/W)
    ox, oy = (1100-L*scale)/2, 140
    s.rect(ox,oy,L*scale,W*scale,PALE,"none")
    ps = [Piece(**p) for p in plan["pieces"] if p["bed_id"]==bed["id"] and p["course"]==course]
    for p in ps:
        (x0,x1),(y0,y1),_ = p.box
        x,y = ox+x0*scale, oy+(W-y1)*scale
        w,h = (x1-x0)*scale,(y1-y0)*scale
        s.rect(x,y,w,h,TIMBER,INK,1.7)
        label = f"C{course}-{p.side} | {p.length_mm}"
        # Keep labels in the clear opening: a fixing dot must not hide its own part label.
        if p.side == "S":
            s.text(x+w/2, y-10, label, 13, INK, "middle", bold=True)
        elif p.side == "N":
            s.text(x+w/2, y+h+20, label, 13, INK, "middle", bold=True)
        elif p.side == "W":
            s.text(x+w+20, y+h/2, label, 13, INK, "middle", bold=True, rotate=-90)
        else:
            s.text(x-13, y+h/2, label, 13, INK, "middle", bold=True, rotate=-90)
        if p.axis=="X":
            s.text(x+8,y+h-7,"A",11,INK,bold=True)
        else:
            s.text(x+6,y+h-8,"A",11,INK,bold=True)
    seen=set()
    for f in plan["fixings"]:
        if f["bed_id"]!=bed["id"] or f["course"]!=course:
            continue
        x,y,_=f["entry_mm"]
        sx,sy=ox+x*scale,oy+(W-y)*scale
        if f["kind"]=="stack":
            s.circle(sx,sy,4)
        else:
            key=(x,y)
            if key in seen:
                continue
            seen.add(key)
            dx,dy,_=f["direction"]
            ex,ey=sx+dx*24,sy-dy*24
            s.line(sx-dx*12,sy+dy*12,ex,ey,ACCENT,2)
            s.circle(ex,ey,2,ACCENT,ACCENT,1)
    dimensions(s,ox,oy-30,ox+L*scale,oy-30,f"Outside {L}")
    dimensions(s,ox-32,oy,ox-32,oy+W*scale,f"Outside {W}",True)
    s.text(ox+L*scale/2,oy+W*scale/2-8,
           f"Clear opening {bed['inside_length_mm']} x {bed['inside_width_mm']}",18,INK,"middle",True)
    s.text(ox+L*scale/2,oy+W*scale/2+20,
           f"Outside diagonals: {bed['diagonal_mm']:g} mm (both equal)",15,MUTED,"middle")
    s.text(ox-4,oy+W*scale+22,"O",15,ACCENT,"middle",True)
    s.text(ox+L*scale/2,oy+W*scale+30,"S / +X runs left to right; +Y runs towards N",14,MUTED,"middle")
    s.text(30,648,"Circles = top fixing entries. Arrows = two corner screws at different heights.",15)
    s.text(30,674,"Piece sheets give the entry face, datum, coordinates and hardware. A is each piece's lower-X / lower-Y end.",14,MUTED)
    return s


def subtract_rect(rect: tuple, obstruction: tuple) -> list[tuple]:
    a,b,c,d=rect
    e,f,g,h=obstruction
    x0,x1,y0,y1=max(a,e),min(b,f),max(c,g),min(d,h)
    if x0>=x1 or y0>=y1:
        return [rect]
    out=[]
    if a<x0: out.append((a,x0,c,d))
    if x1<b: out.append((x1,b,c,d))
    if c<y0: out.append((x0,x1,c,y0))
    if y1<d: out.append((x0,x1,y1,d))
    return out


def visible_faces(pieces: list[Piece]):
    """Exposed positive-X/Y/Z faces; remove actual timber-to-timber contacts."""
    faces=[]
    colours=["#ae7f50", "#c79a67", "#e0bd8e"]
    for p in pieces:
        box=p.box
        for axis in range(3):
            plane=box[axis][1]
            other=[i for i in range(3) if i!=axis]
            patches=[(*box[other[0]],*box[other[1]])]
            for q in pieces:
                if q.id==p.id or q.box[axis][0]!=plane:
                    continue
                cover=(*q.box[other[0]],*q.box[other[1]])
                patches=[v for patch in patches for v in subtract_rect(patch,cover)]
            for a,b,c,d in patches:
                xyz=[]
                for u,v in ((a,c),(b,c),(b,d),(a,d)):
                    point=[0.0,0.0,0.0]
                    point[axis]=plane;point[other[0]]=u;point[other[1]]=v
                    xyz.append(tuple(point))
                faces.append((sum(sum(v) for v in xyz)/4,xyz,colours[axis]))
    return faces


def project(x,y,z):
    return cos(pi/6)*(x-y), (x+y)/2-z


def draw_iso(s: Scene, plan: dict, bed: dict, centre_x: float, base_y: float, scale: float):
    ps=[Piece(**p) for p in plan["pieces"] if p["bed_id"]==bed["id"]]
    L,W,H=bed["length_mm"],bed["width_mm"],bed["height_mm"]
    t=plan["profile"]["thickness_mm"]
    mid=cos(pi/6)*(L-W)/2
    def convert(v):
        px,py=project(*v)
        return centre_x+(px-mid)*scale,base_y+(py-(L+W)/2)*scale
    faces=visible_faces(ps)
    soil=[(t,t,H-bed['freeboard_mm']),(L-t,t,H-bed['freeboard_mm']),
          (L-t,W-t,H-bed['freeboard_mm']),(t,W-t,H-bed['freeboard_mm'])]
    faces.append((sum(sum(v) for v in soil)/4,soil,"#6f7660"))
    for _,vertices,fill in sorted(faces,key=lambda f:f[0]):
        s.polygon([convert(v) for v in vertices],fill,INK,1.25)
    a,b=convert((L,0,0)),convert((L,0,H))
    dimensions(s,a[0]+34,a[1],b[0]+34,b[1],f"{H} mm",True)


def iso_scene(plan: dict, bed: dict) -> Scene:
    s=Scene(1100,720)
    header(s,f"{bed['id']} / {bed['courses']} courses / assembled view",
           f"{plan['status']}  |  Same timber section throughout  |  Schematic colour, not a finish sample")
    L,W,H=bed['length_mm'],bed['width_mm'],bed['height_mm']
    scale=min(850/(cos(pi/6)*(L+W)),450/((L+W)/2+H))
    draw_iso(s,plan,bed,535,605,scale)
    s.text(30,652,f"Outside: {L} x {W} x {H} mm   |   Clear opening: {bed['inside_length_mm']} x {bed['inside_width_mm']} mm",17,bold=True)
    s.text(30,680,f"Geometric fill: {bed['fill_litres']:g} litres at {bed['freeboard_mm']} mm below the top. No settlement allowance.",15,MUTED)
    return s


def comparison_scene(plans: list[dict], design_id: str) -> Scene:
    bed_pairs=[(p,next(b for b in p['beds'] if b['design_id']==design_id)) for p in plans]
    width=700*len(plans)
    s=Scene(width,720)
    header(s,f"{design_id} / height alternatives at the SAME scale", "Draft alternatives, not cumulative purchases. Timber orientation and outside footprint are unchanged.")
    scale=min(min(530/(cos(pi/6)*(b['length_mm']+b['width_mm'])),430/((b['length_mm']+b['width_mm'])/2+b['height_mm'])) for _,b in bed_pairs)
    for i,(p,b) in enumerate(bed_pairs):
        centre=350+i*700
        draw_iso(s,p,b,centre,565,scale)
        s.text(centre,620,f"{b['courses']} courses / {b['height_mm']} mm high",24,INK,"middle",True)
        s.text(centre,653,f"{b['length_mm']} x {b['width_mm']} mm outside / {b['fill_litres']:g} litres fill",16,MUTED,"middle")
        if i:
            s.line(i*700,110,i*700,680,"#dbe4e2",1)
    return s


def cutting_scene(plan: dict, boards: list[dict]) -> Scene:
    s=Scene(1100,140+105*len(boards))
    header(s,"Stock allocation / cutting diagram", "Measure every kerf band from ORIGINAL stock datum A. Finished pieces are exact; this drawing is NOT to scale for tracing.")
    max_length=max(b['gross_length_mm'] for b in boards)
    scale=960/max_length
    for i,b in enumerate(boards):
        y=122+i*105
        s.text(30,y-15,f"{b['id']} | {b['stock_id']} | {b['gross_length_mm']} mm | {len(b['cuts'])} saw cuts | offcut {b['offcut_mm']} mm",15,bold=True)
        x0=60
        s.rect(x0,y,b['gross_length_mm']*scale,35,PALE,INK)
        for part in b['parts']:
            x=x0+part['start_mm']*scale;w=part['length_mm']*scale
            s.rect(x,y,w,35,TIMBER,INK)
            if w>110:
                s.text(x+w/2,y+22,part['piece_id'],12,INK,"middle",True)
            s.text(x+w/2,y+53,str(part['length_mm']),13,INK,"middle")
        for c in b['cuts']:
            s.rect(x0+c['kerf_start_mm']*scale,y,max(1.5,(c['kerf_end_mm']-c['kerf_start_mm'])*scale),35,WARN,WARN)
        s.text(38,y+22,"A",14,ACCENT,"middle",True)
        bands = "; ".join(f"{c['kerf_start_mm']}..{c['kerf_end_mm']}" for c in b['cuts'][:8])
        if len(b['cuts']) > 8:
            bands += "; more in cuts.csv"
        s.text(60, y+73, "Waste kerf bands from original A (mm): " + (bands or "none - use the sound full length"), 12, MUTED)
    s.text(30,s.height-14,"Exact saw band positions and blade-centre coordinates are in cuts.csv. Kerf widths here may be exaggerated for visibility.",13,MUTED)
    return s


def piece_scene(plan: dict, raw: dict) -> Scene:
    p=Piece(**raw)
    fix=[f for f in plan['fixings'] if f['piece_id']==p.id]
    s=Scene(1100,395+24*max(1,len(fix)))
    header(s,f"{p.id} / {p.length_mm} x {p.thickness_mm} x {p.height_mm} mm",
           f"{plan['status']}  |  Datum A = lower global {'X' if p.axis=='X' else 'Y'} end  |  Coordinates in mm, rounded to 0.1 for display")
    scale=950/p.length_mm
    x0=80
    top_y,top_h=112,55
    outer_y,outer_h=224,80
    s.text(30,100,"TOP FACE / U along length; V across width from its lower-coordinate edge",14,bold=True)
    s.rect(x0,top_y,950,top_h,PALE,INK)
    s.text(48,top_y+top_h/2+5,"A",16,ACCENT,"middle",True)
    s.text(x0,top_y+top_h+19,"V=0 edge",12,MUTED)
    s.text(30,211,f"OUTER FACE / U from A; W measured UP from bottom / side {p.side}",14,bold=True)
    s.rect(x0,outer_y,950,outer_h,TIMBER,INK)
    s.text(48,outer_y+outer_h/2+5,"A",16,ACCENT,"middle",True)
    for f in fix:
        u,v,w=f['local_mm']
        x=x0+u*scale
        if f['kind']=='stack':
            y=top_y+top_h*(1-v/p.thickness_mm)
        else:
            y=outer_y+outer_h*(1-w/p.height_mm)
        s.circle(x,y,4)
        s.text(x+8,y-5,f['id'].rsplit('-',1)[-1],12,ACCENT,bold=True)
    s.text(30,337,"Views intentionally stretch section depth for legibility. Use the coordinates below, not a ruler on this sheet.",13,MUTED)
    columns=[30,115,215,330,440,540,695]
    for x,label in zip(columns,["FIXING","FACE","U FROM A","V","W UP","SCREW","PILOT"]):
        s.text(x,366,label,12,MUTED,bold=True)
    s.line(30,374,1070,374,"#bdceca")
    for i,f in enumerate(fix):
        pilot="UNCONFIRMED - mark out only"
        if f['pilot_mode']=='none':pilot="No pilot (recorded instruction)"
        if f['pilot_mode']=='pilot':pilot=f"{f['pilot_diameter_mm']:g} mm x {f['pilot_depth_mm']} mm deep"
        values=[f['id'].rsplit('-',1)[-1],f['entry_face'],*[number(v) for v in f['local_mm']],
                f"{f['diameter_mm']} x {f['screw_length_mm']}",pilot]
        for x,value in zip(columns,values):
            s.text(x,394+i*24,value,13, WARN if "UNCONFIRMED" in value else INK)
    if not fix:
        s.text(30,397,"No screw entry points on this piece; it receives screws from adjoining members.",14,MUTED)
    return s


def scad_model(plan: dict) -> str:
    lines=["// Generated from plan.json; millimetres. Not a structural design.",
           "// Open in OpenSCAD. Increase explode_mm to inspect courses.",
           "explode_mm = 0;", "$fn = 24;", "show_fixing_paths = false;", ""]
    offsets={}
    cursor=0
    for b in plan['beds']:
        offsets[b['id']]=cursor
        cursor+=b['length_mm']+600
    for raw in plan['pieces']:
        p=Piece(**raw)
        (x0,x1),(y0,y1),(z0,z1)=p.box
        lines.extend([f"// {p.id}",f"translate([{x0+offsets[p.bed_id]}, {y0}, {z0}+{p.course-1}*explode_mm])",
                      f"  color([0.70,0.52,0.33]) cube([{x1-x0}, {y1-y0}, {z1-z0}]);"])
    for f in plan['fixings']:
        x,y,z=f['entry_mm'];dx,dy,dz=f['direction']
        rotation={(0,0,-1):"[180,0,0]",(0,1,0):"[-90,0,0]",(0,-1,0):"[90,0,0]",(1,0,0):"[0,90,0]",(-1,0,0):"[0,-90,0]"}[(dx,dy,dz)]
        lines.append(f"if (show_fixing_paths) translate([{x+offsets[f['bed_id']]}, {y}, {z}+{f['course']-1}*explode_mm]) "
                     f"rotate({rotation}) color([0.8,0.1,0.1]) cylinder(d={f['diameter_mm']}, h={f['screw_length_mm']});")
    return "\n".join(lines)+"\n"
