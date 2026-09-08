from __future__ import annotations
import json, math, csv, zipfile
from pathlib import Path
from xml.sax.saxutils import escape
import reportlab
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from review_model import make_plan, verify, export, COMMIT, DATE, MODEL_HASH

ROOT=Path(__file__).resolve().parents[1]
for name,file in [('Body','Lato-Regular.ttf'),('Bold','Lato-Bold.ttf'),('Heavy','Lato-Heavy.ttf')]:
    path=Path('/usr/share/fonts/truetype/lato')/file
    if path.exists(): pdfmetrics.registerFont(TTFont(name,str(path)))
    else:
        fallback=Path('/usr/share/fonts/truetype/dejavu')/('DejaVuSans.ttf' if name=='Body' else 'DejaVuSans-Bold.ttf')
        if not fallback.exists(): fallback=Path(reportlab.__file__).resolve().parent/'fonts'/('Vera.ttf' if name=='Body' else 'VeraBd.ttf')
        pdfmetrics.registerFont(TTFont(name,str(fallback)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Body',boldItalic='Bold')

W,H=landscape(A4)
INK='#173B38'; MUTED='#5B706C'; BG='#FBF9F4'; PALE='#EDF3EF'; TEAL='#187D72';
AMBER='#B7562C'; LIGHTAMBER='#F8E8DC'; BLUE='#3A739A'; RULE='#D3DDD5'; WHITE='#FFFFFF'; RED='#B5453A'
COURSE={1:'#D8AF78',2:'#82B4A5',3:'#D9947E'}
SCREW_CORNER='#B7562C'; SCREW_STACK='#3A739A'; GHOST='#DEE5DF'; DARK='#0F302D'
PLAN=make_plan(3)
assert verify(PLAN)['status']=='PASS'

class Book:
    def __init__(self,name,title,short):
        self.path=ROOT/name
        self.c=canvas.Canvas(str(self.path),pagesize=(W,H),invariant=1,pageCompression=1)
        self.c.setTitle(title); self.c.setAuthor('Sleeperplan')
        self.c.setSubject('DRAFT visual construction pack. Pilot and head-seat details remain unconfirmed.')
        self.n=0; self.short=short
    def page(self,kicker,title,sub='',status='DRAFT / VISUAL BUILD PACK'):
        if self.n:self.c.showPage()
        self.n+=1
        self.rect(0,0,W,H,BG)
        self.rect(0,0,W,6,TEAL)
        self.text(38,32,'SLEEPERPLAN',10,'Heavy',TEAL)
        self.text(W-38,32,self.short.upper(),9,'Bold',MUTED,'right')
        self.text(38,64,kicker.upper(),10,'Bold',TEAL)
        title_size=min(28,max(18,(W-78)/(max(1,len(title))*0.54)))
        self.text(38,95,title,title_size,'Heavy',INK)
        if sub:self.para(sub,38,108,W-76,11,MUTED,maxh=34)
        self.line(38,H-49,W-38,H-49,RULE,.8)
        self.text(38,H-31,status+'  •  2400 × 1400 × 600 mm  •  LONG-THROUGH',8.5,'Bold',AMBER)
        self.text(W-38,H-31,f'{self.n:02}',10,'Heavy',INK,'right')
        self.text(38,H-17,f'08 SEP 2026  |  commit {COMMIT[:7]}  |  millimetres unless noted  |  NOT A SCALE TEMPLATE',7.8,'Body',MUTED)
    def save(self): self.c.save()
    def text(self,x,y,s,size=12,font='Body',colour=INK,align='left'):
        self.c.setFillColor(HexColor(colour)); self.c.setFont(font,size)
        fn={'left':self.c.drawString,'right':self.c.drawRightString,'centre':self.c.drawCentredString}[align]
        fn(x,H-y,str(s))
    def para(self,s,x,y,w,size=12,colour=INK,bold=False,leading=None,maxh=None):
        st=ParagraphStyle('p',fontName='Bold' if bold else 'Body',fontSize=size,leading=leading or size*1.35,textColor=HexColor(colour),spaceAfter=0)
        p=Paragraph(s,st);_,h=p.wrap(w,1000)
        if maxh is not None and h>maxh+0.1: raise ValueError(f'Paragraph overflow p{self.n}: {h}>{maxh}: {s[:40]}')
        p.drawOn(self.c,x,H-y-h); return h
    def rect(self,x,y,w,h,fill=PALE,stroke=None,r=0,width=.8):
        self.c.setFillColor(HexColor(fill)); self.c.setLineWidth(width); self.c.setStrokeColor(HexColor(stroke or fill))
        if r:self.c.roundRect(x,H-y-h,w,h,r,fill=1,stroke=int(stroke is not None))
        else:self.c.rect(x,H-y-h,w,h,fill=1,stroke=int(stroke is not None))
    def line(self,x1,y1,x2,y2,colour=INK,width=1,dash=False):
        self.c.setStrokeColor(HexColor(colour));self.c.setLineWidth(width);self.c.setDash([5,4] if dash else [])
        self.c.line(x1,H-y1,x2,H-y2); self.c.setDash([])
    def poly(self,pts,fill,stroke=INK,width=.8):
        self.c.setFillColor(HexColor(fill));self.c.setStrokeColor(HexColor(stroke));self.c.setLineWidth(width)
        p=self.c.beginPath()
        for i,(x,y) in enumerate(pts):(p.moveTo if i==0 else p.lineTo)(x,H-y)
        p.close();self.c.drawPath(p,fill=1,stroke=1)
    def dot(self,x,y,r=3,fill=WHITE,stroke=TEAL,width=1.4):
        self.c.setFillColor(HexColor(fill));self.c.setStrokeColor(HexColor(stroke));self.c.setLineWidth(width)
        self.c.circle(x,H-y,r,fill=1,stroke=1)
    def arrow(self,x1,y1,x2,y2,colour=TEAL,width=1.8):
        self.line(x1,y1,x2,y2,colour,width)
        ang=math.atan2(y2-y1,x2-x1);a=8
        self.poly([(x2,y2),(x2-a*math.cos(ang-.42),y2-a*math.sin(ang-.42)),(x2-a*math.cos(ang+.42),y2-a*math.sin(ang+.42))],colour,colour)
    def dim(self,x1,y1,x2,y2,label,vertical=False):
        self.line(x1,y1,x2,y2,MUTED,.7)
        if vertical:
            self.line(x1-4,y1,x1+4,y1,MUTED,.7);self.line(x2-4,y2,x2+4,y2,MUTED,.7)
            self.c.saveState();self.c.translate(x1-10,H-(y1+y2)/2);self.c.rotate(90);self.c.setFont('Bold',9.5);self.c.setFillColor(HexColor(MUTED));self.c.drawCentredString(0,0,label);self.c.restoreState()
        else:
            self.line(x1,y1-4,x1,y1+4,MUTED,.7);self.line(x2,y2-4,x2,y2+4,MUTED,.7);self.text((x1+x2)/2,y1-7,label,9.5,'Bold',MUTED,'centre')
    def badge(self,label,x,y,w=120,fill=TEAL):
        self.rect(x,y,w,23,fill,r=5);self.text(x+w/2,y+15,label,8.5,'Bold',WHITE,'centre')
    def callout(self,title,body,x,y,w,h,warning=False):
        col=AMBER if warning else TEAL
        self.rect(x,y,w,h,LIGHTAMBER if warning else PALE,r=8)
        self.rect(x,y,5,h,col)
        title_size = 11.5 if len(title) < 46 else 10.3
        self.text(x+18,y+23,title,title_size,'Heavy',col)
        maxh=h-43
        for fs in (10.8,10.2,9.6,9.0,8.4):
            st=ParagraphStyle('callout',fontName='Body',fontSize=fs,leading=fs*1.32,textColor=HexColor(INK),spaceAfter=0)
            pp=Paragraph(body,st);_,ph=pp.wrap(w-36,1000)
            if ph<=maxh+0.1:
                pp.drawOn(self.c,x+18,H-(y+34)-ph);return
        raise ValueError(f'Callout overflow p{self.n}: {body[:40]}')
    def table(self,rows,x,y,widths,font=9.6):
        st=ParagraphStyle('cell',fontName='Body',fontSize=font,leading=font*1.2,textColor=HexColor(INK))
        hd=ParagraphStyle('head',parent=st,fontName='Bold',textColor=white)
        data=[[Paragraph(escape(str(v)),hd if r==0 else st) for v in row] for r,row in enumerate(rows)]
        t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
        cmds=[('BACKGROUND',(0,0),(-1,0),HexColor(TEAL)),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
              ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
              ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8)]
        for r in range(1,len(rows)):cmds.append(('BACKGROUND',(0,r),(-1,r),HexColor(PALE if r%2 else '#F6F6F1')))
        t.setStyle(TableStyle(cmds));tw,th=t.wrap(1000,1000)
        if y+th>H-55:raise ValueError(f'Table overflow on page {self.n}')
        t.drawOn(self.c,x,H-y-th);return th


def shade(hexcol,amount):
    c=HexColor(hexcol)
    vals=[(v+(1-v)*amount if amount>=0 else v*(1+amount)) for v in (c.red,c.green,c.blue)]
    return '#'+''.join(f'{round(v*255):02x}' for v in vals)

def subtract(rect,cover):
    a,b,c,d=rect;e,f,g,h=cover;x0,x1,y0,y1=max(a,e),min(b,f),max(c,g),min(d,h)
    if x0>=x1 or y0>=y1:return [rect]
    out=[]
    if a<x0:out.append((a,x0,c,d))
    if x1<b:out.append((x1,b,c,d))
    if c<y0:out.append((x0,x1,c,y0))
    if y1<d:out.append((x0,x1,y1,d))
    return out

def _project(pt):
    x,y,z=pt;return ((x-y)*.8660254,(x+y)*.45-z)

def iso(book,plan,x,y,w,h,explode=0,highlight=None,show_fixings=False,fixing_course=None,ghost_below=False):
    pieces=[]
    for src in plan['pieces']:
        p=dict(src);p['box']=[list(t) for t in src['box']];shift=explode*(p['course']-1);p['box'][2]=[v+shift for v in p['box'][2]];pieces.append(p)
    vertices=[(a,b,z) for p in pieces for a in p['box'][0] for b in p['box'][1] for z in p['box'][2]]
    raw=[_project(v) for v in vertices];minx=min(v[0] for v in raw);maxx=max(v[0] for v in raw);miny=min(v[1] for v in raw);maxy=max(v[1] for v in raw)
    sc=min(w/(maxx-minx),h/(maxy-miny));ox=x+(w-(maxx-minx)*sc)/2-minx*sc;oy=y+(h-(maxy-miny)*sc)/2-miny*sc
    def cv(pt):px,py=_project(pt);return ox+px*sc,oy+py*sc
    faces=[]
    for p in pieces:
        for axis in range(3):
            plane=p['box'][axis][1];other=[i for i in range(3) if i!=axis];patches=[(*p['box'][other[0]],*p['box'][other[1]])]
            for q in pieces:
                if q['id']==p['id'] or q['box'][axis][0]!=plane:continue
                cover=(*q['box'][other[0]],*q['box'][other[1]])
                patches=[s for rr in patches for s in subtract(rr,cover)]
            for a,b,c,d in patches:
                pts=[]
                for u,v in [(a,c),(b,c),(b,d),(a,d)]:
                    pt=[0,0,0];pt[axis]=plane;pt[other[0]]=u;pt[other[1]]=v;pts.append(pt)
                col=COURSE[p['course']]
                if highlight and p['course']!=highlight:col=GHOST
                if ghost_below and highlight and p['course']<highlight:col='#E7ECE7'
                faces.append((sum(sum(q) for q in pts)/4,pts,shade(col,[-.18,-.03,.23][axis])))
    for _,pts,fill in sorted(faces,key=lambda v:v[0]):book.poly([cv(p) for p in pts],fill,INK,.65)
    if show_fixings:
        for f in plan['fixings']:
            if fixing_course and f['course']!=fixing_course:continue
            shift=explode*(f['course']-1)
            e=[f['entry'][0],f['entry'][1],f['entry'][2]+shift];t=[f['tip'][0],f['tip'][1],f['tip'][2]+shift]
            a,b=cv(e),cv(t);col=SCREW_CORNER if f['kind']=='corner' else SCREW_STACK
            book.line(a[0],a[1],b[0],b[1],col,1.4);book.dot(a[0],a[1],2.2,WHITE,col,1.2)
    return cv

def plan_view(book,course,x,y,w,h,stack=False,corner=False,labels=True,show_prev=False):
    ps=[p for p in PLAN['pieces'] if p['course']==course];sc=min(w/2400,h/1400);ww=2400*sc;hh=1400*sc;ox=x+(w-ww)/2;oy=y+(h-hh)/2
    def cv(X,Y):return ox+X*sc,oy+(1400-Y)*sc
    if show_prev and course>1:
        book.rect(ox-4,oy-4,ww+8,hh+8,'#F3F5F0',RULE,r=3)
    for p in ps:
        (x0,x1),(y0,y1),_=p['box'];sx,sy=cv(x0,y1);book.rect(sx,sy,(x1-x0)*sc,(y1-y0)*sc,COURSE[course],INK)
        if labels:
            if p['side'] in ('S','N'):
                ly=sy-10 if p['side']=='S' else sy+(y1-y0)*sc+18;book.text(sx+(x1-x0)*sc/2,ly,f"C{course}-{p['side']} / {p['length']}",10.5,'Bold',INK,'centre')
            else:
                ly=sy+(y1-y0)*sc/2;book.text(sx+((x1-x0)*sc+21 if p['side']=='W' else -21),ly,p['side'],10.5,'Heavy',INK,'centre')
    for f in PLAN['fixings']:
        if f['course']!=course:continue
        x0,y0,_=f['entry'];sx,sy=cv(x0,y0)
        if stack and f['kind']=='stack':book.dot(sx,sy,3,WHITE,SCREW_STACK,1.5)
        if corner and f['kind']=='corner':book.dot(sx,sy,2.6,WHITE,SCREW_CORNER,1.4)
    book.text(ox+ww/2,oy+hh/2-2,'2200 × 1200 clear',13,'Bold',INK,'centre')
    return cv,(ox,oy,ww,hh)

def timber_bar(book,x,y,w,h,fill,label='',sub=''):
    book.rect(x,y,w,h,fill,INK,r=2)
    if label:book.text(x+w/2,y+h/2+4,label,14,'Heavy',INK,'centre')
    if sub:book.text(x+w/2,y+h+16,sub,9,'Body',MUTED,'centre')

def draw_drill(book,x,y,angle=0,colour=DARK,scale=1):
    # simple drill/driver icon, pointing right before rotation
    c=book.c;c.saveState();c.translate(x,H-y);c.rotate(-angle)
    c.setFillColor(HexColor(colour));c.setStrokeColor(HexColor(colour))
    c.roundRect(-42*scale,-14*scale,54*scale,28*scale,5*scale,fill=1,stroke=0)
    c.rect(-16*scale,-32*scale,18*scale,20*scale,fill=1,stroke=0)
    c.setFillColor(HexColor('#E7ECE7'));c.rect(-7*scale,-28*scale,6*scale,10*scale,fill=1,stroke=0)
    c.setStrokeColor(HexColor(colour));c.setLineWidth(4*scale);c.line(12*scale,0,56*scale,0)
    c.setLineWidth(1*scale);c.line(56*scale,0,67*scale,0)
    c.restoreState()

def screw_shape(book,x,y,length=90,angle=0,colour=TEAL,scale=1,head=True):
    c=book.c;c.saveState();c.translate(x,H-y);c.rotate(-angle);c.setStrokeColor(HexColor(colour));c.setFillColor(HexColor(colour));c.setLineWidth(3*scale)
    if head:c.roundRect(-8*scale,-10*scale,8*scale,20*scale,2*scale,fill=1,stroke=0)
    c.line(0,0,length*scale-8*scale,0)
    c.line(length*scale-8*scale,0,length*scale,0)
    for i in range(int(18*scale),int(length*scale-10*scale),int(max(5,8*scale))):c.line(i,-5*scale,i+6*scale,5*scale)
    c.restoreState()

def action_num(book,n,x,y):
    book.dot(x,y,15,TEAL,TEAL);book.text(x,y+5,str(n),13,'Heavy',WHITE,'centre')

def storyboard_frame(book,x,y,w,h,n,title,body,kind='corner',stage='mark'):
    book.rect(x,y,w,h,'#F5F7F2',RULE,r=7)
    action_num(book,n,x+22,y+24);book.text(x+48,y+29,title,11,'Heavy',INK)
    book.para(body,x+18,y+h-42,w-36,8.7,MUTED,maxh=30)
    # drawing zone y+52 to y+h-52
    if kind=='corner':
        bx=x+22;by=y+69;th=55;through=95;recv=70
        book.rect(bx,by,through,th,COURSE[1],INK);book.rect(bx+through,by,recv,th,shade(COURSE[1],.30),INK)
        cy=by+th/2
        if stage=='clamp':
            book.line(bx+through-3,by-9,bx+through-3,by+th+9,TEAL,3);book.text(bx+through,by-14,'JOINT CLOSED',7.5,'Bold',TEAL,'centre')
        elif stage=='mark':book.dot(bx,cy,5,WHITE,TEAL,1.8);book.line(bx-9,cy,bx+9,cy,TEAL,1);book.line(bx,cy-9,bx,cy+9,TEAL,1)
        elif stage=='drill':draw_drill(book,bx-38,cy,0,DARK,.55);book.line(bx,cy,bx+through+28,cy,BLUE,2,True);book.text(bx+through/2,by-9,'Ø / DEPTH TBC',7.5,'Bold',AMBER,'centre')
        elif stage=='drive':screw_shape(book,bx-6,cy,through+50,0,SCREW_CORNER,.55);book.text(bx+through/2,by-9,'7 × 150',8,'Bold',SCREW_CORNER,'centre')
    else:
        bx=x+53;by=y+61;tw=120;mh=58
        book.rect(bx,by,tw,mh,COURSE[2],INK);book.rect(bx,by+mh,tw,45,COURSE[1],INK);cx=bx+tw/2
        if stage=='clamp':book.line(bx-10,by+mh,bx+tw+10,by+mh,TEAL,3);book.text(cx,by-9,'FACES FLUSH',7.5,'Bold',TEAL,'centre')
        elif stage=='mark':book.dot(cx,by,5,WHITE,TEAL,1.8);book.line(cx-9,by,cx+9,by,TEAL,1);book.line(cx,by-9,cx,by+9,TEAL,1)
        elif stage=='drill':draw_drill(book,cx,by-37,90,DARK,.55);book.line(cx,by,cx,by+mh+28,BLUE,2,True);book.text(cx+52,by+28,'Ø / DEPTH TBC',7.5,'Bold',AMBER,'centre')
        elif stage=='drive':screw_shape(book,cx,by-3,95,90,SCREW_STACK,.55);book.text(cx+49,by+28,'7 × 250',8,'Bold',SCREW_STACK,'centre')

def corner_face(book,x,y,w=300,h=160,course=1):
    sc=min(w/180,h/200);ww=180*sc;hh=200*sc;book.rect(x,y,ww,hh,COURSE[course],INK)
    for wz in (50,150):cx=x+50*sc;cy=y+(200-wz)*sc;book.dot(cx,cy,4,WHITE,SCREW_CORNER);book.line(cx-8,cy,cx+8,cy,SCREW_CORNER,.8);book.line(cx,cy-8,cx,cy+8,SCREW_CORNER,.8)
    book.dim(x,y-18,x+50*sc,y-18,'50 from A');book.dim(x-22,y,x-22,y+hh,'200 high',True)
    book.text(x,y+hh+20,'A / datum end',9.5,'Bold',TEAL)

def top_strip(book,title,values,x,y,w=500,length=2400,colour=SCREW_STACK):
    book.text(x,y,title,11.5,'Heavy',INK);by=y+27;book.rect(x,by,w,38,PALE,INK);book.line(x,by+19,x+w,by+19,colour,.8,True)
    for v in values:px=x+v/length*w;book.dot(px,by+19,3.4,WHITE,colour);book.text(px,by-6,str(v),9.5,'Bold',colour,'centre')
    book.text(x-9,by+25,'A',9.5,'Heavy',TEAL,'right');book.text(x+w,by+53,f'{length} long • centreline V = 50',8.8,'Body',MUTED,'right')

def quick_icon(book,x,y,kind):
    if kind=='measure':book.line(x-20,y,x+20,y,TEAL,3);[book.line(x+i,y-5,x+i,y+5,TEAL,1) for i in range(-18,19,6)]
    elif kind=='cut':book.line(x-24,y,x+24,y,INK,2);book.line(x,y-16,x,y+16,AMBER,3);book.poly([(x-11,y-14),(x+11,y-14),(x,y-28)],AMBER,AMBER)
    elif kind=='label':book.rect(x-24,y-14,48,28,PALE,TEAL,r=4);book.text(x,y+4,'A',14,'Heavy',TEAL,'centre')
    elif kind=='square':book.line(x-20,y+14,x-20,y-14,TEAL,4);book.line(x-20,y+14,x+20,y+14,TEAL,4)
    elif kind=='drill':draw_drill(book,x,y,0,DARK,.5)
    elif kind=='screw':screw_shape(book,x-20,y,50,0,SCREW_CORNER,.6)
    elif kind=='stack':book.rect(x-24,y-18,48,15,COURSE[2],INK);book.rect(x-24,y+2,48,15,COURSE[1],INK);book.arrow(x,y-27,x,y+1,SCREW_STACK,1.5)
    elif kind=='level':book.rect(x-25,y-7,50,14,TEAL,TEAL,r=5);book.dot(x,y,3,WHITE,WHITE)
    elif kind=='check':book.line(x-18,y,x-5,y+14,TEAL,4);book.line(x-5,y+14,x+22,y-18,TEAL,4)

def construction_manual():
    b=Book('Sleeperplan_Construction_Manual_37db13b_DRAFT.pdf','Sleeperplan construction manual 37db13b','Construction manual')
    # 1 Cover
    b.page('FIELD-TRIAL / THREE-COURSE MODEL','How the bed goes together.','A visual, step-by-step construction pack for the current 2400 × 1400 × 600 mm long-through model.')
    iso(b,PLAN,252,145,525,310,explode=60,show_fixings=False)
    b.text(50,195,'3',63,'Heavy',TEAL);b.text(50,230,'COURSES',12,'Bold',MUTED)
    b.text(50,300,'12',55,'Heavy',TEAL);b.text(50,333,'TIMBER PARTS',12,'Bold',MUTED)
    b.text(50,395,'56',55,'Heavy',TEAL);b.text(50,428,'FIXING ENTRIES',12,'Bold',MUTED)
    b.callout('IMPORTANT: CENTRES ARE KNOWN; DRILL SETTINGS ARE NOT.',
        'This pack shows the exact cut bands, part locations and screw entry centres in the current model. Pilot diameter/depth, screw-head seating and the site support/drainage detail are still unconfirmed. Use the visual sequence now; issue drilling only after those details are verified.',250,456,548,82,True)
    # 2 overview
    b.page('00 / WHAT YOU ARE BUILDING','One footprint, three identical rings.','Each course uses two 2400 long members and two 1200 cross-members. The long members pass through the corners on every course.')
    iso(b,PLAN,51,153,455,305,explode=0)
    b.dim(77,466,453,466,'2400 outside');b.dim(45,195,45,410,'600 high',True)
    b.text(541,160,'FINISHED GEOMETRY',12,'Heavy',TEAL)
    rows=[['ITEM','VALUE'],['Outside footprint','2400 × 1400'],['Total height','600'],['Clear opening','2200 × 1200'],['Course height','200'],['Wall thickness','100'],['Outside diagonal','2778.5'],['Geometric fill to 50 freeboard','1452 litres']]
    b.table(rows,541,183,[150,108],9.7)
    b.callout('CORNER ARRANGEMENT','S and N are full-length through members on courses 1, 2 and 3. W and E fit between them. Do not switch to the older alternating-corner example.',541,391,258,126)
    # 3 parts
    b.page('01 / GET EVERYTHING ON THE FLOOR','Twelve pieces. Two screw families.','Lay the whole job out before cutting. Keep every stock-board ID tied to its resulting part.')
    b.text(39,154,'TIMBER',12,'Heavy',TEAL)
    for c in range(1,4):
        y=178+(c-1)*75;timber_bar(b,52,y,330,27,COURSE[c],f'COURSE {c}: 2 × 2400');timber_bar(b,52,y+34,165,24,COURSE[c],f'2 × 1200')
    b.text(421,154,'FASTENERS',12,'Heavy',TEAL)
    screw_shape(b,445,207,95,0,SCREW_CORNER,.75);b.text(555,201,'CORNER',11,'Heavy',SCREW_CORNER);b.text(555,220,'24 fitted • 7 × 150 • Wickes 287686',10,'Body',INK)
    screw_shape(b,445,276,126,0,SCREW_STACK,.75);b.text(586,270,'STACK',11,'Heavy',SCREW_STACK);b.text(586,289,'32 fitted • 7 × 250 • Wickes 287688',10,'Body',INK)
    b.callout('SHOPPING QUANTITY','The model buys 6 × 2400 sleepers + 6 × 1800 sleepers. Screw allowance in the repo rounds to two packs of 25 of each screw family.',421,328,378,93)
    b.callout('DO NOT MIX THE LABELS','The six 2400 boards are B001-B006. The six 1800 boards are B007-B012. Mark every board and its A end before you touch the saw.',39,431,760,82,True)
    # 4 datum
    b.page('02 / LABEL BEFORE CUTTING','A is the measuring origin.','Every cut and every fixing coordinate is measured from the labelled datum A of that stock or finished part.')
    b.rect(58,180,664,52,COURSE[1],INK);b.text(45,213,'A',17,'Heavy',TEAL,'right');b.arrow(72,253,260,253,TEAL);b.text(271,258,'U increases from A',11,'Bold',TEAL)
    b.text(58,280,'Example: 2400 member',11,'Heavy',INK);b.text(58,302,'TOP face',10,'Bold',TEAL);b.text(118,302,'and',10,'Body',MUTED);b.text(143,302,'OUTER face',10,'Bold',AMBER);b.text(210,302,'must remain identifiable after cutting and carrying.',10,'Body',MUTED)
    b.callout('STOCK DATUM ≠ PART DATUM','Cut coordinates are from the ORIGINAL stock A. Once a part is produced, its local A is the lower-X end for S/N or lower-Y end for W/E. Keep both meanings clear.',54,344,346,131)
    b.callout('WHY THIS MATTERS','The course-3 vertical pattern is intentionally shifted. If a part is flipped end-for-end and measured from the wrong side, the stagger is destroyed even though every individual number still looks plausible.',422,344,377,131,True)
    b.para('<b>Practical marking:</b> write the board ID, A arrow, resulting part ID and TOP/OUTER arrows in pencil or removable crayon. Do not rely on “left/right as I am standing”.',54,494,745,11,MUTED)
    # 5 cuts
    b.page('03 / MAKE THE ONLY SIX CROSSCUTS','Keep 1200. Lose 3 mm of kerf.','The six long sides use sound 2400 stock uncut. Each 1200 cross-member comes from its own 1800 stock board.')
    x,y,sc=62,202,700/1800
    b.rect(x,y,1200*sc,66,COURSE[1],INK);b.rect(x+1200*sc,y,max(2,3*sc),66,AMBER,AMBER);b.rect(x+1203*sc,y,597*sc,66,PALE,INK)
    b.text(x+235,y+38,'KEEP 1200',18,'Heavy',INK,'centre');b.text(x+588,y+38,'OFFCUT 597',15,'Bold',MUTED,'centre');b.text(x-12,y+40,'A',15,'Heavy',TEAL,'right')
    b.dim(x,y-22,x+700,y-22,'1800 measured stock')
    blade=x+1201.5*sc;b.line(blade,y+66,blade,330,AMBER,1.4);b.text(blade,348,'blade centre 1201.5',10.5,'Heavy',AMBER,'centre');b.text(blade,366,'waste band 1200 → 1203',10,'Body',MUTED,'centre')
    rows=[['BOARD','KEEP PART','CUT BAND'],['B007','C1-E / 1200','1200-1203'],['B008','C1-W / 1200','1200-1203'],['B009','C2-E / 1200','1200-1203'],['B010','C2-W / 1200','1200-1203'],['B011','C3-E / 1200','1200-1203'],['B012','C3-W / 1200','1200-1203']]
    b.table(rows,39,380,[75,180,105],8.8)
    b.callout('DO NOT CUT ONE 2400 INTO TWO 1200s','1200 + 3 + 1200 = 2403. The blade removes real material. The model deliberately uses separate 1800 stock for each exact cross-member.',426,399,373,113,True)
    # 6 course 1 place
    b.page('04 / PLACE COURSE 1','Dry-fit the ring before fixing.','Lay S and N full length; fit W and E between them. Clamp the four joints. Square the outside rectangle.')
    cv,(ox,oy,ww,hh)=plan_view(b,1,61,170,480,290,labels=True)
    b.line(*cv(0,0),*cv(2400,1400),MUTED,.8,True);b.line(*cv(2400,0),*cv(0,1400),MUTED,.8,True)
    b.dim(ox,oy-26,ox+ww,oy-26,'2400 outside');b.dim(ox-30,oy,ox-30,oy+hh,'1400 outside',True)
    b.text(ox+ww/2,oy+hh/2+20,'diagonals 2778.5 / 2778.5',9.7,'Bold',MUTED,'centre')
    b.callout('CHECK BEFORE ANY HOLE','1) joints closed; 2) both diagonals equal; 3) long sides parallel; 4) base level. If the rectangle is wrong, do not let screws force it right.',565,184,234,130,True)
    b.callout('COURSE 1 HAS NO VERTICAL STACK SCREWS','Only the eight corner screws belong to course 1. Ground anchoring and supports are a separate design detail.',565,331,234,113)
    # 7 corner centres
    b.page('05 / MARK THE CORNER CENTRES','Four entries on each long member.','These centres repeat on S and N at every course. The short W/E pieces receive the screws in their end grain.')
    corner_face(b,83,181,220,212,1)
    b.text(59,425,'ONE END / OUTER FACE',10,'Heavy',MUTED)
    sx,sy,sw,sh=370,198,403,75;b.rect(sx,sy,sw,sh,COURSE[1],INK)
    for u in (50,2350):
        for wz in (50,150):b.dot(sx+sw*u/2400,sy+sh*(1-wz/200),3.6,WHITE,SCREW_CORNER)
    b.text(sx,292,'A / U = 0',9.5,'Bold',TEAL);b.text(sx+sw,292,'U = 2400',9.5,'Bold',MUTED,'right')
    b.table([['U FROM A','W UP','ENTRIES / LONG MEMBER'],['50 and 2350','50 and 150','4']],368,324,[130,100,175],10)
    b.callout('REPEAT THIS ON SIX LONG MEMBERS','C1-S, C1-N, C2-S, C2-N, C3-S and C3-N all use the same four corner centres. Total: 24 corner screws.',368,411,431,103)
    # 8 corner operation storyboard
    b.page('06 / CORNER: CLAMP → MARK → DRILL → DRIVE','One joint, four visible actions.','The drawing can show the complete sequence now. The exact pilot and head-seat settings remain a hard stop until verified.')
    xs=[39,236,433,630];titles=['CLAMP THE JOINT','MARK THE CENTRE','DRILL ON AXIS','DRIVE THE SCREW'];bodies=['Short-member end tight to the inside face.','Use the scheduled U/W centre on the long member.','Follow the screw axis. Diameter and depth are TBC.','Nominal model: 7 × 150 through 100 + 50 into receiver.'];stages=['clamp','mark','drill','drive']
    for i in range(4):storyboard_frame(b,xs[i],164,178,255,i+1,titles[i],bodies[i],'corner',stages[i])
    b.callout('WHAT THE CROSS-SECTION MEANS','The 150 mm screw path is 100 mm through the long member + 50 mm nominal penetration into the receiving short-member end. That is screw-path geometry, not an issued pilot depth or proof of joint strength.',39,447,760,79,True)
    # 9 course1 complete
    b.page('07 / FINISH COURSE 1','Eight corner screws complete the base ring.','Drive two screws at each corner only after the joint detail is approved and the frame is still clamped square.')
    iso(b,PLAN,74,165,510,315,highlight=1,show_fixings=True,fixing_course=1)
    b.badge('8 × 7 × 150 CORNER SCREWS',558,178,210,SCREW_CORNER)
    b.callout('AFTER DRIVING','Recheck 2400 × 1400, equal diagonals, level and joint closure. Record any movement before adding the next course.',556,221,243,109)
    b.callout('DO NOT HIDE A BAD JOINT','If the timber split, the head damaged the face or the joint opened, stop. Do not cover the evidence with course 2.',556,347,243,108,True)
    # 10 course2 placement
    b.page('08 / PLACE COURSE 2','Put the next four members directly above course 1.','Same long-through corner pattern: S/N are 2400; W/E are 1200. Clamp the layer before marking the top fixings.')
    iso(b,PLAN,63,158,498,320,explode=55,highlight=2,ghost_below=True)
    b.text(584,171,'COURSE 2 PARTS',12,'Heavy',TEAL)
    b.table([['PART','LENGTH','BOARD'],['C2-S','2400','B004'],['C2-N','2400','B003'],['C2-W','1200','B010'],['C2-E','1200','B009']],584,194,[82,70,72],9.5)
    b.callout('SEAT THE COURSE FULLY','The upper course must bear on the timber below, not on debris or projecting hardware. Head seating is still an unresolved detail for any surface that another course will cover.',583,360,216,140,True)
    # 11 course2 marks
    b.page('09 / MARK COURSE 2 TOP FIXINGS','Sixteen vertical entries.','Every top entry is centred across the 100 mm face at V = 50. U is measured from each piece’s A end.')
    top_strip(b,'S + N / EACH 2400 MEMBER',[200,700,1200,1700,2200],64,164,690,2400,SCREW_STACK)
    top_strip(b,'W + E / EACH 1200 MEMBER',[200,600,1000],64,285,690,1200,SCREW_STACK)
    b.callout('COURSE 2 TOTAL','5 + 5 + 3 + 3 = 16 stack screws. These are in addition to the eight ordinary course-2 corner screws.',39,422,365,92)
    b.callout('ENTRY HEIGHT','W = 200 on the upper piece: the screw starts on its TOP face and travels vertically down. The nominal 250 mm shaft crosses 200 mm of upper timber + 50 mm into course 1.',424,422,375,92,True)
    # 12 vertical storyboard
    b.page('10 / STACK: CLAMP → MARK → DRILL → DRIVE','The vertical screw gets its own operation sequence.','The PDF shows the bit and screw moving down the same scheduled axis. The final head-seat condition still needs approval.')
    xs=[39,236,433,630];titles=['CLAMP THE LAYERS','MARK U + V','DRILL VERTICALLY','DRIVE 7 × 250'];bodies=['Upper and lower members fully seated.','U from A; V = 50 centreline of top face.','Follow the vertical path. Diameter/depth TBC.','Nominal path: 200 through + 50 into the lower member.'];stages=['clamp','mark','drill','drive']
    for i in range(4):storyboard_frame(b,xs[i],164,178,255,i+1,titles[i],bodies[i],'stack',stages[i])
    b.callout('HEAD-SEAT HARD STOP','Course-2 stack screw heads sit on a surface that course 3 must bear on. The current software does not model head diameter, head height or recess. Confirm that detail before covering these heads.',39,447,760,79,True)
    # 13 course2 complete
    b.page('11 / COMPLETE COURSE 2','Eight corner + sixteen stack screws.','Finish the corner fixings, then the vertical schedule. Recheck the layer before course 3 hides the interfaces.')
    iso(b,PLAN,69,163,500,315,highlight=2,show_fixings=True,fixing_course=2,ghost_below=True)
    b.badge('8 CORNER',582,179,94,SCREW_CORNER);b.badge('16 STACK',690,179,108,SCREW_STACK)
    b.callout('INSPECT ALL FOUR SIDES','Look for gaps between courses, proud heads, splitting, wandering screws and movement at the corners. A clean visual inspection belongs in the repeatable process.',581,222,218,124)
    b.callout('ONLY THEN ADD COURSE 3','The next layer is deliberately staggered relative to the vertical screw rows below. Do not simply copy the course-2 template.',581,363,218,118,True)
    # 14 course3 placement
    b.page('12 / PLACE COURSE 3','Final ring, same corner layout.','Course 3 uses the last two 2400 members and last two 1200 cross-members.')
    iso(b,PLAN,70,158,506,322,explode=62,highlight=3,ghost_below=True)
    b.table([['PART','LENGTH','BOARD'],['C3-S','2400','B006'],['C3-N','2400','B005'],['C3-W','1200','B012'],['C3-E','1200','B011']],592,178,[78,68,70],9.5)
    b.callout('DO NOT COPY COURSE 2','The course-3 vertical entries move 40 mm along each piece in the current model. That stagger avoids the nominal shafts below.',580,356,219,126,True)
    # 15 course3 marks
    b.page('13 / MARK THE STAGGERED TOP ROW','Course 3 shifts by 40 mm.','The same V = 50 centreline applies, but every U value moves +40 relative to course 2.')
    top_strip(b,'S + N / EACH 2400 MEMBER',[240,740,1240,1740,2240],64,164,690,2400,AMBER)
    top_strip(b,'W + E / EACH 1200 MEMBER',[240,640,1040],64,285,690,1200,AMBER)
    b.callout('WHY THE SHIFT EXISTS','The software generates all corner paths first, then positions stack fixings to avoid modelled shafts. Course 3 therefore uses a different mark-out row from course 2.',39,422,365,92)
    b.callout('DO NOT GENERALISE THE 40 mm','That offset belongs to this exact geometry and screw-path model. A different footprint, timber section, screw length or recess detail can require a different schedule.',424,422,375,92,True)
    # 16 all screws
    b.page('14 / SEE ALL 56 FIXINGS','The screw map is easier to trust when you can see the whole system.','Orange = corner screws through the visible outer faces. Blue = vertical stack screws from courses 2 and 3.')
    iso(b,PLAN,46,142,612,360,explode=43,show_fixings=True)
    b.badge('24 CORNER',668,179,111,SCREW_CORNER);b.badge('32 STACK',668,211,111,SCREW_STACK)
    b.callout('COUNT BEFORE YOU FINISH','Course 1: 8. Course 2: 24. Course 3: 24. Total = 56 fitted screws. The purchase allowance is larger than the fitted count.',647,260,152,145)
    b.callout('NOT A STRENGTH CHECK','Placement only: no soil-load, screw-capacity, bracing or foundation calculation.',647,421,152,104,True)
    # 17 final
    b.page('15 / FINISHED TIMBER SHELL','The assembled bed should read as three clean courses.','Before liner, fill or planting, inspect the geometry and all visible interfaces while corrections are still possible.')
    iso(b,PLAN,65,158,520,320,explode=0)
    b.text(614,168,'FINAL CHECK',12,'Heavy',TEAL)
    checks=['Outside 2400 × 1400','Top height 600','Both diagonals 2778.5','All 12 parts labelled / reconciled','24 corner screws accounted for','32 stack screws accounted for','No unresolved proud-head interference','Cut ends treated per timber requirement','Separate support/drainage detail complete']
    y=196
    for item in checks:quick_icon(b,624,y+5,'check');b.text(650,y+9,item,9.8,'Body',INK);y+=34
    # 18 quick sequence
    b.page('16 / THE WHOLE BUILD IN ONE PAGE','A compact workshop sequence.','Use this page as the pre-flight card; use the detailed pages for actual mark-out.')
    steps=[('measure','Measure / verify timber and site'),('label','Label B001-B012 and every A datum'),('cut','Cut B007-B012 at the 1200-1203 waste band'),('square','Dry-fit course 1 square and level'),('drill','Mark / prepare corner centres from the approved joint recipe'),('screw','Drive 8 course-1 corner screws'),('stack','Place course 2, mark 16 stack entries + 8 corners'),('drill','Prepare / drive course 2; inspect head seating'),('stack','Place course 3, use the +40 staggered top schedule'),('screw','Drive course 3; reconcile all 56 fitted screws'),('level','Final geometry + interface inspection'),('check','Only then proceed to reviewed supports / drainage / fill')]
    for i,(icon,text) in enumerate(steps):
        col=i%3;row=i//3;x=46+col*255;y=159+row*86
        b.rect(x,y,238,69,'#F4F7F2',RULE,r=7);action_num(b,i+1,x+24,y+22);quick_icon(b,x+62,y+35,icon);b.para(text,x+91,y+16,132,9.5,INK,maxh=40)
    b.callout('STOP IF THE PACK STILL SAYS TBC','Do not drill until pilot and head-seat operations are verified for the actual screw, timber and joint.',46,484,753,55,True)
    # 19 exact tables
    b.page('17 / EXACT MARK-OUT SUMMARY','The numbers behind the pictures.','All centres below are local coordinates from the labelled A end of the piece.')
    rows=[['COURSE / PIECE','CORNER U / W','STACK U','V'],
          ['C1-S, C1-N','U 50, 2350 × W 50, 150','-','outer face'],
          ['C1-W, C1-E','receivers only','-','-'],
          ['C2-S, C2-N','same corner pattern','200, 700, 1200, 1700, 2200','50'],
          ['C2-W, C2-E','receivers only','200, 600, 1000','50'],
          ['C3-S, C3-N','same corner pattern','240, 740, 1240, 1740, 2240','50'],
          ['C3-W, C3-E','receivers only','240, 640, 1040','50']]
    b.table(rows,42,158,[170,170,282,90],9.2)
    b.callout('CORNER W COORDINATE','The two corner centres are 50 and 150 mm up the 200 mm outer face. The long member carries four entries total: two heights at each end.',42,366,368,106)
    b.callout('STACK W COORDINATE','All stack entries begin on TOP: local W = 200. Their screw direction is vertically down. “200 through + 50 penetration” is not a pilot depth instruction.',431,366,368,106,True)
    b.para('<b>Nominal screw path:</b> corner = 7 × 150, 100 through + 50 into receiver. Stack = 7 × 250, 200 through + 50 into receiver. Pilot diameter, pilot depth and head-seat dimensions intentionally remain TBC.',42,491,757,10.5,MUTED)
    # 20 boundary
    b.page('18 / WHAT IS STILL TBC','The pack is visually complete; the joint recipe is not.','These are the remaining pieces of information needed before this becomes a drill-ready issued construction manual.')
    items=[('PILOT / CLEARANCE','Exact bit diameter(s), depth(s), which member each operation prepares, and the depth datum.'),('HEAD SEAT','Whether the washer head remains proud, beds flush by design, or uses a specifically permitted recess; dimensions and driver access.'),('CONNECTION REVIEW','Suitability of the selected screw for treated timber, end-grain corner joint and the required connection capacity.'),('SUPPORT / DRAINAGE','Base preparation, restraint/bracing, liner/drainage details and actual site conditions.'),('PHYSICAL TRIAL','One controlled corner and one stacked interface built with the real timber and hardware; record fit, finish and any corrections.')]
    for i,(title,body) in enumerate(items):
        x=42+(i%2)*381;y=160+(i//2)*113;w=360 if i<4 else 741
        if i==4:x=42
        b.callout(title,body,x,y,w,94,True)
    b.para(f'<b>Traceability:</b> source commit {COMMIT}. Core geometry transcribed from the 2400 × 1400 long-through model in the repo. Exact parts/cuts/fixings checked against the committed r08 build artifacts. Review-model SHA-256: {MODEL_HASH}.',42,503,757,9.4,MUTED)
    b.save();return b.path

def markout_pack():
    b=Book('Sleeperplan_Workshop_Markout_37db13b_DRAFT.pdf','Sleeperplan workshop mark-out 37db13b','Workshop mark-out')
    # M1
    b.page('REFERENCE / CUT + PART REGISTER','Cut and label sheet.','Keep this beside the saw. Every dimension is from original stock datum A.')
    rows=[['STOCK BOARD','STOCK LENGTH','RESULT'],['B001','2400','C1-N / full length'],['B002','2400','C1-S / full length'],['B003','2400','C2-N / full length'],['B004','2400','C2-S / full length'],['B005','2400','C3-N / full length'],['B006','2400','C3-S / full length'],['B007','1800','C1-E / cut 1200; offcut 597'],['B008','1800','C1-W / cut 1200; offcut 597'],['B009','1800','C2-E / cut 1200; offcut 597'],['B010','1800','C2-W / cut 1200; offcut 597'],['B011','1800','C3-E / cut 1200; offcut 597'],['B012','1800','C3-W / cut 1200; offcut 597']]
    b.table(rows,40,151,[110,120,394],9.4)
    b.callout('ALL SIX CROSSCUTS','Kerf_start = 1200. Kerf_end = 1203. Blade centre = 1201.5. Keep the datum side. This assumes 3 mm kerf and zero end trims.',40,454,624,72,True)
    # M2 corner
    b.page('REFERENCE / CORNER ENTRY CARD','Use on every long S/N member.','Outer-face mark-out only. Pilot/head-seat recipe remains TBC.')
    corner_face(b,77,177,254,245,1)
    b.text(396,164,'EACH LONG MEMBER',12,'Heavy',TEAL)
    b.table([['END','U FROM A','HEIGHT W','SCREW'],['A end','50','50 and 150','7 × 150'],['Far end','2350','50 and 150','7 × 150']],396,190,[92,90,105,89],10)
    b.callout('QUANTITY','4 entries per long member × 6 long members = 24 fitted corner screws.',396,343,376,85)
    b.callout('RECEIVER','At U = 50 the screw enters W. At U = 2350 it enters E. Clamp the receiving short-member end against the inner face of the long member.',396,446,376,80,True)
    # M3 C2
    b.page('REFERENCE / COURSE 2 STACK CARD','Mark sixteen top entries.','V = 50 across every 100 mm top face. W = 200, entry from TOP.')
    top_strip(b,'C2-S + C2-N',[200,700,1200,1700,2200],66,165,685,2400,SCREW_STACK)
    top_strip(b,'C2-W + C2-E',[200,600,1000],66,292,685,1200,SCREW_STACK)
    b.table([['PIECES','ENTRIES EACH','TOTAL'],['S / N','5','10'],['W / E','3','6'],['COURSE 2 STACK','','16']],66,414,[150,120,110],9.8)
    b.callout('PLUS CORNERS','Course 2 also has the ordinary 8 corner entries on S/N. Total fixing entries belonging to course 2 = 24.',467,414,332,101)
    # M4 C3
    b.page('REFERENCE / COURSE 3 STACK CARD','Mark the staggered sixteen top entries.','V = 50; W = 200. Every U value is 40 mm beyond the corresponding course-2 value.')
    top_strip(b,'C3-S + C3-N',[240,740,1240,1740,2240],66,165,685,2400,AMBER)
    top_strip(b,'C3-W + C3-E',[240,640,1040],66,292,685,1200,AMBER)
    b.table([['PIECES','ENTRIES EACH','TOTAL'],['S / N','5','10'],['W / E','3','6'],['COURSE 3 STACK','','16']],66,414,[150,120,110],9.8)
    b.callout('PLUS CORNERS','Course 3 also has 8 ordinary corner entries. Total fixing entries belonging to course 3 = 24.',467,414,332,101)
    # M5 screw card
    b.page('REFERENCE / FASTENER PATHS','Nominal paths, not drill depths.','Use these only to identify the selected hardware and the modelled path through the timber.')
    b.text(45,157,'CORNER',12,'Heavy',SCREW_CORNER);storyboard_frame(b,43,178,344,235,1,'7 × 150','Outer-face entry. Nominal 100 through + 50 into receiving short-member end.','corner','drive')
    b.text(430,157,'STACK',12,'Heavy',SCREW_STACK);storyboard_frame(b,428,178,344,235,2,'7 × 250','Top entry. Nominal 200 through + 50 into the course below.','stack','drive')
    b.callout('DO NOT TURN THESE NUMBERS INTO A PILOT DEPTH','A screw path and a drilling operation are not the same thing. Pilot diameter/depth, any through-bore and any head-seat operation must be separately approved.',43,438,729,86,True)
    # M6 checklist
    b.page('REFERENCE / PRE-DRILL HOLD POINT','Release checklist.','Tick these before replacing TBC with real drill instructions.')
    items=['Actual timber section and usable ends measured','Actual saw kerf confirmed','Exact screw product / lot on hand','Corner joint recipe reviewed','Stack joint recipe reviewed','Pilot / clearance operation recorded','Head seating / recess operation recorded','Driver bit and tool access confirmed','Course-2 head interference physically checked','Support / drainage detail reviewed','Controlled corner trial completed','Controlled stacked-interface trial completed','Job physical-design hash matches approval']
    y=161
    for i,item in enumerate(items):
        col=i//7;row=i%7;x=46+col*385;yy=y+row*48
        b.rect(x,yy-14,17,17,WHITE,TEAL,r=2);b.text(x+29,yy,item,10,'Body',INK)
    b.callout('UNTIL THEN','Use this pack for layout, dry-fit and cutting. Do not infer a drill bit or recess from screw diameter.',46,484,753,55,True)
    b.save();return b.path

def main():
    export(ROOT)
    p1=construction_manual();p2=markout_pack()
    manifest={
      'source_commit':COMMIT,
      'source_model':'examples/first-model-2400x1400.json',
      'source_build_artifacts':'build/first-model-2400x1400-long-through-manual-pdf-r08',
      'model_hash':MODEL_HASH,
      'status':'DRAFT_VISUAL_CONSTRUCTION_PACK',
      'dimensions_mm':[2400,1400,600],
      'parts':12,'fixings':56,'corner_fixings':24,'stack_fixings':32,
      'unconfirmed':['pilot diameter/depth','head seat/recess','connection capacity','supports/drainage/site']
    }
    (ROOT/'pack_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (ROOT/'README.txt').write_text('Sleeperplan construction PDF pack for commit '+COMMIT+'\n\n'+
        'Files:\n- '+p1.name+' : visual step-by-step construction manual\n- '+p2.name+' : workshop cut / mark-out reference cards\n- mark_out_2400x1400_three_courses.csv : full transcribed 56-fixing register\n- pack_manifest.json : provenance and unresolved release items\n\n'+
        'Status: DRAFT. Exact cutting locations and fixing centres are shown. Pilot-hole and head-seat instructions remain unconfirmed and are deliberately shown as TBC.\n')
    zip_path=ROOT/'Sleeperplan_Construction_PDF_Pack_37db13b_DRAFT.zip'
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
        for f in [p1,p2,ROOT/'mark_out_2400x1400_three_courses.csv',ROOT/'independent_checks.json',ROOT/'pack_manifest.json',ROOT/'README.txt']:
            z.write(f,f.name)
        z.write(Path(__file__),'source/make_construction_pack.py')
        z.write(Path(__file__).with_name('review_model.py'),'source/review_model.py')
    print(p1);print(p2);print(zip_path)

if __name__=='__main__':main()
