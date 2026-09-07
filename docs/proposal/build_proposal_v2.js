// Builds the one-page proposal v2 (.docx) — Amazon new-product traction.
const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, AlignmentType, BorderStyle } = require("docx");
const OUT = process.argv[2];
const FONT = "Calibri";
const BODY = Number(process.argv[3] || 22);
const HEAD = BODY + 2;

function runs(spec) {
  return spec.map(s => typeof s === "string"
    ? new TextRun({ text: s, font: FONT, size: BODY })
    : new TextRun({ text: s[0], font: FONT, size: BODY, bold: !!s[1].bold, italics: !!s[1].italics }));
}
const P = (spec, opts = {}) => new Paragraph({ children: runs(spec), spacing: { after: opts.after ?? 70, line: 240 }, alignment: AlignmentType.LEFT });
const H = (text) => new Paragraph({ children: [new TextRun({ text, font: FONT, size: HEAD, bold: true })], spacing: { before: 90, after: 40 } });

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: BODY } } } },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 800, bottom: 800, left: 1080, right: 1080 } } },
    children: [
      new Paragraph({ children: [new TextRun({ text: "GBUS 8496 — Final Project Proposal", font: FONT, size: 32, bold: true })], spacing: { after: 40 }, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "222222", space: 2 } } }),
      P([["Team: ", { bold: true }], "Bakul Badwal · Malorie Black · Reid Jacobson · Thadeus Knospe · Rodolfo Perez-Cortes Manrique — Group [#]"], { after: 20 }),
      P([["Working title: ", { bold: true }], ["Will it sell? Predicting new-product traction on Amazon from what a seller can see at launch", { italics: true }]], { after: 60 }),

      H("1. Problem and business application"),
      P(["Third-party sellers and resellers decide every week which candidate products to list or stock on Amazon, and at what price. Capital tied up in a product that never moves costs inventory, storage fees, and the margin that inventory could have earned elsewhere; skipping a product that takes off costs the margin outright. Today that call is made from gut feel or from paid tools that infer sales from best-seller rank without showing their work."]),
      P([["User: ", { bold: true }], "the buyer at a reseller or private-label seller. ", ["Decision: ", { bold: true }], "stock this SKU or skip it, and in which price band. The costs are explicit and asymmetric (cost of a dud versus margin on a winner), so the model's output can be turned into a stock/skip rule with a stated expected profit rather than a score. A second output, which attributes are associated with traction within a category (price band, image count, description length, brand presence), is what a seller actually pays for, stated as association rather than cause."]),

      H("2. Dataset and source"),
      P([["Amazon Reviews 2023", { italics: true }], " (McAuley Lab, UC San Diego; huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023): 571 million reviews on 48 million items across 33 categories, May 1996 to September 2023, with per-item metadata (title, description, features, price, images, videos, store, category path, details) and per-review timestamps. Public, not gated, downloadable per category without a login (verified Sep 6). We use two to three categories that fit on a laptop, starting with All Beauty (213 MB metadata, 327 MB reviews), so the pipeline can be re-run by anyone."]),
      P([["Ground truth, constructed and stated as such: ", { bold: true }], "a product “gains traction” if it receives at least N reviews in the 12 months after its first review, with N set per category and the window fully observed before the September 2023 cutoff. Review counts are the standard public proxy for sales volume; we report sensitivity to N."]),

      H("3. What we will build"),
      P(["A traction classifier on ", ["launch-observable features only", { bold: true }], ": price, image and video counts, description and feature-list length, store presence, category depth, and structured details. The metadata’s rating_number and average_rating are 2023 snapshots of the outcome itself and are excluded; keeping them would be leakage, and we will show what happens to the score if they are left in. Two tiers: ", ["(a)", { bold: true }], " gradient boosting on the tabular features; ", ["(b)", { bold: true }], " the same plus sentence-transformer embeddings of title and description (the Session 7 pipeline). On top: a ", ["decision layer", { bold: true }], " whose stock/skip threshold is derived from the stated payoffs rather than tuned, and per-category attribute analysis (partial dependence by price band, image count, and description length), which is where the price-positioning question lives."]),

      H("4. Evaluation"),
      P([["Split: ", { bold: true }], "time-based by first-review date, training on earlier product cohorts and testing on later ones, untouched during development. ", ["Model metrics: ", { bold: true }], "AUC and calibration per tier and per category. ", ["Baselines: ", { bold: true }], "the category base rate, a price-only rule, and tabular-only versus tabular-plus-text, so we can say whether text earned its cost. ", ["Decision metric: ", { bold: true }], "expected profit of the stock/skip policy on the test cohort versus ", ["stock everything", { italics: true }], " and ", ["stock nothing", { italics: true }], ", under stated dud and winner payoffs, with a sensitivity table. ", ["Error analysis: ", { bold: true }], "where the model fails, cut by category, price band, and brand presence. ", ["Limitations we will measure, not just mention: ", { bold: true }], "the 2023 dump only contains products that still exist (survivorship), and the listed price is a 2023 snapshot rather than the launch price, so we report performance with price removed. ", ["A negative result is reportable: ", { bold: true }], "if launch metadata predicts traction no better than the base rate, that tells a seller the paid tools built on the same signals are selling noise."]),

      H("5. What we need from you"),
      P(["(1) Confirmation that a constructed label (N reviews in 12 months) is an acceptable ground truth when stated as a proxy and tested for sensitivity. (2) Whether two to three categories is acceptable scope, given the full dataset runs to hundreds of gigabytes. (3) Any objection to the survivorship limitation above; we will state it either way."], { after: 0 }),
    ],
  }],
});
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log("wrote", OUT, buf.length, "bytes"); });
