import * as THREE from "./vendor/three.module.js";
import { OrbitControls } from "./vendor/OrbitControls.module.js";

THREE.Object3D.DEFAULT_UP.set(0, 0, 1);

const OFFERS = [
  { id: "c1", label: "1 course", sub: "Low", title: "Low profile",
    blurb: "A subtle edge for easy access and lighter visual weight.",
    manifestPath: "./demo/offer-c1/web-manifest.json" },
  { id: "c2", label: "2 courses", sub: "Mid", title: "Mid profile",
    blurb: "Balanced height for mixed planting and a stronger frame presence.",
    manifestPath: "./demo/offer-c2/web-manifest.json" },
  { id: "c3", label: "3 courses", sub: "Tall", title: "High profile",
    blurb: "Statement option with deeper root space and clearer zone definition.",
    manifestPath: "./demo/offer-c3/web-manifest.json" },
];

const APPROACH_GAP_MM = 40;

const canvas = document.getElementById("viewer");
const statusNode = document.getElementById("status");
const offerHeadlineNode = document.getElementById("offerHeadline");
const offerBlurbNode = document.getElementById("offerBlurb");
const statHeightNode = document.getElementById("statHeight");
const statSizeNode = document.getElementById("statSize");
const statPriceNode = document.getElementById("statPrice");
const statFillNode = document.getElementById("statFill");
const linkAssembledNode = document.getElementById("linkAssembled");
const linkProcessNode = document.getElementById("linkProcess");
const linkManualNode = document.getElementById("linkManual");
const linkPdfNode = document.getElementById("linkPdf");
const offerTabsNode = document.getElementById("offerTabs");
const blockersWrapNode = document.getElementById("planBlockers");
const planStatusLineNode = document.getElementById("planStatusLine");
const blockerListNode = document.getElementById("blockerList");
const stepCounterNode = document.getElementById("stepCounter");
const stepSliderNode = document.getElementById("stepSlider");
const stepTitleNode = document.getElementById("stepTitle");
const stepTextNode = document.getElementById("stepText");
const driveProgressWrapNode = document.getElementById("driveProgressWrap");
const driveSliderNode = document.getElementById("driveSlider");
const playBtnNode = document.getElementById("stepPlay");

const scene = new THREE.Scene();
scene.background = new THREE.Color("#e8efec");

const camera = new THREE.PerspectiveCamera(45, 1, 1, 200000);
camera.up.set(0, 0, 1);
camera.position.set(3500, 2600, 2100);

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;

const hemi = new THREE.HemisphereLight(0xffffff, 0x9da6a0, 0.92);
hemi.position.set(0, 0, 1);
scene.add(hemi);
const keyLight = new THREE.DirectionalLight(0xffffff, 0.72);
keyLight.position.set(1, 0.4, 1.5);
scene.add(keyLight);

const grid = new THREE.GridHelper(12000, 40, 0x8aa6a9, 0xcad8d6);
grid.rotation.x = Math.PI / 2;
scene.add(grid);

const timberMat = new THREE.MeshStandardMaterial({ color: 0xc69b6b, roughness: 0.6, metalness: 0.05 });
const timberHiddenMat = new THREE.MeshStandardMaterial({ color: 0xc69b6b, roughness: 0.6, metalness: 0.05, transparent: true, opacity: 0.12 });
const timberActiveMat = new THREE.MeshStandardMaterial({ color: 0xe0b06a, roughness: 0.5, metalness: 0.05, emissive: 0x553311, emissiveIntensity: 0.35 });
const fixingMat = new THREE.MeshStandardMaterial({ color: 0x1a7f87, roughness: 0.4, metalness: 0.2 });
const edgeMat = new THREE.LineBasicMaterial({ color: 0x111111 });

const timberGroup = new THREE.Group();
const fixingGroup = new THREE.Group();
scene.add(timberGroup);
scene.add(fixingGroup);

let lastManifest = null;
let lastPlan = null;
let lastOperations = null;
let bedOffsets = new Map();

const player = { ops: [], index: 0, playing: false, driveProgress: 1 };

function setStatus(message) {
  statusNode.textContent = message;
}

function disposeObject(root) {
  root.traverse((obj) => {
    if (obj.geometry) obj.geometry.dispose();
  });
}

function clearGroup(group) {
  disposeObject(group);
  group.clear();
}

function relativeUrl(base, path) {
  try {
    return new URL(path, base).toString();
  } catch {
    return path;
  }
}

function penceToGbpText(pence) {
  if (typeof pence !== "number") return "-";
  return `GBP ${(pence / 100).toFixed(2)}`;
}

function bedOffsetX(plan, bedId) {
  // Display-only offsets keep multi-bed batches separated; manufacturing
  // coordinates in plan/CSVs are never altered.
  let cursor = 0;
  const map = new Map();
  for (const b of plan.beds || []) {
    map.set(b.id, cursor);
    cursor += b.length_mm + 600;
  }
  return map.get(bedId) ?? 0;
}

function computeBedOffsets(plan) {
  bedOffsets = new Map();
  let cursor = 0;
  for (const b of plan.beds || []) {
    bedOffsets.set(b.id, cursor);
    cursor += b.length_mm + 600;
  }
}

function pieceDimensions(piece) {
  const dx = piece.axis === "X" ? piece.length_mm : piece.thickness_mm;
  const dy = piece.axis === "X" ? piece.thickness_mm : piece.length_mm;
  return [dx, dy, piece.height_mm];
}

function buildSceneFromPlan(plan) {
  clearGroup(timberGroup);
  clearGroup(fixingGroup);
  computeBedOffsets(plan);

  const pieceMeshes = new Map();
  const fixingMeshes = new Map();

  for (const piece of plan.pieces || []) {
    const [dx, dy, dz] = pieceDimensions(piece);
    const box = new THREE.BoxGeometry(dx, dy, dz);
    const mesh = new THREE.Mesh(box, timberHiddenMat);
    mesh.position.set(piece.x_mm + dx / 2, piece.y_mm + dy / 2, piece.z_mm + dz / 2);
    mesh.userData.id = piece.id;
    const edges = new THREE.EdgesGeometry(box);
    const outline = new THREE.LineSegments(edges, edgeMat);
    outline.renderOrder = 2;
    mesh.add(outline);
    const bedGroup = timberGroup.children.find((g) => g.userData.bedId === piece.bed_id)
      || (() => {
        const g = new THREE.Group();
        g.userData.bedId = piece.bed_id;
        timberGroup.add(g);
        return g;
      })();
    bedGroup.add(mesh);
    pieceMeshes.set(piece.id, mesh);
  }

  for (const fixing of plan.fixings || []) {
    const radius = Math.max(1.5, fixing.diameter_mm / 2);
    const cyl = new THREE.CylinderGeometry(radius, radius, fixing.screw_length_mm, 12);
    const mesh = new THREE.Mesh(cyl, fixingMat);
    mesh.visible = false;
    mesh.userData.id = fixing.id;
    const dir = new THREE.Vector3(...fixing.direction).normalize();
    const entry = new THREE.Vector3(...fixing.entry_mm);
    mesh.position.copy(entry.clone().add(dir.clone().multiplyScalar(fixing.screw_length_mm / 2)));
    mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
    const bedGroup = fixingGroup.children.find((g) => g.userData.bedId === fixing.bed_id)
      || (() => {
        const g = new THREE.Group();
        g.userData.bedId = fixing.bed_id;
        fixingGroup.add(g);
        return g;
      })();
    bedGroup.add(mesh);
    fixingMeshes.set(fixing.id, mesh);
  }

  timberGroup.children.forEach((g) => { g.position.x = bedOffsets.get(g.userData.bedId) ?? 0; });
  fixingGroup.children.forEach((g) => { g.position.x = bedOffsets.get(g.userData.bedId) ?? 0; });

  return { pieceMeshes, fixingMeshes };
}

let meshes = { pieceMeshes: new Map(), fixingMeshes: new Map() };

function fitFromBounds(minV, maxV, offsetX = 0) {
  const minVec = new THREE.Vector3(...minV);
  const maxVec = new THREE.Vector3(...maxV);
  const box = new THREE.Box3(minVec, maxVec);
  const sphere = box.getBoundingSphere(new THREE.Sphere());
  const radius = Math.max(sphere.radius, 400);
  camera.position.set(
    sphere.center.x + offsetX + radius * 2.05,
    sphere.center.y + radius * 1.7,
    sphere.center.z + radius * 1.35,
  );
  controls.target.copy(sphere.center);
  controls.minDistance = Math.max(120, radius * 0.2);
  controls.maxDistance = Math.max(1500, radius * 8);
  controls.update();
}

function applyManifestCamera(manifest) {
  const c = manifest?.viewer?.camera;
  if (!c || !Array.isArray(c.position_mm) || !Array.isArray(c.target_mm)) return false;
  const target = new THREE.Vector3(...c.target_mm);
  const position = new THREE.Vector3(...c.position_mm);
  const offset = position.sub(target).multiplyScalar(1.1);
  camera.position.copy(target.clone().add(offset));
  controls.target.copy(target);
  controls.minDistance = c.min_distance_mm ?? controls.minDistance;
  controls.maxDistance = c.max_distance_mm ?? controls.maxDistance;
  camera.fov = c.fov_degrees ?? 45;
  camera.updateProjectionMatrix();
  controls.update();
  return true;
}

function resetView() {
  if (lastManifest?.viewer?.bounds_mm) {
    const b = lastManifest.viewer.bounds_mm;
    fitFromBounds(b.min, b.max);
    applyManifestCamera(lastManifest);
    setStatus("View reset");
    return;
  }
  if (!lastPlan?.pieces?.length) return;
  const mins = [Infinity, Infinity, Infinity];
  const maxs = [-Infinity, -Infinity, -Infinity];
  for (const piece of lastPlan.pieces) {
    const [dx, dy, dz] = pieceDimensions(piece);
    mins[0] = Math.min(mins[0], piece.x_mm);
    mins[1] = Math.min(mins[1], piece.y_mm);
    mins[2] = Math.min(mins[2], piece.z_mm);
    maxs[0] = Math.max(maxs[0], piece.x_mm + dx);
    maxs[1] = Math.max(maxs[1], piece.y_mm + dy);
    maxs[2] = Math.max(maxs[2], piece.z_mm + dz);
  }
  fitFromBounds(mins, maxs);
  setStatus("View reset");
}

function updateLink(node, baseUrl, path, label) {
  if (!path) {
    node.removeAttribute("href");
    node.textContent = `${label} unavailable`;
    node.style.opacity = "0.55";
    return;
  }
  node.href = relativeUrl(baseUrl, path);
  node.textContent = label;
  node.style.opacity = "1";
}

function findDrawingPath(manifest, kind) {
  const drawing = (manifest.drawings || []).find((item) => item.kind === kind);
  return drawing ? drawing.path : "";
}

function populateClientPanel(offer, manifest, plan, baseUrl) {
  const bed = plan.beds?.[0] || null;
  offerHeadlineNode.textContent = `${offer.label} - ${offer.title}`;
  offerBlurbNode.textContent = offer.blurb;

  statHeightNode.textContent = bed ? `${bed.height_mm} mm (${bed.courses} courses)` : "-";
  statSizeNode.textContent = plan.beds?.length > 1
    ? `${plan.beds.length} beds (job view)`
    : bed ? `${bed.length_mm} x ${bed.width_mm} mm` : "-";
  statPriceNode.textContent = penceToGbpText(plan.costs?.timber_and_screw_purchase_pence);
  statFillNode.textContent = bed ? `${bed.fill_litres} litres` : "-";

  updateLink(linkAssembledNode, baseUrl, findDrawingPath(manifest, "assembled"), "Assembled drawing");
  updateLink(linkProcessNode, baseUrl, findDrawingPath(manifest, "process_overview"), "Process overview");
  updateLink(linkManualNode, baseUrl, manifest.artifacts?.workshop_manual, "Workshop manual");
  updateLink(linkPdfNode, baseUrl, manifest.artifacts?.workshop_pdf, "Printable PDF pack");

  const blockers = (plan.issues || []).filter((i) => i.blocking);
  blockersWrapNode.hidden = false;
  planStatusLineNode.textContent = `${plan.status} | plan ${plan.input_sha256.slice(0, 12)} | physical ${plan.physical_design_hash?.slice(0, 12)}`;
  blockerListNode.innerHTML = "";
  for (const b of blockers) {
    const li = document.createElement("li");
    li.textContent = `${b.code}: ${b.message}`;
    blockerListNode.append(li);
  }
}

async function loadManifestFromUrl(url) {
  const manifestRes = await fetch(url, { cache: "no-store" });
  if (!manifestRes.ok) throw new Error(`Manifest fetch failed (${manifestRes.status})`);
  const manifest = await manifestRes.json();
  const planUrl = relativeUrl(url, manifest.artifacts?.plan || "plan.json");
  const planRes = await fetch(planUrl, { cache: "no-store" });
  if (!planRes.ok) throw new Error(`Plan fetch failed (${planRes.status})`);
  const plan = await planRes.json();
  if (manifest.plan_sha256 && plan.input_sha256 && manifest.plan_sha256 !== plan.input_sha256) {
    throw new Error("Manifest does not belong to this plan (hash mismatch) - refusing bundle");
  }
  let operations = null;
  if (manifest.artifacts?.operations) {
    const opsRes = await fetch(relativeUrl(url, manifest.artifacts.operations), { cache: "no-store" });
    if (opsRes.ok) operations = await opsRes.json();
  }
  return { manifest, plan, operations, baseUrl: url };
}

function setActiveOfferButton(offerId) {
  for (const node of offerTabsNode.querySelectorAll("button")) {
    const active = node.dataset.offerId === offerId;
    node.classList.toggle("active", active);
    node.setAttribute("aria-selected", String(active));
  }
}

/* ---------- assembly player: state = f(plan, operation index, drive progress) ---------- */

function installedSets(ops, index) {
  const pieces = new Set();
  const fixings = new Set();
  for (let i = 0; i <= index; i++) {
    const op = ops[i];
    for (const id of op.piece_ids || []) pieces.add(id);
    if ((op.action === "drive" || op.action === "drill") && op.fixing_id) fixings.add(op.fixing_id);
  }
  return { pieces, fixings };
}

function applyPlayerState() {
  if (!lastPlan || !player.ops.length) return;
  const { pieceMeshes, fixingMeshes } = meshes;
  const installed = installedSets(player.ops, player.index);
  const op = player.ops[player.index];
  const activePieces = new Set(op.piece_ids || []);

  for (const [id, mesh] of pieceMeshes) {
    if (installed.pieces.has(id)) mesh.material = activePieces.has(id) ? timberActiveMat : timberMat;
    else mesh.material = timberHiddenMat;
  }

  for (const [id, mesh] of fixingMeshes) {
    if (installed.fixings.has(id)) {
      mesh.visible = true;
      setScrewToFinal(mesh, id);
    } else if (op.fixing_id === id && (op.action === "drive" || op.action === "drill" || op.action === "mark")) {
      mesh.visible = true;
      if (op.action === "drive") setScrewProgress(mesh, id, player.driveProgress);
      else setScrewProgress(mesh, id, 0);
    } else {
      mesh.visible = false;
    }
  }
}

function fixingById(id) {
  return lastPlan.fixings.find((f) => f.id === id);
}

function setScrewToFinal(mesh, fixingId) {
  const f = fixingById(fixingId);
  if (!f) return;
  const dir = new THREE.Vector3(...f.direction).normalize();
  const entry = new THREE.Vector3(...f.entry_mm);
  mesh.position.copy(entry.clone().add(dir.clone().multiplyScalar(f.screw_length_mm / 2)));
}

// head(u) = E - d*(L+g)*(1-u); tip and shaft follow. u=1 must equal the
// approved modelled position exactly (deterministic, no frame-count drift).
function setScrewProgress(mesh, fixingId, u) {
  const f = fixingById(fixingId);
  if (!f) return;
  const dir = new THREE.Vector3(...f.direction).normalize();
  const entry = new THREE.Vector3(...f.entry_mm);
  const travel = f.screw_length_mm + APPROACH_GAP_MM;
  const head = entry.clone().sub(dir.clone().multiplyScalar(travel * (1 - u)));
  mesh.position.copy(head.clone().add(dir.clone().multiplyScalar(f.screw_length_mm / 2)));
}

function updatePlayerUi() {
  if (!player.ops.length) return;
  const op = player.ops[player.index];
  stepCounterNode.textContent = `Step ${player.index + 1} / ${player.ops.length} - ${op.action.toUpperCase()}`;
  stepSliderNode.max = player.ops.length - 1;
  stepSliderNode.value = player.index;
  stepTitleNode.textContent = op.title;
  stepTextNode.textContent = op.detail;
  driveProgressWrapNode.hidden = op.action !== "drive";
  if (op.action === "drive") driveSliderNode.value = Math.round(player.driveProgress * 1000);
}

function gotoStep(index, { fit = true } = {}) {
  if (!player.ops.length) return;
  player.index = Math.max(0, Math.min(player.ops.length - 1, index));
  player.driveProgress = 1;
  const op = player.ops[player.index];
  applyPlayerState();
  updatePlayerUi();
  if (fit && op.piece_ids?.length && lastPlan) {
    const piece = lastPlan.pieces.find((p) => p.id === op.piece_ids[0]);
    if (piece) {
      const [dx, dy, dz] = pieceDimensions(piece);
      fitFromBounds([piece.x_mm, piece.y_mm, piece.z_mm], [piece.x_mm + dx, piece.y_mm + dy, piece.z_mm + dz],
        bedOffsets.get(piece.bed_id) ?? 0);
      if (op.camera_hint === "overview") resetView();
    }
  }
}

function loadPlayer(operationsDoc) {
  player.ops = operationsDoc?.operations || [];
  player.index = 0;
  player.playing = false;
  playBtnNode.textContent = "\u25B6";
  if (player.ops.length) {
    applyPlayerState();
    updatePlayerUi();
  } else {
    stepTitleNode.textContent = "No compiled operation schedule in this bundle.";
  }
}

let playTimer = null;
function togglePlay() {
  player.playing = !player.playing;
  playBtnNode.textContent = player.playing ? "\u23F8" : "\u25B6";
  if (playTimer) clearInterval(playTimer);
  if (player.playing) {
    playTimer = setInterval(() => {
      if (player.index >= player.ops.length - 1) {
        player.playing = false;
        playBtnNode.textContent = "\u25B6";
        clearInterval(playTimer);
        return;
      }
      gotoStep(player.index + 1, { fit: true });
    }, 2600);
  }
}

async function loadOffer(offer) {
  const url = new URL(offer.manifestPath, window.location.href).toString();
  setStatus("Loading option...");
  const buttons = [...offerTabsNode.querySelectorAll("button")];
  for (const node of buttons) node.disabled = true;
  try {
    const { manifest, plan, operations, baseUrl } = await loadManifestFromUrl(url);
    lastManifest = manifest;
    lastPlan = plan;
    lastOperations = operations;
    meshes = buildSceneFromPlan(plan);
    populateClientPanel(offer, manifest, plan, baseUrl);
    if (!applyManifestCamera(manifest)) resetView();
    setActiveOfferButton(offer.id);
    loadPlayer(operations);
    const share = new URL(window.location.href);
    share.searchParams.set("offer", offer.id);
    history.replaceState(null, "", share);
    setStatus(`Showing ${offer.label}`);
  } catch (err) {
    setStatus(`Load failed: ${err.message}`);
  } finally {
    for (const node of buttons) node.disabled = false;
  }
}

function populateOfferTabs() {
  offerTabsNode.innerHTML = "";
  for (const offer of OFFERS) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "offerBtn";
    button.dataset.offerId = offer.id;
    button.id = `offer-tab-${offer.id}`;
    button.setAttribute("role", "tab");
    button.setAttribute("aria-selected", "false");
    const main = document.createElement("span");
    main.textContent = offer.label;
    const sub = document.createElement("span");
    sub.className = "sub";
    sub.textContent = offer.sub;
    sub.setAttribute("aria-hidden", "true");
    button.append(main, sub);
    button.addEventListener("click", () => loadOffer(offer));
    offerTabsNode.append(button);
  }
}

function renderFrame() {
  const w = canvas.clientWidth;
  const h = canvas.clientHeight;
  const dpr = renderer.getPixelRatio();
  if (w > 0 && h > 0 && (canvas.width !== Math.floor(w * dpr) || canvas.height !== Math.floor(h * dpr))) {
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  controls.update();
  renderer.render(scene, camera);
  requestAnimationFrame(renderFrame);
}

document.getElementById("resetView").addEventListener("click", resetView);
document.getElementById("toggleFixings").addEventListener("change", (ev) => {
  if (ev.target.checked) {
    for (const [, mesh] of meshes.fixingMeshes) mesh.visible = true;
  } else {
    applyPlayerState();
    for (const [, mesh] of meshes.fixingMeshes) mesh.visible = false;
  }
});
document.getElementById("stepPrev").addEventListener("click", () => gotoStep(player.index - 1));
document.getElementById("stepNext").addEventListener("click", () => gotoStep(player.index + 1));
document.getElementById("stepFirst").addEventListener("click", () => gotoStep(0));
document.getElementById("stepLast").addEventListener("click", () => gotoStep(player.ops.length - 1));
playBtnNode.addEventListener("click", togglePlay);
stepSliderNode.addEventListener("input", () => gotoStep(Number(stepSliderNode.value)));
driveSliderNode.addEventListener("input", () => {
  player.driveProgress = Number(driveSliderNode.value) / 1000;
  const op = player.ops[player.index];
  if (op?.fixing_id) setScrewProgress(meshes.fixingMeshes.get(op.fixing_id), op.fixing_id, player.driveProgress);
});

populateOfferTabs();
const queryOffer = new URLSearchParams(window.location.search).get("offer");
const startOffer = OFFERS.find((x) => x.id === queryOffer) || OFFERS[2];
loadOffer(startOffer);

window.addEventListener("resize", () => {
  const w = canvas.clientWidth;
  const h = canvas.clientHeight;
  const dpr = renderer.getPixelRatio();
  if (w > 0 && h > 0) {
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
});

renderFrame();
