"""Optional two-page PDF export. Requires reportlab; not needed for the tests."""
import json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/pdf/epi2me-component-case-study.pdf"
run = json.loads((ROOT / "evidence/component-20260911-01/run.json").read_text())
benchmark = json.loads((ROOT / "evidence/validator-20260911-01/report.json").read_text())
assert sum(r["status"] == "PASS" for r in run["results"]) == 8
assert sum(r["status"] == "OBSERVATION" for r in run["results"]) == 4
assert benchmark["metrics"]["counts"] == dict(tp=12, tn=8, fp=0, fn=0, unclassified_positive=0, unclassified_negative=0)

navy, teal, grey = colors.HexColor("#17334B"), colors.HexColor("#136E73"), colors.HexColor("#51616D")
styles = {
    "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=24, leading=28, textColor=navy, spaceAfter=12),
    "sub": ParagraphStyle("sub", fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=navy, spaceBefore=13, spaceAfter=6),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=10, leading=14, textColor=navy, spaceAfter=7),
    "small": ParagraphStyle("small", fontName="Helvetica", fontSize=8.5, leading=11.5, textColor=grey, spaceAfter=6),
    "label": ParagraphStyle("label", fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=teal, spaceAfter=8),
    "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=9, leading=12, textColor=navy),
}


def p(text, style="body"):
    return Paragraph(text, styles[style])


def table(rows, widths):
    cells = [[p(escape(str(c)), "cell") for c in row] for row in rows]
    result = Table(cells, colWidths=widths, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2EFF0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F7F9")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, teal),
    ]))
    return result


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#CDD7DC"))
    canvas.line(48, 41, A4[0] - 48, 41)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(grey)
    canvas.drawString(48, 28, "Run: 11 September 2026  |  Report revised: 12 September 2026")
    canvas.drawRightString(A4[0] - 48, 28, f"{doc.page} / 2")
    canvas.restoreState()


story = [p("BIOINFORMATICS SOFTWARE VERIFICATION / TECHNICAL REPORT", "label"),
         p("EPI2ME AAV QC<br/>Component verification", "title"),
         p("Executed evidence, explicit assumptions and a reproducible metadata investigation.", "body"),
         table([["Contract checks", "Exploratory probes", "Harness unit tests"],
                ["8 / 8 passed", "4 recorded", "28 passed"]], [166, 166, 167]),
         p("Purpose and scope", "sub"),
         p("AAV preparation QC summarises reads associated with transgene, host and plasmid references. This experiment checks whether selected counts, denominators and sample labels are handled correctly by Oxford Nanopore's actual contamination-summary component."),
         p("Small synthetic alignment tables were supplied directly to the upstream CLI. NumPy, pandas and native SeqKit executed normally. The source was preserved unchanged. No full Nextflow run, sequencing, alignment or variant calling was performed."),
         p("Method", "sub"),
         p("Expected results were declared before execution. Eight checks covered a known mixture, repeated alignments, row order, all-mapped and transgene-only inputs, sample identity, a missing column and a missing FASTA. Each case retains inputs, expectations, commands, exit status, diagnostics and any output."),
         p("Manual calculation: reads and alignments", "sub"),
         table([["Measure", "C01: baseline", "C02: extra alignment"],
                ["Total input reads", "100", "100"],
                ["Alignment rows", "95", "96"],
                ["Unique mapped reads", "95", "95"],
                ["Mapped / unmapped", "95% / 5%", "95% / 5%"],
                ["Transgene alignments", "80", "81"],
                ["Transgene / all alignment rows", "80/95 = 84.21%", "81/96 = 84.38%"]], [213, 120, 166]),
         Spacer(1, 8),
         p("The duplicate alignment changes the alignment denominator, not the count of mapped reads. Reference-category percentages cannot be interpreted as percentages of all input reads. Rounding can make category percentages sum to 100.01%.", "small"),
         p("Recorded environment", "sub"),
         p("Windows; Python 3.12.14; NumPy 2.2.6; pandas 2.2.3; SeqKit 2.13.0. Target: wf-aav-qc v1.3.1, commit 43a4266fc30a131c9e2b49654a97a3fd59e41d94. Dependencies describe this experiment, not the full upstream container.", "small"),
         PageBreak(),
         p("INVESTIGATION / LIMITATIONS / EVIDENCE", "label"),
         p("When a successful exit<br/>is not enough", "title"),
         p("OBS-002: inconsistent total-read metadata", "sub"),
         p("Probe X03 supplied 95 distinct mapped reads but declared only 94 total input reads. The unmodified component exited with code 0 and produced:"),
         table([["Output", "Observed value"], ["Mapped", "95 reads / 101.06382978723404%"],
                ["Unmapped", "-1 read / -1.0638297872340425%"]], [145, 354]),
         Spacer(1, 9),
         p("The component subtracts the distinct mapped count from the supplied total without a local consistency guard. Proposed controls are to reject inconsistent metadata with a clear diagnostic and independently check nonnegative counts and read percentages between 0 and 100."),
         p("This is confirmed component behaviour under deliberately inconsistent input. Full-workflow reachability is unproven: upstream processing may prevent the condition. The controls are proposed, not implemented. No upstream issue or patch has been submitted."),
         p("Other boundary observations", "sub"),
         p("X01/X02 raised ZeroDivisionError for an empty alignment table or zero total-read count. X04 included an unlisted reference in the alignment denominator without a matching named category. Each needs contract and workflow-reachability review before defect classification."),
         p("Separate FASTQ validator benchmark", "sub"),
         table([["True positive", "False negative", "True negative", "False positive"],
                ["12", "0", "8", "0"]], [125, 125, 125, 124]),
         Spacer(1, 8),
         p("Positive means one malformed FASTQ file under the project's four-line A/C/G/T/N, Phred+33 dialect. Twenty authored challenge files yielded sensitivity 12/12, specificity 8/8 and coverage 20/20. These examples are related to the unit-test design; they are not external validation or EPI2ME/clinical accuracy."),
         p("Traceability and remaining work", "sub"),
         p("Requirements link to the Nextflow process, Python component, cases and saved results. Technical risk notes record failure consequences, proposed controls and review status. samtools/bcftools exercises remain BLOCKED locally; a container-free Eddie installer is prepared. Full workflow execution and independent review remain pending. Later CI runs have separate evidence; the first Linux run failed file-tool checks."),
         p("Evidence and attribution", "sub"),
         p("Repository: evidence/component-20260911-01; evidence/validator-20260911-01; docs/component-test-plan.md; docs/observation-002.md; docs/component-risk-review.md. Upstream code is Oxford Nanopore's work, supplied unchanged with its licence. Clinical validation and medical-device compliance are outside the demonstrated scope. Development assistance is documented in NOTICE.md.", "small"),
         p('<link href="https://github.com/epi2me-labs/wf-aav-qc/tree/43a4266fc30a131c9e2b49654a97a3fd59e41d94" color="#136E73">Source: Oxford Nanopore wf-aav-qc, pinned revision</link>', "small")]
OUT.parent.mkdir(parents=True, exist_ok=True)
doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=48, rightMargin=48,
                        topMargin=43, bottomMargin=55, title="EPI2ME AAV QC component verification",
                        author="EPI2ME AAV QC verification project")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
