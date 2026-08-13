const I18N = {
  pl: {
    kicker: "Laboratorium badawcze",
    title: "Specyfikacja v16.1 — Jacobson / P",
    lede: "To nie jest ukończona Teoria Wszystkiego. To domknięty program: grupa Spin(10), standardowe oszacowania GUT, niezależna bramka d_S oraz szczelina masowa bez wkładania celu. Empirycznie nadal otwarty.",
    chipPred: "zwalidowanych predykcji obserwacyjnych",
    chipStatus: "program wewnętrznie domknięty",
    chipTheory: "empirycznie otwarty",
    side: "Silnik liczy na żywo w Pythonie. Wynik referencyjny ≠ potwierdzenie obserwacyjne.",
    nav: {
      dash: "Pulpit",
      rge: "Unifikacja RGE",
      spectral: "Wymiar spektralny",
      tcd: "Audyt TCD",
      lqc: "LQC / bounce",
      inflation: "Inflacja α",
      theory: "Teoria v16.1",
      jacobson: "Jacobson / P",
      data: "Dane",
      ledger: "Rejestr twierdzeń",
    },
    run: "Oblicz",
    running: "Liczenie…",
    keep: "KEEP — zostaje",
    hold: "HOLD — czeka na dowód",
    nogo: "NO-GO — odrzucone",
    whatIs: "Czym to jest",
    whatNot: "Czym to nie jest",
    modules: "Moduły, które naprawdę liczą",
    rgeNote: "Standardowe bieganie sprzężeń SM → próg Split-SUSY / MSSM. Sprzężenia w M_Z są wejściem, nie predykcją.",
    specNote: "Estymator d_S = −2 d ln P / d ln t na grafach o znanym wymiarze. Pass waliduje numerikę, nie interpolację TCD.",
    tcdNote: "Diagnostyki zabawkowe z bramkami wymiarowymi. T_c sieciowe jest wejściem. Wzór TCD na crossover jest NO-GO.",
    lqcNote: "Standardowa algebra LQC: H² ∝ ρ(1−ρ/ρ_c). Nie jest to predykcja IFT-EGR ani wyprowadzenie stałej kosmologicznej.",
    infNote: "Fenomenologia α-attractorów. Identyfikacja α = dim(Spin(10))/12 = 3.75 to hipoteza projektu.",
    jacNote: "Lokalny Clausius Jacobsona jest ustalony. Akcja ∫ P R jest dla zadanego P. P(N,T) nadal nie jest wyprowadzone. G_eff=G0/P to nie równanie pola.",
    ledgerNote: "Księga założeń TCD v15 oraz legacy-claimy silnika z jawną klasyfikacją.",
    nNodes: "N węzłów",
    omega: "ω (kinetyczny, niepochodny)",
    mSusy: "M_SUSY [GeV]",
    loops: "Pętle",
    graph: "Graf",
    size: "Rozmiar",
    walkers: "Błądzący",
    steps: "Kroki",
    gamma: "Immirzi γ",
    spin: "Spin j",
    punctures: "Przebicia",
    alpha: "α attractor",
    nefolds: "N e-folds",
    cycle: "cykl 1D",
    torus: "torus 2D",
    random: "4-regularny",
  },
  en: {
    kicker: "Research laboratory",
    title: "v16.1 specification — Jacobson / P",
    lede: "This is not a completed Theory of Everything. It is a closed programme: Spin(10) group theory, standard GUT estimates, an independent d_S gate, and a mass gap that does not import its target. Empirically it remains open.",
    chipPred: "validated observational predictions",
    chipStatus: "internally closed programme",
    chipTheory: "empirically open",
    side: "The engine computes live in Python. A reference match is not observational confirmation.",
    nav: {
      dash: "Overview",
      rge: "RGE unification",
      spectral: "Spectral dimension",
      tcd: "TCD audit",
      lqc: "LQC / bounce",
      inflation: "α-inflation",
      theory: "Theory v16.1",
      jacobson: "Jacobson / P",
      data: "Data",
      ledger: "Claim ledger",
    },
    run: "Compute",
    running: "Computing…",
    keep: "KEEP",
    hold: "HOLD — needs evidence",
    nogo: "NO-GO — rejected",
    whatIs: "What this is",
    whatNot: "What this is not",
    modules: "Modules that actually compute",
    rgeNote: "Standard SM → Split-SUSY / MSSM running. Couplings at M_Z are inputs, not predictions.",
    specNote: "Estimator d_S = −2 d ln P / d ln t on graphs of known dimension. A pass validates numerics, not the TCD interpolation.",
    tcdNote: "Toy diagnostics with dimensional gates. Lattice T_c is an input. The TCD crossover formula is NO-GO.",
    lqcNote: "Standard LQC algebra: H² ∝ ρ(1−ρ/ρ_c). Not an IFT-EGR prediction and not a derivation of Λ.",
    infNote: "α-attractor phenomenology. Identifying α = dim(Spin(10))/12 = 3.75 is a project hypothesis.",
    ledgerNote: "TCD v15 assumption ledger and legacy engine claims with explicit classification.",
    mSusy: "M_SUSY [GeV]",
    loops: "Loops",
    graph: "Graph",
    size: "Size",
    walkers: "Walkers",
    steps: "Steps",
    gamma: "Immirzi γ",
    spin: "Spin j",
    punctures: "Punctures",
    alpha: "α attractor",
    nefolds: "N e-folds",
    cycle: "1D cycle",
    torus: "2D torus",
    random: "4-regular",
  },
};

const NAV = [
  ["dash", "overview"],
  ["rge", "gauge"],
  ["spectral", "walk"],
  ["tcd", "audit"],
  ["lqc", "bounce"],
  ["inflation", "slow-roll"],
  ["theory", "spec"],
  ["jacobson", "clausius"],
  ["data", "data"],
  ["ledger", "claims"],
];

const STATUS_LABEL = {
  established_physics: "established",
  project_hypothesis: "hypothesis",
  unverified_assumption: "unverified",
  rejected_as_stated: "rejected",
  incomplete_prediction: "incomplete",
  calibration: "calibration",
  compatible: "compatible",
  not_excluded: "not excluded",
  excluded: "excluded",
  circular: "circular",
  rejected_formula: "rejected formula",
  incomplete: "incomplete",
};

let lang = "pl";
let statusData = null;
let currentPanel = "dash";
const cache = {};

function t(key) {
  const parts = key.split(".");
  let cur = I18N[lang];
  for (const p of parts) cur = cur?.[p];
  return cur ?? key;
}

function $(id) {
  return document.getElementById(id);
}

function fmt(value, digits = 4) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  const n = Number(value);
  if (!Number.isFinite(n)) return "—";
  const abs = Math.abs(n);
  if (abs !== 0 && (abs < 1e-3 || abs >= 1e5)) return n.toExponential(3);
  return n.toLocaleString(undefined, { maximumFractionDigits: digits });
}

function badge(status) {
  const label = STATUS_LABEL[status] || status;
  const cls = String(status || "hypothesis").replace(/\s+/g, "_");
  return `<span class="badge ${cls}">${label}</span>`;
}

async function api(path, body) {
  const opts = body
    ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }
    : { method: "GET" };
  const res = await fetch(path, opts);
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const err = await res.json();
      detail = err.detail || JSON.stringify(err);
    } catch (_) { /* ignore */ }
    throw new Error(detail);
  }
  return res.json();
}

function drawChart(canvas, spec) {
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  const w = Math.max(320, rect.width);
  const h = Math.max(220, rect.height);
  canvas.width = w * dpr;
  canvas.height = h * dpr;
  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, w, h);

  const pad = { l: 56, r: 16, t: 16, b: 36 };
  const iw = w - pad.l - pad.r;
  const ih = h - pad.t - pad.b;
  const series = (spec.series || []).filter((s) => s.x?.length && s.y?.length);
  if (!series.length) {
    ctx.fillStyle = "#8b9bb4";
    ctx.font = "13px IBM Plex Sans, sans-serif";
    ctx.fillText("No data", pad.l, h / 2);
    return;
  }

  const xs = series.flatMap((s) => s.x);
  const ys = series.flatMap((s) => s.y).filter((v) => Number.isFinite(v));
  let x0 = spec.xMin ?? Math.min(...xs);
  let x1 = spec.xMax ?? Math.max(...xs);
  let y0 = spec.yMin ?? Math.min(...ys);
  let y1 = spec.yMax ?? Math.max(...ys);
  if (x0 === x1) { x0 -= 1; x1 += 1; }
  if (y0 === y1) { y0 -= 1; y1 += 1; }
  if (!spec.yMin && !spec.yMax) {
    const span = y1 - y0 || 1;
    y0 -= 0.08 * span;
    y1 += 0.08 * span;
  }

  const xLog = !!spec.xLog;
  const yLog = !!spec.yLog;
  const tx = (x) => {
    if (xLog) {
      const a = Math.log10(Math.max(x0, 1e-300));
      const b = Math.log10(Math.max(x1, 1e-300));
      return pad.l + ((Math.log10(Math.max(x, 1e-300)) - a) / (b - a)) * iw;
    }
    return pad.l + ((x - x0) / (x1 - x0)) * iw;
  };
  const ty = (y) => {
    if (yLog) {
      const a = Math.log10(Math.max(y0, 1e-300));
      const b = Math.log10(Math.max(y1, 1e-300));
      return pad.t + ih - ((Math.log10(Math.max(y, 1e-300)) - a) / (b - a)) * ih;
    }
    return pad.t + ih - ((y - y0) / (y1 - y0)) * ih;
  };

  ctx.fillStyle = "#0b1220";
  ctx.fillRect(pad.l, pad.t, iw, ih);
  ctx.strokeStyle = "#1c2a45";
  ctx.lineWidth = 1;
  ctx.strokeRect(pad.l, pad.t, iw, ih);

  ctx.font = "11px IBM Plex Mono, monospace";
  ctx.fillStyle = "#5b6b86";
  const ticks = 5;
  for (let i = 0; i <= ticks; i++) {
    const yu = i / ticks;
    const yv = yLog
      ? 10 ** (Math.log10(Math.max(y0, 1e-300)) + yu * (Math.log10(Math.max(y1, 1e-300)) - Math.log10(Math.max(y0, 1e-300))))
      : y0 + yu * (y1 - y0);
    const y = ty(yv);
    ctx.beginPath();
    ctx.strokeStyle = "#152038";
    ctx.moveTo(pad.l, y);
    ctx.lineTo(pad.l + iw, y);
    ctx.stroke();
    ctx.fillStyle = "#5b6b86";
    ctx.textAlign = "right";
    ctx.fillText(fmt(yv, 3), pad.l - 8, y + 3);
    const xu = i / ticks;
    const xv = xLog
      ? 10 ** (Math.log10(Math.max(x0, 1e-300)) + xu * (Math.log10(Math.max(x1, 1e-300)) - Math.log10(Math.max(x0, 1e-300))))
      : x0 + xu * (x1 - x0);
    const x = tx(xv);
    ctx.textAlign = "center";
    ctx.fillText(fmt(xv, 2), x, h - 12);
  }

  for (const band of spec.bands || []) {
    ctx.fillStyle = band.color || "rgba(52,211,153,0.12)";
    const top = ty(band.y1);
    const bot = ty(band.y0);
    ctx.fillRect(pad.l, Math.min(top, bot), iw, Math.abs(bot - top));
  }
  for (const line of spec.hlines || []) {
    ctx.beginPath();
    ctx.setLineDash(line.dashed ? [5, 4] : []);
    ctx.strokeStyle = line.color || "#fbbf24";
    ctx.lineWidth = 1.2;
    ctx.moveTo(pad.l, ty(line.y));
    ctx.lineTo(pad.l + iw, ty(line.y));
    ctx.stroke();
    ctx.setLineDash([]);
  }
  for (const line of spec.vlines || []) {
    ctx.beginPath();
    ctx.setLineDash(line.dashed ? [5, 4] : []);
    ctx.strokeStyle = line.color || "#818cf8";
    ctx.lineWidth = 1.2;
    ctx.moveTo(tx(line.x), pad.t);
    ctx.lineTo(tx(line.x), pad.t + ih);
    ctx.stroke();
    ctx.setLineDash([]);
  }

  for (const s of series) {
    ctx.beginPath();
    ctx.setLineDash(s.dashed ? [6, 4] : []);
    ctx.strokeStyle = s.color || "#22d3ee";
    ctx.lineWidth = s.width || 2;
    let started = false;
    for (let i = 0; i < s.x.length; i++) {
      if (!Number.isFinite(s.y[i])) continue;
      const x = tx(s.x[i]);
      const y = ty(s.y[i]);
      if (!started) { ctx.moveTo(x, y); started = true; }
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.setLineDash([]);
  }

  ctx.fillStyle = "#8b9bb4";
  ctx.font = "11px IBM Plex Sans, sans-serif";
  ctx.textAlign = "center";
  if (spec.xLabel) ctx.fillText(spec.xLabel, pad.l + iw / 2, h - 1);
  if (spec.yLabel) {
    ctx.save();
    ctx.translate(12, pad.t + ih / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText(spec.yLabel, 0, 0);
    ctx.restore();
  }
}

function drawNet(canvas) {
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  const w = rect.width;
  const h = rect.height;
  canvas.width = w * dpr;
  canvas.height = h * dpr;
  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  const n = 28;
  const nodes = Array.from({ length: n }, (_, i) => ({
    x: (0.08 + 0.84 * ((i * 0.37) % 1)) * w,
    y: (0.12 + 0.76 * ((i * 0.61) % 1)) * h,
    r: 2 + (i % 3),
    p: i * 0.4,
  }));
  let t0 = 0;
  function frame(ts) {
    t0 = ts * 0.001;
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = "#070d18";
    ctx.fillRect(0, 0, w, h);
    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) {
        const dx = nodes[i].x - nodes[j].x;
        const dy = nodes[i].y - nodes[j].y;
        const d = Math.hypot(dx, dy);
        if (d < 90) {
          ctx.strokeStyle = `rgba(34,211,238,${0.18 * (1 - d / 90)})`;
          ctx.beginPath();
          ctx.moveTo(nodes[i].x, nodes[i].y);
          ctx.lineTo(nodes[j].x, nodes[j].y);
          ctx.stroke();
        }
      }
    }
    for (const node of nodes) {
      const pulse = 0.55 + 0.45 * Math.sin(t0 * 1.4 + node.p);
      ctx.fillStyle = `rgba(129,140,248,${0.35 + 0.4 * pulse})`;
      ctx.beginPath();
      ctx.arc(node.x, node.y, node.r + pulse, 0, Math.PI * 2);
      ctx.fill();
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

function renderShell() {
  $("kicker").textContent = t("kicker");
  $("title").textContent = t("title");
  $("lede").textContent = t("lede");
  $("chip-pred").textContent = t("chipPred");
  $("chip-status").textContent = t("chipStatus");
  $("chip-theory").textContent = t("chipTheory");
  $("side-note").textContent = t("side");
  $("lang-pl").classList.toggle("active", lang === "pl");
  $("lang-en").classList.toggle("active", lang === "en");
  document.documentElement.lang = lang;

  const nav = $("nav");
  nav.innerHTML = NAV.map(([id]) => (
    `<button type="button" data-panel="${id}">${t("nav." + id)}</button>`
  )).join("");
  nav.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", () => showPanel(btn.dataset.panel));
  });
}

function showPanel(id) {
  currentPanel = id;
  document.querySelectorAll(".panel").forEach((el) => el.classList.toggle("active", el.id === `panel-${id}`));
  document.querySelectorAll("#nav button").forEach((btn) => btn.classList.toggle("active", btn.dataset.panel === id));
  if (id === "dash") renderDash();
  if (id === "rge") (cache.rge ? displayRGE(cache.rge) : runRGE());
  if (id === "spectral") (cache.spectral ? displaySpectral(cache.spectral) : runSpectral());
  if (id === "tcd") (cache.tcd ? displayTCD(cache.tcd) : runTCD());
  if (id === "lqc") (cache.lqc ? displayLQC(cache.lqc) : runLQC());
  if (id === "inflation") (cache.inflation ? displayInflation(cache.inflation) : runInflation());
  if (id === "theory") (cache.theory ? displayTheory(cache.theory) : runTheory());
  if (id === "jacobson") (cache.jacobson ? displayJacobson(cache.jacobson) : runJacobson());
  if (id === "data") (cache.data ? displayData(cache.data) : runData());
  if (id === "ledger") (cache.ledger ? displayLedger(cache.ledger) : runLedger());
}

function renderDash() {
  const s = statusData || { gates: { KEEP: [], HOLD: [], "NO-GO": [] }, what_this_is: "", what_this_is_not: "", modules: [] };
  $("panel-dash").innerHTML = `
    <canvas class="hero-net" id="net"></canvas>
    <div class="status-row">
      ${badge("established_physics")} ${badge("project_hypothesis")} ${badge("rejected_as_stated")}
    </div>
    <div class="grid grid-3" style="margin-top:14px">
      <article class="card gate keep"><h3>${t("keep")}</h3><ul>${(s.gates.KEEP || []).map((x) => `<li>${x}</li>`).join("")}</ul></article>
      <article class="card gate hold"><h3>${t("hold")}</h3><ul>${(s.gates.HOLD || []).map((x) => `<li>${x}</li>`).join("")}</ul></article>
      <article class="card gate nogo"><h3>${t("nogo")}</h3><ul>${(s.gates["NO-GO"] || []).map((x) => `<li>${x}</li>`).join("")}</ul></article>
    </div>
    <div class="grid grid-2eq" style="margin-top:14px">
      <article class="card"><h3>${t("whatIs")}</h3><p>${s.what_this_is || ""}</p></article>
      <article class="card"><h3>${t("whatNot")}</h3><p>${s.what_this_is_not || ""}</p></article>
    </div>
    <article class="card" style="margin-top:14px">
      <h3>${t("modules")}</h3>
      <div class="metrics">
        ${(s.modules || []).map((m) => `<div class="metric"><span>${m.label}</span><b>${STATUS_LABEL[m.status] || m.status}</b></div>`).join("")}
      </div>
    </article>
  `;
  const net = $("net");
  if (net) drawNet(net);
}

function bindRun(panel, handler) {
  panel.querySelector(".run")?.addEventListener("click", handler);
}

function setBusy(panel, busy) {
  const btn = panel.querySelector(".run");
  if (!btn) return;
  btn.disabled = busy;
  btn.textContent = busy ? t("running") : t("run");
}

function showError(host, err) {
  host.insertAdjacentHTML("afterbegin", `<div class="err">${err.message}</div>`);
}

function renderRGEPanel() {
  const p = $("panel-rge");
  p.innerHTML = `
    <div class="controls">
      <div class="field"><label>${t("mSusy")}</label><input id="rge-msusy" type="range" min="500" max="20000" step="100" value="5000"><div class="val" id="rge-msusy-v">5000</div></div>
      <div class="field"><label>${t("loops")}</label>
        <select id="rge-loops"><option value="2">2</option><option value="1">1</option></select>
      </div>
      <button class="run" type="button">${t("run")}</button>
    </div>
    <div id="rge-out"></div>
  `;
  $("rge-msusy").addEventListener("input", (e) => { $("rge-msusy-v").textContent = e.target.value; });
  bindRun(p, runRGE);
}

async function runRGE() {
  const panel = $("panel-rge");
  setBusy(panel, true);
  try {
    const data = await api("/api/rge", {
      m_susy: Number($("rge-msusy").value),
      loops: Number($("rge-loops").value),
    });
    cache.rge = data;
    displayRGE(data);
  } catch (err) {
    $("rge-out").innerHTML = "";
    showError($("rge-out"), err);
  } finally {
    setBusy(panel, false);
  }
}

function displayRGE(data) {
    if (!$("rge-out")) return;
    const a = data.analysis;
    $("rge-out").innerHTML = `
      <div class="metrics">
        <div class="metric"><span>M_GUT</span><b>${fmt(a.M_GUT_GeV)} GeV</b><em>${badge(data.status)}</em></div>
        <div class="metric"><span>α_GUT<sup>−1</sup></span><b>${fmt(a.alpha_GUT_inv, 3)}</b></div>
        <div class="metric"><span>unification σ(g)/⟨g⟩</span><b>${fmt(a.unification_accuracy, 4)}</b></div>
        <div class="metric"><span>sin²θ_W(GUT)</span><b>${fmt(a.sin2_theta_W_GUT, 4)}</b><em>target 3/8 = 0.375</em></div>
      </div>
      <div class="grid grid-2">
        <article class="card">
          <h3>1/αᵢ(μ)</h3>
          <div class="chart-wrap"><canvas class="chart" id="rge-chart"></canvas></div>
          <div class="legend">
            <span><i class="swatch" style="background:#fb7185"></i>1/α₁</span>
            <span><i class="swatch" style="background:#fbbf24"></i>1/α₂</span>
            <span><i class="swatch" style="background:#22d3ee"></i>1/α₃</span>
          </div>
        </article>
        <article class="card">
          <h3>Calibration audit</h3>
          <p>${data.calibration_audit.note}</p>
          <div class="metrics" style="grid-template-columns:1fr 1fr;margin-top:12px">
            <div class="metric"><span>α_s(M_Z) input</span><b>${fmt(a.alpha_s_MZ_input, 4)}</b><em>PDG ${data.calibration_audit.pdg_alpha_s_MZ}</em></div>
            <div class="metric"><span>1/α_em(M_Z)</span><b>${fmt(a.alpha_em_MZ_inv, 2)}</b><em>hidden offset ${data.calibration_audit.apex_hidden_alpha_em_offset}</em></div>
          </div>
          <div class="note warn">${data.note}</div>
        </article>
      </div>
    `;
    drawChart($("rge-chart"), {
      xLog: true,
      xLabel: "μ [GeV]",
      yLabel: "1/α",
      vlines: [{ x: data.inputs.M_SUSY_GeV, color: "#818cf8", dashed: true }],
      series: [
        { x: data.mu_GeV, y: data.alpha_inv["1"], color: "#fb7185", label: "1/α1" },
        { x: data.mu_GeV, y: data.alpha_inv["2"], color: "#fbbf24", label: "1/α2" },
        { x: data.mu_GeV, y: data.alpha_inv["3"], color: "#22d3ee", label: "1/α3" },
      ],
    });
}

function renderSpectralPanel() {
  const p = $("panel-spectral");
  p.innerHTML = `
    <div class="controls">
      <div class="field"><label>${t("graph")}</label>
        <select id="sp-graph">
          <option value="torus">${t("torus")}</option>
          <option value="cycle">${t("cycle")}</option>
          <option value="random">${t("random")}</option>
        </select>
      </div>
      <div class="field"><label>${t("size")}</label><input id="sp-size" type="range" min="12" max="36" value="20"><div class="val" id="sp-size-v">20</div></div>
      <div class="field"><label>${t("walkers")}</label><input id="sp-walkers" type="range" min="800" max="8000" step="200" value="4000"><div class="val" id="sp-walkers-v">4000</div></div>
      <div class="field"><label>${t("steps")}</label><input id="sp-steps" type="range" min="40" max="160" step="10" value="80"><div class="val" id="sp-steps-v">80</div></div>
      <button class="run" type="button">${t("run")}</button>
    </div>
    <div id="sp-out"></div>
  `;
  ["sp-size", "sp-walkers", "sp-steps"].forEach((id) => {
    $(id).addEventListener("input", (e) => { $(id + "-v").textContent = e.target.value; });
  });
  bindRun(p, runSpectral);
}

async function runSpectral() {
  const panel = $("panel-spectral");
  setBusy(panel, true);
  try {
    const kind = $("sp-graph").value;
    let size = Number($("sp-size").value);
    if (kind === "cycle") size = Math.min(400, size * 6);
    if (kind === "random") size = Math.min(120, size * 3);
    const data = await api("/api/spectral", {
      graph: kind,
      size,
      walkers: Number($("sp-walkers").value),
      steps: Number($("sp-steps").value),
    });
    cache.spectral = data;
    displaySpectral(data);
  } catch (err) {
    $("sp-out").innerHTML = "";
    showError($("sp-out"), err);
  } finally {
    setBusy(panel, false);
  }
}

function displaySpectral(data) {
  if (!$("sp-out")) return;
  $("sp-out").innerHTML = `
    <div class="metrics">
      <div class="metric"><span>⟨d_S⟩ fit</span><b>${fmt(data.fit_mean_d_S, 3)}</b></div>
      <div class="metric"><span>expected</span><b>${data.expected_dimension ?? "—"}</b></div>
      <div class="metric"><span>|error|</span><b>${fmt(data.absolute_error, 3)}</b><em>threshold 0.15</em></div>
      <div class="metric"><span>estimator</span><b>${data.estimator_pass ? "PASS" : (data.expected_dimension == null ? "n/a" : "FAIL")}</b><em>${fmt(data.elapsed_ms, 0)} ms · ${data.n_nodes} nodes</em></div>
    </div>
    <div class="grid grid-2eq">
      <article class="card"><h3>d_S(t)</h3><div class="chart-wrap"><canvas class="chart" id="sp-ds"></canvas></div></article>
      <article class="card"><h3>P(return)</h3><div class="chart-wrap"><canvas class="chart" id="sp-p"></canvas></div></article>
    </div>
    <div class="note">${data.note} ${data.hypothesis_note}</div>
  `;
  const hlines = data.expected_dimension != null
    ? [{ y: data.expected_dimension, color: "#34d399", dashed: true }]
    : [];
  drawChart($("sp-ds"), {
    xLabel: "t",
    yLabel: "d_S",
    yMin: 0,
    yMax: Math.max(4.2, ...data.d_S),
    hlines,
    series: [{ x: data.t, y: data.d_S, color: "#22d3ee" }],
  });
  drawChart($("sp-p"), {
    xLabel: "t",
    yLabel: "P(t)",
    yLog: true,
    series: [{ x: data.t, y: data.return_probability, color: "#818cf8" }],
  });
}

function renderTCDPanel() {
  const p = $("panel-tcd");
  p.innerHTML = `
    <div class="controls"><button class="run" type="button">${t("run")}</button></div>
    <div id="tcd-out"></div>
  `;
  bindRun(p, runTCD);
}

function auditRow(name, item) {
  const status = item.status || "";
  const decision = item.decision || "";
  return `<tr>
    <td>${name}</td>
    <td>${badge(status)}</td>
    <td class="mono">${decision}</td>
    <td>${item.reason || item.note || item.source || ""}</td>
  </tr>`;
}

async function runTCD() {
  const panel = $("panel-tcd");
  setBusy(panel, true);
  try {
    const data = await api("/api/tcd", { points: 80 });
    cache.tcd = data;
    displayTCD(data);
  } catch (err) {
    $("tcd-out").innerHTML = "";
    showError($("tcd-out"), err);
  } finally {
    setBusy(panel, false);
  }
}

function displayTCD(data) {
    if (!$("tcd-out")) return;
    const a = data.audits;
    $("tcd-out").innerHTML = `
      <div class="metrics">
        <div class="metric"><span>lattice T_c</span><b>${fmt(a.lattice_Tc_MeV.value, 1)} MeV</b><em>${badge(a.lattice_Tc_MeV.status)}</em></div>
        <div class="metric"><span>TCD formula T_c</span><b>${fmt(a.qcd_crossover.formula_value_GeV * 1000, 1)} MeV</b><em>${badge(a.qcd_crossover.status)}</em></div>
        <div class="metric"><span>Λ candidate / ref</span><b>${fmt(a.dark_energy.lambda_ratio_candidate_to_reference)}</b><em>${badge(a.dark_energy.status)}</em></div>
        <div class="metric"><span>ΔG/G at BBN</span><b>${fmt(a.delta_g.bbn_1MeV)}</b><em>not 10⁻²</em></div>
      </div>
      <div class="grid grid-2eq">
        <article class="card"><h3>Polyakov & CF</h3><div class="chart-wrap"><canvas class="chart" id="tcd-poly"></canvas></div>
          <div class="legend"><span><i class="swatch" style="background:#22d3ee"></i>L(T)</span><span><i class="swatch" style="background:#fb7185"></i>CF(T)</span></div>
        </article>
        <article class="card"><h3>σ(T) and η/s</h3><div class="chart-wrap"><canvas class="chart" id="tcd-eos"></canvas></div>
          <div class="legend"><span><i class="swatch" style="background:#fbbf24"></i>σ [GeV²]</span><span><i class="swatch" style="background:#818cf8"></i>η/s</span></div>
        </article>
      </div>
      <article class="card" style="margin-top:14px">
        <h3>d_S(T) ansatz — HOLD</h3>
        <div class="chart-wrap"><canvas class="chart" id="tcd-ds"></canvas></div>
        <div class="note warn">${data.spectral.frozen_predictions ? "Frozen HOLD values: " + Object.entries(data.spectral.frozen_predictions).map(([k, v]) => `T/T*=${k} → ${fmt(v, 3)}`).join(" · ") : ""}</div>
      </article>
      <article class="card" style="margin-top:14px">
        <h3>Audit gates</h3>
        <div class="table-wrap"><table>
          <thead><tr><th>Claim</th><th>Status</th><th>Decision</th><th>Reason</th></tr></thead>
          <tbody>
            ${auditRow("QCD crossover formula", a.qcd_crossover)}
            ${auditRow("Dark energy T_c⁴/M_Pl²", a.dark_energy)}
            ${auditRow("Lattice β = 1/g²", a.lattice_beta_unit_norm)}
            ${auditRow("Carnot Planck→GUT", a.carnot_planck_to_gut)}
            ${auditRow("Thermal ΔG/G", a.delta_g)}
            ${auditRow("Coherence P(N,T)", a.coherence_P)}
            ${auditRow("Lattice T_c input", a.lattice_Tc_MeV)}
          </tbody>
        </table></div>
      </article>
    `;
    drawChart($("tcd-poly"), {
      xLog: true, xLabel: "T [MeV]",
      vlines: [{ x: data.t_c_mev, color: "#fbbf24", dashed: true }],
      series: [
        { x: data.t_mev, y: data.polyakov.values, color: "#22d3ee" },
        { x: data.t_mev, y: data.causal_fraction.values, color: "#fb7185" },
      ],
    });
    drawChart($("tcd-eos"), {
      xLog: true, xLabel: "T [MeV]",
      vlines: [{ x: data.t_c_mev, color: "#fbbf24", dashed: true }],
      hlines: [{ y: data.kss_bound, color: "#818cf8", dashed: true }],
      series: [
        { x: data.t_mev, y: data.string_tension_GeV2.values, color: "#fbbf24" },
        { x: data.t_mev, y: data.eta_over_s.values, color: "#818cf8" },
      ],
    });
    drawChart($("tcd-ds"), {
      xLog: true, xLabel: "T [GeV]", yLabel: "d_S",
      yMin: 1.8, yMax: 4.2,
      hlines: [{ y: 4, color: "#34d399", dashed: true }, { y: 2, color: "#fb7185", dashed: true }],
      series: [{ x: data.spectral.T_GeV, y: data.spectral.d_S, color: "#22d3ee" }],
    });
}

function renderLQCPanel() {
  const p = $("panel-lqc");
  p.innerHTML = `
    <div class="controls">
      <div class="field"><label>${t("gamma")}</label><input id="lqc-g" type="range" min="0.1" max="0.6" step="0.0025" value="0.2375"><div class="val" id="lqc-g-v">0.2375</div></div>
      <div class="field"><label>${t("spin")}</label>
        <select id="lqc-j">
          <option value="0.5">1/2</option><option value="1">1</option>
          <option value="2">2</option><option value="5">5</option>
        </select>
      </div>
      <div class="field"><label>${t("punctures")}</label><input id="lqc-n" type="range" min="10" max="400" step="10" value="100"><div class="val" id="lqc-n-v">100</div></div>
      <button class="run" type="button">${t("run")}</button>
    </div>
    <div id="lqc-out"></div>
  `;
  $("lqc-g").addEventListener("input", (e) => { $("lqc-g-v").textContent = e.target.value; });
  $("lqc-n").addEventListener("input", (e) => { $("lqc-n-v").textContent = e.target.value; });
  bindRun(p, runLQC);
}

async function runLQC() {
  const panel = $("panel-lqc");
  setBusy(panel, true);
  try {
    const data = await api("/api/lqc", {
      gamma: Number($("lqc-g").value),
      spin: Number($("lqc-j").value),
      punctures: Number($("lqc-n").value),
    });
    cache.lqc = data;
    displayLQC(data);
  } catch (err) {
    $("lqc-out").innerHTML = "";
    showError($("lqc-out"), err);
  } finally {
    setBusy(panel, false);
  }
}

function displayLQC(data) {
    if (!$("lqc-out")) return;
    $("lqc-out").innerHTML = `
      <div class="metrics">
        <div class="metric"><span>ρ_c / ρ_Pl</span><b>${fmt(data.rho_c_over_rho_Pl, 3)}</b></div>
        <div class="metric"><span>Δ / ℓ_P²</span><b>${fmt(data.area_gap_planck, 3)}</b></div>
        <div class="metric"><span>A_j / ℓ_P²</span><b>${fmt(data.puncture_area_planck, 3)}</b></div>
        <div class="metric"><span>S_upper / (N A)</span><b>${fmt(data.entropy_per_area, 4)}</b><em>BH target 0.25</em></div>
      </div>
      <div class="grid grid-2eq">
        <article class="card"><h3>LQC bounce H²(ρ)</h3><div class="chart-wrap"><canvas class="chart" id="lqc-h"></canvas></div></article>
        <article class="card"><h3>GFT N(φ) ansatz</h3><div class="chart-wrap"><canvas class="chart" id="lqc-gft"></canvas></div></article>
      </div>
      <div class="note">${data.note} ${data.immirzi_note}</div>
      <div class="note">Causal diamond: partial order = ${data.causal_order.is_partial_order}; violation (causal) = ${fmt(data.causal_order.violation_causal_kernel, 3)}; violation (backward weight) = ${fmt(data.causal_order.violation_with_backward_weight, 3)}.</div>
    `;
    drawChart($("lqc-h"), {
      xLabel: "ρ / ρ_Pl", yLabel: "H²",
      vlines: [{ x: data.rho_c_over_rho_Pl, color: "#fb7185", dashed: true }],
      series: [{ x: data.bounce.rho_over_rho_Pl, y: data.bounce.H2, color: "#22d3ee" }],
    });
    drawChart($("lqc-gft"), {
      xLabel: "φ", yLabel: "N(φ)",
      series: [{ x: data.gft.phi, y: data.gft.N_phi, color: "#818cf8" }],
    });
}

function renderInflationPanel() {
  const p = $("panel-inflation");
  p.innerHTML = `
    <div class="controls">
      <div class="field"><label>${t("alpha")}</label><input id="inf-a" type="range" min="0.2" max="10" step="0.05" value="3.75"><div class="val" id="inf-a-v">3.75</div></div>
      <div class="field"><label>${t("nefolds")}</label><input id="inf-n" type="range" min="45" max="75" step="0.5" value="60"><div class="val" id="inf-n-v">60</div></div>
      <button class="run" type="button">${t("run")}</button>
    </div>
    <div id="inf-out"></div>
  `;
  $("inf-a").addEventListener("input", (e) => { $("inf-a-v").textContent = e.target.value; });
  $("inf-n").addEventListener("input", (e) => { $("inf-n-v").textContent = e.target.value; });
  bindRun(p, runInflation);
}

async function runInflation() {
  const panel = $("panel-inflation");
  setBusy(panel, true);
  try {
    const data = await api("/api/inflation", {
      alpha: Number($("inf-a").value),
      n_efolds: Number($("inf-n").value),
    });
    cache.inflation = data;
    displayInflation(data);
  } catch (err) {
    $("inf-out").innerHTML = "";
    showError($("inf-out"), err);
  } finally {
    setBusy(panel, false);
  }
}

function displayInflation(data) {
    if (!$("inf-out")) return;
    const o = data.observables;
    const c = data.comparison;
    $("inf-out").innerHTML = `
      <div class="metrics">
        <div class="metric"><span>n_s = 1−2/N</span><b>${fmt(o.n_s_leading, 4)}</b><em>Planck ${c.planck_n_s} ± ${c.planck_n_s_err}</em></div>
        <div class="metric"><span>pull</span><b>${fmt(c.n_s_pull_sigma, 2)} σ</b></div>
        <div class="metric"><span>r = 12α/N²</span><b>${fmt(o.r, 4)}</b><em>BICEP &lt; ${c.bicep_r_limit}</em></div>
        <div class="metric"><span>ε</span><b>${fmt(o.epsilon, 5)}</b><em>α_Spin(10)=${data.spin10_alpha}</em></div>
      </div>
      <div class="grid grid-2eq">
        <article class="card"><h3>n_s(N)</h3><div class="chart-wrap"><canvas class="chart" id="inf-ns"></canvas></div></article>
        <article class="card"><h3>r(N)</h3><div class="chart-wrap"><canvas class="chart" id="inf-r"></canvas></div></article>
      </div>
      <div class="note warn">${data.note}</div>
    `;
    drawChart($("inf-ns"), {
      xLabel: "N", yLabel: "n_s",
      bands: [{ y0: c.planck_n_s - c.planck_n_s_err, y1: c.planck_n_s + c.planck_n_s_err, color: "rgba(52,211,153,0.12)" }],
      hlines: [{ y: c.planck_n_s, color: "#34d399", dashed: true }],
      vlines: [{ x: data.inputs.N_efolds, color: "#818cf8", dashed: true }],
      series: [{ x: data.n_grid, y: data.n_s_of_N, color: "#22d3ee" }],
    });
    drawChart($("inf-r"), {
      xLabel: "N", yLabel: "r",
      hlines: [{ y: c.bicep_r_limit, color: "#fb7185", dashed: true }],
      vlines: [{ x: data.inputs.N_efolds, color: "#818cf8", dashed: true }],
      series: [{ x: data.n_grid, y: data.r_of_N, color: "#fbbf24" }],
    });
}

function renderTheoryPanel() {
  const p = $("panel-theory");
  p.innerHTML = `
    <div class="controls"><button class="run" type="button">${t("run")}</button></div>
    <div id="th-out"></div>
  `;
  bindRun(p, runTheory);
}

async function runTheory() {
  const panel = $("panel-theory");
  setBusy(panel, true);
  try {
    const data = await api("/api/theory", { fast: true });
    cache.theory = data;
    displayTheory(data);
  } catch (err) {
    $("th-out").innerHTML = "";
    showError($("th-out"), err);
  } finally {
    setBusy(panel, false);
  }
}

function displayTheory(data) {
  if (!$("th-out")) return;
  const g1 = data.gate1_independent_spectral_flow || {};
  const g2 = data.gate2_mass_gap || {};
  const u = data.unification || {};
  const points = g1.points || [];
  $("th-out").innerHTML = `
    <div class="metrics">
      <div class="metric"><span>spec</span><b>v${data.version}</b><em>${data.scientific_status}</em></div>
      <div class="metric"><span>Gate 1 d_S</span><b>${g1.decision || "—"}</b><em>${g1.n_fail ?? "—"} / ${g1.n_points ?? "—"} fail</em></div>
      <div class="metric"><span>Gate 2 R=m/√σ</span><b>${fmt(g2.R_m_over_sqrt_sigma, 3)}</b><em>2D U(1), no 1.71 GeV input</em></div>
      <div class="metric"><span>Gate 3 G_eff</span><b>${g3.decisions?.geff_is_the_field_equation || "—"}</b><em>prescribed P; P not derived</em></div>
    </div>
    <div class="grid grid-2eq">
      <article class="card">
        <h3>Axioms</h3>
        <div class="table-wrap"><table>
          <thead><tr><th>ID</th><th>Status</th><th>Statement</th></tr></thead>
          <tbody>
            ${(data.axioms || []).map((a) => `<tr><td class="mono">${a.id}</td><td>${badge(a.status)}</td><td>${a.statement}</td></tr>`).join("")}
          </tbody>
        </table></div>
      </article>
      <article class="card">
        <h3>Spin(10) 16</h3>
        <div class="table-wrap"><table>
          <thead><tr><th>field</th><th>SU(3)</th><th>SU(2)</th><th>Y</th></tr></thead>
          <tbody>
            ${(data.group?.spinor_16 || []).map((f) => `<tr><td class="mono">${f.field}</td><td>${f.SU3}</td><td>${f.SU2}</td><td class="mono">${f.Y}</td></tr>`).join("")}
          </tbody>
        </table></div>
        <div class="note">${data.group?.n_generations?.reason || ""}</div>
      </article>
    </div>
    <article class="card" style="margin-top:14px">
      <h3>Gate 1 — independent d_S vs HOLD interpolation</h3>
      <div class="chart-wrap"><canvas class="chart" id="th-ds"></canvas></div>
      <div class="legend">
        <span><i class="swatch" style="background:#22d3ee"></i>measured</span>
        <span><i class="swatch" style="background:#fb7185"></i>HOLD ansatz</span>
      </div>
      <div class="note ${g1.decision === "NO-GO" ? "bad" : "warn"}">${g1.protocol || ""} Decision: <b>${g1.decision}</b>. ${g1.note || ""}</div>
    </article>
    <article class="card" style="margin-top:14px">
      <h3>Prediction registry</h3>
      <div class="table-wrap"><table>
        <thead><tr><th>ID</th><th>Observable</th><th>Value</th><th>Status</th></tr></thead>
        <tbody>
          ${(data.registry || []).map((row) => `<tr>
            <td class="mono">${row.id}</td>
            <td>${row.observable}</td>
            <td class="mono">${row.value === null || row.value === undefined ? "—" : (typeof row.value === "number" ? fmt(row.value) : row.value)}</td>
            <td>${badge(row.status)}</td>
          </tr>`).join("")}
        </tbody>
      </table></div>
    </article>
    <div class="grid grid-2eq" style="margin-top:14px">
      <article class="card gate keep"><h3>Closed</h3><ul>${(data.what_is_closed || []).map((x) => `<li>${x}</li>`).join("")}</ul></article>
      <article class="card gate nogo"><h3>Not closed</h3><ul>${(data.what_is_not_closed || []).map((x) => `<li>${x}</li>`).join("")}</ul></article>
    </div>
    <div class="metrics" style="margin-top:14px">
      <div class="metric"><span>M_GUT diagnostic</span><b>${fmt(u.M_GUT_GeV)} GeV</b></div>
      <div class="metric"><span>sin²θ_W(GUT)</span><b>${fmt(u.sin2_theta_W_GUT, 4)}</b><em>3/8 = 0.375</em></div>
      <div class="metric"><span>m_ν (declared seesaw)</span><b>${fmt(data.seesaw?.m_nu_eV)} eV</b></div>
      <div class="metric"><span>observational validations</span><b>${data.validated_observational_predictions}</b></div>
    </div>
  `;
  if (points.length) {
    drawChart($("th-ds"), {
      xLog: true,
      xLabel: "T / T* (convention)",
      yLabel: "d_S",
      yMin: 1.5,
      yMax: 5,
      series: [
        { x: points.map((p) => p.T_over_Tstar_convention), y: points.map((p) => p.d_S_measured), color: "#22d3ee" },
        { x: points.map((p) => p.T_over_Tstar_convention), y: points.map((p) => p.d_S_hold), color: "#fb7185", dashed: true },
      ],
    });
  }
}

function renderJacobsonPanel() {
  const p = $("panel-jacobson");
  p.innerHTML = `
    <div class="controls">
      <div class="field"><label>${t("nNodes")}</label>
        <input id="jc-n" type="range" min="3" max="9" step="0.1" value="6">
        <div class="val" id="jc-n-v">1e6</div>
      </div>
      <div class="field"><label>${t("omega")}</label>
        <input id="jc-w" type="range" min="0" max="40" step="1" value="0">
        <div class="val" id="jc-w-v">0</div>
      </div>
      <button class="run" type="button">${t("run")}</button>
    </div>
    <div id="jc-out"></div>
  `;
  const syncN = () => {
    const exp = Number($("jc-n").value);
    $("jc-n-v").textContent = `1e${exp}`;
  };
  $("jc-n").addEventListener("input", syncN);
  $("jc-w").addEventListener("input", (e) => { $("jc-w-v").textContent = e.target.value; });
  bindRun(p, runJacobson);
}

async function runJacobson() {
  const panel = $("panel-jacobson");
  setBusy(panel, true);
  try {
    const nNodes = Math.round(10 ** Number($("jc-n").value));
    const data = await api("/api/jacobson", {
      n_nodes: nNodes,
      omega: Number($("jc-w").value),
      points: 80,
    });
    cache.jacobson = data;
    displayJacobson(data);
  } catch (err) {
    $("jc-out").innerHTML = "";
    showError($("jc-out"), err);
  } finally {
    setBusy(panel, false);
  }
}

function displayJacobson(data) {
  if (!$("jc-out")) return;
  const d = data.decisions || {};
  const ir = data.ir_approximation || {};
  const geff = data.geff_substitution || {};
  const action = data.prescribed_action || {};
  const ident = data.identity_check || {};
  const domain = data.domain || {};
  const epochs = data.epochs || [];
  const sweep = data.sweep || {};
  $("jc-out").innerHTML = `
    <div class="metrics">
      <div class="metric"><span>Jacobson ⇒ P</span><b>${d.jacobson_derives_P || "—"}</b><em>${badge("rejected_as_stated")}</em></div>
      <div class="metric"><span>G_eff = G0/P</span><b>${d.geff_is_the_field_equation || "—"}</b><em>unless ∇P = 0</em></div>
      <div class="metric"><span>IR approximation</span><b>${d.ir_geff_approximation || "—"}</b><em>ε_F &lt; ${fmt(ir.threshold, 3)} today + BBN</em></div>
      <div class="metric"><span>P ansatz</span><b>${d.p_ansatz || "HOLD"}</b><em>${badge("project_hypothesis")}</em></div>
    </div>
    <div class="grid grid-2eq">
      <article class="card">
        <h3>Prescribed action</h3>
        <p class="mono">${action.action || ""}</p>
        <p class="mono" style="margin-top:8px">${action.metric_equation || ""}</p>
        <div class="note">${action.note || data.note || ""}</div>
      </article>
      <article class="card">
        <h3>What this does not do</h3>
        <ul>
          <li>does not derive P(N,T) from δQ = T dS</li>
          <li>does not make Einstein-with-G_eff the field equation</li>
          <li>does not supply ω(P) or V(P) for a dynamical scalar</li>
          <li>does not increment TOE validated (still 0)</li>
        </ul>
        <div class="note warn">${geff.nogo_rule || ""}</div>
      </article>
    </div>
    <article class="card" style="margin-top:14px">
      <h3>ε_F(T) = T |P′| / P</h3>
      <div class="chart-wrap"><canvas class="chart" id="jc-eps"></canvas></div>
      <div class="legend">
        <span><i class="swatch" style="background:#22d3ee"></i>ε_F</span>
        <span><i class="swatch" style="background:#fb7185"></i>threshold ${fmt(ir.threshold, 3)}</span>
      </div>
    </article>
    <article class="card" style="margin-top:14px">
      <h3>Frozen clocks</h3>
      <div class="table-wrap"><table>
        <thead><tr><th>Clock</th><th>T [GeV]</th><th>P</th><th>ε_F</th><th>IR</th><th>Note</th></tr></thead>
        <tbody>
          ${epochs.map((row) => `<tr>
            <td class="mono">${row.id}</td>
            <td class="mono">${fmt(row.T_GeV)}</td>
            <td class="mono">${row.P == null ? "—" : fmt(row.P, 6)}</td>
            <td class="mono">${row.eps_friedmann == null ? "—" : fmt(row.eps_friedmann)}</td>
            <td>${row.inside_domain ? (row.ir_ok ? badge("compatible") : badge("excluded")) : badge("rejected_as_stated")}</td>
            <td>${row.note || ""}</td>
          </tr>`).join("")}
        </tbody>
      </table></div>
      <div class="note">Domain wall: T_max = ${domain.T_max_GeV != null ? fmt(domain.T_max_GeV) + " GeV" : "—"}. Identity check ${ident.passed ? "PASS" : "—" } (algebra, not nature). ${data.p_derivation?.statement || ""}</div>
    </article>
  `;
  if (sweep.T_GeV?.length && $("jc-eps")) {
    drawChart($("jc-eps"), {
      xLog: true,
      yLog: true,
      xLabel: "T [GeV]",
      yLabel: "ε_F",
      hlines: [{ y: ir.threshold || 0.01, color: "#fb7185", dashed: true }],
      series: [{ x: sweep.T_GeV, y: sweep.eps_friedmann, color: "#22d3ee" }],
    });
  }
}

function renderDataPanel() {
  const p = $("panel-data");
  p.innerHTML = `
    <div class="controls">
      <div class="field"><label>${t("alpha")}</label><input id="da-a" type="range" min="0.2" max="10" step="0.05" value="3.75"><div class="val" id="da-a-v">3.75</div></div>
      <div class="field"><label>${t("nefolds")}</label><input id="da-n" type="range" min="45" max="75" step="0.5" value="60"><div class="val" id="da-n-v">60</div></div>
      <div class="field"><label>${t("mSusy")}</label><input id="da-m" type="range" min="500" max="20000" step="100" value="5000"><div class="val" id="da-m-v">5000</div></div>
      <div class="field"><label>α_H [GeV³]</label><input id="da-h" type="range" min="0.005" max="0.03" step="0.001" value="0.015"><div class="val" id="da-h-v">0.015</div></div>
      <button class="run" type="button">${t("run")}</button>
    </div>
    <div id="da-out"></div>
  `;
  ["da-a", "da-n", "da-m", "da-h"].forEach((id) => {
    $(id).addEventListener("input", (e) => { $(id + "-v").textContent = e.target.value; });
  });
  bindRun(p, runData);
}

async function runData() {
  const panel = $("panel-data");
  setBusy(panel, true);
  try {
    const data = await api("/api/confrontation", {
      alpha: Number($("da-a").value),
      n_efolds: Number($("da-n").value),
      m_susy: Number($("da-m").value),
      alpha_h_gev3: Number($("da-h").value),
    });
    cache.data = data;
    displayData(data);
  } catch (err) {
    $("da-out").innerHTML = "";
    showError($("da-out"), err);
  } finally {
    setBusy(panel, false);
  }
}

function displayData(data) {
  if (!$("da-out")) return;
  const c = data.counts || {};
  const pulls = (data.rows || []).filter((row) => row.pull !== null && row.pull !== undefined);
  $("da-out").innerHTML = `
    <div class="metrics">
      <div class="metric"><span>TOE validated</span><b>${data.validated_observational_predictions}</b><em>still 0</em></div>
      <div class="metric"><span>pheno contract</span><b>${data.phenomenology_contracts_passed || 0}</b><em>C1: N from reheating</em></div>
      <div class="metric"><span>compatible</span><b>${c.compatible || 0}</b><em>|pull| &lt; 2</em></div>
      <div class="metric"><span>not excluded</span><b>${c.not_excluded || 0}</b></div>
      <div class="metric"><span>excluded</span><b>${c.excluded || 0}</b></div>
    </div>
    <div class="note warn">${data.validation_rule}</div>
    <article class="card" style="margin-top:14px">
      <h3>Frozen data card ${data.card_id}</h3>
      <div class="table-wrap"><table>
        <thead><tr><th>ID</th><th>Observable</th><th>Theory</th><th>Data / limit</th><th>Pull</th><th>Verdict</th></tr></thead>
        <tbody>
          ${(data.rows || []).map((row) => `<tr>
            <td class="mono">${row.id}</td>
            <td>${row.observable}</td>
            <td class="mono">${row.theory === null || row.theory === undefined ? "—" : fmt(row.theory)}</td>
            <td class="mono">${fmt(row.data)}</td>
            <td class="mono">${row.pull === null || row.pull === undefined ? "—" : fmt(row.pull, 2)}</td>
            <td>${badge(row.verdict)}</td>
          </tr>`).join("")}
        </tbody>
      </table></div>
    </article>
    <article class="card" style="margin-top:14px">
      <h3>Gaussian pulls</h3>
      <div class="chart-wrap"><canvas class="chart" id="da-pull"></canvas></div>
      <div class="note">χ² = ${fmt(data.chi2_compatible_gaussian, 3)} for ${data.ndof_compatible_gaussian} compatible Gaussian row(s) only. Circular rows are shown but not counted as confirmation.</div>
    </article>
    <article class="card" style="margin-top:14px">
      <h3>Why nothing is validated</h3>
      <ul>${(data.rows || []).map((row) => `<li><span class="mono">${row.id}</span> — ${row.why_not_validated}</li>`).join("")}</ul>
    </article>
  `;
  if (pulls.length && $("da-pull")) {
    drawChart($("da-pull"), {
      xLabel: "index",
      yLabel: "pull",
      hlines: [{ y: 0, color: "#64748b", dashed: true }, { y: 2, color: "#fb7185", dashed: true }, { y: -2, color: "#fb7185", dashed: true }],
      series: [{
        x: pulls.map((_, i) => i + 1),
        y: pulls.map((row) => row.pull),
        color: "#22d3ee",
      }],
    });
  }
}

function renderLedgerPanel() {
  $("panel-ledger").innerHTML = `<div id="led-out"></div>`;
}

async function runLedger() {
  try {
    const data = await api("/api/ledger");
    cache.ledger = data;
    displayLedger(data);
  } catch (err) {
    $("led-out").innerHTML = "";
    showError($("led-out"), err);
  }
}

function displayLedger(data) {
    if (!$("led-out")) return;
    const entries = data.ledger.entries || [];
    $("led-out").innerHTML = `
      <article class="card">
        <h3>Legacy engine claims</h3>
        <div class="table-wrap"><table>
          <thead><tr><th>Observable</th><th>Legacy value</th><th>Reference</th><th>Status</th><th>Reason</th></tr></thead>
          <tbody>
            ${data.legacy_claims.map((row) => `<tr>
              <td class="mono">${row.observable}</td>
              <td class="mono">${row.legacy_value}</td>
              <td>${row.reference}</td>
              <td>${badge(row.status)}</td>
              <td>${row.reason}</td>
            </tr>`).join("")}
          </tbody>
        </table></div>
      </article>
      <article class="card" style="margin-top:14px">
        <h3>TCD assumption ledger · ${data.ledger.ledger_id}</h3>
        <div class="table-wrap"><table>
          <thead><tr><th>ID</th><th>Class</th><th>Statement</th><th>Impact</th></tr></thead>
          <tbody>
            ${entries.map((e) => `<tr>
              <td class="mono">${e.id}</td>
              <td>${badge(e.classification)}</td>
              <td>${e.statement}</td>
              <td>${e.impact}</td>
            </tr>`).join("")}
          </tbody>
        </table></div>
        <div class="note">Validated TCD predictions: <b>${data.validated_predictions}</b></div>
      </article>
    `;
}

function paintStaticPanels() {
  renderRGEPanel();
  renderSpectralPanel();
  renderTCDPanel();
  renderLQCPanel();
  renderInflationPanel();
  renderTheoryPanel();
  renderJacobsonPanel();
  renderDataPanel();
  renderLedgerPanel();
}

async function boot() {
  renderShell();
  paintStaticPanels();
  $("lang-pl").addEventListener("click", () => { lang = "pl"; renderShell(); paintStaticPanels(); showPanel(currentPanel); });
  $("lang-en").addEventListener("click", () => { lang = "en"; renderShell(); paintStaticPanels(); showPanel(currentPanel); });
  window.addEventListener("resize", () => {
    if (currentPanel === "rge" && cache.rge) displayRGE(cache.rge);
    if (currentPanel === "spectral" && cache.spectral) displaySpectral(cache.spectral);
    if (currentPanel === "tcd" && cache.tcd) displayTCD(cache.tcd);
    if (currentPanel === "lqc" && cache.lqc) displayLQC(cache.lqc);
    if (currentPanel === "inflation" && cache.inflation) displayInflation(cache.inflation);
    if (currentPanel === "theory" && cache.theory) displayTheory(cache.theory);
    if (currentPanel === "data" && cache.data) displayData(cache.data);
  });
  try {
    statusData = await api("/api/status");
  } catch (err) {
    statusData = { gates: { KEEP: [], HOLD: [], "NO-GO": [] }, modules: [], what_this_is: err.message, what_this_is_not: "" };
  }
  showPanel("dash");
}

boot();
t api("/api/status");
  } catch (err) {
    statusData = { gates: { KEEP: [], HOLD: [], "NO-GO": [] }, modules: [], what_this_is: err.message, what_this_is_not: "" };
  }
  showPanel("dash");
}

boot();
