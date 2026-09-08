// Proposal v4 — "Predicting the Second Gift", styled .docx (Canvas-legal), one page, US Letter.
// House look on paper: navy ink, brass rule, warm-paper "at a glance" strip, right-aligned repo link.
const fs = require("fs");
const D = require("docx");
const { Document, Packer, Paragraph, TextRun, AlignmentType, BorderStyle, LevelFormat, Table, TableRow, TableCell,
        WidthType, ShadingType, TabStopType, ExternalHyperlink, Tab } = D;

const OUT = process.argv[2];
const BODY = Number(process.argv[3] || 21);           // half-points: 21 = 10.5pt
const FONT = "Calibri";
const NAVY = "0B1F33", BRASS = "B08D4A", INKMUTED = "5A5548", PAPER = "F6F2EA";
const USABLE = 12240 - 2 * 900;                        // page width minus margins, DXA

const t = (text, o = {}) => new TextRun({ text, font: FONT, size: o.size || BODY, bold: !!o.bold, italics: !!o.italics, color: o.color, characterSpacing: o.tracking });
const runs = spec => spec.map(s => typeof s === "string" ? t(s) : t(s[0], s[1]));
const P = (spec, o = {}) => new Paragraph({ children: runs(spec), spacing: { after: o.after ?? 60, line: 238 }, alignment: AlignmentType.LEFT });
const B = spec => new Paragraph({ children: runs(spec), numbering: { reference: "bul", level: 0 }, spacing: { after: 30, line: 238 } });
const H = text => new Paragraph({
  children: [t(text, { size: BODY + 1, bold: true, color: NAVY })],
  spacing: { before: 100, after: 30 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: BRASS, space: 1 } },
});

// "At a glance" strip: 5 cells on warm paper
const glance = [
  ["STAKEHOLDER", "Development lead at a ~$500K nonprofit, no data staff"],
  ["DECISION", "Which first-time donors get a personal follow-up, and where the cutoff sits"],
  ["DATA", "DonorsChoose Open Data 2002–2019 (ICPSR 37898): 11.4M donations, 2.1M projects"],
  ["GROUND TRUTH", "Observed second gift within 12 months, held-out 2017–18 cohorts"],
  ["HONEST BASELINE", "RFM — the recency-and-amount rule small nonprofits actually use"],
];
const cellW = Math.floor(USABLE / glance.length);
const strip = new Table({
  width: { size: cellW * glance.length, type: WidthType.DXA },
  columnWidths: glance.map(() => cellW),
  borders: { top: { style: BorderStyle.NONE, size: 0 }, bottom: { style: BorderStyle.NONE, size: 0 }, left: { style: BorderStyle.NONE, size: 0 }, right: { style: BorderStyle.NONE, size: 0 },
             insideHorizontal: { style: BorderStyle.NONE, size: 0 }, insideVertical: { style: BorderStyle.SINGLE, size: 4, color: "FFFFFF" } },
  rows: [new TableRow({ children: glance.map(([k, v]) => new TableCell({
    width: { size: cellW, type: WidthType.DXA },
    shading: { type: ShadingType.CLEAR, fill: PAPER, color: "auto" },
    margins: { top: 70, bottom: 70, left: 90, right: 90 },
    children: [
      new Paragraph({ children: [t(k, { size: 14, bold: true, color: BRASS, tracking: 20 })], spacing: { after: 20, line: 220 } }),
      new Paragraph({ children: [t(v, { size: BODY - 3, color: NAVY })], spacing: { after: 0, line: 228 } }),
    ],
  })) })],
});

const doc = new Document({
  styles: {
    default: { document: { run: { font: FONT, size: BODY, color: "1E1E1E" } } },
    characterStyles: [{ id: "Hyperlink", name: "Hyperlink", basedOn: "DefaultParagraphFont", run: { color: NAVY, underline: { type: "single", color: BRASS } } }],
  },
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 300, hanging: 200 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 680, bottom: 640, left: 900, right: 900 } } },
    children: [
      // Eyebrow + right-aligned repo link on one line
      new Paragraph({
        tabStops: [{ type: TabStopType.RIGHT, position: USABLE }],
        spacing: { after: 30 },
        children: [
          t("GBUS 8496 · MACHINE LEARNING AND AI FOR BUSINESS · PROF. MICHAEL ALBERT · GROUP 11 · SEPTEMBER 8, 2026", { size: 14, bold: true, color: BRASS, tracking: 18 }),
          new TextRun({ children: [new Tab()], font: FONT, size: 14 }),
          new ExternalHyperlink({ link: "https://github.com/bakulbadwal/gbus8496-project", children: [t("↗ github.com/bakulbadwal/gbus8496-project", { size: 15, bold: true, color: NAVY })] }),
        ],
      }),
      new Paragraph({ children: [t("Predicting the Second Gift", { size: 40, bold: true, color: NAVY })], spacing: { after: 10 } }),
      new Paragraph({
        children: [t("Which first-time donors will give again, and which ones a small nonprofit should spend its scarce staff hours on.", { size: BODY + 2, italics: true, color: INKMUTED })],
        spacing: { after: 60 },
        border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: BRASS, space: 3 } },
      }),
      P([["Team ", { bold: true, color: NAVY }], "Bakul Badwal · Malorie Black · Reid Jacobson · Thadeus Knospe · Rodolfo Perez-Cortes Manrique"], { after: 80 }),

      H("1 · Problem and business application"),
      P(["Most nonprofits acquire a donor once and never hear from them again. The second gift is the highest-leverage moment in the donor lifecycle, and small organizations are the least equipped to work it. Our stakeholder is the development lead at a nonprofit with roughly a $500K budget and no data staff: each month she can personally follow up with only a fraction of first-time donors, and today she builds that list by hand from recency and gift size."]),
      P([["The decision is specific: ", { bold: true }], "given a fixed outreach budget in staff hours, which first-time donors receive follow-up, and where does the cutoff sit? Our output is a ranked follow-up list with a recommended threshold and the expected dollars behind it. One of us founded GoGood Technologies, a donor-engagement platform serving exactly this customer, so real practitioners can check the output. ", ["In practice: ", { bold: true }], "the hand-built list becomes a scored one, and the budget question gets a number."]),

      H("2 · Dataset and source"),
      P([["DonorsChoose Open Data, United States, 2002–2019", { italics: true }], " (ICPSR 37898, doi.org/10.3886/ICPSR37898.v1). Public-use files, free with a no-cost ICPSR account. Two files: Donations (11,377,479 records) and Projects (2,149,817), covering September 2002 to June 2019 with activity through December 2019. Donations carries DONOR_ID, so we reconstruct each donor's history and build our own label, plus amount, month, donor type, and matched, teacher-referred, and thank-you-packet flags. Two constraints accepted up front: dates are month-level, and there is no demographics file, so donor type is the only donor attribute."]),

      H("3 · What we will build"),
      B([["Label. ", { bold: true }], "For each donor whose first recorded gift falls in the observation window: a second gift within 12 months? Only cohorts whose window closes before December 2019 are labeled."]),
      B([["Features. ", { bold: true }], "Donation-side (amount, seasonality, matched, gift card, teacher-referred, donor type, thank-you packet) and project-side (subject, grade, cost, state). Fields that could post-date the second gift are checked for timing before use."]),
      B([["Split. ", { bold: true }], "Time-based, never random: train on first-gift cohorts through 2016, hold out 2017 and 2018, observe outcomes through December 2019."]),
      B([["Decision layer. ", { bold: true }], "Predicted probability and second-gift amount become expected value per contact, minus an explicit cost per contact in staff time; the threshold is derived from those payoffs, not tuned."]),
      B([["Cost at scale. ", { bold: true }], "Scoring a year of first-time donors is a batch job on one machine, no API spend. The operating cost is the staff hours the threshold allocates, reported explicitly."]),

      H("4 · Evaluation — what we measure, against what ground truth"),
      P(["Ground truth is observed donor behavior in the held-out cohorts, not hand labels. Four measurements:"], { after: 30 }),
      B([["Discrimination and calibration. ", { bold: true }], "PR-AUC because the class is imbalanced, plus a calibration curve: an uncalibrated score cannot support a threshold."]),
      B([["Honest baselines. ", { bold: true }], "RFM, the recency-and-amount heuristic small nonprofits actually use, plus random targeting and contact-everyone. Business metric: net value retained per hour of outreach at a fixed budget. If the model does not beat RFM, that is the finding."]),
      B([["Does stewardship predict retention? ", { bold: true }], "The thank-you-packet flag records a real post-gift action. We estimate its association with a second gift controlling for gift size; packets were not randomly assigned, so association, not cause."]),
      B([["Error analysis by cohort. ", { bold: true }], "We expect the model to be weakest on donors with the thinnest history, the case the stakeholder cares about most."]),
      P([["Limitation we test rather than assume. ", { bold: true }], "DonorsChoose donors are marketplace donors; small-nonprofit donors are relational. We test which signal survives: behavioral features versus platform-specific ones."], { after: 30 }),

      H("5 · What we need from you"),
      B(["Confirmation that a well-supported negative finding against the RFM baseline is an acceptable result."]),
      B(["Guidance on ~13 GB on JupyterHub, or approval to use a stratified sample of donor cohorts."]),
      new Paragraph({ children: runs(["Any concern about anchoring the framing to a company a team member founded."]), numbering: { reference: "bul", level: 0 }, spacing: { after: 0, line: 238 } }),
    ],
  }],
});
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log("wrote", OUT, buf.length, "bytes"); });
