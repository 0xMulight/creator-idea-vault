import unittest,tempfile
from pathlib import Path
from creator_idea_vault.__main__ import canon_url, connect, save_source, rows, export_md, import_csv

class VaultTest(unittest.TestCase):
 def test_clean_url(self):
  self.assertEqual(canon_url('https://EXAMPLE.com/post/?utm_source=x&v=1#abc'),'https://example.com/post?v=1')
  with self.assertRaises(ValueError):canon_url('javascript:alert(1)')
 def test_idempotent_and_export(self):
  with tempfile.TemporaryDirectory() as d:
   db=connect(Path(d)/'ideas.sqlite')
   with db:
    save_source(db,'X','https://example.com/a?utm_source=x','测试','实际摘录','笔记')
    save_source(db,'X','https://example.com/a','测试','实际摘录更新','更新笔记')
   self.assertEqual(len(rows(db)),1)
   self.assertIn('更新笔记',export_md(rows(db)))
   db.close()
 def test_needs_summary(self):
  with tempfile.TemporaryDirectory() as d:
   db=connect(Path(d)/'a.sqlite')
   with self.assertRaises(ValueError):save_source(db,'X','https://example.org','标题','','')
   db.close()

if __name__=='__main__':unittest.main()
