// Builds the one-page proposal .docx from Proposal_v1.md-equivalent content.
const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, AlignmentType, BorderStyle } = require("docx");

const OUT = process.argv[2];
const FONT = "Calibri";
const BODY = 22;
const HEAD = 24;

function runs(spec) {
  // spec: array of [text, {bold?, italics?}] or plain strings
  return spec.map(s => typeof s === "string"
    ? new TextRun({ text: s, font: FONT, size: BODY })
    : new TextRun({ text: s[0], font: FONT, size: BODY, bold: !!s[1].bold, italics: !!s[1].italics }));
}
const P = (spec, opts = {}) => new Paragraph({
  children: runs(spec),
  spacing: { after: opts.after ?? 70, line: 240 },
  alignment: AlignmentType.LEFT,
});
const H = (text) => new Paragraph({
  children: [new TextRun({ text, font: FONT, size: HEAD, bold: true })],
  spacing: { before: 90, after: 40 },
});

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: BODY } } } },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 800, bottom: 800, left: 1080, right: 1080 } } },
    children: [
      new Paragraph({
        children: [new TextRun({ text: "GBUS 8496 — Final Project Proposal", font: FONT, size: 32, bold: true })],
        spacing: { after: 40 },
        border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "222222", space: 2 } },
      }),
      P([["Team: ", { bold: true }], "Bakul Badwal · Thadeus Knospe · Malorie Black · [names] — Group [#]"], { after: 20 }),
      P([["Working title: ", { bold: true }], ["Who reads this one? Screening triage for a nonprofit's volunteer reviewers", { italics: true }]], { after: 60 }),

      H("1. Problem and business application"),
      P(["DonorsChoose.org is a nonprofit through which public-school teachers post classroom project requests that donors fund. Before a request goes live, a volunteer screener reads it against the organization's approval criteria. Volume runs to hundreds of thousands of proposals a year, and volunteer reviewers are the scarce resource: they set how fast a request reaches donors. Today every proposal gets a full human read."]),
      P([["User: ", { bold: true }], "the operations lead for project screening. ", ["Decision: ", { bold: true }], "which incoming proposals can be approved with no human read, which go to a reviewer as routine, and which are flagged for a closer read. The costs are explicit and asymmetric: a reviewer-hour; approving a proposal that should have been rejected (donor money misdirected, trust damaged); and rejecting or delaying a good classroom request. The output turns a flat queue into a triage policy with a stated reviewer-hours saving and error budget."]),

      H("2. Dataset and source"),
      P([["DonorsChoose.org Application Screening", { italics: true }], " — released by DonorsChoose for the 2018 Kaggle competition of the same name: about 182,000 real proposals submitted in 2016–2017, each with the teacher's essays, title, resource summary, subject categories, grade band, state, and count of prior projects; a linked resources table (requested items and prices); and the human screener's actual decision, project_is_approved (roughly 85% approved). Ground truth is a real human judgment. Source: kaggle.com/competitions/donorschoose-application-screening; login-free mirror on Hugging Face (udayl/donors_choose_data, 200 MB + 127 MB)."]),

      H("3. What we will build"),
      P(["A screening-triage system built as three tiers of increasing cost, compared honestly: ", ["(a)", { bold: true }], " a tabular-only gradient-boosting model on categories, prices, and teacher history; ", ["(b)", { bold: true }], " the same model plus sentence-transformer embeddings of the essays (the Session 7 pipeline); ", ["(c)", { bold: true }], " a frontier LLM asked to screen each proposal with DonorsChoose's published criteria in the prompt (Session 8). On top of whichever tier wins, a ", ["decision layer", { bold: true }], ": approve / route / flag thresholds derived from the stated payoffs rather than tuned, plus the cost per 1,000 proposals of each tier at production volume."]),

      H("4. Evaluation"),
      P([["Ground truth: ", { bold: true }], "the human screener's decision on a ", ["time-based held-out split", { bold: true }], " (train on earlier submissions, test on the final months), untouched during development. ", ["Model metrics: ", { bold: true }], "AUC and calibration per tier. ", ["Decision metric: ", { bold: true }], "reviewer-hours saved and expected error cost under our policy versus two honest baselines, ", ["review everything", { italics: true }], " and ", ["approve everything", { italics: true }], " (the 85% majority rule). ", ["Error analysis: ", { bold: true }], "where each tier fails, cut by subject, grade, state, essay length, and request price, including whether errors fall unevenly across teacher groups. ", ["Ceiling: ", { bold: true }], "because the label is itself a human judgment, we hand-read a stratified sample of about 100 model–human disagreements to estimate how noisy the human decision is, which sets the ceiling for any model. The LLM tier is scored on a cost-bounded subset of about 2,000 test proposals. ", ["A negative result is reportable: ", { bold: true }], "if essay text adds nothing over tabular features, or the LLM screener agrees with humans no better than the cheap model, we report it, with the cost implications."]),

      H("5. What we need from you"),
      P(["(1) Confirmation that scoring the LLM tier on a ~2,000-proposal subset of the test split is an acceptable evaluation scope. (2) Whether the JupyterHub API tokens may be used for those calls, or we should bring our own keys. (3) Any objection to grounding a 2026 recommendation in 2016–17 data; we will state the limitation either way."], { after: 0 }),
    ],
  }],
});

Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log("wrote", OUT, buf.length, "bytes"); });
