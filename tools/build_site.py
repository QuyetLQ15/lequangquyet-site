"""Tạo các trang bài viết từ content/*/*.md, cập nhật danh sách trên trang chủ và sitemap.
Chạy: python tools/build_site.py   (chỉ cần Python 3, không cần cài thêm gì)
Thêm bài mới: tạo file .md trong content/mua-N/ (copy từ bài có sẵn), đặt published: yes, rồi chạy lệnh trên."""
import re, os, json, html, datetime, shutil
try:
    from PIL import Image
except Exception:
    Image=None
from string import Template
from urllib.parse import quote
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE='https://lequangquyet.com'
TODAY=datetime.date.today().isoformat()
def parse(path):
    t=open(path,encoding='utf-8').read(); m=re.match(r'---\n(.*?)\n---\n(.*)',t,re.S); meta={}
    for line in m.group(1).split('\n'):
        k,_,v=line.partition(':'); meta[k.strip()]=v.strip()
    meta['body']=m.group(2).strip(); meta['season']=int(meta['season']); meta['number']=int(meta['number']); meta.setdefault('series','Contact Center Insights'); return meta
def inline(s):
    s=html.escape(s,quote=False)
    s=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',s)
    return re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)',r'<a href="\2" target="_blank" rel="noopener">\1</a>',s)
def dims(path):
    if Image is None: return ''
    try:
        w,h=Image.open(os.path.join(ROOT,path)).size; return ' width="%d" height="%d"'%(w,h)
    except Exception: return ''
def src_of(path,prefix): return path if re.match(r'^(https?:)?//|^/',path) else prefix+path
def figure(alt,path,cap,prefix):
    return '<figure><img src="%s" alt="%s" loading="lazy" decoding="async"%s>%s</figure>'%(html.escape(src_of(path,prefix)),html.escape(alt),dims(path),('<figcaption>%s</figcaption>'%html.escape(cap)) if cap else '')
def render(body,prefix=''):
    out=[]
    for b in re.split(r'\n\s*\n',body):
        L=b.split('\n')
        im=re.match(r'^!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)$',b.strip())
        if im: out.append(figure(im.group(1),im.group(2),im.group(3),prefix)); continue
        if b.startswith('## '): out.append('<h2>%s</h2>'%inline(b[3:]))
        elif all(l.startswith('- ') for l in L): out.append('<ul>'+''.join('<li%s>%s</li>'%(' class="emo"' if not l[2:3].isalnum() else '',inline(l[2:])) for l in L)+'</ul>')
        else: out.append('<p>%s</p>'%inline(b).replace('\n','<br>'))
    res=[];i=0
    while i<len(out):
        if out[i].startswith('<figure>'):
            k=i
            while k<len(out) and out[k].startswith('<figure>'): k+=1
            res.append(('<div class="gallery">'+''.join(out[i:k])+'</div>') if k-i>1 else out[i]); i=k
        else: res.append(out[i]); i+=1
    return '\n'.join(res)
def plain(body): return re.sub(r'\s+',' ',re.sub(r'[#*\-]|\[|\]\(.*?\)','',body))
def desc(body):
    for b in re.split(r'\n\s*\n',body):
        if len(b)>=70 and not b.startswith(('## ','- ')):
            s=re.sub(r'\s+',' ',b); return s if len(s)<=155 else s[:155].rsplit(' ',1)[0]+'…'
    return ''
def fmt(d): return datetime.date.fromisoformat(d).strftime('%d/%m/%Y') if d else ''
posts=[]
for sd in sorted(os.listdir(os.path.join(ROOT,'content'))):
    p=os.path.join(ROOT,'content',sd)
    if os.path.isdir(p) and sd.startswith('mua-'):
        for f in sorted(os.listdir(p)):
            if f.endswith('.md'):
                m=parse(os.path.join(p,f))
                if m['published']=='yes': posts.append(m)
posts.sort(key=lambda m:(m['season'],m['number']))
seen=set()
for m in posts:
    if m['slug'] in seen: m['slug']+='-mua-%d'%m['season']
    seen.add(m['slug'])
for old in ('insights','blog'): shutil.rmtree(os.path.join(ROOT,old),ignore_errors=True)
def url(m): return 'blog/%s/'%m['slug']
ART=Template(open(os.path.join(ROOT,'tools','article_template.html'),encoding='utf-8').read())
def C(n,root): return Template(open(os.path.join(ROOT,'tools',n+'.html'),encoding='utf-8').read()).substitute(root=root)
for i,m in enumerate(posts):
    prv=posts[i-1] if i>0 and posts[i-1]['season']==m['season'] else None
    nxt=posts[i+1] if i+1<len(posts) and posts[i+1]['season']==m['season'] else None
    canon='%s/%s'%(SITE,url(m)); words=len(plain(m['body']).split()); mins=max(1,round(words/200))
    cov=m.get('cover',''); ogimg=SITE+'/assets/og-image.jpg'; ogtags='<meta property="og:image" content="%s">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">'%ogimg; cover_html=''
    if cov:
        ogimg=SITE+'/'+cov; dm=re.search(r'width="(\d+)" height="(\d+)"',dims(cov))
        ogtags='<meta property="og:image" content="%s">'%ogimg+('\n<meta property="og:image:width" content="%s">\n<meta property="og:image:height" content="%s">'%dm.groups() if dm else '')+'\n<meta property="og:image:alt" content="%s">'%html.escape(m.get('cover_alt') or m['title'])
        cover_html='<figure class="cover"><img src="../../%s" alt="%s" fetchpriority="high" decoding="async"%s></figure>'%(html.escape(cov),html.escape(m.get('cover_alt') or m['title']),dims(cov))
    ld={"@context":"https://schema.org","@type":"BlogPosting","headline":m['title'],"inLanguage":"vi-VN","datePublished":m['date'] or None,"dateModified":m['date'] or None,"mainEntityOfPage":canon,"image":ogimg,"author":{"@id":SITE+"/#person"},"isPartOf":{"@type":"Blog","name":m["series"]}}
    ld={k:v for k,v in ld.items() if v}
    def pn(x,lab,cls): return '<a class="%s" href="../../%s">%s<strong>%s</strong></a>'%(cls,url(x),lab,html.escape(x['title'])) if x else '<span></span>'
    li=('<a href="%s" target="_blank" rel="noopener">Xem bản gốc trên LinkedIn</a>'%m['linkedin']) if m.get('linkedin') else ''
    page=ART.substitute(title=html.escape(m['title'])+' | Lê Quang Quyết',desc=html.escape(desc(m['body'])),canon=canon,h1=html.escape(m['title']),
        crumb='%s · Mùa %d'%(html.escape(m['series']),m['season']),chapter=html.escape(m['chapter']),date=fmt(m['date']),iso=m['date'] or '',mins=mins,body=render(m['body'],'../../'),cover=cover_html,ogimage_tags=ogtags,meta=' · '.join(([('<time datetime="%s">%s</time>'%(m['date'],fmt(m['date'])))] if m['date'] else [])+['%d phút đọc'%mins,'Lê Quang Quyết']),pubmeta=('<meta property="article:published_time" content="%s">'%m['date']) if m['date'] else '',
        ld=json.dumps(ld,ensure_ascii=False),share_li='https://www.linkedin.com/sharing/share-offsite/?url='+quote(canon,safe=''),share_fb='https://www.facebook.com/sharer/sharer.php?u='+quote(canon,safe=''),
        canon_js=canon,header=C('header','../../'),footer=C('footer','../../'),float=C('float','../../'),prev=pn(prv,'Bài trước','pn'),next=pn(nxt,'Bài sau','pn r'),linkedin=li)
    d=os.path.join(ROOT,url(m)); os.makedirs(d,exist_ok=True); open(os.path.join(d,'index.html'),'w',encoding='utf-8').write(page)
# trang chủ
S=open(os.path.join(ROOT,'index.html'),encoding='utf-8').read()
def between(s,a,b,new): i=s.index(a)+len(a); j=s.index(b,i); return s[:i]+new+s[j:]
STARTS=[(4,'Khi hotline luôn quá tải','Quá tải thường không chỉ là chuyện thiếu người. Điều gì đang thật sự đẩy hàng chờ dài ra?'),(3,'Khi chỉ số đẹp nhưng khách vẫn phàn nàn','Vì sao ép thời gian xử lý ngắn có thể làm khách gọi lại nhiều hơn, và chỉ số nào mới phản ánh vấn đề được giải quyết.'),(7,'Khi QA chỉ nghe được một phần nhỏ cuộc gọi','QA trong ngân hàng làm gì, và vì sao chỉ nghe một phần nhỏ cuộc gọi là chưa đủ.'),(21,'Khi dự án đầu tư lớn nhưng không chạy','Công nghệ tốt nhưng dự án vẫn chậm và không như kỳ vọng. Điểm nghẽn thường nằm ở đâu?'),(10,'Khi nghe nói AI sẽ thay thế con người','Câu trả lời thẳng là không. AI nên nhận những việc lặp đi lặp lại để con người làm việc cần chất xám.')]
by={(m['season'],m['number']):m for m in posts}
# Bắt đầu từ đây: "sân khấu" xoay vòng (sửa STARTS ở trên để đổi bài, nhãn, mô tả; bài nào có cover thì hiện ảnh)
def spot_slide(m,tg,sm,k,total):
    cov=m.get('cover','')
    if cov: im='<img src="%s" alt="%s" loading="lazy" decoding="async"%s>'%(html.escape(cov),html.escape(m.get('cover_alt') or m['title']),dims(cov))
    else: im='<span class="spot-n">#%s</span><span class="spot-c">%s</span>'%(m['number'],html.escape(m['chapter']))
    return ('<article class="spot-slide%s" id="spot-%d" role="tabpanel"><a class="spot-art g%d%s" href="%s" tabindex="-1" aria-hidden="true">%s</a>'
            '<div class="spot-body"><span class="spot-no">%02d / %02d</span><span class="tag">%s</span><h3><a href="%s">%s</a></h3><p>%s</p><a class="btn p" href="%s">Xem chi tiết</a></div></article>\n')%(
            ' on' if k==0 else '',k,m['number']%4,'' if cov else ' noimg',url(m),im,k+1,total,html.escape(tg),url(m),html.escape(m['title']),html.escape(sm),url(m))
_st=[(by[(1,n)],tg,sm) for n,tg,sm in STARTS if (1,n) in by]
sl=''.join(spot_slide(m,tg,sm,k,len(_st)) for k,(m,tg,sm) in enumerate(_st))
tabs=''.join('<button type="button" role="tab" class="%s" aria-controls="spot-%d" aria-selected="%s"><b>%02d</b><span>%s</span></button>'%('on' if k==0 else '',k,'true' if k==0 else 'false',k+1,html.escape(tg)) for k,(m,tg,sm) in enumerate(_st))
S=between(S,'<!--START:begin-->','<!--START:end-->','\n<div class="spot" id="spot" role="region" aria-roledescription="carousel" aria-label="Bắt đầu từ đây">\n<div class="spot-stage">\n'+sl+'</div>\n<div class="spot-tabs" role="tablist">'+tabs+'</div>\n</div>\n<p class="more"><a class="btn" href="blog/">Xem tất cả bài viết</a></p>\n')
S=between(S,'<!--HEADER:begin-->','<!--HEADER:end-->',C('header',''))
S=between(S,'<!--FOOT:begin-->','<!--FOOT:end-->',C('footer',''))
S=between(S,'<!--FLOAT:begin-->','<!--FLOAT:end-->',C('float',''))
open(os.path.join(ROOT,'index.html'),'w',encoding='utf-8').write(S)
# trang Blog
groups=[]
for m in posts:
    g=(m['series'],m['season'])
    if g not in groups: groups.append(g)
groups=sorted(groups,key=lambda g:(g[0],-g[1]))
multi=len({g[0] for g in groups})>1; key={g:'g%d'%i for i,g in enumerate(groups)}
chips='<button type="button" aria-pressed="true" data-f="all">Tất cả</button>'+''.join('<button type="button" aria-pressed="false" data-f="%s">%s</button>'%(key[g],html.escape(('%s · Mùa %d'%g) if multi else 'Mùa %d'%g[1])) for g in groups)
blocks=''
for g in groups:
    lis=''.join('<li data-t="%s"><span class="tag">%s</span><div><h3>%s<a href="%s/">%s</a></h3></div></li>\n'%(key[g],html.escape(m['chapter']),('#%s. '%m['label']) if m.get('label') else '',m['slug'],html.escape(m['title'])) for m in posts if (m['series'],m['season'])==g)
    blocks+='<h3 class="season">%s · Mùa %d</h3>\n<ul class="posts">\n%s</ul>\n'%(html.escape(g[0]),g[1],lis)
if not any(g[1]==2 for g in groups):
    blocks='<div class="soon"><h3>Mùa 2 đang bắt đầu: công nghệ phía sau Contact Center</h3><p>Kiến trúc hệ thống, IVR và ACD, tích hợp CRM với core banking, Voicebot và AI trong vận hành thực tế, và những bài học khi triển khai dự án. Các bài sẽ lần lượt ra mắt tại đây.</p></div>\n'+blocks
B=Template(open(os.path.join(ROOT,'tools','blog_template.html'),encoding='utf-8').read())
bdesc='Các chuỗi bài viết về vận hành và công nghệ Contact Center cho ngân hàng, bảo hiểm, tài chính. %d bài viết, tìm theo từ khóa hoặc theo mùa.'%len(posts)
os.makedirs(os.path.join(ROOT,'blog'),exist_ok=True)
open(os.path.join(ROOT,'blog','index.html'),'w',encoding='utf-8').write(B.substitute(desc=bdesc,lead='Các chuỗi bài viết về vận hành và công nghệ Contact Center dành cho các anh/chị quản lý trong khối BFSI, và sẽ còn nhiều chủ đề khác.',count=len(posts),chips=chips,groups=blocks,header=C('header','../'),footer=C('footer','../'),float=C('float','../')))
# ----- Hoạt động -----
def parse_raw(path):
    t=open(path,encoding='utf-8').read(); mm=re.match(r'---\n(.*?)\n---\n(.*)',t,re.S); d={}
    for line in mm.group(1).split('\n'):
        k,_,v=line.partition(':'); d[k.strip()]=v.strip()
    d['body']=mm.group(2).strip(); return d
acts=[]
ad=os.path.join(ROOT,'content','hoat-dong')
if os.path.isdir(ad):
    for f in sorted(os.listdir(ad)):
        if f.endswith('.md'):
            a=parse_raw(os.path.join(ad,f))
            if a.get('published')=='yes': acts.append(a)
acts.sort(key=lambda a:a.get('date',''),reverse=True)
shutil.rmtree(os.path.join(ROOT,'hoat-dong'),ignore_errors=True)
def aurl(a): return 'hoat-dong/%s/'%a['slug']
tags=[]
for a in acts:
    if a['tag'] not in tags: tags.append(a['tag'])
tkey={t:'t%d'%i for i,t in enumerate(tags)}
def card(a,lp,ip):
    cov=a.get('cover','')
    img=('<img src="%s" alt="%s" loading="lazy" decoding="async"%s>'%(html.escape(ip+cov),html.escape(a.get('cover_alt') or a['title']),dims(cov))) if cov else ''
    return '<article class="act" data-t="%s"><a class="ph" href="%s%s/" tabindex="-1" aria-hidden="true"><span>Hình ảnh sắp cập nhật</span>%s</a><div class="bd"><span class="tag">%s</span><h3><a href="%s%s/">%s</a></h3><time>%s</time><p>%s</p></div></article>\n'%(tkey[a['tag']],lp,a['slug'],img,html.escape(a['tag']),lp,a['slug'],html.escape(a['title']),fmt(a.get('date')) or 'Đang cập nhật',html.escape(a.get('summary','')))
def tile(a,lp,ip):
    cov=a.get('cover','')
    img=('<img src="%s" alt="%s" loading="lazy" decoding="async"%s>'%(html.escape(ip+cov),html.escape(a.get('cover_alt') or a['title']),dims(cov))) if cov else ''
    return ('<a class="tile" data-t="%s" href="%s%s/"><span class="tile-img%s">%s</span><span class="tile-shade"></span><span class="tile-in"><span class="tag">%s</span><strong>%s</strong><span class="tile-meta">%s%s</span><em>%s</em></span></a>\n')%(
            tkey[a['tag']],lp,a['slug'],'' if cov else ' noimg',img,html.escape(a['tag']),html.escape(a['title']),fmt(a.get('date')) or 'Đang cập nhật',(' · '+html.escape(a['place'])) if a.get('place') and a['place']!='Đang cập nhật' else '',html.escape(a.get('summary','')))
def apn(x,lab,cls): return '<a class="%s" href="../../%s">%s<strong>%s</strong></a>'%(cls,aurl(x),lab,html.escape(x['title'])) if x else '<span></span>'
AT=Template(open(os.path.join(ROOT,'tools','activity_template.html'),encoding='utf-8').read())
for i,a in enumerate(acts):
    newer=acts[i-1] if i>0 else None; older=acts[i+1] if i+1<len(acts) else None
    canon='%s/%s'%(SITE,aurl(a)); cov=a.get('cover',''); ogimg=SITE+'/assets/og-image.jpg'
    ogtags='<meta property="og:image" content="%s">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">'%ogimg; cover_html=''
    if cov:
        ogimg=SITE+'/'+cov; dm=re.search(r'width="(\d+)" height="(\d+)"',dims(cov))
        ogtags='<meta property="og:image" content="%s">'%ogimg+('\n<meta property="og:image:width" content="%s">\n<meta property="og:image:height" content="%s">'%dm.groups() if dm else '')
        cover_html='<figure class="cover"><img src="../../%s" alt="%s" fetchpriority="high" decoding="async"%s></figure>'%(html.escape(cov),html.escape(a.get('cover_alt') or a['title']),dims(cov))
    ld={"@context":"https://schema.org","@type":"Article","headline":a['title'],"inLanguage":"vi-VN","datePublished":a.get('date') or None,"mainEntityOfPage":canon,"image":ogimg,"author":{"@id":SITE+"/#person"}}
    ld={k:v for k,v in ld.items() if v}
    meta=' · '.join(x for x in [fmt(a.get('date')),html.escape(a.get('place','')) if a.get('place') and 'cập nhật' not in a['place'] else ''] if x)
    li=('<a href="%s" target="_blank" rel="noopener">Xem bài đăng gốc trên LinkedIn</a>'%a['linkedin']) if a.get('linkedin') else ''
    page=AT.substitute(title=html.escape(a['title'])+' | Hoạt động | Lê Quang Quyết',desc=html.escape(a.get('summary','')),canon=canon,h1=html.escape(a['title']),crumb=html.escape(a['tag']),chapter=html.escape(a['tag']),
        meta=meta,iso=a.get('date',''),pubmeta=('<meta property="article:published_time" content="%s">'%a['date']) if a.get('date') else '',cover=cover_html,ogimage_tags=ogtags,body=render(a['body'],'../../'),ld=json.dumps(ld,ensure_ascii=False),
        share_li='https://www.linkedin.com/sharing/share-offsite/?url='+quote(canon,safe=''),share_fb='https://www.facebook.com/sharer/sharer.php?u='+quote(canon,safe=''),canon_js=canon,
        prev=apn(newer,'Mới hơn','pn'),next=apn(older,'Cũ hơn','pn r'),linkedin=li,header=C('header','../../'),footer=C('footer','../../'),float=C('float','../../'))
    d=os.path.join(ROOT,aurl(a)); os.makedirs(d,exist_ok=True); open(os.path.join(d,'index.html'),'w',encoding='utf-8').write(page)
if acts:
    LT=Template(open(os.path.join(ROOT,'tools','activities_template.html'),encoding='utf-8').read())
    chips='<button type="button" aria-pressed="true" data-f="all">Tất cả</button>'+''.join('<button type="button" aria-pressed="false" data-f="%s">%s</button>'%(tkey[t],html.escape(t)) for t in tags)
    adesc='Những chương trình và sự kiện Lê Quang Quyết tham gia cùng đồng nghiệp, đối tác và cộng đồng.'
    os.makedirs(os.path.join(ROOT,'hoat-dong'),exist_ok=True)
    open(os.path.join(ROOT,'hoat-dong','index.html'),'w',encoding='utf-8').write(LT.substitute(desc=adesc,lead='Những chương trình và sự kiện tôi tham gia cùng đồng nghiệp, đối tác và cộng đồng.',chips=chips,cards=''.join(card(a,'','../') for a in acts),header=C('header','../'),footer=C('footer','../'),float=C('float','../')))
S2=open(os.path.join(ROOT,'index.html'),encoding='utf-8').read()
S2=between(S2,'<!--ACT:begin-->','<!--ACT:end-->','\n'+(''.join(tile(a,'hoat-dong/','') for a in acts[:3]) or '<p>Nội dung đang được cập nhật.</p>\n'))
S2=re.sub(r'(data-since="(\d{4})"[^>]*>)\d+',lambda m:m.group(1)+str(datetime.date.today().year-int(m.group(2))),S2)
open(os.path.join(ROOT,'index.html'),'w',encoding='utf-8').write(S2)
urls=[(SITE+'/',TODAY),(SITE+'/blog/',TODAY)]+([(SITE+'/hoat-dong/',TODAY)] if acts else [])+[(SITE+'/'+url(m),m['date'] or TODAY) for m in posts]+[(SITE+'/'+aurl(a),a.get('date') or TODAY) for a in acts]
open(os.path.join(ROOT,'sitemap.xml'),'w',encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('  <url><loc>%s</loc><lastmod>%s</lastmod></url>\n'%u for u in urls)+'</urlset>\n')
# trang 404 (GitHub Pages tự dùng file này khi gõ sai địa chỉ)
open(os.path.join(ROOT,'404.html'),'w',encoding='utf-8').write('''<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Không tìm thấy trang | Lê Quang Quyết</title><meta name="robots" content="noindex">
<link rel="icon" href="/favicon.ico"><link rel="stylesheet" href="/assets/style.css"></head><body>
'''+C('header','/')+'''<main class="wrap" style="padding-top:90px;padding-bottom:90px;min-height:55vh"><p class="eyebrow"><span></span> LỖI 404</p><h1>Không tìm thấy trang này</h1>
<p class="lead">Địa chỉ có thể đã đổi hoặc gõ chưa đúng. Anh/chị có thể quay về trang chủ hoặc xem các bài viết.</p>
<p><a class="btn p" href="/">Về trang chủ</a> <a class="btn" href="/blog/">Xem Blog</a></p></main>
'''+C('footer','/')+C('float','/')+'''<script src="/assets/site.js"></script></body></html>''')
# cache-busting: gắn số phiên bản vào đường dẫn CSS và JS để trình duyệt luôn tải bản mới sau khi bạn sửa
import hashlib
def _ver(f): return hashlib.md5(open(os.path.join(ROOT,'assets',f),'rb').read()).hexdigest()[:8]
_V={'style.css':_ver('style.css'),'site.js':_ver('site.js')}
def _bust(path):
    t=open(path,encoding='utf-8').read()
    n=re.sub(r'(assets/(style\.css|site\.js))(\?v=[0-9a-f]+)?(?=")',lambda m:m.group(1)+'?v='+_V[m.group(2)],t)
    if n!=t: open(path,'w',encoding='utf-8').write(n)
for _d,_,_fs in os.walk(ROOT):
    if set(os.path.relpath(_d,ROOT).replace('\\','/').split('/'))&{'.git','.idea','content','tools'}: continue
    for _f in _fs:
        if _f.endswith('.html'): _bust(os.path.join(_d,_f))
print('đã tạo %d trang bài viết, %d trang hoạt động'%(len(posts),len(acts)))
