// Render card HTML -> print PDF (vector text, 96x61mm incl. bleed) + 300 DPI PNG.
// usage: node render.mjs <name> [<name> ...]   (names from html/, without .html)
import { chromium } from "playwright-core";
import path from "node:path";
import fs from "node:fs";

const ROOT = path.dirname(new URL(import.meta.url).pathname);
const names = process.argv.slice(2);
const DPR = 300 / 96; // CSS px are 96/in
const W = Math.round((96 / 25.4) * 96), H = Math.round((61 / 25.4) * 96);

const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: DPR });
fs.mkdirSync(`${ROOT}/out`, { recursive: true });

for (const n of names) {
  if (n.endsWith("-marks")) {
    await page.goto(`file://${ROOT}/html/${n}.html`); await page.evaluate(() => document.fonts.ready); await page.waitForLoadState("networkidle");
    await page.pdf({ path: `${ROOT}/out/${n}.pdf`, width: "108mm", height: "73mm", printBackground: true, pageRanges: "1" });
    console.log("ok", n); continue;
  }
  await page.goto(`file://${ROOT}/html/${n}.html`);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForLoadState("networkidle");
  // overflow / safe-area check: every text element must sit within the 5mm safe area
  const issues = await page.evaluate(() => {
    const mm = 96 / 25.4, out = [];
    const safe = { l: 8 * mm, t: 8 * mm, r: 88 * mm, b: 53 * mm };
    document.querySelectorAll(".trim p, .trim li, .trim img, .qrwrap, .plate").forEach((el) => {
      let r = el.getBoundingClientRect();
      if (el.matches("p, li")) { const rg = document.createRange(); rg.selectNodeContents(el); r = rg.getBoundingClientRect(); }
      const tol = 0.6;
      if (r.left < safe.l - tol || r.top < safe.t - tol || r.right > safe.r + tol || r.bottom > safe.b + tol)
        out.push(`${el.className || el.tagName} [${(r.left / mm).toFixed(1)},${(r.top / mm).toFixed(1)} → ${(r.right / mm).toFixed(1)},${(r.bottom / mm).toFixed(1)}]mm`);
    });
    return out;
  });
  if (issues.length) console.log(`! ${n} outside safe area:\n  ` + issues.join("\n  "));
  await page.screenshot({ path: `${ROOT}/out/${n}.png`, fullPage: false });
  if (!n.endsWith("-guides")) await page.pdf({ path: `${ROOT}/out/${n}.pdf`, width: "96mm", height: "61mm", printBackground: true, pageRanges: "1" });
  console.log("ok", n);
}
await browser.close();
