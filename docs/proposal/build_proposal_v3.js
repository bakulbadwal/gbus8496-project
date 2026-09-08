// Proposal v3 FINAL — "Predicting the Second Gift" (Malorie's draft, blanks filled, facts tightened).
const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, AlignmentType, BorderStyle, LevelFormat } = require("docx");
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
const B = (spec) => new Paragraph({ children: runs(spec), numbering: { reference: "bul", level: 0 }, spacing: { after: 40, line: 240 } });
const H = (text) => new Paragraph({ children: [new TextRun({ text, font: FONT, size: HEAD, bold: true })], spacing: { before: 90, after: 40 } });

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: BODY } } } },
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 240 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 800, bottom: 800, left: 1080, right: 1080 } } },
    children: [
      new Paragraph({ children: [new TextRun({ text: "Project Proposal: Predicting the Second Gift", font: FONT, size: 32, bold: true })], spacing: { after: 40 }, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "222222", space: 2 } } }),
      P(["GBUS 8496 Machine Learning and AI for Business · Prof. Michael Albert · Group 11 · September 8, 2026"], { after: 20 }),
      P([["Team: ", { bold: true }], "Bakul Badwal · Malorie Black · Reid Jacobson · Thadeus Knospe · Rodolfo Perez-Cortes Manrique"], { after: 20 }),
      P([["Repository: ", { bold: true }], "github.com/bakulbadwal/gbus8496-project — this proposal, the two fallback directions we considered, the data recipe, and the working notebooks as they are built."], { after: 60 }),

      H("Problem and business application"),
      P(["Most nonprofits acquire a donor once and never hear from them again. The highest-leverage moment in the donor lifecycle is the second gift, and the organizations least equipped to work it are small ones. Our stakeholder is the development lead at a nonprofit with roughly a $500K annual budget and no dedicated data staff. Each month she can personally follow up with only a fraction of the people who gave for the first time, and today she builds that list by hand from recency and gift size."]),
      P(["The decision we support is specific: given a fixed outreach budget measured in staff hours, which first-time donors should receive follow-up, and where should the cutoff sit? Our output is a ranked, scored follow-up list with a recommended threshold and the expected dollars behind it. One of us founded GoGood Technologies, a volunteer and donor engagement platform serving exactly this customer, so we can validate the output against real practitioners."]),

      H("Dataset and source"),
      P([["DonorsChoose Open Data, United States, 2002–2019", { italics: true }], " (ICPSR 37898, https://doi.org/10.3886/ICPSR37898.v1). Public-use files; free, with a no-cost ICPSR account and no institutional membership required. We use two files: Donations (11,377,479 records) and Projects public-use data (2,149,817 records), covering projects posted September 2002 through June 2019 with activity through December 2019; record counts confirmed against the DOI registration. Donations carries DONOR_ID, so we can reconstruct each donor's giving history and build our own outcome label rather than inheriting someone else's. It also carries AMOUNT, CREATED_MONTH, DONOR_TYPE, PAYMENT_WAS_MATCHED, IS_TEACHER_REFERRED, and THANK_YOU_PACKET_MAILED. Two constraints we accept up front: dates are month-level, and there is no donor demographics file, so DONOR_TYPE is our only donor attribute."]),

      H("What we will build"),
      P(["A second-gift model plus a decision layer on top of it."], { after: 40 }),
      B([["Label. ", { bold: true }], "For each donor whose first recorded donation falls in the observation window, did they give again within 12 months? Only cohorts whose 12-month window closes before December 2019 are labeled."]),
      B([["Features. ", { bold: true }], "Donation-side (amount, month and seasonality, matched, campaign gift card, teacher-referred, donor type, thank-you packet mailed) and project-side (subject category, grade level, cost, school state)."]),
      B([["Split. ", { bold: true }], "Time-based, not random. Train on first-gift cohorts through 2016, hold out the 2017 and 2018 cohorts, and observe outcomes through December 2019. A random split would leak future information."]),
      B([["Decision layer. ", { bold: true }], "Convert predicted probability and predicted second-gift amount into expected value per contact, subtract an explicit cost per contact in staff time, and derive the threshold from those payoffs rather than tuning it."]),

      H("Evaluation"),
      P(["Our ground truth is observed donor behavior in the held-out cohorts, not hand labels. Four measurements:"], { after: 40 }),
      B([["Discrimination and calibration ", { bold: true }], "on the held-out cohorts. PR-AUC because the class is imbalanced, plus a calibration curve, since an uncalibrated score cannot support a threshold recommendation."]),
      B([["Against honest baselines. ", { bold: true }], "The baseline that matters is RFM, the recency-and-amount heuristic small nonprofits actually use, alongside random targeting and contact-everyone. The business metric is net value retained per hour of outreach at a fixed budget. If the model does not beat RFM, we report that as the finding."]),
      B([["Does stewardship predict retention? ", { bold: true }], "THANK_YOU_PACKET_MAILED records a real post-gift action. We estimate its association with a second gift while controlling for gift size, and state plainly that packets were not randomly assigned, so this is association and not a causal effect."]),
      B([["Error analysis by cohort. ", { bold: true }], "We expect the model to be weakest on donors with the thinnest history, which is precisely the case our stakeholder cares about most."]),
      P([["Limitation we will address head-on. ", { bold: true }], "DonorsChoose donors are marketplace donors who often fund classrooms they have no prior relationship with; small-nonprofit donors are relational. Rather than assume the model transfers, we test which signal survives: behavioral features (likely to transfer) versus platform-specific ones (likely not)."], { after: 40 }),

      H("What we need from you"),
      B(["Confirmation that a well-supported negative finding against the RFM baseline is an acceptable result."]),
      B(["Guidance on working with roughly 13 GB on JupyterHub, or approval to use a stratified sample of donor cohorts."]),
      B(["Any concern about anchoring the framing to a company a team member founded."]),
    ],
  }],
});
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log("wrote", OUT, buf.length, "bytes"); });
