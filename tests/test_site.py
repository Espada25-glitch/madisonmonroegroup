"""Static-site regression checks for Madison & Monroe Concept B."""
import json
import unittest
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
BASE="https://www.madisonmonroegroup.com/"
NEW=["index.html","expertise/index.html","approach/index.html","about/index.html","insights/index.html","contact/index.html"] + ["services/"+p+"/index.html" for p in ["strategic-brand-positioning","business-growth-strategy","ai-discoverability-innovation","customer-insights-analytics"]]
class Page(HTMLParser):
 def __init__(self,path):
  super().__init__();self.tags=[];self.schemas=[];self.capture=False;self.buffer="";self.feed(path.read_text())
 def handle_starttag(self,tag,attrs):
  a=dict(attrs);self.tags.append((tag,a))
  if tag=="script" and a.get("type")=="application/ld+json":self.capture=True;self.buffer=""
 def handle_data(self,data):
  if self.capture:self.buffer+=data
 def handle_endtag(self,tag):
  if tag=="script" and self.capture:self.schemas.append(json.loads(self.buffer));self.capture=False
class SiteTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.pages={p:Page(p) for p in ROOT.rglob("*.html")}
 def test_new_pages_have_metadata_and_semantics(self):
  for file in NEW:
   path=ROOT/file
   with self.subTest(file=file):
    self.assertTrue(path.exists())
    page=self.pages[path]
    self.assertEqual(sum(t=="main" for t,a in page.tags),1)
    self.assertEqual(sum(t=="h1" for t,a in page.tags),1)
    self.assertTrue(page.schemas)
    canonical=BASE+file.replace("index.html","")
    self.assertEqual([a.get("href") for t,a in page.tags if t=="link" and a.get("rel")=="canonical"],[canonical])
    self.assertTrue(any(a.get("name")=="description" for t,a in page.tags))
    self.assertTrue(any(a.get("property")=="og:image" for t,a in page.tags))
    src=path.read_text()
    self.assertIn("G-J1WS6C2650",src)
    self.assertIn("247902140",src)
 def test_hubspot_contact_form_preserved(self):
  html=(ROOT/"contact/index.html").read_text()
  self.assertIn("3d92aefc-2eeb-4910-9014-61fb46ca2239",html)
  self.assertIn("https://js-na2.hsforms.net/forms/embed/247902140.js",html)
 def test_new_service_schema(self):
  for file in NEW:
   if not file.startswith("services/"):continue
   nodes=self.pages[ROOT/file].schemas[0]["@graph"]
   self.assertTrue(any(n.get("@type")=="Service" for n in nodes))
   self.assertTrue(any(n.get("@type")=="BreadcrumbList" for n in nodes))
 def test_local_paths_exist(self):
  for path,page in self.pages.items():
   for tag,a in page.tags:
    for attr in ("href","src"):
     value=a.get(attr,"")
     if not value or value.startswith(("#","mailto:","tel:")):continue
     u=urlsplit(value)
     if u.scheme or u.netloc:continue
     dest=ROOT/u.path.lstrip("/") if u.path.startswith("/") else path.parent/u.path
     if dest.is_dir():dest=dest/"index.html"
     self.assertTrue(dest.exists(),f"{path}: {value}")
 def test_sitemap_covers_every_html_page(self):
  urls={n.text for n in ET.parse(ROOT/"sitemap.xml").iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")}
  self.assertEqual(urls,{BASE+str(p.relative_to(ROOT)).replace("index.html","") for p in self.pages})
  self.assertIn("Sitemap: "+BASE+"sitemap.xml",(ROOT/"robots.txt").read_text())
if __name__=="__main__":unittest.main()
