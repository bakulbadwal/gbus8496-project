// Group 11 deck — house style (deep navy, brass, warm paper ink), 16:9.
// Slides 1, 3, 4, 6 carry real content; 2 has the real chart; 5, 7, 8, 9, 10 are styled frames
// with each owner's one-sentence brief and a marked drop zone.
const pptxgen = require("pptxgenjs");
const OUT = process.argv[2];
const ASSETS = process.argv[3]; // docs/slides/assets, absolute

const NAVY = "081321", S1 = "0D1C2B", S2 = "13253A", BRASS = "C9A96A";
const INK = "F2EDE3", MUTED = "D9D3C6", SUBTLE = "B4AE9F", TERT = "8A8474";
const BLUE = "3987E5", ORANGE = "D95926";
const T = "Cambria", B = "Calibri", M = "Courier New";

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
pres.author = "Group 11 — GBUS 8496";
pres.title = "Predicting the Second Gift";

const W = 10, H = 5.625, MX = 0.55;

function base(slide, eyebrow, owner, n) {
  slide.background = { color: NAVY };
  slide.addText(eyebrow.toUpperCase(), { x: MX, y: 0.32, w: 6.6, h: 0.28, fontFace: M, fontSize: 9, color: BRASS,
    charSpacing: 2, isTextBox: true, margin: 0 });
  slide.addText(`${owner}  ·  ${n} / 10`, { x: W - MX - 3.2, y: 0.32, w: 3.2, h: 0.28, fontFace: M, fontSize: 9,
    color: TERT, align: "right", isTextBox: true, margin: 0 });
}
function title(slide, text, opts = {}) {
  slide.addText(text, { x: MX, y: opts.y ?? 0.68, w: opts.w ?? (W - 2 * MX), h: opts.h ?? 0.95, fontFace: T,
    fontSize: opts.size ?? 30, bold: true, color: "FFFFFF", isTextBox: true, margin: 0, valign: "top",
    lineSpacingMultiple: 1.05 });
}
function card(slide, x, y, w, h, fill = S1) {
  slide.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: fill }, line: { color: fill, width: 0 },
    rectRadius: 0.06 });
}
function body(slide, text, x, y, w, h, opts = {}) {
  slide.addText(text, { x, y, w, h, fontFace: B, fontSize: opts.size ?? 13, color: opts.color ?? MUTED,
    isTextBox: true, margin: 0, valign: opts.valign ?? "top", italic: !!opts.italic, bold: !!opts.bold,
    lineSpacingMultiple: 1.15, align: opts.align ?? "left" });
}
function label(slide, text, x, y, w) {
  slide.addText(text.toUpperCase(), { x, y, w, h: 0.22, fontFace: M, fontSize: 8, color: BRASS, charSpacing: 2,
    isTextBox: true, margin: 0 });
}
function dropzone(slide, x, y, w, h, what) {
  slide.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: NAVY }, rectRadius: 0.06,
    line: { color: BRASS, width: 0.75, dashType: "dash" } });
  slide.addText([{ text: "DROP HERE", options: { fontFace: M, fontSize: 8, color: BRASS, charSpacing: 2, breakLine: true } },
                 { text: what, options: { fontFace: B, fontSize: 12, color: SUBTLE, italic: true } }],
    { x: x + 0.2, y: y + 0.2, w: w - 0.4, h: h - 0.4, isTextBox: true, margin: 0, valign: "middle", align: "center" });
}
function stat(slide, big, small, x, y, w) {
  slide.addText(big, { x, y, w, h: 0.62, fontFace: T, fontSize: 34, bold: true, color: "FFFFFF", isTextBox: true, margin: 0 });
  slide.addText(small.toUpperCase(), { x, y: y + 0.62, w, h: 0.22, fontFace: M, fontSize: 8, color: TERT, charSpacing: 1.5,
    isTextBox: true, margin: 0 });
}
const chartFrame = {
  chartArea: { fill: { color: NAVY } }, plotArea: { fill: { color: NAVY } },
  catAxisLabelColor: MUTED, catAxisLabelFontFace: B, catAxisLabelFontSize: 11,
  valAxisLabelColor: TERT, valAxisLabelFontFace: B, valAxisLabelFontSize: 9,
  valGridLine: { color: S2, size: 0.5 }, catGridLine: { style: "none" }, valAxisLineShow: false, catAxisLineShow: false,
  showTitle: false, dataLabelFontFace: B, dataLabelColor: INK, dataLabelFontSize: 11,
};

// ── 1 · Title + disclosure ──────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  base(s, "GBUS 8496 · Machine Learning and AI for Business · Group 11", "Malorie", 1);
  s.addText("Predicting the", { x: MX, y: 1.15, w: 8, h: 0.75, fontFace: T, fontSize: 40, color: INK, isTextBox: true, margin: 0 });
  s.addText("Second Gift", { x: MX, y: 1.85, w: 8, h: 0.9, fontFace: T, fontSize: 54, bold: true, color: "FFFFFF", isTextBox: true, margin: 0 });
  body(s, "Which first-time donors will give again, and which ones a small nonprofit should spend staff time on.",
    MX, 2.85, 6.2, 0.6, { size: 15, italic: true, color: MUTED });
  body(s, "Malorie Black · Reid Jacobson · Thadeus Knospe · Rodolfo Perez-Cortes Manrique · Bakul Badwal",
    MX, 3.55, 8.9, 0.3, { size: 11, color: SUBTLE });
  card(s, MX, 4.15, W - 2 * MX, 0.95, S2);
  label(s, "Disclosure, said first", MX + 0.25, 4.27, 4);
  body(s, "One of us founded GoGood Technologies, a donor-engagement platform whose customers are the stakeholder in this talk. That is why we chose the problem. Weigh what we say accordingly.",
    MX + 0.25, 4.5, W - 2 * MX - 0.5, 0.55, { size: 12, color: INK });
  s.addNotes("30 seconds. Title, five names, then the disclosure out loud — Albert asked for it explicitly. Saying it first makes it a strength: we picked a problem one of us has watched people have.");
}

// ── 2 · 71% never come back ─────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  base(s, "The problem", "Malorie", 2);
  s.addText("71%", { x: MX, y: 0.75, w: 3.6, h: 1.45, fontFace: T, fontSize: 96, bold: true, color: BRASS, isTextBox: true, margin: 0 });
  body(s, "of DonorsChoose donors gave once and never again.", MX, 2.2, 3.7, 0.7, { size: 18, color: "FFFFFF", bold: true });
  body(s, "3.5 million donors, seventeen years. The second gift is where retention is won or lost, and small organizations have the least capacity to work it.",
    MX, 2.95, 3.7, 0.9, { size: 12 });
  card(s, MX, 3.95, 3.7, 1.15, S1);
  label(s, "Our stakeholder", MX + 0.2, 4.05, 3);
  body(s, "A development lead at a ~$500K nonprofit, no data staff. Each month she can personally follow up with a fraction of last month's new donors. She builds that list by hand, from recency and gift size.",
    MX + 0.2, 4.28, 3.3, 0.8, { size: 10.5, color: INK });
  s.addImage({ path: ASSETS + "/slide2_donations_per_donor_dark.png", x: 4.55, y: 0.85, w: 4.9, h: 4.25 });
  s.addNotes("60 seconds. Land the number and the person, then stop. Chart data: evals/results/01_check_donor_id.txt.");
}

// ── 3 · What a second gift is ───────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  base(s, "Data and label", "Bakul", 3);
  title(s, "Four decisions turn eleven million rows into one label. Each could have gone the other way.", { size: 24, h: 1.0 });
  stat(s, "11.4M", "donations", MX, 1.85, 2.5); stat(s, "3.28M", "labelled donors", MX, 2.7, 2.5);
  stat(s, "15.8%", "repeat within 12 mo", MX, 3.55, 2.5);
  body(s, "ICPSR 37898, 2002–2019. Train through 2016, hold out 2017–18: a random split would let the model see the future.",
    MX, 4.55, 2.5, 0.65, { size: 9.5, color: SUBTLE });
  const cards = [
    ["Same-month repeats don't count", "One checkout can fund several classrooms. Two gifts in month one are one event, not a return. She cannot steward back someone who never left."],
    ["Twelve whole months", "M+1 to M+12. Dates are month-level, so no finer definition exists and none is claimed."],
    ["Unclosed windows: dropped, not zeroed", "A 2019 donor has not had a year to come back. Labelling them 0 teaches the model that recent donors never return."],
    ["Refunds are not gifts", "The codebook lists a minimum amount of −$15. A reversal cannot open a cohort or count as a return. 151 rows, excluded."],
  ];
  const cx = 3.35, cw = 2.95, ch = 1.62, gap = 0.2;
  cards.forEach(([h, t], i) => {
    const x = cx + (i % 2) * (cw + gap), y = 1.85 + Math.floor(i / 2) * (ch + gap);
    card(s, x, y, cw, ch, S1);
    s.addText(String(i + 1), { x: x + 0.18, y: y + 0.14, w: 0.4, h: 0.35, fontFace: T, fontSize: 20, bold: true, color: BRASS, isTextBox: true, margin: 0 });
    body(s, h, x + 0.55, y + 0.17, cw - 0.7, 0.45, { size: 12, bold: true, color: "FFFFFF" });
    body(s, t, x + 0.18, y + 0.62, cw - 0.36, ch - 0.72, { size: 10, color: MUTED });
  });
  s.addNotes("55 seconds. One line per decision. The point is not the decisions themselves but that each is stated and reversible — the notebook reports the positive rate both ways for the same-month rule.");
}

// ── 4 · The finding that almost fooled us ───────────────────────────────────────────────────
{
  const s = pres.addSlide();
  base(s, "The finding", "Bakul", 4);
  title(s, "708 organizations hold 62% of every repeat dollar.", { size: 26, h: 0.55 });
  body(s, "Our first result found 80% of all repeat dollars at 10% capacity with the dumbest possible rule: rank by gift size. It looked like a triumph.",
    MX, 1.75, 3.55, 0.9, { size: 12, color: INK });
  body(s, "It was measuring corporate matching programs. The largest made 66,348 donations in its twelve-month window. Any ranker wins the pooled contest by finding them — and she already knows who they are.",
    MX, 2.7, 3.55, 1.1, { size: 12 });
  card(s, MX, 3.95, 3.55, 1.15, S2);
  label(s, "The decision", MX + 0.2, 4.05, 3);
  body(s, "Score citizen donors only — 86% of people, the ones she actually calls. One line in config, reversible, both numbers kept.",
    MX + 0.2, 4.28, 3.15, 0.8, { size: 10.5, color: INK });
  s.addImage({ path: ASSETS + "/slide4_donor_type_shares_dark.png", x: 4.83, y: 1.32, w: 4.62, h: 3.8 });
  s.addNotes("60 seconds. Tell it as it happened. This is the slide the 'genuine insight' vote is won on. Chart data: evals/results/03_profile_cohorts.txt, holdout cohorts.");
}

// ── 5 · What predicts a return (Reid) ───────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  base(s, "Features", "Reid", 5);
  title(s, "What predicts a return", { size: 30, h: 0.7 });
  body(s, "Gift size finds dollars; [feature] finds people. Here is what moved and what did not.", MX, 1.4, 4, 0.7, { size: 13, italic: true, color: BRASS });
  body(s, "Structure to keep: one chart of importance or lift, one sentence per feature that mattered, one on what did not. Text is masked by ICPSR — no embeddings. Tie back to slide 4.",
    MX, 2.15, 3.6, 1.4, { size: 11 });
  dropzone(s, 4.55, 1.3, 4.9, 3.85, "Feature importance or lift table — one chart");
  s.addNotes("55 seconds. Owner fills in. Serves the 'genuine insight' question.");
}

// ── 6 · Model vs the honest baseline (Rodolfo) ──────────────────────────────────────────────
{
  const s = pres.addSlide();
  base(s, "The headline", "Rodolfo", 6);
  title(s, "At her capacity, dollars identified per contact", { size: 28, h: 0.7 });
  body(s, "Citizen donors · top 10% of each month's new donors · 2017–18 holdout · value identified, never “caused”",
    MX, 1.38, 8.9, 0.3, { size: 10, color: SUBTLE });
  const hdr = (t) => ({ text: t, options: { bold: true, color: BRASS, fontFace: M, fontSize: 8, fill: { color: S2 }, align: "left", valign: "middle" } });
  const cell = (t, o = {}) => ({ text: t, options: { color: o.color ?? MUTED, fontFace: B, fontSize: 11, bold: !!o.bold, fill: { color: o.fill ?? NAVY }, align: o.align ?? "right", valign: "middle" } });
  const rows = [
    [hdr("RANKING"), hdr("PRECISION"), hdr("RECALL"), hdr("VALUE FOUND"), hdr("$ / CONTACT")],
    [cell("Our model", { align: "left", bold: true, color: "FFFFFF", fill: S1 }), cell("[  ]", { fill: S1, color: BRASS }), cell("[  ]", { fill: S1, color: BRASS }), cell("[  ]", { fill: S1, color: BRASS }), cell("$[   ]", { fill: S1, color: BRASS, bold: true })],
    [cell("First gift size — the honest baseline", { align: "left", color: INK }), cell("19.7%"), cell("15.7%"), cell("56.4%"), cell("$116", { bold: true, color: INK })],
    [cell("First-month gift count", { align: "left" }), cell("20.4%"), cell("16.2%"), cell("41.4%"), cell("$85")],
    [cell("Random", { align: "left" }), cell("12.7%"), cell("10.1%"), cell("9.1%"), cell("$19")],
    [cell("Contact everyone", { align: "left" }), cell("12.6%"), cell("100%"), cell("100%"), cell("$21")],
  ];
  s.addTable(rows, { x: MX, y: 1.8, w: W - 2 * MX, colW: [3.5, 1.35, 1.35, 1.55, 1.15], rowH: 0.42, border: { type: "solid", color: S2, pt: 0.5 }, margin: 0.08 });
  body(s, "The baseline is fair: on a first-gift cohort, RFM collapses to gift size, and gift size is what she does by hand. If the model does not beat $116, say so and go to slide 9.",
    MX, 4.5, 8.9, 0.6, { size: 10.5, color: SUBTLE, italic: true });
  s.addNotes("60 seconds. Headline metric is dollars per contact, not AUC — Albert said the ranking at capacity is the decision. Baseline rows are real (evals/results/04_score_citizen.txt); the model row is the owner's.");
}

// ── 7 · How we know it works (Thadeus) ──────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  base(s, "Evaluation", "Thadeus", 7);
  title(s, "How we know it works — and where it does not", { size: 28, h: 0.7 });
  body(s, "It is calibrated here, it is not calibrated there, and it is weakest on exactly the donors she cares about most.", MX, 1.4, 4, 0.8, { size: 13, italic: true, color: BRASS });
  body(s, "Calibration curve on the holdout. Error analysis by cohort year — does 2018 behave like 2015? — and by first-gift size band, where most of her donors live.",
    MX, 2.3, 3.6, 1.3, { size: 11 });
  dropzone(s, 4.55, 1.3, 2.35, 3.85, "Calibration curve");
  dropzone(s, 7.1, 1.3, 2.35, 3.85, "Error by cohort year / gift band");
  s.addNotes("60 seconds. Answers Albert's 'how do you know it works' directly. The honest sentence about where it is weakest is the one the room respects.");
}

// ── 8 · What she does on Monday (Malorie) ───────────────────────────────────────────────────
{
  const s = pres.addSlide();
  base(s, "The decision", "Malorie", 8);
  title(s, "What she does on Monday", { size: 30, h: 0.7 });
  const cols = [["[N] hrs", "monthly capacity"], ["[N] calls", "at [ ] min each"], ["$[  ]", "per contact"], ["$0", "to run, monthly"]];
  cols.forEach(([b, sm], i) => {
    const x = MX + i * 2.25; card(s, x, 1.5, 2.05, 1.45, S1);
    s.addText(b, { x: x + 0.2, y: 1.66, w: 1.75, h: 0.6, fontFace: T, fontSize: 28, bold: true, color: "FFFFFF", isTextBox: true, margin: 0 });
    s.addText(sm.toUpperCase(), { x: x + 0.2, y: 2.36, w: 1.75, h: 0.4, fontFace: M, fontSize: 8, color: TERT, charSpacing: 1.5, isTextBox: true, margin: 0 });
  });
  body(s, "Given her hours, work this list and expect roughly $[Y] in subsequent giving that the old list would have missed. Amount model: cohort median to start (Albert: fine). This answers 'what would it cost at scale' in one line.",
    MX, 3.15, 8.9, 0.8, { size: 12 });
  dropzone(s, MX, 4.05, W - 2 * MX, 1.05, "The recommendation sentence a development lead repeats to her board");
  s.addNotes("60 seconds. Cost per contact from real practice — a number GoGood can defend. Production cost is effectively zero and should be said as such.");
}

// ── 9 · What we are not claiming (Thadeus) ──────────────────────────────────────────────────
{
  const s = pres.addSlide();
  base(s, "Limits", "Thadeus", 9);
  title(s, "What we did not find, and what we are not claiming", { size: 26, h: 0.7 });
  const items = [
    ["No causal claim", "Nobody was randomly assigned to be contacted. We rank by predicted future value and say “identified”, never “caused”."],
    ["Thank-you packet: dropped", "The codebook gives no timing. The flag may record something that happened after the second gift. Albert pre-approved dropping it."],
    ["Transfer is a hypothesis", "DonorsChoose donors are marketplace donors; small-nonprofit donors are relational. Behavioural features likely transfer; platform-specific ones likely do not."],
  ];
  items.forEach(([h, t], i) => {
    const x = MX + i * 3.0; card(s, x, 1.5, 2.85, 3.2, S1);
    s.addText(String(i + 1), { x: x + 0.22, y: x ? 1.7 : 1.7, w: 0.5, h: 0.5, fontFace: T, fontSize: 26, bold: true, color: BRASS, isTextBox: true, margin: 0 });
    body(s, h, x + 0.22, 2.3, 2.45, 0.5, { size: 13, bold: true, color: "FFFFFF" });
    body(s, t, x + 0.22, 2.85, 2.45, 1.7, { size: 10.5 });
  });
  s.addNotes("50 seconds. Three things, plainly. Serves the insight question and the honesty Albert grades under 'technical contribution'.");
}

// ── 10 · The recommendation ─────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  base(s, "Recommendation", "Malorie", 10);
  s.addText("Rank this month's first-time donors by [model / gift size], call the top [N], and expect to reach [X] percent of next year's repeat giving with [Y] hours.",
    { x: MX + 0.3, y: 1.35, w: W - 2 * MX - 0.6, h: 2.3, fontFace: T, fontSize: 28, color: "FFFFFF", isTextBox: true, margin: 0, valign: "middle", lineSpacingMultiple: 1.15 });
  body(s, "One sentence. Then stop.", MX + 0.3, 3.85, 4, 0.35, { size: 12, italic: true, color: BRASS });
  body(s, "github.com/bakulbadwal/gbus8496-project  ·  every number reproduces with  python evals/run_all.py",
    MX + 0.3, 4.65, 8.6, 0.3, { size: 9.5, color: TERT });
  s.addNotes("20 seconds. The exact words come from slides 6 and 8.");
}

pres.writeFile({ fileName: OUT }).then(() => console.log("wrote", OUT));
