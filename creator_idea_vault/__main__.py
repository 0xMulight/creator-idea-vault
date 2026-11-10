"""Local, offline SQLite idea vault. User-owned notes only; never scrapes X/TikTok."""
import argparse
import csv
import sqlite3
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode
from datetime import datetime,timezone
import re
import hashlib

TRACKING={'utm_source','utm_medium','utm_campaign','utm_content','utm_term','fbclid','gclid','igshid'}
MAX_CSV=5*1024*1024

def canon_url(url):
    u=url.strip()
    if not u:return ''
    parts=urlsplit(u)
    if parts.scheme.lower() not in ('http','https') or not parts.netloc:raise ValueError('网址必须是 http(s) 的完整链接')
    query=urlencode([(k,v) for k,v in parse_qsl(parts.query,keep_blank_values=True) if k.lower() not in TRACKING])
    return urlunsplit((parts.scheme.lower(),parts.netloc.lower(),parts.path.rstrip('/') or '/',query,''))

def make_id(url,title,content):
    key=url or (title+'\n'+content)
    return hashlib.sha256(key.encode('utf-8')).hexdigest()[:16]

def connect(path):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(p)
    db.execute("""CREATE TABLE IF NOT EXISTS sources (id TEXT PRIMARY KEY,platform TEXT NOT NULL, url TEXT NOT NULL, title TEXT NOT NULL, content TEXT NOT NULL, notes TEXT NOT NULL, added_at TEXT NOT NULL)""")
    return db

def save_source(db,platform,url,title,content,notes='',added_at=''):
    u=canon_url(url) if url else ''
    title=title.strip();content=content.strip();notes=notes.strip()
    if not title or not (content or notes):raise ValueError('必须填写title以及content或notes。只有链接不能分析内容。')
    if sum(len(s) for s in (title,content,notes))>40000:raise ValueError('单条内容过长，请提供授权摘要')
    sid=make_id(u,title,content)
    when=added_at.strip() or datetime.now(timezone.utc).date().isoformat()
    db.execute("""INSERT INTO sources(id,platform,url,title,content,notes,added_at) VALUES (?,?,?,?,?,?,?)
      ON CONFLICT(id) DO UPDATE SET platform=excluded.platform,title=excluded.title,content=excluded.content,notes=excluded.notes""", (sid,platform.strip() or 'unknown',u,title,content,notes,when))
    return sid

def import_csv(db,path):
    p=Path(path)
    if not p.is_file() or p.stat().st_size>MAX_CSV:raise ValueError('CSV不存在或超过5MB')
    with p.open(encoding='utf-8-sig',newline='') as f:
        r=csv.DictReader(f)
        if not r.fieldnames or not {'title','content'}.issubset(r.fieldnames):raise ValueError('CSV至少有title,content两列')
        n=0
        with db:
            for row in r:
                if not any((v or '').strip() for v in row.values()):continue
                save_source(db, row.get('platform') or '',row.get('source_url') or '',row.get('title') or '',row.get('content') or '',row.get('notes') or '',row.get('added_at') or '');n+=1
    return n

def rows(db,query=''):
    if query:
       term='%'+query.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%'
       return db.execute("SELECT id,platform,url,title,content,notes,added_at FROM sources WHERE title LIKE ? ESCAPE '\\' OR content LIKE ? ESCAPE '\\' OR notes LIKE ? ESCAPE '\\' ORDER BY added_at DESC,id", (term,term,term)).fetchall()
    return db.execute('SELECT id,platform,url,title,content,notes,added_at FROM sources ORDER BY added_at DESC,id').fetchall()

def brief(s):
    return re.sub(r'\s+',' ',s).strip()[:180]

def clean(s):return s.replace('\\','\\\\').replace('|','\\|').replace('\n',' ')

def angles(row):
    _,platform,url,title,content,notes,date=row
    quote=brief(content or notes)
    return [
      ('实操拆解',f'围绕「{title}」做一份可验证的步骤清单；先确认实际可操作的入口与条件。'),
      ('争议/局限',f'结合原始材料「{quote[:60]}」讨论适用范围、成本和哪些结论尚未得到证实。'),
      ('横向比较',f'把「{title}」与自己真正使用过的另一种方法做对照，不编造功能和价格。'),
    ]

def export_md(items):
    out=['# 创作者选题库（离线资料整理）','','由用户手动提供的素材生成，不代表已联网验证链接、热度或内容真实性。','']
    for row in items:
       sid,platform,url,title,content,notes,date=row
       out += [f'## {title}','','- 来源平台：'+platform, '- 链接：'+(url or '未提供'), '- 录入日期：'+date, '- 来源ID：`'+sid+'`', '- 素材摘录：'+brief(content or notes), '- 备注：'+(notes or '无'),'', '**可写的三个角度**']
       out += [f'{i}. **{kind}**：{angle}' for i,(kind,angle) in enumerate(angles(row),1)]
       out += ['','**发布前核对**：原文内容、日期、必要的授权、数据和引用来源。','']
    return '\n'.join(out)

def export_csv(items,outpath):
    with Path(outpath).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['source_id','platform','title','source_url','angle_type','candidate','source_excerpt','notes'])
        for row in items:
            sid,platform,url,title,content,notes,date=row
            for kind,candidate in angles(row):w.writerow([sid,platform,title,url,kind,candidate,brief(content or notes),notes])

def main(argv=None):
    a=argparse.ArgumentParser(description='Creator Idea Vault - 素材入库、去重、选题导出')
    a.add_argument('--db',default='data/idea-vault.sqlite')
    sp=a.add_subparsers(dest='cmd',required=True)
    b=sp.add_parser('import');b.add_argument('--file',required=True)
    b=sp.add_parser('add');b.add_argument('--title',required=True);b.add_argument('--content',required=True);b.add_argument('--url',default='');b.add_argument('--platform',default='other');b.add_argument('--notes',default='')
    b=sp.add_parser('search');b.add_argument('--query',required=True)
    b=sp.add_parser('export');b.add_argument('--output',default='reports');b.add_argument('--query',default='')
    sp.add_parser('stats')
    args=a.parse_args(argv)
    db=connect(args.db)
    try:
      if args.cmd=='import':print(f'导入/更新{import_csv(db,args.file)}行；去重后共{db.execute("select count(*) from sources").fetchone()[0]}条。')
      elif args.cmd=='add':
        with db:sid=save_source(db,args.platform,args.url,args.title,args.content,args.notes)
        print('素材已保存：',sid)
      elif args.cmd=='search':
        for row in rows(db,args.query):print(row[0],row[3],row[2])
      elif args.cmd=='stats':
        print('素材条数：',db.execute('select count(*) from sources').fetchone()[0])
        for p,n in db.execute('select platform,count(*) from sources group by platform order by count(*) desc'):print(p,n)
      elif args.cmd=='export':
        out=Path(args.output);out.mkdir(parents=True,exist_ok=True);items=rows(db,args.query)
        (out/'idea-vault.md').write_text(export_md(items),encoding='utf-8')
        export_csv(items,out/'notion-import.csv')
        print('生成：',out/'idea-vault.md','、',out/'notion-import.csv',f'（{len(items)}条素材）')
    finally:db.close()

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,sqlite3.Error) as e:raise SystemExit(f'错误：{e}')
