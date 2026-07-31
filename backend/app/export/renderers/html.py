import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from app.export.renderers.base import BaseRenderer

logger = logging.getLogger("proposalcraft.export.html")

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "templates" / "export"
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ proposal.metadata.proposal_title or "Proposal" }}</title>
<style>
  @page { margin: 20mm; size: A4; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', Arial, sans-serif; color: #333; line-height: 1.6; }
  .cover-page { text-align: center; padding: 80px 0 40px; page-break-after: always; }
  .cover-page h1 { font-size: 32px; color: #1a56db; margin-bottom: 10px; }
  .cover-page h2 { font-size: 20px; color: #666; font-weight: 400; }
  .cover-page .meta { margin-top: 60px; font-size: 14px; color: #888; }
  .toc { page-break-after: always; }
  .toc h2 { margin-bottom: 20px; }
  .toc ul { list-style: none; }
  .toc li { padding: 6px 0; border-bottom: 1px dotted #ddd; }
  .section { page-break-inside: avoid; margin-bottom: 30px; }
  .section h2 { color: #1a56db; border-bottom: 2px solid #1a56db; padding-bottom: 8px; margin-bottom: 16px; font-size: 22px; }
  .section h3 { color: #444; margin: 14px 0 8px; font-size: 17px; }
  .section p { margin-bottom: 10px; }
  .section ul { margin: 8px 0 8px 20px; }
  .section li { margin-bottom: 4px; }
  table { width: 100%; border-collapse: collapse; margin: 12px 0; }
  th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
  th { background: #f5f7fa; font-weight: 600; }
  .pricing-table .total { font-weight: 700; background: #eef2ff; }
  .footer { text-align: center; font-size: 11px; color: #aaa; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; }
  .page-break { page-break-before: always; }
</style>
</head>
<body>
<div class="cover-page">
  <h1>{{ proposal.metadata.proposal_title or "Proposal" }}</h1>
  <h2>{{ proposal.metadata.subtitle or "" }}</h2>
  <div class="meta">
    <p><strong>Prepared for:</strong> {{ proposal.metadata.prepared_for or proposal.metadata.client_name or "Client" }}</p>
    <p><strong>Prepared by:</strong> {{ proposal.metadata.prepared_by or proposal.metadata.company_name or "Company" }}</p>
    <p><strong>Date:</strong> {{ proposal.metadata.date or "" }}</p>
    <p><strong>Version:</strong> {{ proposal.metadata.version or "1.0" }}</p>
    <p><strong>Status:</strong> {{ proposal.metadata.status or "Draft" }}</p>
  </div>
</div>

{% if proposal.executive_summary %}
<div class="section page-break">
  <h2>Executive Summary</h2>
  {% if proposal.executive_summary.business_overview %}<p><strong>Overview:</strong> {{ proposal.executive_summary.business_overview }}</p>{% endif %}
  {% if proposal.executive_summary.problem_statement %}<p><strong>Problem:</strong> {{ proposal.executive_summary.problem_statement }}</p>{% endif %}
  {% if proposal.executive_summary.proposed_solution %}<p><strong>Solution:</strong> {{ proposal.executive_summary.proposed_solution }}</p>{% endif %}
  {% if proposal.executive_summary.expected_roi %}<p><strong>Expected ROI:</strong> {{ proposal.executive_summary.expected_roi }}</p>{% endif %}
  {% if proposal.executive_summary.business_value %}<p><strong>Business Value:</strong> {{ proposal.executive_summary.business_value }}</p>{% endif %}
  {% if proposal.executive_summary.key_benefits %}<h3>Key Benefits</h3><ul>{% for b in proposal.executive_summary.key_benefits %}<li>{{ b }}</li>{% endfor %}</ul>{% endif %}
</div>
{% endif %}

{% if proposal.proposed_solution %}
<div class="section">
  <h2>Proposed Solution</h2>
  {% if proposal.proposed_solution.overview %}<p>{{ proposal.proposed_solution.overview }}</p>{% endif %}
  {% if proposal.proposed_solution.architecture %}<h3>Architecture</h3><p>{{ proposal.proposed_solution.architecture }}</p>{% endif %}
  {% if proposal.proposed_solution.workflow %}<h3>Workflow</h3><p>{{ proposal.proposed_solution.workflow }}</p>{% endif %}
  {% if proposal.proposed_solution.security %}<h3>Security</h3><p>{{ proposal.proposed_solution.security }}</p>{% endif %}
</div>
{% endif %}

{% if proposal.module_breakdown %}
<div class="section">
  <h2>Modules</h2>
  <ul>{% for m in proposal.module_breakdown %}<li><strong>{{ m.name or m }}</strong>{% if m.description %}: {{ m.description }}{% endif %}</li>{% endfor %}</ul>
</div>
{% endif %}

{% if proposal.technology_stack %}
<div class="section">
  <h2>Technology Stack</h2>
  <table>
    <tr><th>Layer</th><th>Technologies</th></tr>
    {% for layer, techs in proposal.technology_stack.items() if techs %}
    <tr><td>{{ layer|title }}</td><td>{{ techs|join(", ") }}</td></tr>
    {% endfor %}
  </table>
</div>
{% endif %}

{% if proposal.timeline %}
<div class="section">
  <h2>Timeline</h2>
  {% if proposal.timeline.gantt_chart %}<pre>{{ proposal.timeline.gantt_chart }}</pre>{% endif %}
  {% if proposal.timeline.milestones %}<h3>Milestones</h3><ul>{% for m in proposal.timeline.milestones %}<li>{{ m }}</li>{% endfor %}</ul>{% endif %}
</div>
{% endif %}

{% if proposal.pricing %}
<div class="section pricing-table">
  <h2>Investment</h2>
  <table>
    <tr><th>Item</th><th>Amount</th></tr>
    {% if proposal.pricing.development_cost %}<tr><td>Development</td><td>{{ proposal.pricing.development_cost }}</td></tr>{% endif %}
    {% if proposal.pricing.cloud_cost %}<tr><td>Cloud Infrastructure</td><td>{{ proposal.pricing.cloud_cost }}</td></tr>{% endif %}
    {% if proposal.pricing.support_cost %}<tr><td>Support</td><td>{{ proposal.pricing.support_cost }}</td></tr>{% endif %}
    {% if proposal.pricing.amc %}<tr><td>Annual Maintenance</td><td>{{ proposal.pricing.amc }}</td></tr>{% endif %}
    <tr class="total"><td><strong>Total</strong></td><td><strong>{{ proposal.pricing.development_cost or "—" }}</strong></td></tr>
  </table>
  {% if proposal.pricing.payment_terms %}<p><strong>Payment Terms:</strong> {{ proposal.pricing.payment_terms }}</p>{% endif %}
</div>
{% endif %}

{% if proposal.support %}
<div class="section">
  <h2>Support</h2>
  <table>
    <tr><th>Plan</th><th>Details</th></tr>
    {% for plan, details in proposal.support.items() if details %}
    <tr><td>{{ plan|title }}</td><td>{{ details }}</td></tr>
    {% endfor %}
  </table>
</div>
{% endif %}

{% if proposal.sla %}
<div class="section">
  <h2>SLA</h2>
  <table>
    <tr><th>Severity</th><th>Response Time</th></tr>
    {% for severity, time in proposal.sla.items() if time %}
    <tr><td>{{ severity|title }}</td><td>{{ time }}</td></tr>
    {% endfor %}
  </table>
</div>
{% endif %}

{% if proposal.team %}
<div class="section">
  <h2>Team</h2>
  <ul>{% for member in proposal.team %}<li><strong>{{ member.name or member.role or member }}</strong>{% if member.experience %} — {{ member.experience }}{% endif %}</li>{% endfor %}</ul>
</div>
{% endif %}

{% if proposal.conclusion %}
<div class="section">
  <h2>Conclusion</h2>
  <p>{{ proposal.conclusion.summary or "" }}</p>
</div>
{% endif %}

<div class="footer">
  <p>{{ proposal.metadata.company_name or "" }} — Confidential</p>
</div>
</body>
</html>"""


class HTMLRenderer(BaseRenderer):
    extension = ".html"

    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))

    def render(self, proposal: dict, output_path: str) -> str:
        template = self.env.from_string(HTML_TEMPLATE)
        html = template.render(proposal=proposal)
        path = Path(output_path).with_suffix(".html")
        path.write_text(html, encoding="utf-8")
        logger.info("HTML exported to %s", path)
        return str(path)
