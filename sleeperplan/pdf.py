"""Optional print output. ReportLab is imported lazily; the planner has no dependencies."""
from __future__ import annotations
from html import escape
from pathlib import Path
from .model import PlanError
from .drawing import Scene, iso_scene, layer_scene, piece_scene, cutting_scene
from .costing import pounds


def _imports():
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable
        from reportlab.pdfgen.canvas import Canvas
    except ImportError as exc:
        raise PlanError('PDF output needs the optional dependency: python -m pip install -e ".[pdf]"') from exc
    return colors, A4, landscape, getSampleStyleSheet, ParagraphStyle, SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable, Canvas


def draw_scene(canvas, scene: Scene, x: float, y: float, scale: float):
    from reportlab.lib.colors import toColor as HexColor
    canvas.saveState()
    canvas.translate(x,y)
    canvas.scale(scale,scale)
    H=scene.height
    for e in scene.elements:
        k=e['kind']
        if k=='text':
            canvas.saveState()
            canvas.setFillColor(HexColor(e['colour']))
            canvas.setFont('Helvetica-Bold' if e['bold'] else 'Helvetica',e['size'])
            canvas.translate(e['x'],H-e['y'])
            canvas.rotate(-e['rotate'])
            fn={'start':canvas.drawString,'middle':canvas.drawCentredString,'end':canvas.drawRightString}[e['anchor']]
            fn(0,0,e['value'])
            canvas.restoreState()
        elif k=='line':
            canvas.setStrokeColor(HexColor(e['colour']))
            canvas.setLineWidth(e['width'])
            canvas.setDash([6,4] if e['dash'] else [])
            canvas.line(e['x1'],H-e['y1'],e['x2'],H-e['y2'])
            canvas.setDash([])
        else:
            fill=e['fill']!='none';stroke=e['stroke']!='none'
            if fill:canvas.setFillColor(HexColor(e['fill']))
            if stroke:canvas.setStrokeColor(HexColor(e['stroke']))
            canvas.setLineWidth(e['width'])
            if k=='rect':
                canvas.rect(e['x'],H-e['y']-e['h'],e['w'],e['h'],stroke=stroke,fill=fill)
            elif k=='circle':
                canvas.circle(e['x'],H-e['y'],e['r'],stroke=stroke,fill=fill)
            else:
                path=canvas.beginPath()
                for i,(px,py) in enumerate(e['points']):
                    (path.moveTo if i==0 else path.lineTo)(px,H-py)
                path.close()
                canvas.drawPath(path,stroke=stroke,fill=fill)
    canvas.restoreState()


def write_workshop_pdf(plan: dict, destination: Path):
    (colors,A4,landscape,getSampleStyleSheet,ParagraphStyle,SimpleDocTemplate,Paragraph,Spacer,
     Table,TableStyle,PageBreak,Flowable,Canvas)=_imports()
    page=landscape(A4)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle('SmallBody',fontName='Helvetica',fontSize=9,leading=13,spaceAfter=5))
    styles.add(ParagraphStyle('JobTitle',fontName='Helvetica-Bold',fontSize=23,leading=27,spaceAfter=12,textColor=colors.HexColor('#183339')))
    styles.add(ParagraphStyle('Label',fontName='Helvetica-Bold',fontSize=11,leading=15,spaceAfter=8,textColor=colors.HexColor('#147c80')))
    doc=SimpleDocTemplate(str(destination),pagesize=page,rightMargin=30,leftMargin=30,topMargin=24,bottomMargin=30,
                         title=f"Sleeperplan - {plan['name']}",author='Sleeperplan',pageCompression=1)
    story=[]
    def para(t,style='SmallBody'):
        return Paragraph(escape(str(t)),styles[style])
    def table(rows,widths):
        converted=[[para(cell) for cell in row] for row in rows]
        t=Table(converted,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#edf3f1')),
                              ('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),0.8,colors.HexColor('#a8bbb7')),
                              ('BOTTOMPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5)]))
        return t
    class SceneFlow(Flowable):
        def __init__(self,scene):
            super().__init__();self.scene=scene
            self.factor=min(770/scene.width,525/scene.height)
            self.width=scene.width*self.factor;self.height=scene.height*self.factor
        def draw(self):
            draw_scene(self.canv,self.scene,0,0,self.factor)
    def figure(scene):
        story.extend([PageBreak(),SceneFlow(scene)])
    story += [para('SLEEPERPLAN / WORKSHOP PACK','JobTitle'),para(plan['status'],'Label'),
              para(plan['name'],'Heading2'),
              para(f"As of {plan['as_of']} | Generator {plan['generator_version']} | Plan {plan['input_sha256'][:16]}"),
              para('Worked example unless your own surveyed job file has been used. A reviewed status records human checks; it is not structural certification.'),Spacer(1,10)]
    rows=[['BED','OUTSIDE L x W x H (mm)','COURSES','CLEAR OPENING (mm)','FILL (litres)']]
    for b in plan['beds']:
        rows.append([b['id'],f"{b['length_mm']} x {b['width_mm']} x {b['height_mm']}",b['courses'],
                     f"{b['inside_length_mm']} x {b['inside_width_mm']}",b['fill_litres']])
    story += [table(rows,[120,235,80,205,130]),Spacer(1,12)]
    c=plan['cut_plan'];cost=plan['costs']
    story += [para(f"{len(plan['pieces'])} labelled pieces | {len(plan['fixings'])} fixing entries | "
                   f"{c['purchased_sleepers']} purchased sleepers | {c['saw_cuts']} saw cuts",'Label'),
              para(f"Timber + screw purchases: {pounds(cost['timber_and_screw_purchase_pence'])}"),
              para(f"Known subtotal: {pounds(cost['known_subtotal_pence'])}. "
                   + ('All required cost lines supplied.' if cost['is_complete'] else 'NOT a completed job cost. Unpriced items remain.')),
              para(f"Cutting: {c['algorithm']}. {c['reason']}"),
              para('Use BUILD.md for the assembly sequence. Use cuts.csv for saw bands and fixings.csv for full coordinates. ' 
                   'Treat all pilot entries marked UNCONFIRMED as mark-out only, not a drilling instruction.')]
    story += [PageBreak(),para('REVIEW GATES & ASSUMPTIONS','JobTitle')]
    story.append(table([['TYPE','CHECK']] + [[('BLOCKER' if i['blocking'] else 'NOTE'),i['message']] for i in plan['issues']],[82,688]))
    story += [PageBreak(),para('PURCHASES & COSTS','JobTitle'),para(cost['basis'])]
    rows=[['ITEM','NEED / BUY','LINE TOTAL']]
    for r in cost['rows']:
        quantity=f"{r['needed']} needed / {r['buy_quantity']} {r['unit']}" if r['needed'] is not None else 'UNCONFIRMED'
        rows.append([f"{r['id']} - {r['description']}",quantity,pounds(r['line_pence'])])
    story.append(table(rows,[470,185,115]))
    story += [Spacer(1,8),para(f"Known subtotal: {pounds(cost['known_subtotal_pence'])}",'Label')]
    for b in plan['beds']:
        figure(iso_scene(plan,b))
        for layer in range(1,b['courses']+1):
            figure(layer_scene(plan,b,layer))
    boards=c['boards']
    for i in range(0,len(boards),5):
        figure(cutting_scene(plan,boards[i:i+5]))
    for p in plan['pieces']:
        figure(piece_scene(plan,p))
    def footer(canvas,doc):
        canvas.saveState();canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#52666a'))
        canvas.drawString(30,16,f"Sleeperplan | {plan['input_sha256'][:12]} | {plan['status']}")
        canvas.drawRightString(page[0]-30,16,str(doc.page));canvas.restoreState()
    def invariant_canvas(*args,**kwargs):
        kwargs['invariant']=1
        return Canvas(*args,**kwargs)
    doc.build(story,onFirstPage=footer,onLaterPages=footer,canvasmaker=invariant_canvas)


def write_scene_pdf(scenes: list[Scene], destination: Path, title: str='Sleeperplan comparison'):
    _,A4,landscape,*_= _imports()
    from reportlab.pdfgen.canvas import Canvas
    page=landscape(A4)
    c=Canvas(str(destination),pagesize=page,invariant=1)
    c.setTitle(title);c.setAuthor('Sleeperplan')
    for scene in scenes:
        scale=min((page[0]-40)/scene.width,(page[1]-40)/scene.height)
        draw_scene(c,scene,(page[0]-scene.width*scale)/2,(page[1]-scene.height*scale)/2,scale)
        c.showPage()
    c.save()
