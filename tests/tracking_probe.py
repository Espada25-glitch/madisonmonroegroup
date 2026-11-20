"""Non-invasive external tracking and HubSpot form probe, no test lead submitted."""
import asyncio, http.server, json, os, pathlib, socketserver, threading
from playwright.async_api import async_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
PORT=8766
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
async def main():
 os.chdir(ROOT)
 with socketserver.TCPServer(("127.0.0.1",PORT),Quiet) as server:
  threading.Thread(target=server.serve_forever,daemon=True).start()
  try:
   async with async_playwright() as pw:
    browser=await pw.chromium.launch(headless=True,args=["--no-sandbox"])
    page=await browser.new_page(viewport={"width":1440,"height":900})
    requests=[];responses=[];failures=[]
    keys=("googletagmanager.com","google-analytics.com","hs-scripts.com","hsforms.net","hubspot.com","hs-analytics.net","hubspotusercontent")
    page.on("request",lambda req: requests.append({"url":req.url,"method":req.method}) if any(k in req.url for k in keys) else None)
    page.on("response",lambda res: responses.append({"url":res.url,"status":res.status}) if any(k in res.url for k in keys) else None)
    page.on("requestfailed",lambda req: failures.append({"url":req.url,"error":req.failure}) if any(k in req.url for k in keys) else None)
    await page.goto(f"http://127.0.0.1:{PORT}/contact/",wait_until="domcontentloaded",timeout=30000)
    await page.wait_for_timeout(9000)
    observed=await page.evaluate("""() => ({
      gaInitialized: typeof window.gtag === 'function',
      gaDataLayer: Array.isArray(window.dataLayer),
      gaConfig: JSON.stringify(window.dataLayer || []).includes('G-J1WS6C2650'),
      hubspotQueue: Array.isArray(window._hsq),
      formContainer: !!document.querySelector('[data-form-id="3d92aefc-2eeb-4910-9014-61fb46ca2239"]'),
      formIframeCount: document.querySelectorAll('iframe[src*="hubspot"],iframe[src*="hsforms"]').length,
      hubspotFormFields: document.querySelectorAll('.hs-form-frame input,.hs-form-frame textarea').length
    })""")
    report={"page":"/contact/","observed":observed,"requests":requests,"responses":responses,"requestFailures":failures,"note":"This observes browser request and embedding behavior only. Google Analytics and HubSpot dashboard event attribution require live post-release confirmation. No test lead submitted."}
    out=ROOT/"test-artifacts";out.mkdir(exist_ok=True)
    (out/"tracking-probe.json").write_text(json.dumps(report,indent=2))
    print("Tracking probe:",json.dumps({"observed":observed,"requestCount":len(requests),"responseCount":len(responses),"failedRequests":len(failures),"responseHosts":sorted(set(r["url"].split("/")[2] for r in responses))}))
    for r in responses:
     print("TRACKING RESPONSE:",r["status"],r["url"][:130])
    for r in failures[:6]:print("TRACKING REQUEST FAILED:",r["url"][:140],r["error"])
    if not all([observed["gaInitialized"],observed["gaDataLayer"],observed["gaConfig"],observed["formContainer"]]):
     raise SystemExit("FAIL: first-party tracking initialization or HubSpot form embed container missing")
    await browser.close()
  finally:server.shutdown()
if __name__=="__main__":asyncio.run(main())
