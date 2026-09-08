from __future__ import annotations

if __package__:
    from ._ui_presentation import localize_html as _ui_localize_html
else:
    from _ui_presentation import localize_html as _ui_localize_html


import html
import json
from pathlib import Path
from typing import Any

from .util import write_text


def generate_dashboard(plan: dict[str, Any], output: Path) -> Path:
    selected = plan.get("selected_route") or {}
    pareto = plan.get("pareto_routes", [])
    rows = []
    for route in pareto:
        c = route.get("cost", {})
        rows.append(
            "<tr>"
            f"<td>{html.escape(' → '.join(route.get('capability_ids', [])))}</td>"
            f"<td>{float(c.get('expected_energy_j', 0)):.2f}</td>"
            f"<td>{float(c.get('latency_ms', 0))/1000:.2f}</td>"
            f"<td>{float(c.get('money', 0)):.4f}</td>"
            f"<td>{float(route.get('quality', 0)):.3f}</td>"
            f"<td>{float(route.get('score', 0)):.4f}</td>"
            "</tr>"
        )
    raw = json.dumps(plan, ensure_ascii=False, indent=2).replace("</", "<\\/")
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>DIKWP MINEX Route Dashboard</title><style>
body{{font-family:Inter,system-ui,sans-serif;background:#09131f;color:#e8f0f7;margin:0}}main{{max-width:1180px;margin:auto;padding:28px}}
.card{{background:#112235;border:1px solid #28445e;border-radius:16px;padding:20px;margin:16px 0}}h1{{margin:0 0 8px}}.pill{{display:inline-block;padding:5px 10px;border-radius:99px;background:#173f4d;color:#aef0d8;margin-right:6px}}
table{{width:100%;border-collapse:collapse}}th,td{{padding:9px;border-bottom:1px solid #28445e;text-align:left}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#07101a;padding:16px;border-radius:12px}}.ok{{color:#7ee2a8}}
</style></head><body><main><h1>DIKWP MINEX Capability Fabric</h1><p>Intent first. Apps optional. Capabilities liquid. Proof before execution.</p>
<div class="card"><span class="pill">Pareto routes: {len(pareto)}</span><span class="pill">External authority: 0</span><h2>Selected route</h2><p class="ok">{html.escape(' → '.join(selected.get('capability_ids', [])) or 'No admissible route')}</p></div>
<div class="card"><h2>Pareto frontier</h2><table><thead><tr><th>Route</th><th>Expected energy (J)</th><th>Latency (s)</th><th>Money</th><th>Quality</th><th>Score</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<div class="card"><h2>Machine-readable plan</h2><pre>{html.escape(raw)}</pre></div>
</main></body></html>"""
    return _ui_localize_html(write_text(output, _ui_localize_html(doc)))
