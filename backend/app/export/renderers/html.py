import logging
from pathlib import Path
from html import escape

from app.export.renderers.base import BaseRenderer
from app.export.renderers.common import iter_renderable_sections, build_section_blocks

logger = logging.getLogger("proposalcraft.export.html")


class HTMLRenderer(BaseRenderer):
    extension = ".html"

    def render(self, proposal: dict, output_path: str) -> str:
        meta = proposal.get("metadata", {})
        html = [
            "<!DOCTYPE html>",
            '<html lang="en"><head><meta charset="UTF-8">',
            f"<title>{escape(meta.get('proposal_title', 'Proposal'))}</title>",
            "<style>",
            "body{font-family:'Segoe UI',Arial,sans-serif;color:#333;line-height:1.6;max-width:900px;margin:0 auto;padding:20px}",
            ".cover-page{text-align:center;padding:80px 0 40px;page-break-after:always}",
            ".cover-page h1{font-size:32px;color:#1a56db;margin-bottom:10px}",
            ".cover-page h2{font-size:20px;color:#666;font-weight:400}",
            ".cover-page .meta{margin-top:60px;font-size:14px;color:#888}",
            ".section{margin-bottom:30px}",
            ".section h2{color:#1a56db;border-bottom:2px solid #1a56db;padding-bottom:8px;margin-bottom:16px;font-size:22px}",
            ".section h3{color:#444;margin:14px 0 8px;font-size:17px}",
            ".section p{margin-bottom:10px}",
            ".section ul{margin:8px 0 8px 20px}",
            ".section li{margin-bottom:4px}",
            "table{width:100%;border-collapse:collapse;margin:12px 0}",
            "th,td{border:1px solid #ddd;padding:8px 12px;text-align:left}",
            "th{background:#f5f7fa;font-weight:600}",
            ".footer{text-align:center;font-size:11px;color:#aaa;margin-top:40px;padding-top:20px;border-top:1px solid #eee}",
            "</style></head><body>",
            '<div class="cover-page">',
            f"<h1>{escape(meta.get('proposal_title', 'Proposal'))}</h1>",
            f"<h2>{escape(meta.get('subtitle', ''))}</h2>",
            '<div class="meta">',
            f"<p><strong>Prepared for:</strong> {escape(meta.get('prepared_for') or meta.get('client_name') or 'Client')}</p>",
            f"<p><strong>Prepared by:</strong> {escape(meta.get('prepared_by') or meta.get('company_name') or 'Company')}</p>",
            f"<p><strong>Date:</strong> {escape(meta.get('date', ''))}</p>",
            f"<p><strong>Version:</strong> {escape(meta.get('version', '1.0'))}</p>",
            f"<p><strong>Status:</strong> {escape(meta.get('status', 'Draft'))}</p>",
            "</div></div>",
        ]

        for key, title, data in iter_renderable_sections(proposal):
            html.append(f'<div class="section"><h2>{escape(title)}</h2>')
            for block in build_section_blocks(key, data):
                html.append(_block_to_html(block))
            html.append("</div>")

        html.append(
            f'<div class="footer"><p>{escape(meta.get("company_name", ""))} — Confidential</p></div></body></html>'
        )

        path = Path(output_path).with_suffix(".html")
        path.write_text("\n".join(html), encoding="utf-8")
        logger.info("HTML exported to %s", path)
        return str(path)


def _block_to_html(block: tuple) -> str:
    kind = block[0]
    if kind == "h3":
        return f"<h3>{escape(block[1])}</h3>"
    if kind == "p":
        return f"<p>{escape(block[1])}</p>"
    if kind == "bullets":
        return "<ul>" + "".join(f"<li>{escape(i)}</li>" for i in block[1]) + "</ul>"
    if kind == "table":
        headers, rows = block[1], block[2]
        out = ["<table><thead><tr>"]
        out += [f"<th>{escape(h)}</th>" for h in headers]
        out.append("</tr></thead><tbody>")
        for row in rows:
            out.append("<tr>" + "".join(f"<td>{escape(str(v))}</td>" for v in row) + "</tr>")
        out.append("</tbody></table>")
        return "".join(out)
    return ""
