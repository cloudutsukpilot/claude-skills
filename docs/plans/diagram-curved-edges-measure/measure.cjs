const path = require('path'), fs = require('fs');
const { chromium } = require(path.join(process.env.HOME, '.cache/interactive-diagrams/node_modules/playwright-core'));
const exe = fs.readdirSync(path.join(process.env.HOME, '.cache/ms-playwright')).filter((d) => /^chromium-\d+$/.test(d)).sort().pop();
const CHROME = path.join(process.env.HOME, '.cache/ms-playwright', exe, 'chrome-linux/chrome');
const STYLES = { stable: ['orthogonal', 'rounded', 'smooth', 'direct', 'direct-tight'], auto: ['orthogonal', 'splines', 'direct'] };
const only = process.argv[2];
(async () => {
  const browser = await chromium.launch({ executablePath: fs.existsSync(CHROME) ? CHROME : undefined });
  const rows = [];
  for (const dir of fs.readdirSync(__dirname).filter((d) => fs.existsSync(path.join(__dirname, d, 'index.html')) && (!only || d.startsWith(only)))) {
    const layout = dir.split('-').pop();
    for (const style of STYLES[layout]) {
      const page = await browser.newPage({ viewport: { width: 1500, height: 950 } });
      const msgs = [];
      page.on('console', (c) => { if (c.type() === 'warning' || c.type() === 'error') msgs.push(c.text().slice(0, 200)); });
      const errs = [];
      try {
      page.on('pageerror', (e) => errs.push(String(e)));
      await page.goto('file://' + path.join(__dirname, dir, 'index.html') + '?edges=' + style);
      const sel = '#dgm-' + dir;
      await page.waitForSelector(sel + '.is-ready', { timeout: 180000 });
      const max = await page.$eval(sel, (f) => f._dgm.maxLevel);
      for (let L = 0; L <= max; L++) {
        const ms = await page.$eval(sel, async (f, L) => { const t = performance.now(); await f._dgm.setLevel(L); return performance.now() - t; }, L);
        await page.$eval(sel, (f) => f._dgm.overview(false));
        await page.waitForTimeout(400);
        const m = await page.$eval(sel, (f) => {
          const d = f._dgm, P = d._placed, vis = d._vis;
          const nodes = [...P.nodes.entries()].map(([id, b]) => ({ id, ...b }));
          const leaves = nodes.filter((n) => !n.group);
          let [x0, y0, x1, y1] = [1e9, 1e9, -1e9, -1e9];
          const grow = (x, y) => { x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); };
          nodes.forEach((n) => { grow(n.x, n.y); grow(n.x + n.w, n.y + n.h); });
          const edges = vis.map((v) => ({ v, pts: (P.edges.get(v.key) || {}).pts })).filter((e) => e.pts && e.pts.length > 1);
          edges.forEach((e) => e.pts.forEach(([x, y]) => grow(x, y)));
          let ink = 0;
          for (const e of edges) for (let i = 1; i < e.pts.length; i++) ink += Math.hypot(e.pts[i][0] - e.pts[i - 1][0], e.pts[i][1] - e.pts[i - 1][1]);
          // crossings, ignoring points near either arrow's ends (fans at a shared component)
          const near = (p, e) => [e.pts[0], e.pts[e.pts.length - 1]].some((q) => Math.hypot(p[0] - q[0], p[1] - q[1]) < 16);
          const bb = (e) => e.pts.reduce((b, [x, y]) => [Math.min(b[0], x), Math.min(b[1], y), Math.max(b[2], x), Math.max(b[3], y)], [1e9, 1e9, -1e9, -1e9]);
          edges.forEach((e) => (e.bb = bb(e)));
          const X = (a, b, c, d2) => {
            const r = (b[0] - a[0]) * (d2[1] - c[1]) - (b[1] - a[1]) * (d2[0] - c[0]);
            if (Math.abs(r) < 1e-9) return null;
            const t = ((c[0] - a[0]) * (d2[1] - c[1]) - (c[1] - a[1]) * (d2[0] - c[0])) / r;
            const u = ((c[0] - a[0]) * (b[1] - a[1]) - (c[1] - a[1]) * (b[0] - a[0])) / r;
            return t >= 0 && t <= 1 && u >= 0 && u <= 1 ? [a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])] : null;
          };
          let cross = 0;
          for (let i = 0; i < edges.length; i++) for (let j = i + 1; j < edges.length; j++) {
            const A = edges[i], B = edges[j];
            if (A.bb[2] < B.bb[0] || B.bb[2] < A.bb[0] || A.bb[3] < B.bb[1] || B.bb[3] < A.bb[1]) continue;
            const hits = [];
            for (let s = 1; s < A.pts.length; s++) for (let t = 1; t < B.pts.length; t++) {
              const p = X(A.pts[s - 1], A.pts[s], B.pts[t - 1], B.pts[t]);
              if (p && !near(p, A) && !near(p, B) && !hits.some((h) => Math.hypot(h[0] - p[0], h[1] - p[1]) < 4)) hits.push(p);
            }
            cross += hits.length;
          }
          // arrows over components they don't connect
          let overN = 0, overPx = 0;
          for (const e of edges) {
            const own = new Set([e.v.from, e.v.to, ...d.ancestorsOf(e.v.from).map((a) => a.id), ...d.ancestorsOf(e.v.to).map((a) => a.id)]);
            const foreign = leaves.filter((n) => !own.has(n.id));
            let px = 0;
            for (let i = 1; i < e.pts.length; i++) {
              const a = e.pts[i - 1], b = e.pts[i], L = Math.hypot(b[0] - a[0], b[1] - a[1]), k = Math.max(1, Math.ceil(L / 3));
              for (let s = 0; s < k; s++) {
                const x = a[0] + ((b[0] - a[0]) * (s + 0.5)) / k, y = a[1] + ((b[1] - a[1]) * (s + 0.5)) / k;
                if (foreign.some((n) => x > n.x + 2 && x < n.x + n.w - 2 && y > n.y + 2 && y < n.y + n.h - 2)) px += L / k;
              }
            }
            if (px > 6) { overN++; overPx += px; }
          }
          // pill and label clashes, on screen
          const R = (el) => el.getBoundingClientRect();
          const leafR = [...d.nodeEls.values()].filter((el) => el.isConnected && el.dataset.kind === 'leaf').map((el) => R(el.querySelector('rect') || el));
          const labs = [...f.querySelectorAll('.dgm-pill, .dgm-link-label')].map(R);
          const ov = (a, b) => Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left)) * Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top)) > 4;
          let clash = 0;
          labs.forEach((a, i) => { if (leafR.some((b) => ov(a, b))) clash++; else if (labs.some((b, j) => j !== i && ov(a, b))) clash++; });
          return { leaves: leaves.length, arrows: edges.length, w: Math.round(x1 - x0), h: Math.round(y1 - y0), area: Math.round(((x1 - x0) * (y1 - y0)) / 1000), ink: Math.round(ink), cross, overN, overPx: Math.round(overPx), labels: labs.length, clash };
        });
        await page.screenshot({ path: path.join(__dirname, 'shots', `${dir}-L${L}-${style}.png`) });
        rows.push({ dir, style, L, ms: Math.round(ms), ...m, errs: errs.length });
        console.log(JSON.stringify(rows[rows.length - 1]));
        fs.writeFileSync(path.join(__dirname, only ? `results-${only}.json` : 'results.json'), JSON.stringify(rows, null, 1));
      }
      } catch (err) {
        rows.push({ dir, style, failed: String(err).split('\n')[0], msgs: msgs.slice(0, 5), errs: errs.slice(0, 3) });
        console.log(JSON.stringify(rows[rows.length - 1]));
        fs.writeFileSync(path.join(__dirname, only ? `results-${only}.json` : 'results.json'), JSON.stringify(rows, null, 1));
      }
      await page.close();
    }
  }
  fs.writeFileSync(path.join(__dirname, only ? `results-${only}.json` : 'results.json'), JSON.stringify(rows, null, 1));
  await browser.close();
})();
