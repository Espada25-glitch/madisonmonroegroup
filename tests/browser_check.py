"""Browser-level responsive smoke tests, screenshots, navigation and tracking requests."""
import asyncio, contextlib, http.server, json, os, pathlib, socketserver, threading
from playwright.async_api import async_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
ROUTES=["/","/expertise/","/approach/","/about/","/insights/","/contact/",
"/services/strategic-brand-positioning/","/services/business-growth-strategy/",
"/services/ai-discoverability-innovation/","/services/customer-insights-analytics/"]
PORT=8765
class QuietHandler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
async def main():
 os.chdir(ROOT)
 with socketserver.TCPServer(("127.0.0.1",PORT),QuietHandler) as server:
  thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:
   async with async_playwright() as pw:
    browser=await pw.chromium.launch(headless=True,args=["--no-sandbox"])
    failures=[];report=[];out=ROOT/"test-artifacts";out.mkdir(exist_ok=True)
    for width in [375,768,1440]:
     page=await browser.new_page(viewport={"width":width,"height":900},device_scale_factor=1)
     for route in ROUTES:
      errors=[];page.on("pageerror",lambda exc,errors=errors:errors.append(str(exc)))
      response=await page.goto(f"http://127.0.0.1:{PORT}{route}",wait_until="domcontentloaded",timeout=30000)
      await page.locator("h1").wait_for()
      await page.evaluate("document.fonts.ready")
      dims=await page.evaluate("""() => ({
        scroll: document.documentElement.scrollWidth,
        client: document.documentElement.clientWidth,
        h1: document.querySelectorAll('h1').length,
        main: document.querySelectorAll('main').length,
        font: getComputedStyle(document.querySelector('h1')).fontFamily,
        bodyFont: getComputedStyle(document.body).fontFamily,
        navLinks: document.querySelectorAll('nav a').length,
        hasGoogle: !!document.querySelector('script[src*="googletagmanager.com/gtag/js"]'),
        hasHubspot: !!document.querySelector('script[src*="hs-scripts.com/247902140.js"]'),
        hasHubspotForm: !!document.querySelector('[data-form-id="3d92aefc-2eeb-4910-9014-61fb46ca2239"]')
      })""")
      problems=[]
      if response.status!=200:problems.append("HTTP "+str(response.status))
      if dims["scroll"]>dims["client"]+1:problems.append(f"horizontal overflow {dims['scroll']} > {dims['client']}")
      if dims["h1"]!=1 or dims["main"]!=1:problems.append("missing/duplicate landmarks")
      if "Space Grotesk" not in dims["font"] or "DM Sans" not in dims["bodyFont"]:problems.append("incorrect fonts: "+str(dims["font"])+" | "+str(dims["bodyFont"]))
      if not dims["hasGoogle"] or not dims["hasHubspot"]:problems.append("missing analytics script")
      if route=="/contact/" and not dims["hasHubspotForm"]:problems.append("missing HubSpot form")
      if errors:problems.append("page JS errors: "+str(errors[:2]))
      report.append({"width":width,"route":route,"status":"PASS" if not problems else "FAIL","dimensions":dims,"issues":problems})
      failures.extend(f"{width}px {route}: {p}" for p in problems)
      if width in [375,1440] and route in ["/","/expertise/","/about/","/contact/"]:
       name=route.strip("/").replace("/","-") or "home"
       await page.screenshot(path=str(out/f"{name}-{width}.png"),full_page=True)
     if width==1440:
      await page.goto(f"http://127.0.0.1:{PORT}/",wait_until="domcontentloaded")
      await page.get_by_role("link",name="Expertise",exact=True).first.click()
      if not page.url.endswith("/expertise/"):failures.append("Navigation: home to expertise failed")
     await page.close()
    await browser.close()
    (out/"browser-report.json").write_text(json.dumps(report,indent=2))
    print("Browser tests:",len(report),"cases,",len(failures),"failures")
    for f in failures:print("FAIL:",f)
    if failures:raise SystemExit(1)
  finally:server.shutdown()
if __name__=="__main__":asyncio.run(main())
