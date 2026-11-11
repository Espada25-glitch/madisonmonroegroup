"""Dependency-free regression checks for the published static site."""
import json, unittest
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
BASE='https://www.madisonmonroegroup.com/'
class Page(HTMLParser):
 def __init__(self,path):
  super().__init__();self.tags=[];self.schemas=[];self.capture=False;self.buffer='';self.feed(path.read_text())
 def handle_starttag(self,tag,attrs):
  a=dict(attrs);self.tags.append((tag,a))
  if tag=='script' and a.get('type')=='application/ld+json':self.capture=True;self.buffer=''
 def handle_data(self,data):
  if self.capture:self.buffer+=data
 def handle_endtag(self,tag):
  if tag=='script' and self.capture:self.schemas.append(json.loads(self.buffer));self.capture=False
class SiteTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.pages={p:Page(p) for p in ROOT.rglob('*.html') if '.git' not in p.parts}
 def test_metadata_and_landmarks(self):
  titles=[]
  for path,p in self.pages.items():
   with self.subTest(page=str(path.relative_to(ROOT))):
    self.assertEqual(sum(t=='h1' for t,a in p.tags),1)
    self.assertEqual(sum(t=='main' for t,a in p.tags),1)
    expected=BASE+str(path.relative_to(ROOT)).replace('index.html','')
    self.assertEqual([a['href'] for t,a in p.tags if t=='link' and a.get('rel')=='canonical'],[expected])
    for key in ['description','twitter:card','twitter:image']:
     self.assertTrue(any(a.get('name')==key and a.get('content') for t,a in p.tags))
    self.assertTrue(any(a.get('property')=='og:url' and a.get('content')==expected for t,a in p.tags))
    ids=[a['id'] for t,a in p.tags if 'id' in a];self.assertEqual(len(ids),len(set(ids)))
 def test_local_links_and_fragments(self):
  for path,p in self.pages.items():
   for tag,a in p.tags:
    for attr in ('href','src'):
     value=a.get(attr,'');u=urlsplit(value)
     if not value or u.scheme or u.netloc:continue
     dest=(ROOT/u.path.lstrip('/')) if u.path.startswith('/') else path.parent/u.path
     if not u.path:dest=path
     if dest.is_dir():dest=dest/'index.html'
     self.assertTrue(dest.exists(),f'{path}: {value}')
     if u.fragment and dest.suffix=='.html':
      self.assertIn(unquote(u.fragment),[x.get('id') for _,x in Page(dest).tags],f'{path}: {value}')
 def test_schema_and_service_coverage(self):
  for path,p in self.pages.items():
   self.assertTrue(p.schemas)
   for schema in p.schemas:
    self.assertNotIn('"Event"',json.dumps(schema))
    for node in schema.get('@graph',[]):
     if node.get('@type')=='Service':
      self.assertTrue(node['description']);self.assertEqual(node['provider']['@id'],BASE+'#organization')
  home=self.pages[ROOT/'index.html'];nodes=home.schemas[0]['@graph']
  self.assertEqual(sum(n['@type']=='Service' for n in nodes),6)
  self.assertEqual(len(list((ROOT/'services').glob('*/index.html'))),6)
 def test_sitemap_and_robots(self):
  urls={n.text for n in ET.parse(ROOT/'sitemap.xml').iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
  self.assertEqual(urls,{BASE+str(p.relative_to(ROOT)).replace('index.html','') for p in self.pages})
  self.assertIn('Sitemap: '+BASE+'sitemap.xml',(ROOT/'robots.txt').read_text())
 def test_first_party_size_budget(self):
  self.assertLess((ROOT/'style.css').stat().st_size,30000)
  for p in self.pages:self.assertLess(p.stat().st_size,40000)
if __name__=='__main__':unittest.main()
