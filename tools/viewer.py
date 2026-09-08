import csv
import json
from pathlib import Path

def generate_viewer_html(build_dir: Path):
    build_dir = Path(build_dir)
    parts_csv = build_dir / "parts.csv"
    fixings_csv = build_dir / "fixings.csv"
    plan_json_path = build_dir / "plan.json"
    drawings_dir = build_dir / "drawings"

    if not parts_csv.exists() or not fixings_csv.exists():
        print(f"Skipping {build_dir}, missing csvs")
        return

    # Read parts
    parts = []
    with open(parts_csv, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            parts.append({
                "id": r["id"],
                "course": int(r["course"]),
                "side": r["side"],
                "axis": r["axis"],
                "x": float(r["x_mm"]),
                "y": float(r["y_mm"]),
                "z": float(r["z_mm"]),
                "dx": float(r["length_mm"]) if r["axis"] == "X" else float(r["thickness_mm"]),
                "dy": float(r["length_mm"]) if r["axis"] == "Y" else float(r["thickness_mm"]),
                "dz": float(r["height_mm"])
            })

    # Read fixings
    fixings = []
    with open(fixings_csv, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            x = float(r["entry_x_mm"])
            y = float(r["entry_y_mm"])
            z = float(r["entry_z_mm"])
            dx = float(r["direction_x"])
            dy = float(r["direction_y"])
            dz = float(r["direction_z"])
            L = float(r["screw_length_mm"])
            course = int(r["course"])
            fixings.append({
                "id": r["id"],
                "piece_id": r["piece_id"],
                "kind": r["kind"],
                "course": course,
                "x1": x, "y1": y, "z1": z,
                "x2": x + dx * L, "y2": y + dy * L, "z2": z + dz * L
            })

    # Read plan summary if present
    plan_title = "Sleeper Bed Visualiser"
    status = "WORKSHOP PLAN"
    if plan_json_path.exists():
        with open(plan_json_path, "r", encoding="utf-8-sig") as f:
            pj = json.load(f)
            plan_title = pj.get("name", plan_title)
            status = pj.get("status", status)

    # Incoming plan values are untrusted data in a public workflow: escape them
    # for HTML contexts and make embedded JSON safe for <script> bodies.
    from html import escape as _escape
    plan_title_html = _escape(str(plan_title))
    status_html = _escape(str(status))
    plan_title_json = json.dumps(str(plan_title)).replace("</", "<\\/")
    status_json = json.dumps(str(status)).replace("</", "<\\/)")

    # Get list of drawings
    svg_files = []
    if drawings_dir.exists():
        for s in sorted(drawings_dir.glob("*.svg")):
            name = s.name
            label = name
            if "assembled" in name:
                label = "★ 3D Assembled Overview (" + name + ")"
            elif "plan" in name:
                label = "📐 Course Plan (" + name + ")"
            elif "cuts" in name:
                label = "🪚 Cutting Diagram (" + name + ")"
            elif "fixings" in name:
                label = "🔩 Mark-out Sheet (" + name + ")"
            svg_files.append({"name": name, "label": label, "path": f"drawings/{name}"})

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{plan_title_html} - Visual Model & Technical Drawings</title>
<style>
  :root {{
    --bg: #0f172a;
    --card-bg: #1e293b;
    --border: #334155;
    --accent: #14b8a6;
    --accent-hover: #0d9488;
    --text: #f8fafc;
    --text-muted: #94a3b8;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
  body {{ background: var(--bg); color: var(--text); padding: 16px; display: flex; flex-direction: column; gap: 16px; min-height: 100vh; }}
  header {{ display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; background: var(--card-bg); border-radius: 12px; border: 1px solid var(--border); }}
  h1 {{ font-size: 1.3rem; color: #fff; }}
  .badge {{ background: #064e3b; color: #34d399; font-weight: 600; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; letter-spacing: 0.05em; }}
  .layout {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; flex: 1; }}
  @media (max-width: 1080px) {{ .layout {{ grid-template-columns: 1fr; }} }}
  .panel {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; display: flex; flex-direction: column; overflow: hidden; }}
  .panel-header {{ padding: 12px 16px; background: #162032; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }}
  .panel-title {{ font-size: 0.95rem; font-weight: 600; display: flex; align-items: center; gap: 8px; }}
  .controls {{ display: flex; gap: 12px; align-items: center; flex-wrap: wrap; font-size: 0.85rem; color: var(--text-muted); }}
  .controls label {{ display: flex; align-items: center; gap: 6px; cursor: pointer; }}
  input[type="range"] {{ accent-color: var(--accent); }}
  .canvas-container {{ position: relative; flex: 1; min-height: 540px; background: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%); cursor: grab; }}
  .canvas-container:active {{ cursor: grabbing; }}
  canvas {{ width: 100%; height: 100%; display: block; }}
  .canvas-hint {{ position: absolute; bottom: 12px; left: 16px; font-size: 0.75rem; color: #64748b; pointer-events: none; }}
  .drawing-select {{ background: #0f172a; color: #fff; border: 1px solid var(--border); padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; outline: none; }}
  .drawing-container {{ flex: 1; display: flex; align-items: center; justify-content: center; background: #ffffff; padding: 16px; min-height: 540px; overflow: auto; }}
  .drawing-container img {{ max-width: 100%; max-height: 650px; object-fit: contain; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
  .btn {{ background: var(--accent); color: #042f2e; text-decoration: none; padding: 6px 14px; border-radius: 6px; font-size: 0.85rem; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; transition: 0.15s; }}
  .btn:hover {{ background: var(--accent-hover); }}
  .btn-outline {{ background: transparent; border: 1px solid var(--accent); color: var(--accent); }}
  .btn-outline:hover {{ background: rgba(20, 184, 166, 0.1); }}
</style>
</head>
<body>

<header>
  <div>
    <h1>{plan_title_html}</h1>
    <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">Interactive 3D Visual Solids & 2D Technical Vector Drawings</div>
  </div>
  <div style="display: flex; gap: 12px; align-items: center;">
    <span class="badge">{status_html}</span>
    <a href="workshop.pdf" target="_blank" class="btn">📄 Open Workshop PDF</a>
    <a href="model.scad" download class="btn btn-outline">🧊 Download 3D .SCAD</a>
  </div>
</header>

<div class="layout">
  <!-- Left: 3D Interactive Model -->
  <div class="panel">
    <div class="panel-header">
      <div class="panel-title">🧊 Interactive 3D Model</div>
      <div class="controls">
        <label title="Explode courses vertically">
          Explode:
          <input type="range" id="explodeSlider" min="0" max="300" value="0" step="5" style="width: 80px;">
          <span id="explodeVal">0 mm</span>
        </label>
        <label>
          <input type="checkbox" id="screwsToggle" checked>
          Screws
        </label>
        <button class="btn btn-outline" style="padding: 3px 8px; font-size: 0.75rem;" onclick="resetCamera()">Reset</button>
      </div>
    </div>
    <div class="canvas-container" id="canvasContainer">
      <canvas id="renderCanvas"></canvas>
      <div class="canvas-hint">Drag to rotate | Mouse wheel to zoom | Shift + Drag to pan</div>
    </div>
  </div>

  <!-- Right: Technical Drawings Viewer -->
  <div class="panel">
    <div class="panel-header">
      <div class="panel-title">📐 Technical Drawings</div>
      <div>
        <select id="drawingSelect" class="drawing-select" onchange="changeDrawing()">
          {"".join(f'<option value="{d["path"]}">{d["label"]}</option>' for d in svg_files)}
        </select>
      </div>
    </div>
    <div class="drawing-container">
      <img id="drawingImage" src="{svg_files[0]["path"] if svg_files else ""}" alt="Technical Drawing Sheet">
    </div>
  </div>
</div>

<script>
const parts = {json.dumps(parts)};
const fixings = {json.dumps(fixings)};

const canvas = document.getElementById('renderCanvas');
const ctx = canvas.getContext('2d');
let width, height;

function resize() {{
  const rect = canvas.parentElement.getBoundingClientRect();
  width = canvas.width = rect.width * window.devicePixelRatio;
  height = canvas.height = rect.height * window.devicePixelRatio;
  render();
}}
window.addEventListener('resize', resize);

let yaw = -0.7;
let pitch = 0.55;
let zoom = 0.28;
let panX = 0;
let panY = 0;
let isDragging = false;
let isPanning = false;
let lastX = 0;
let lastY = 0;

function resetCamera() {{
  yaw = -0.7;
  pitch = 0.55;
  zoom = 0.28;
  panX = 0;
  panY = 0;
  document.getElementById('explodeSlider').value = 0;
  document.getElementById('explodeVal').innerText = "0 mm";
  render();
}}

let minX = Infinity, maxX = -Infinity;
let minY = Infinity, maxY = -Infinity;
let minZ = Infinity, maxZ = -Infinity;

parts.forEach(p => {{
  minX = Math.min(minX, p.x);
  maxX = Math.max(maxX, p.x + p.dx);
  minY = Math.min(minY, p.y);
  maxY = Math.max(maxY, p.y + p.dy);
  minZ = Math.min(minZ, p.z);
  maxZ = Math.max(maxZ, p.z + p.dz);
}});

const cx = (minX + maxX) / 2;
const cy = (minY + maxY) / 2;
const cz = (minZ + maxZ) / 2;

function project(x, y, z) {{
  let px = x - cx;
  let py = y - cy;
  let pz = z - cz;

  const cosY = Math.cos(yaw);
  const sinY = Math.sin(yaw);
  const x1 = px * cosY - py * sinY;
  const y1 = px * sinY + py * cosY;
  const z1 = pz;

  const cosP = Math.cos(pitch);
  const sinP = Math.sin(pitch);
  const x2 = x1;
  const y2 = y1 * cosP - z1 * sinP;
  const z2 = y1 * sinP + z1 * cosP;

  const scale = zoom * (width / 1200);
  const sx = width / 2 + x2 * scale + panX;
  const sy = height / 2 - z2 * scale + panY;

  return {{ sx, sy, depth: y2 }};
}}

function render() {{
  ctx.clearRect(0, 0, width, height);

  const explode = parseFloat(document.getElementById('explodeSlider').value);
  const showScrews = document.getElementById('screwsToggle').checked;

  const polygons = [];

  parts.forEach(p => {{
    const ez = p.z + (p.course - 1) * explode;
    const x0 = p.x, x1 = p.x + p.dx;
    const y0 = p.y, y1 = p.y + p.dy;
    const z0 = ez, z1 = ez + p.dz;

    const corners = [
      project(x0, y0, z0), project(x1, y0, z0), project(x1, y1, z0), project(x0, y1, z0),
      project(x0, y0, z1), project(x1, y0, z1), project(x1, y1, z1), project(x0, y1, z1)
    ];

    const faces = [
      {{ pts: [corners[4], corners[5], corners[6], corners[7]], col: '#e2be8f', depth: (corners[4].depth + corners[5].depth + corners[6].depth + corners[7].depth) / 4 }},
      {{ pts: [corners[0], corners[1], corners[5], corners[4]], col: '#c89d6a', depth: (corners[0].depth + corners[1].depth + corners[5].depth + corners[4].depth) / 4 }},
      {{ pts: [corners[1], corners[2], corners[6], corners[5]], col: '#ae8152', depth: (corners[1].depth + corners[2].depth + corners[6].depth + corners[5].depth) / 4 }},
      {{ pts: [corners[2], corners[3], corners[7], corners[6]], col: '#a37648', depth: (corners[2].depth + corners[3].depth + corners[7].depth + corners[6].depth) / 4 }},
      {{ pts: [corners[3], corners[0], corners[4], corners[7]], col: '#b98c5c', depth: (corners[3].depth + corners[0].depth + corners[4].depth + corners[7].depth) / 4 }},
      {{ pts: [corners[3], corners[2], corners[1], corners[0]], col: '#7a5530', depth: (corners[3].depth + corners[2].depth + corners[1].depth + corners[0].depth) / 4 }}
    ];

    faces.forEach(f => polygons.push({{ type: 'face', ...f }}));
  }});

  if (showScrews) {{
    fixings.forEach(f => {{
      const ez = (f.course - 1) * explode;
      const p1 = project(f.x1, f.y1, f.z1 + ez);
      const p2 = project(f.x2, f.y2, f.z2 + ez);
      polygons.push({{
        type: 'screw',
        p1, p2,
        depth: (p1.depth + p2.depth) / 2
      }});
    }});
  }}

  polygons.sort((a, b) => a.depth - b.depth);

  polygons.forEach(item => {{
    if (item.type === 'face') {{
      ctx.beginPath();
      ctx.moveTo(item.pts[0].sx, item.pts[0].sy);
      for (let i = 1; i < item.pts.length; i++) {{
        ctx.lineTo(item.pts[i].sx, item.pts[i].sy);
      }}
      ctx.closePath();
      ctx.fillStyle = item.col;
      ctx.fill();
      ctx.strokeStyle = '#1e293b';
      ctx.lineWidth = 1 * window.devicePixelRatio;
      ctx.stroke();
    }} else if (item.type === 'screw') {{
      ctx.beginPath();
      ctx.moveTo(item.p1.sx, item.p1.sy);
      ctx.lineTo(item.p2.sx, item.p2.sy);
      ctx.strokeStyle = '#ef4444';
      ctx.lineWidth = 3 * window.devicePixelRatio;
      ctx.stroke();

      ctx.beginPath();
      ctx.arc(item.p1.sx, item.p1.sy, 4 * window.devicePixelRatio, 0, Math.PI * 2);
      ctx.fillStyle = '#dc2626';
      ctx.fill();
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 1 * window.devicePixelRatio;
      ctx.stroke();
    }}
  }});
}}

const container = document.getElementById('canvasContainer');

container.addEventListener('mousedown', e => {{
  if (e.shiftKey || e.button === 1) isPanning = true;
  else isDragging = true;
  lastX = e.clientX;
  lastY = e.clientY;
}});

window.addEventListener('mousemove', e => {{
  if (!isDragging && !isPanning) return;
  const dx = e.clientX - lastX;
  const dy = e.clientY - lastY;
  lastX = e.clientX;
  lastY = e.clientY;

  if (isDragging) {{
    yaw += dx * 0.008;
    pitch = Math.max(-1.4, Math.min(1.4, pitch + dy * 0.008));
  }} else if (isPanning) {{
    panX += dx * window.devicePixelRatio;
    panY += dy * window.devicePixelRatio;
  }}
  render();
}});

window.addEventListener('mouseup', () => {{
  isDragging = false;
  isPanning = false;
}});

container.addEventListener('wheel', e => {{
  e.preventDefault();
  const factor = e.deltaY > 0 ? 0.9 : 1.1;
  zoom = Math.max(0.05, Math.min(2.0, zoom * factor));
  render();
}}, {{ passive: false }});

document.getElementById('explodeSlider').addEventListener('input', e => {{
  document.getElementById('explodeVal').innerText = e.target.value + " mm";
  render();
}});

document.getElementById('screwsToggle').addEventListener('change', render);

function changeDrawing() {{
  const select = document.getElementById('drawingSelect');
  document.getElementById('drawingImage').src = select.value;
}}

setTimeout(resize, 50);
</script>
</body>
</html>
"""

    (build_dir / "viewer.html").write_text(html_content, encoding="utf-8")
    print(f"Generated viewer.html in {build_dir}")

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "published/first-model-2400x1400-options/3-courses"
    path = Path(target)
    if not path.is_absolute():
        path = Path.cwd() / path
    generate_viewer_html(path)

