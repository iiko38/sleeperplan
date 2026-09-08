"""Optional print output. ReportLab is imported lazily; the planner has no dependencies."""
from __future__ import annotations
from html import escape
from pathlib import Path
from .model import PlanError
from .drawing import (Scene, iso_scene, layer_scene, piece_scene, cutting_scene,
                      process_scene, stock_scene, fastener_scene, parts_scene)
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
    piece_rows=18
    if len(plan['pieces'])>piece_rows:
        for pg in range((len(plan['pieces'])+piece_rows-1)//piece_rows):
            figure(parts_scene(plan,page=pg,rows_per_page=piece_rows))
    else:
        figure(parts_scene(plan))
    figure(process_scene(plan))
    figure(stock_scene(plan))
    for screw_id in sorted({f['screw_id'] for f in plan['fixings']}):
        figure(fastener_scene(plan,screw_id))
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


def write_options_pdf(plans: list[dict], heights: list[int], destination: Path, *, job_name: str=''):
    """One document covering every height alternative and how to build each.

    plans/heights are parallel lists in presentation order. Overview and
    comparison first, then a per-option section with build sequence and sheets.
    """
    (colors,A4,landscape,getSampleStyleSheet,ParagraphStyle,SimpleDocTemplate,Paragraph,Spacer,
     Table,TableStyle,PageBreak,Flowable,Canvas)=_imports()
    from .drawing import comparison_scene
    page=landscape(A4)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle('SmallBody',fontName='Helvetica',fontSize=9,leading=13,spaceAfter=5))
    styles.add(ParagraphStyle('JobTitle',fontName='Helvetica-Bold',fontSize=23,leading=27,spaceAfter=12,textColor=colors.HexColor('#183339')))
    styles.add(ParagraphStyle('Label',fontName='Helvetica-Bold',fontSize=11,leading=15,spaceAfter=8,textColor=colors.HexColor('#147c80')))
    doc=SimpleDocTemplate(str(destination),pagesize=page,rightMargin=30,leftMargin=30,topMargin=24,bottomMargin=30,
                         title=f"Sleeperplan - {job_name or plans[0]['name']} - height options",
                         author='Sleeperplan',pageCompression=1)
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

    name=job_name or plans[0]['name']
    story += [para('SLEEPERPLAN / HEIGHT OPTIONS & BUILD GUIDE','JobTitle'),
              para(name,'Heading2'),
              para(f"As of {plans[0]['as_of']} | Generator {plans[0]['generator_version']} | Status {plans[0]['status']}"),
              para('Independent alternatives at the same footprint: each option is planned from the same starting inventory and none consumes another. '
                   'Purchases are not cumulative across options. Until the review gates are recorded, every option remains a draft for mark-out, not a build permission.'),
              Spacer(1,10)]
    rows=[['OPTION','OUTSIDE L x W x H (mm)','COURSES','PIECES','FIXINGS','SLEEPERS','SAW CUTS','TIMBER + SCREWS']]
    for n,p in zip(heights,plans):
        b=p['beds'][0]
        rows.append([f"{n} course{'s' if n!=1 else ''}",
                     f"{b['length_mm']} x {b['width_mm']} x {b['height_mm']}",n,
                     len(p['pieces']),len(p['fixings']),
                     p['cut_plan']['purchased_sleepers'],p['cut_plan']['saw_cuts'],
                     pounds(p['costs']['timber_and_screw_purchase_pence'])])
    story.append(table(rows,[95,180,62,55,60,72,62,84]))
    story += [Spacer(1,8),
              para('How to read this pack: the option pages that follow give the build sequence, the assembled view, one plan page per course, '
                   'the cutting diagram and the process/parts boards for that height. Full per-piece drilling coordinates stay in each option\'s '
                   'own workshop.pdf and fixings.csv inside this compare folder.'),
              para('Fill volumes are geometric cavity measures to the stated freeboard, without settlement or compaction allowances. '
                   'Pilot entries marked UNCONFIRMED are mark-out only and are never a drilling instruction.')]
    for design_id in dict.fromkeys(b['design_id'] for b in plans[0]['beds']):
        figure(comparison_scene(plans,design_id))
    build_steps=[
        'Survey the footprint and access; confirm a level base and an open drainage path before any ground work.',
        'Inspect and measure the timber; measure the real saw kerf with a test cut and set end trims before regenerating if they differ.',
        'Cut stock exactly as the cutting pages show. Each kerf_start..kerf_end band is waste; coordinates run from the ORIGINAL stock datum A.',
        'Label every produced piece with its ID and keep the A / TOP / OUTER orientation from the stock board.',
        'Assemble course 1 square and level. Corner screws enter the OUTER side face of the through member, never its cut end.',
        'Add each further course using its own plan page. Stack screws enter vertically through the TOP and are staggered against the course below.',
        'Pilots: where the schedule says UNCONFIRMED, stop and confirm diameter/depth evidence before drilling. This is a hard stop, not advice.',
        'Fit the separately reviewed supports, liner and drainage details, then fill to the stated freeboard and record actual purchases and offcuts.',
    ]
    for n,p in zip(heights,plans):
        b=p['beds'][0]
        patterns={bed['corner_pattern'] for bed in p['beds']}
        if patterns=={'alternating'}:
            corner='Alternating corners: odd courses run two full members one way, even courses the other; follow each course page exactly.'
        elif patterns=={'long_through'}:
            corner='Long-through corners: the same pair of sides passes through the corner on every course; follow each course page exactly.'
        else:
            corner='Corner pattern can differ per bed design in this batch; follow each course page exactly.'
        story += [PageBreak(),para(f"OPTION {n} - {b['height_mm']} mm OUTSIDE HEIGHT ({n} COURSE{'S' if n!=1 else ''})",'JobTitle'),
                  para(f"{len(p['pieces'])} labelled pieces | {len(p['fixings'])} fixing entries | "
                       f"{p['cut_plan']['purchased_sleepers']} purchased sleepers | {p['cut_plan']['saw_cuts']} saw cuts | "
                       f"cutting {p['cut_plan']['algorithm']} | timber + screws {pounds(p['costs']['timber_and_screw_purchase_pence'])}",'Label'),
                  para(corner),
                  para('Build sequence for this option:')]
        for i,step in enumerate(build_steps,1):
            story.append(para(f"{i}. {step}"))
        story += [Spacer(1,6),
                  para(f"Full per-piece drilling sheets for this option: {n}-courses/workshop.pdf with cuts.csv and fixings.csv in the same folder.")]
        for bed in p['beds']:
            figure(iso_scene(p,bed))
            for layer in range(1,bed['courses']+1):
                figure(layer_scene(p,bed,layer))
        boards=p['cut_plan']['boards']
        for i in range(0,len(boards),5):
            figure(cutting_scene(p,boards[i:i+5]))
        figure(process_scene(p))
        piece_rows=18
        total_pages=max(1,(len(p['pieces'])+piece_rows-1)//piece_rows)
        for pg in range(total_pages):
            figure(parts_scene(p,page=pg,rows_per_page=piece_rows))
    def footer(canvas,doc):
        canvas.saveState();canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#52666a'))
        canvas.drawString(30,16,f"Sleeperplan | {plans[0]['input_sha256'][:12]} | {plans[0]['status']} | height options")
        canvas.drawRightString(page[0]-30,16,str(doc.page));canvas.restoreState()
    def invariant_canvas(*args,**kwargs):
        kwargs['invariant']=1
        return Canvas(*args,**kwargs)
    doc.build(story,onFirstPage=footer,onLaterPages=footer,canvasmaker=invariant_canvas)
