import math
import re
from app.engines.base_engine import BaseEngine

COLORS = {
    "primary": "#1a56db",
    "secondary": "#2d6eb0",
    "accent": "#059669",
    "warning": "#d97706",
    "light_bg": "#ebf4ff",
    "border": "#93c5fd",
    "text": "#1e293b",
    "muted": "#64748b",
    "white": "#ffffff",
}

TIMELINE_COLORS = ["#1a56db", "#2d6eb0", "#059669", "#d97706", "#7c3aed", "#dc2626", "#0891b2", "#ca8a04"]

ARCH_LAYER_MAP = [
    ("frontend", "Frontend Layer"),
    ("backend", "Backend Layer"),
    ("database", "Data Layer"),
    ("ai_ml", "AI & ML Layer"),
    ("cloud", "Cloud & Infrastructure"),
    ("devops", "DevOps & Monitoring"),
]


class DiagramEngine(BaseEngine):
    name = "diagram"

    def run(self, context: dict) -> dict:
        modules = (context.get("module_data") or {}).get("modules", [])
        phases = (context.get("timeline_data") or {}).get("phases", [])
        tech_stack = context.get("tech_stack_data", {})

        workflow_svg = self._generate_workflow_svg(modules, context)
        timeline_svg = self._generate_timeline_svg(phases, context)
        architecture_svg = self._generate_architecture_svg(tech_stack, context)

        return {
            "workflow_svg": workflow_svg,
            "timeline_svg": timeline_svg,
            "architecture_svg": architecture_svg,
            "mermaid_workflow": self._generate_mermaid_workflow(modules, context),
            "mermaid_timeline": self._generate_mermaid_timeline(phases, context),
        }

    def _sanitize_id(self, name: str) -> str:
        return re.sub(r"[^a-zA-Z0-9]", "_", name)[:20]

    def _wrap_text(self, text: str, max_chars: int, max_lines: int = 3) -> list[str]:
        text = text.strip()
        if len(text) <= max_chars:
            return [text]
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            if not current:
                current = word
            elif len(current) + 1 + len(word) <= max_chars:
                current += " " + word
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            lines[-1] = lines[-1][: max(max_chars - 3, 1)] + "..."
        return lines

    def _svg_header(self, svg_w: int, svg_h: int) -> list[str]:
        return [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" style="width:100%;height:auto;">',
        ]

    def _generate_workflow_svg(self, modules: list, context: dict) -> str:
        if not modules:
            modules = [
                {"name": "User Portal", "description": "Client-facing interface"},
                {"name": "Core Engine", "description": "Business logic & processing"},
                {"name": "Analytics", "description": "Reporting & insights"},
                {"name": "Integration", "description": "Third-party connectors"},
            ]

        n = len(modules)
        box_w = 160
        font_size = 12
        gap = 30
        pad = 40
        max_chars = int((box_w - 24) / (0.6 * font_size))
        labels = [
            self._wrap_text(mod.get("name", f"Module {i+1}"), max_chars)
            for i, mod in enumerate(modules)
        ]
        lines_per_box = max(len(l) for l in labels)
        box_h = max(50, lines_per_box * 16 + 14)
        svg_w = max(n * (box_w + gap) - gap + pad * 2, 600)
        svg_h = 100 + box_h + 40

        lines = [
            *self._svg_header(svg_w, svg_h),
            "<defs>",
            f'  <linearGradient id="boxGrad" x1="0%" y1="0%" x2="0%" y2="100%">',
            f'    <stop offset="0%" stop-color="{COLORS["primary"]}"/>',
            f'    <stop offset="100%" stop-color="{COLORS["secondary"]}"/>',
            "  </linearGradient>",
            f'  <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8" orient="auto">',
            f'    <path d="M0,0 L10,5 L0,10 Z" fill="{COLORS["primary"]}"/>',
            "  </marker>",
            "</defs>",
            f'<rect x="0" y="0" width="{svg_w}" height="{svg_h}" fill="{COLORS["white"]}" rx="8"/>',
            f'<text x="{svg_w/2}" y="30" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="{COLORS["text"]}" text-anchor="middle">Solution Workflow</text>',
        ]

        total_w = n * (box_w + gap) - gap
        start_x = (svg_w - total_w) / 2
        y = 100

        for i, mod in enumerate(modules):
            x = start_x + i * (box_w + gap)

            lines.append(f'  <rect x="{x}" y="{y}" width="{box_w}" height="{box_h}" rx="8" fill="url(#boxGrad)" stroke="{COLORS["border"]}" stroke-width="1"/>')
            text_lines = labels[i]
            first_baseline = y + box_h / 2 - (len(text_lines) - 1) * 8 + 4
            for li, tline in enumerate(text_lines):
                ty = first_baseline + li * 16
                lines.append(f'  <text x="{x+box_w/2}" y="{ty}" font-family="Arial, sans-serif" font-size="{font_size}" font-weight="bold" fill="{COLORS["white"]}" text-anchor="middle">{self._escape_xml(tline)}</text>')

            if i < n - 1:
                ax = x + box_w
                ay = y + box_h / 2
                bx = x + box_w + gap
                lines.append(f'  <line x1="{ax}" y1="{ay}" x2="{bx}" y2="{ay}" stroke="{COLORS["primary"]}" stroke-width="2" marker-end="url(#arrow)"/>')

        lines.append("</svg>")
        return "\n".join(lines)

    def _generate_timeline_svg(self, phases: list, context: dict) -> str:
        if not phases:
            phases = [
                {"name": "Discovery", "duration_weeks": 2},
                {"name": "Design", "duration_weeks": 3},
                {"name": "Development", "duration_weeks": 6},
                {"name": "Testing", "duration_weeks": 3},
                {"name": "Launch", "duration_weeks": 2},
            ]

        n = len(phases)
        bar_h = 36
        gap = 12
        pad_h = 60
        pad_v = 80
        label_w = 130
        font_size = 10

        label_max_chars = int((label_w + pad_h / 2 - 12) / (0.6 * font_size))
        labels = [
            self._wrap_text(phase.get("name", f"Phase {i+1}"), label_max_chars, max_lines=2)
            for i, phase in enumerate(phases)
        ]
        two_line_rows = sum(1 for l in labels if len(l) > 1)
        row_h = bar_h + gap + (10 if two_line_rows else 0)
        svg_h = max(n * (bar_h + gap) + pad_v + (10 if two_line_rows else 0), 200)

        total_weeks = sum(p.get("duration_weeks", 2) for p in phases)
        scale = max((800 - label_w - pad_h) / max(total_weeks, 1), 20)
        svg_w = max(label_w + total_weeks * scale + pad_h, 700)

        lines = [
            *self._svg_header(svg_w, svg_h),
            f'<rect x="0" y="0" width="{svg_w}" height="{svg_h}" fill="{COLORS["white"]}" rx="8"/>',
            f'<text x="{svg_w/2}" y="30" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="{COLORS["text"]}" text-anchor="middle">Project Timeline</text>',
        ]

        week_labels_interval = max(1, int(total_weeks / 8))
        for w in range(0, total_weeks + 1, week_labels_interval):
            lx = label_w + pad_h / 2 + w * scale
            lines.append(f'  <text x="{lx}" y="52" font-family="Arial, sans-serif" font-size="9" fill="{COLORS["muted"]}" text-anchor="middle">W{w}</text>')

        current_week = 0
        for i, phase in enumerate(phases):
            y = 65 + i * row_h
            name_lines = labels[i]
            weeks = phase.get("duration_weeks", 2)
            bar_w = weeks * scale
            bx = label_w + pad_h / 2 + current_week * scale
            color = TIMELINE_COLORS[i % len(TIMELINE_COLORS)]

            if len(name_lines) == 1:
                lines.append(f'  <text x="{label_w + pad_h / 2 - 8}" y="{y + bar_h / 2 + 4}" font-family="Arial, sans-serif" font-size="{font_size}" fill="{COLORS["text"]}" text-anchor="end">{self._escape_xml(name_lines[0])}</text>')
            else:
                lines.append(f'  <text x="{label_w + pad_h / 2 - 8}" y="{y + bar_h / 2}" font-family="Arial, sans-serif" font-size="{font_size}" fill="{COLORS["text"]}" text-anchor="end">{self._escape_xml(name_lines[0])}</text>')
                lines.append(f'  <text x="{label_w + pad_h / 2 - 8}" y="{y + bar_h / 2 + 12}" font-family="Arial, sans-serif" font-size="{font_size}" fill="{COLORS["text"]}" text-anchor="end">{self._escape_xml(name_lines[1])}</text>')

            lines.append(f'  <rect x="{bx}" y="{y}" width="{max(bar_w, 4)}" height="{bar_h}" rx="6" fill="{color}" opacity="0.85"/>')
            if bar_w > 40:
                lines.append(f'  <text x="{bx + bar_w / 2}" y="{y + bar_h / 2 + 4}" font-family="Arial, sans-serif" font-size="{font_size}" font-weight="bold" fill="{COLORS["white"]}" text-anchor="middle">{weeks}w</text>')

            current_week += weeks

        lines.append("</svg>")
        return "\n".join(lines)

    def _generate_architecture_svg(self, tech_stack: dict, context: dict) -> str:
        palette = [
            COLORS["primary"], COLORS["secondary"], COLORS["accent"],
            COLORS["warning"], "#7c3aed", "#0891b2", "#dc2626",
        ]

        stack = tech_stack.get("technology_stack", {}) if isinstance(tech_stack, dict) else {}
        layers: list[tuple] = []
        if isinstance(stack, dict) and stack:
            for idx, (key, label) in enumerate(ARCH_LAYER_MAP):
                items = stack.get(key) or []
                names = []
                for it in items:
                    names.append(it.get("name", str(it)) if isinstance(it, dict) else str(it))
                if names:
                    layers.append((label, names, palette[idx % len(palette)]))
        else:
            layers = [
                ("Client Layer", ["Web App", "Mobile App"], palette[0]),
                ("API Layer", ["Load Balancer", "API Gateway"], palette[1]),
                ("Service Layer", ["Auth", "Proposal", "AI", "Export"], palette[2]),
                ("Data Layer", ["MongoDB", "Redis", "Qdrant", "S3"], palette[3]),
            ]

        box_w = 500
        pad = 40
        svg_w = box_w + pad * 2

        blocks = []
        y = 45
        font_size = 9
        for label, items, color in layers:
            sub_w = min((box_w - 20) / max(len(items), 1) - 6, 130)
            sub_w = max(sub_w, 60)
            max_chars = int((sub_w - 10) / (0.6 * font_size))
            wrapped = [self._wrap_text(it, max_chars, max_lines=2) for it in items]
            max_lines = max(len(w) for w in wrapped)
            sub_h = 20 + max_lines * 11
            container_h = 26 + sub_h + 6
            blocks.append((label, items, wrapped, color, sub_w, sub_h, y))
            y += container_h + 12
        svg_h = y + 20

        lines = [
            *self._svg_header(svg_w, svg_h),
            f'<rect x="0" y="0" width="{svg_w}" height="{svg_h}" fill="{COLORS["white"]}" rx="8"/>',
            f'<text x="{svg_w/2}" y="25" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="{COLORS["text"]}" text-anchor="middle">System Architecture</text>',
        ]

        for i, (layer_name, items, wrapped, color, sub_w, sub_h, y) in enumerate(blocks):
            label_y = y + 16
            sub_y = y + 26

            lines.append(f'  <rect x="{pad}" y="{y}" width="{box_w}" height="{sub_h + 32}" rx="6" fill="{color}" opacity="0.08" stroke="{color}" stroke-width="1" stroke-dasharray="4,2"/>')
            lines.append(f'  <text x="{pad + 10}" y="{label_y}" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="{color}">{self._escape_xml(layer_name)}</text>')

            total_items_w = len(items) * sub_w + (len(items) - 1) * 6
            sub_start_x = pad + (box_w - total_items_w) / 2
            for j, item in enumerate(items):
                sx = sub_start_x + j * (sub_w + 6)
                lines.append(f'  <rect x="{sx}" y="{sub_y}" width="{sub_w}" height="{sub_h}" rx="4" fill="{color}" opacity="0.9"/>')
                text_lines = wrapped[j]
                if len(text_lines) == 1:
                    lines.append(f'  <text x="{sx + sub_w / 2}" y="{sub_y + sub_h / 2 + 4}" font-family="Arial, sans-serif" font-size="{font_size}" font-weight="bold" fill="{COLORS["white"]}" text-anchor="middle">{self._escape_xml(text_lines[0])}</text>')
                else:
                    lines.append(f'  <text x="{sx + sub_w / 2}" y="{sub_y + sub_h / 2 - 2}" font-family="Arial, sans-serif" font-size="{font_size}" font-weight="bold" fill="{COLORS["white"]}" text-anchor="middle">{self._escape_xml(text_lines[0])}</text>')
                    lines.append(f'  <text x="{sx + sub_w / 2}" y="{sub_y + sub_h / 2 + 9}" font-family="Arial, sans-serif" font-size="{font_size}" font-weight="bold" fill="{COLORS["white"]}" text-anchor="middle">{self._escape_xml(text_lines[1])}</text>')

        lines.append("</svg>")
        return "\n".join(lines)

    def _generate_mermaid_workflow(self, modules: list, context: dict) -> str:
        if not modules:
            modules = [{"name": "Core Platform"}, {"name": "User Management"}, {"name": "Reporting"}]
        lines = ["flowchart LR"]
        prev = None
        for i, m in enumerate(modules[:10]):
            safe = self._sanitize_id(m["name"])
            lines.append(f"    {safe}[{m['name']}]")
            if prev:
                lines.append(f"    {prev} --> {safe}")
            prev = safe
        return "\n".join(lines)

    def _generate_mermaid_timeline(self, phases: list, context: dict) -> str:
        if not phases:
            return "gantt\n    title Project Timeline\n    dateFormat  YYYY-MM-DD\n    axisFormat  %b %d\n    section Phase 1\n    Discovery :p1, 2026-01-01, 2w"
        lines = ["gantt", "    title Project Timeline", "    dateFormat  YYYY-MM-DD", "    axisFormat  %b %d"]
        cumulative = 0
        for phase in phases:
            weeks = phase.get("duration_weeks", 2)
            lines.append(f"    section Phase {phase.get('phase', cumulative + 1)}")
            dep = f"after p{cumulative}, " if cumulative > 0 else ""
            if cumulative == 0:
                lines.append(f"    {phase.get('name', 'Phase')} :p{cumulative + 1}, {weeks}w")
            else:
                lines.append(f"    {phase.get('name', 'Phase')} :p{cumulative + 1}, after p{cumulative}, {weeks}w")
            cumulative += 1
        return "\n".join(lines)

    def _escape_xml(self, text: str) -> str:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
