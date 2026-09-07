from __future__ import annotations

import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "DIKWP_MINEX_CAPABILITY_FABRIC_OS_v1.0.0.html"
OUT = ROOT / "validation"


async def main() -> None:
    console_errors: list[str] = []
    page_errors: list[str] = []
    network: list[str] = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        page = await browser.new_page(viewport={"width": 1280, "height": 1180}, device_scale_factor=1)
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))
        page.on("request", lambda req: network.append(req.url) if not req.url.startswith(("data:", "blob:")) else None)
        await page.set_content(HTML.read_text(encoding="utf-8"), wait_until="load")
        await page.click("#planBtn")
        await page.wait_for_selector("#view-routes.active")
        selected = (await page.locator("#selectedRoute").inner_text()).strip()
        why = (await page.locator("#whyPanel").inner_text()).strip()
        receipt = await page.locator("#receiptCode").inner_text()
        route_id_1 = json.loads(receipt)["selected_route"]["route_id"]
        await page.click("#planBtn")
        route_id_2 = json.loads(await page.locator("#receiptCode").inner_text())["selected_route"]["route_id"]
        await page.screenshot(path=str(OUT / "DIKWP_MINEX_BROWSER_SCREENSHOT_v1.0.0.png"), full_page=True)
        before = await page.locator("#langBtn").inner_text()
        await page.click("#langBtn")
        after = await page.locator("#langBtn").inner_text()
        await browser.close()
    result = {
        "selected_route_text": selected,
        "why_panel": why,
        "receipt_present": "MINEX_PLAN_RECEIPT" in receipt,
        "deterministic_route_id": route_id_1 == route_id_2,
        "route_id_second": route_id_2,
        "route_id": route_id_1,
        "language_toggle_before": before,
        "language_toggle_after": after,
        "unexpected_network_requests": [u for u in network if u not in {"about:blank"}],
        "console_errors": console_errors,
        "page_errors": page_errors,
        "screenshot": str(OUT / "DIKWP_MINEX_BROWSER_SCREENSHOT_v1.0.0.png"),
    }
    (OUT / "browser-smoke.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if not result["receipt_present"] or not result["deterministic_route_id"] or result["unexpected_network_requests"] or console_errors or page_errors:
        raise SystemExit(json.dumps(result, indent=2, ensure_ascii=False))
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
