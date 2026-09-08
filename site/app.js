import * as THREE from "./vendor/three.module.js";
import { OrbitControls } from "./vendor/OrbitControls.module.js";

THREE.Object3D.DEFAULT_UP.set(0, 0, 1);

const OFFERS = [
  {
    id: "c1",
    label: "1 course",
    sub: "Low",
    title: "Low profile",
    blurb: "A subtle edge for easy access and lighter visual weight.",
    manifestPath: "./demo/offer-c1/web-manifest.json",
  },
  {
    id: "c2",
    label: "2 courses",
    sub: "Mid",
    title: "Mid profile",
    blurb: "Balanced height for mixed planting and a stronger frame presence.",
    manifestPath: "./demo/offer-c2/web-manifest.json",
  },
  {
    id: "c3",
    label: "3 courses",
    sub: "Tall",
    title: "High profile",
    blurb: "Statement option with deeper root space and clearer zone definition.",
    manifestPath: "./demo/offer-c3/web-manifest.json",
  },
];

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

const grid = new THREE.GridHelper(8000, 40, 0x8aa6a9, 0xcad8d6);
grid.rotation.x = Math.PI / 2;
scene.add(grid);

const timberMat = new THREE.MeshStandardMaterial({ color: 0xc69b6b, roughness: 0.6, metalness: 0.05 });
const fixingMat = new THREE.MeshStandardMaterial({ color: 0x1a7f87, roughness: 0.4, metalness: 0.2 });
const edgeMat = new THREE.LineBasicMaterial({ color: 0x111111 });

const timberGroup = new THREE.Group();
const fixingGroup = new THREE.Group();
scene.add(timberGroup);
scene.add(fixingGroup);

let lastManifest = null;
let lastPlan = null;

function setStatus(message) {
  statusNode.textContent = message;
}

function clearGroup(group) {
  while (group.children.length) {
    const child = group.children.pop();
    if (child.geometry) child.geometry.dispose();
  }
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

function fitFromBounds(minV, maxV) {
  const minVec = new THREE.Vector3(...minV);
  const maxVec = new THREE.Vector3(...maxV);
  const box = new THREE.Box3(minVec, maxVec);
  const sphere = box.getBoundingSphere(new THREE.Sphere());
  const radius = Math.max(sphere.radius, 400);
  camera.position.set(
    sphere.center.x + radius * 2.05,
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

function pieceDimensions(piece) {
  const dx = piece.axis === "X" ? piece.length_mm : piece.thickness_mm;
  const dy = piece.axis === "X" ? piece.thickness_mm : piece.length_mm;
  return [dx, dy, piece.height_mm];
}

function buildSceneFromPlan(plan) {
  clearGroup(timberGroup);
  clearGroup(fixingGroup);

  for (const piece of plan.pieces || []) {
    const [dx, dy, dz] = pieceDimensions(piece);
    const box = new THREE.BoxGeometry(dx, dy, dz);
    const mesh = new THREE.Mesh(box, timberMat);
    mesh.position.set(piece.x_mm + dx / 2, piece.y_mm + dy / 2, piece.z_mm + dz / 2);

    const edges = new THREE.EdgesGeometry(box);
    const outline = new THREE.LineSegments(edges, edgeMat);
    outline.renderOrder = 2;
    mesh.add(outline);
    timberGroup.add(mesh);
  }

  for (const fixing of plan.fixings || []) {
    const radius = Math.max(1.5, fixing.diameter_mm / 2);
    const cyl = new THREE.CylinderGeometry(radius, radius, fixing.screw_length_mm, 12);
    const mesh = new THREE.Mesh(cyl, fixingMat);
    const dir = new THREE.Vector3(...fixing.direction).normalize();
    const entry = new THREE.Vector3(...fixing.entry_mm);
    mesh.position.copy(entry.clone().add(dir.clone().multiplyScalar(fixing.screw_length_mm / 2)));
    mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
    fixingGroup.add(mesh);
  }
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
  statSizeNode.textContent = bed ? `${bed.length_mm} x ${bed.width_mm} mm` : "-";
  statPriceNode.textContent = penceToGbpText(plan.costs?.timber_and_screw_purchase_pence);
  statFillNode.textContent = bed ? `${bed.fill_litres} litres` : "-";

  updateLink(linkAssembledNode, baseUrl, findDrawingPath(manifest, "assembled"), "Assembled drawing");
  updateLink(linkProcessNode, baseUrl, findDrawingPath(manifest, "process_overview"), "Process overview");
  updateLink(linkManualNode, baseUrl, manifest.artifacts?.workshop_manual, "Workshop manual");
  updateLink(linkPdfNode, baseUrl, manifest.artifacts?.workshop_pdf, "Printable PDF pack");
}

async function loadManifestFromUrl(url) {
  const manifestRes = await fetch(url, { cache: "no-store" });
  if (!manifestRes.ok) throw new Error(`Manifest fetch failed (${manifestRes.status})`);
  const manifest = await manifestRes.json();
  const planUrl = relativeUrl(url, manifest.artifacts?.plan || "plan.json");
  const planRes = await fetch(planUrl, { cache: "no-store" });
  if (!planRes.ok) throw new Error(`Plan fetch failed (${planRes.status})`);
  const plan = await planRes.json();
  return { manifest, plan, baseUrl: url };
}

function setActiveOfferButton(offerId) {
  for (const node of offerTabsNode.querySelectorAll("button")) {
    const active = node.dataset.offerId === offerId;
    node.classList.toggle("active", active);
    node.setAttribute("aria-selected", String(active));
  }
}

async function loadOffer(offer) {
  const url = new URL(offer.manifestPath, window.location.href).toString();
  setStatus("Loading option...");
  const buttons = [...offerTabsNode.querySelectorAll("button")];
  for (const node of buttons) node.disabled = true;
  try {
    const { manifest, plan, baseUrl } = await loadManifestFromUrl(url);
    lastManifest = manifest;
    lastPlan = plan;
    buildSceneFromPlan(plan);
    populateClientPanel(offer, manifest, plan, baseUrl);
    if (!applyManifestCamera(manifest)) resetView();
    setActiveOfferButton(offer.id);
    setStatus(`Showing ${offer.label}`);
    const share = new URL(window.location.href);
    share.searchParams.set("offer", offer.id);
    history.replaceState(null, "", share);
  } catch (err) {
    setStatus(`Load failed: ${err.message}`);
  } finally {
    for (const node of buttons) node.disabled = false;
  }
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
  if (canvas.width !== w || canvas.height !== h) {
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
  fixingGroup.visible = ev.target.checked;
});

populateOfferTabs();
const queryOffer = new URLSearchParams(window.location.search).get("offer");
const startOffer = OFFERS.find((x) => x.id === queryOffer) || OFFERS[2];
loadOffer(startOffer);

window.addEventListener("resize", () => {
  const w = canvas.clientWidth;
  const h = canvas.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
});

renderFrame();
