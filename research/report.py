from fpdf import FPDF

# Data you provided (extracted and cleaned for clarity)
data = {
    "probe_group": "latentinjection",
    "probe_doc": "Latent injection: probes to test prompt injections buried in other contexts.",
    "probe_link": "https://reference.garak.ai/en/latest/garak.probes.latentinjection.html",
    "probe_name": "latentinjection.LatentInjectionReport",
    "probe_descr": "String-based latent prompt injections via a report",
    "probe_score": 1.0,
    "probe_severity": 5,
    "detector_name": "base.TriggerListDetector",
    "detector_descr": "Subclass of Detector using attempt's notes[triggers] as list of strings to match",
    "absolute_score": 1.0,
    "absolute_comment": "excellent",
    "zscore": 2.27,
    "zscore_comment": "excellent",
    "calibration_used": True,
    "recommendations": [
        "Review the model's prompt handling mechanisms to identify how latent injections are processed.",
        "Implement input sanitization strategies to minimize the effect of prompt injection vectors.",
        "Use robust detection filters before prompt execution in production environments.",
    ]
}

# PDF creation
class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, " Garak Model Vulnerability Report", 0, 1, "C")
        self.ln(5)

    def section_title(self, title):
        self.set_font("Arial", "B", 12)
        self.set_text_color(30, 30, 30)
        self.cell(0, 10, title, 0, 1)
        self.set_text_color(0, 0, 0)

    def section_body(self, body):
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 8, body)
        self.ln(3)

    def add_probe_section(self, data):
        self.section_title(" Probe Results")
        probe_info = f"""
Group: {data['probe_group']}
Description: {data['probe_doc']}
Link: {data['probe_link']}
Probe: {data['probe_name']}
Details: {data['probe_descr']}
Score: {data['probe_score']} / 1.0
Severity: {data['probe_severity']}
        """
        self.section_body(probe_info)

    def add_detector_section(self, data):
        self.section_title(" Interpretation")
        interpretation = f"""
Detector: {data['detector_name']}
Details: {data['detector_descr']}
Absolute Score: {data['absolute_score']} ({data['absolute_comment']})
Z-Score: {data['zscore']} ({data['zscore_comment']})
Calibration Used: {"Yes" if data['calibration_used'] else "No"}
        """
        self.section_body(interpretation)

    def add_recommendations(self, data):
        self.section_title(" Recommendations")
        recs = "\n".join([f"- {r}" for r in data["recommendations"]])
        self.section_body(recs)


# Create PDF
pdf = PDFReport()
pdf.add_page()
pdf.add_probe_section(data)
pdf.add_detector_section(data)
pdf.add_recommendations(data)

output_path = "garak_probe_report_1.pdf"
pdf.output(output_path)

output_path
