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
TRHOST='lequangquyet-com.translate.goog'
def tr(path): return 'https://%s/%s?_x_tr_sl=vi&_x_tr_tl=en&_x_tr_hl=en&_x_tr_pto=wapp'%(TRHOST,path)
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
def share_img(cov):
    """Cắt ảnh bìa thành khung 1200x630 (đúng khung xem trước Facebook/LinkedIn), lưu ở assets/share/. Trả về đường dẫn tương đối."""
    if Image is None or not cov: return cov
    try:
        src=os.path.join(ROOT,cov); name=re.sub(r'[^A-Za-z0-9]+','-',os.path.splitext(cov)[0]).strip('-')+'.jpg'
        rel='assets/share/'+name; dst=os.path.join(ROOT,rel)
        if os.path.exists(dst) and os.path.getmtime(dst)>=os.path.getmtime(src): return rel
        im=Image.open(src).convert('RGB'); w,h=im.size; tw,th=1200,630
        sc=max(tw/w,th/h); im=im.resize((max(tw,round(w*sc)),max(th,round(h*sc))),Image.LANCZOS); w,h=im.size
        l=(w-tw)//2; t=int((h-th)*0.35)
        os.makedirs(os.path.dirname(dst),exist_ok=True); im.crop((l,t,l+tw,t+th)).save(dst,quality=85,optimize=True,progressive=True)
        return rel
    except Exception: return cov
def src_of(path,prefix): return path if re.match(r'^(https?:)?//|^/',path) else prefix+path
def figure(alt,path,cap,prefix):
    return '<figure><img src="%s" alt="%s" loading="lazy" decoding="async"%s>%s</figure>'%(html.escape(src_of(path,prefix)),html.escape(alt),dims(path),('<figcaption>%s</figcaption>'%html.escape(cap)) if cap else '')
def video(path,cap,prefix):
    c=('<figcaption>%s</figcaption>'%html.escape(cap)) if cap else ''
    yt=re.match(r'^https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})',path)
    if yt: return '<figure class="video yt"><div class="vbox"><iframe src="https://www.youtube-nocookie.com/embed/%s" title="%s" loading="lazy" allow="accelerometer; encrypted-media; picture-in-picture" allowfullscreen></iframe></div>%s</figure>'%(yt.group(1),html.escape(cap or 'Video'),c)
    poster=re.sub(r'\.\w+$','.jpg',path); has=os.path.exists(os.path.join(ROOT,poster)) and not re.match(r'^(https?:)?//',path)
    d=dims(poster) if has else ''
    return '<figure class="video"><video controls playsinline preload="none"%s%s><source src="%s" type="video/mp4">Trình duyệt chưa hỗ trợ phát video.</video>%s</figure>'%((' poster="%s"'%html.escape(src_of(poster,prefix))) if has else '',d,html.escape(src_of(path,prefix)),c)
def render(body,prefix=''):
    out=[]
    for b in re.split(r'\n\s*\n',body):
        L=b.split('\n')
        vm=re.match(r'^!\[video\]\((\S+?)(?:\s+"([^"]*)")?\)$',b.strip())
        if vm: out.append(video(vm.group(1),vm.group(2),prefix)); continue
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
        ogimg=SITE+'/'+share_img(cov); dm=re.search(r'(\d+)x(\d+)','1200x630')
        ogtags='<meta property="og:image" content="%s">'%ogimg+('\n<meta property="og:image:width" content="%s">\n<meta property="og:image:height" content="%s">'%dm.groups() if dm else '')+'\n<meta property="og:image:alt" content="%s">'%html.escape(m.get('cover_alt') or m['title'])
        cover_html='<figure class="cover"><img src="../../%s" alt="%s" fetchpriority="high" decoding="async"%s></figure>'%(html.escape(cov),html.escape(m.get('cover_alt') or m['title']),dims(cov))
    ld={"@context":"https://schema.org","@type":"BlogPosting","headline":m['title'],"inLanguage":"vi-VN","datePublished":m['date'] or None,"dateModified":m['date'] or None,"mainEntityOfPage":canon,"image":ogimg,"author":{"@id":SITE+"/#person"},"isPartOf":{"@type":"Blog","name":m["series"]}}
    ld={k:v for k,v in ld.items() if v}
    def pn(x,lab,cls): return '<a class="%s" href="../../%s">%s<strong>%s</strong></a>'%(cls,url(x),lab,html.escape(x['title'])) if x else '<span></span>'
    li=('<a href="%s" target="_blank" rel="noopener">Xem bản gốc trên LinkedIn</a>'%m['linkedin']) if m.get('linkedin') else ''
    page=ART.substitute(title=html.escape(m['title'])+' | Lê Quang Quyết',desc=html.escape(desc(m['body'])),canon=canon,h1=html.escape(m['title']),
        crumb='%s · Mùa %d'%(html.escape(m['series']),m['season']),chapter=html.escape(m['chapter']),date=fmt(m['date']),iso=m['date'] or '',mins=mins,body=render(m['body'],'../../'),cover=cover_html,ogimage_tags=ogtags,meta=' · '.join(([('<time datetime="%s">%s</time>'%(m['date'],fmt(m['date'])))] if m['date'] else [])+['%d phút đọc'%mins,'Lê Quang Quyết']),pubmeta=('<meta property="article:published_time" content="%s">'%m['date']) if m['date'] else '',
        ld=json.dumps(ld,ensure_ascii=False),share_li='https://www.linkedin.com/sharing/share-offsite/?url='+quote(canon,safe=''),share_fb='https://www.facebook.com/sharer/sharer.php?u='+quote(canon,safe=''),
        canon_js=canon,header=C('header','../../'),footer=C('footer','../../'),float=C('float','../../'),prev=pn(prv,'Bài trước','pn'),next=pn(nxt,'Bài sau','pn r'),linkedin=li,translate_url=html.escape(tr(url(m))))
    d=os.path.join(ROOT,url(m)); os.makedirs(d,exist_ok=True); open(os.path.join(d,'index.html'),'w',encoding='utf-8').write(page)
# trang chủ
S=open(os.path.join(ROOT,'index.html'),encoding='utf-8').read()
def between(s,a,b,new): i=s.index(a)+len(a); j=s.index(b,i); return s[:i]+new+s[j:]
STARTS=[(4,'Khi hotline luôn quá tải','Quá tải thường không chỉ là chuyện thiếu người. Điều gì đang thật sự đẩy hàng chờ dài ra?'),(3,'Khi chỉ số đẹp nhưng khách vẫn phàn nàn','Vì sao ép thời gian xử lý ngắn có thể làm khách gọi lại nhiều hơn, và chỉ số nào mới phản ánh vấn đề được giải quyết.'),(7,'Khi QA chỉ nghe được một phần nhỏ cuộc gọi','QA trong ngân hàng làm gì, và vì sao chỉ nghe một phần nhỏ cuộc gọi là chưa đủ.'),(21,'Khi dự án đầu tư lớn nhưng không chạy','Công nghệ tốt nhưng dự án vẫn chậm và không như kỳ vọng. Điểm nghẽn thường nằm ở đâu?'),(10,'Khi nghe nói AI sẽ thay thế con người','Câu trả lời thẳng là không. AI nên nhận những việc lặp đi lặp lại để con người làm việc cần chất xám.')]
by={(m['season'],m['number']):m for m in posts}
# Bắt đầu từ đây: "sân khấu" xoay vòng (sửa STARTS ở trên để đổi bài, nhãn, mô tả; bài nào có cover thì hiện ảnh)
# Mô tả ngắn cho khung "Bắt đầu từ đây" (bài mới: ghi summary: trong front matter của bài, mục này chỉ là mô tả dự phòng cho Mùa 1)
SUM_S1={
1:'Nhiều người vẫn coi Contact Center là tổng đài nghe gọi. Sự khác biệt cốt lõi nằm ở cách nhìn khách hàng trên mọi kênh.',
2:'Ở ngân hàng lớn, Contact Center là cả một hệ sinh thái vận hành từ 200 đến 1000 người, không chỉ là những agent ngồi nghe điện thoại.',
3:'Vì sao ép thời gian xử lý ngắn có thể làm khách gọi lại nhiều hơn, và chỉ số nào mới phản ánh vấn đề được giải quyết.',
4:'Quá tải thường không chỉ là chuyện thiếu người. Điều gì đang thật sự đẩy hàng chờ dài ra?',
5:'70 đến 100 cuộc gọi mỗi ngày không chỉ là một con số năng suất. Đằng sau đó là áp lực mà agent phải gánh từng cuộc.',
6:'Khi áp lực kéo dài, tỷ lệ nghỉ việc có thể lên đến 45% mỗi năm. Vấn đề thường nằm ở quy trình hơn là ở con người.',
7:'QA trong ngân hàng làm gì, và vì sao chỉ nghe một phần nhỏ cuộc gọi là chưa đủ.',
8:'Chỉ nghe được 1 đến 3% cuộc gọi, QA thủ công bỏ sót phần lớn dữ liệu. Trợ lý AI giám sát có thể mở rộng việc kiểm tra ra toàn bộ.',
9:'Chi phí nhân sự chiếm 60 đến 70% chi phí vận hành, lớn hơn nhiều so với hệ thống và phần mềm. Đây là phần chìm của tảng băng.',
10:'Câu trả lời thẳng là không. AI nên nhận những việc lặp đi lặp lại để con người làm việc cần chất xám.',
11:'Giữa thời đại số, hotline vẫn là điểm tựa niềm tin và lớp bảo mật mà ứng dụng khó thay thế hoàn toàn.',
12:'Agent phải mở ba màn hình chỉ để biết đang nói chuyện với ai. CRM tốt biến hồ sơ khách hàng thành một cái nhìn duy nhất.',
13:'Khách hàng không ghét chờ đợi, họ ghét phải kể lại câu chuyện lần thứ hai. Vì sao dữ liệu không đi theo họ qua các kênh?',
14:'Có nhiều kênh chưa phải là Omnichannel. Điểm khác nằm ở chỗ ngữ cảnh của khách hàng có đi theo họ qua từng kênh hay không.',
15:'Điều khiến khách hài lòng sau một cuộc gọi hotline thường không phải là sự giỏi giang, mà là cảm giác được hiểu.',
16:'Công nghệ tốt vẫn thất bại nếu tự động hóa một quy trình đang hỗn loạn. Hãy sắp xếp quy trình trước khi mua thêm công nghệ.',
17:'Trong thời đại một chạm, vì sao vẫn có người chờ nhạc chờ để nói chuyện với một con người khi tài khoản biến động bất thường?',
18:'Nếu QA chỉ nghe khoảng 2% cuộc gọi thì 98% còn lại là vùng tối. Speech Analytics biến lượng dữ liệu đó thành thông tin dùng được.',
19:'Mỗi cuộc gọi là một viên kim cương thô: tiếng nói thật của khách hàng, chứa thông tin về sản phẩm, rủi ro và cơ hội bán hàng.',
20:'Contact Center thường bị coi là trung tâm chi phí. Khi biết khai thác dữ liệu và cuộc gọi, nó có thể trở thành nơi tạo doanh thu.',
21:'Công nghệ tốt và ngân sách lớn vẫn có thể thất bại. Những nguyên nhân lặp đi lặp lại phần lớn nằm ngoài phần mềm.',
22:'AI không thay thế agent mà giúp họ làm việc tốt hơn. So sánh một ngày làm việc trước và sau khi có AI.',
23:'Contact Center trong ngành BFSI sẽ ra sao sau 5 đến 10 năm tới, và Agentic AI sẽ thay đổi vai trò của nó thế nào?',
24:'Sau 24 kỳ bàn về công nghệ, điều tạo ra khác biệt cuối cùng vẫn là con người giúp đỡ con người.',
25:'Nhìn lại Mùa 1: từ agent, QA, WFM đến CRM, Omnichannel và AI, những mảnh ghép nằm sau một cuộc gọi hotline.',
}
def blurb(m): return m.get('summary') or (SUM_S1.get(m['number']) if m['season']==1 else None) or desc(m['body'])
def spot_slide(m,tg,sm,k,total):
    cov=m.get('cover','')
    if cov: im='<img src="%s" alt="%s" loading="lazy" decoding="async"%s>'%(html.escape(cov),html.escape(m.get('cover_alt') or m['title']),dims(cov))
    else: im='<span class="spot-n">#%s</span><span class="spot-c">%s</span>'%(m['number'],html.escape(m['chapter']))
    return ('<article class="spot-slide%s" id="spot-%d" role="tabpanel"><a class="spot-art g%d%s"%s href="%s" tabindex="-1" aria-hidden="true">%s</a>'
            '<div class="spot-body"><span class="spot-no">%02d / %02d</span><span class="tag">%s</span><h3><a href="%s">%s</a></h3><p>%s</p><a class="btn p" href="%s">Xem chi tiết</a></div></article>\n')%(
            ' on' if k==0 else '',k,m['number']%4,' has' if cov else ' noimg',(' style="--bg:url(%s)"'%html.escape(cov)) if cov else '',url(m),im,k+1,total,html.escape(tg),url(m),html.escape(m['title']),html.escape(sm),url(m))
_st=[(by[(1,n)],tg,sm) for n,tg,sm in STARTS if (1,n) in by]
sl=''.join(spot_slide(m,tg,sm,k,len(_st)) for k,(m,tg,sm) in enumerate(_st))
tabs=''.join('<button type="button" role="tab" class="%s" aria-controls="spot-%d" aria-selected="%s"><b>%02d</b><span>%s</span></button>'%('on' if k==0 else '',k,'true' if k==0 else 'false',k+1,html.escape(tg)) for k,(m,tg,sm) in enumerate(_st))
# danh sách các bài có ảnh bìa để trình duyệt tự chọn ngẫu nhiên 5 bài mỗi lần vào trang
def _pool():
    out=[]
    for m in posts:
        if not m.get('cover'): continue
        d=re.search(r'width="(\d+)" height="(\d+)"',dims(m['cover'])); w,h=(d.groups() if d else ('1280','720'))
        out.append({'u':url(m),'c':m['cover'],'a':m.get('cover_alt') or m['title'],'w':int(w),'h':int(h),'t':m['chapter'],'n':m['title'],'s':blurb(m)})
    return out
POOL=json.dumps(_pool(),ensure_ascii=False).replace('</','<\\/')
S=between(S,'<!--START:begin-->','<!--START:end-->','\n<div class="spot" id="spot" role="region" aria-roledescription="carousel" aria-label="Bắt đầu từ đây">\n<div class="spot-stage">\n'+sl+'</div>\n<div class="spot-tabs" role="tablist">'+tabs+'</div>\n</div>\n<script type="application/json" id="spot-data">'+POOL+'</script>\n<p class="more"><a class="btn" href="blog/">Xem tất cả bài viết</a></p>\n')
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
        ogimg=SITE+'/'+share_img(cov); dm=re.search(r'(\d+)x(\d+)','1200x630')
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
# số bài viết tự đếm theo các bài published (mọi mùa), giữ dấu +
S2=re.sub(r'<b data-n="\d+"( data-s="\+")?>\d+\+?</b>(<span>bài viết)',lambda m:'<b data-n="%d" data-s="+">%d+</b>%s'%(len(posts),len(posts),m.group(2)),S2)
S2=re.sub(r'(data-since="(\d{4})"[^>]*>)\d+',lambda m:m.group(1)+str(datetime.date.today().year-int(m.group(2))),S2)
open(os.path.join(ROOT,'index.html'),'w',encoding='utf-8').write(S2)
urls=[(SITE+'/',TODAY),(SITE+'/blog/',TODAY)]+([(SITE+'/hoat-dong/',TODAY)] if acts else [])+[(SITE+'/'+url(m),m['date'] or TODAY) for m in posts]+[(SITE+'/'+aurl(a),a.get('date') or TODAY) for a in acts]
open(os.path.join(ROOT,'sitemap.xml'),'w',encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('  <url><loc>%s</loc><lastmod>%s</lastmod></url>\n'%u for u in urls)+'</urlset>\n')
# ngày cập nhật (dateModified) cho trang chủ trong dữ liệu JSON-LD, tự đặt theo ngày build
_h=open(os.path.join(ROOT,'index.html'),encoding='utf-8').read()
_m=re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)',_h,re.S)
if _m:
    try:
        _d=json.loads(_m.group(2))
        for _n in _d.get('@graph',[]):
            if _n.get('@type')=='ProfilePage': _n['dateModified']=TODAY
        _h=_h[:_m.start(2)]+'\n'+json.dumps(_d,ensure_ascii=False,indent=1)+'\n'+_h[_m.end(2):]
        open(os.path.join(ROOT,'index.html'),'w',encoding='utf-8').write(_h)
    except ValueError: pass
# ---- bản tiếng Anh của trang chủ: /en/ (nội dung ở tools/en_index.html; các bài viết dẫn tới bản dịch tự động của Google)
EN_STARTS=[(4,'When the hotline is always overloaded','Why do so many contact centers stay overloaded?','Overload is rarely just a shortage of people. What is really making the queue longer?'),
(3,'When the metrics look good but customers still complain','Many contact centers are measuring the wrong KPIs','Why pushing handling time down can make customers call back more, and which metrics show whether the issue was resolved.'),
(7,'When QA hears only a small part of the calls','How does QA work in a contact center?','What QA does in a bank, and why hearing only a small share of calls is not enough.'),
(21,'When a big investment does not take off','Why do so many contact center projects fail?','Good technology, yet the project is slow and below expectations. Where is the bottleneck usually?'),
(10,'When people say AI will replace humans','Can a voicebot replace agents?','The straight answer is no. AI should take the repetitive work so people can do the work that needs thinking.')]
def CE(n,**kw): return Template(open(os.path.join(ROOT,'tools',n+'.html'),encoding='utf-8').read()).substitute(**kw)
_trb=html.escape(tr('blog/')); _tra=html.escape(tr('hoat-dong/'))
_st=''.join('<li><span class="tag">%s</span><div><h3><a href="%s" rel="nofollow">%s</a></h3><p>%s</p></div></li>\n'%(html.escape(tg),html.escape(tr(url(by[(1,n)]))),html.escape(t),html.escape(sm)) for n,tg,t,sm in EN_STARTS if (1,n) in by)
EN_ACTS={'go-live-cisco-omicx-mobifone':('Project','Go-live of Cisco Contact Center with MPT OmiCX for MobiFone, nationwide','Nationwide','The Cisco Contact Center and OmiCX solution went live for MobiFone across Vietnam, with teams working from Hanoi, Hai Phong, Da Nang, Ho Chi Minh City and Can Tho towards one shared goal.'),
'chuong-trinh-20-11':('Activity','Vietnamese Teachers\' Day (20/11) at MPT: Thanking the "teachers" of the MPT family','MPT office lobby','On 20/11 we thanked our Training team and in-house Trainers, the people who quietly pass on knowledge and energy to everyone at MPT, with flowers, gifts and a small gathering.'),
'chuong-trinh-20-10':('Activity',"Women's Day (20/10) at MPT: Strong, Confident, Shining",'MPT office','On 20/10, the MPT team gave flowers, gifts and wishes to our female colleagues, with a greeting clip and two mascots joining in.'),
'vietnam-retail-banking-forum-2026':('Industry event','Vietnam Retail Banking Forum 2026 and Growthverse Finance Day 2026','Rex Hotel Saigon, Ho Chi Minh City','On 30 September I attended two events back to back: Vietnam Retail Banking Forum 2026 in the morning and Growthverse Finance Day 2026 in the afternoon.'),
'chuong-trinh-trung-thu-2026':('Activity','Dream Mid-Autumn 2026 at 1 June Special School','Khanh Hoi Ward, Ho Chi Minh City','With the Khanh Hoi Ward Youth Union and kind donors, we organised a Mid-Autumn programme for the children at 1 June Special School.')}
def _etile(a):
    tg,t,pl,sm=EN_ACTS.get(a['slug'],(a['tag'],a['title'],a.get('place',''),a.get('summary','')))
    cov=a.get('cover','')
    img=('<img src="../%s" alt="%s" loading="lazy" decoding="async"%s>'%(html.escape(cov),html.escape(t),dims(cov))) if cov else ''
    d=datetime.date.fromisoformat(a['date']).strftime('%d %b %Y') if a.get('date') else ''
    meta=d+((' · '+html.escape(pl)) if pl and pl!='Đang cập nhật' else '')
    return '<a class="tile" data-t="%s" href="%s" rel="nofollow"><span class="tile-img%s">%s</span><span class="tile-shade"></span><span class="tile-in"><span class="tag">%s</span><strong>%s</strong><span class="tile-meta">%s</span><em>%s</em></span></a>\n'%(tkey[a['tag']],html.escape(tr(aurl(a))),'' if cov else ' noimg',img,html.escape(tg),html.escape(t),meta,html.escape(sm))
_ea=''.join(_etile(a) for a in acts[:3])
E=open(os.path.join(ROOT,'tools','en_index.html'),encoding='utf-8').read()
E=E.replace('<!--HEADER_EN-->',CE('header_en',tr_blog=_trb,tr_act=_tra)).replace('<!--FOOT_EN-->',CE('footer_en',tr_blog=_trb,tr_act=_tra)).replace('<!--FLOAT_EN-->',open(os.path.join(ROOT,'tools','float_en.html'),encoding='utf-8').read())
E=E.replace('<!--ACT_EN-->','\n'+(_ea or '<p>Content is being updated.</p>\n')).replace('<!--START_EN-->','<ul class="posts">\n'+_st+'</ul>').replace('__TR_BLOG__',_trb).replace('__TR_ACT__',_tra).replace('__POSTS__',str(len(posts))).replace('__YEARS__',str(datetime.date.today().year-2016)).replace('__TODAY__',TODAY)
os.makedirs(os.path.join(ROOT,'en'),exist_ok=True)
open(os.path.join(ROOT,'en','index.html'),'w',encoding='utf-8').write(E)
# ---- sửa lỗi Search Console (Profile page): mainEntity phải là đối tượng Person đầy đủ, dateModified phải có giờ + múi giờ
def _ld_fix(path, person):
    h=open(path,encoding='utf-8').read()
    for m in re.finditer(r'(<script type="application/ld\+json">)(.*?)(</script>)',h,re.S):
        try: d=json.loads(m.group(2))
        except ValueError: continue
        g=d.get('@graph')
        if not g: continue
        ch=False
        for n in g:
            if n.get('@type')=='ProfilePage' and person:
                n['mainEntity']=person; n['dateModified']=TODAY+'T00:00:00+07:00'; ch=True
        if ch:
            h=h[:m.start(2)]+'\n'+json.dumps(d,ensure_ascii=False,indent=1)+'\n'+h[m.end(2):]
            open(path,'w',encoding='utf-8').write(h)
        return
_vp=os.path.join(ROOT,'index.html')
_P=None
for _m2 in re.finditer(r'<script type="application/ld\+json">(.*?)</script>',open(_vp,encoding='utf-8').read(),re.S):
    try:
        for _n in json.loads(_m2.group(1)).get('@graph',[]):
            if _n.get('@type')=='Person': _P=_n
    except ValueError: pass
if _P:
    _ld_fix(_vp,_P)
    _ld_fix(os.path.join(ROOT,'en','index.html'),_P)
_sm=open(os.path.join(ROOT,'sitemap.xml'),encoding='utf-8').read()
_sm=_sm.replace('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">')
_alt='<xhtml:link rel="alternate" hreflang="vi" href="%s/"/><xhtml:link rel="alternate" hreflang="en" href="%s/en/"/>'%(SITE,SITE)
_sm=_sm.replace('<url><loc>%s/</loc><lastmod>%s</lastmod></url>'%(SITE,TODAY),'<url><loc>%s/</loc><lastmod>%s</lastmod>%s</url>\n  <url><loc>%s/en/</loc><lastmod>%s</lastmod>%s</url>'%(SITE,TODAY,_alt,SITE,TODAY,_alt),1)
open(os.path.join(ROOT,'sitemap.xml'),'w',encoding='utf-8').write(_sm)
# llms.txt: bản tóm tắt site cho công cụ AI, tự tạo từ danh sách bài viết
_L=['# Lê Quang Quyết','','> Banking Solutions Sales Manager tại Minh Phúc Transformation (MPT). Chia sẻ giải pháp chăm sóc khách hàng đa kênh cho nhóm BFSI (ngân hàng, bảo hiểm, tài chính).','',
'Trang cá nhân của Lê Quang Quyết (Quyet Le). Nội dung bằng tiếng Việt, quan điểm trình bày là của cá nhân tác giả.','','## Trang chính','',
'- [Trang chủ](%s/): giới thiệu, giải pháp và hoạt động'%SITE,'- [Blog](%s/blog/): chuỗi bài Contact Center Insights'%SITE,'- [English homepage](%s/en/): introduction in English'%SITE]
if acts: _L.append('- [Hoạt động](%s/hoat-dong/): chương trình và sự kiện'%SITE)
_L+=['','## Bài viết','']+['- [%s](%s/%s)'%(m['title'],SITE,url(m)) for m in posts]
_L+=['','## Liên hệ','','- Email: quyetlq@mpt.com.vn','- LinkedIn: https://www.linkedin.com/in/quyetlq','']
open(os.path.join(ROOT,'llms.txt'),'w',encoding='utf-8').write('\n'.join(_L))
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
_V={'style.css':_ver('style.css'),'site.js':_ver('site.js'),'comments.js':_ver('comments.js'),'lead.js':_ver('lead.js')}
def _bust(path):
    t=open(path,encoding='utf-8').read()
    n=re.sub(r'(assets/(style\.css|site\.js|comments\.js|lead\.js))(\?v=[0-9a-f]+)?(?=")',lambda m:m.group(1)+'?v='+_V[m.group(2)],t)
    if n!=t: open(path,'w',encoding='utf-8').write(n)
for _d,_,_fs in os.walk(ROOT):
    if set(os.path.relpath(_d,ROOT).replace('\\','/').split('/'))&{'.git','.idea','content','tools'}: continue
    for _f in _fs:
        if _f.endswith('.html'): _bust(os.path.join(_d,_f))
print('đã tạo %d trang bài viết, %d trang hoạt động'%(len(posts),len(acts)))
