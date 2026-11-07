"""Nhập bài từ file Excel Contact Center Insight thành các file Markdown trong thư mục content/.
Chạy một lần: python tools/import_excel.py duong_dan/Contact_Center_Insight.xlsx   (cần: pip install openpyxl)
Sau đó chỉ cần sửa các file .md và chạy python tools/build_site.py"""
import re, os, sys, unicodedata, datetime
from openpyxl import load_workbook
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XL=sys.argv[1] if len(sys.argv)>1 else 'Contact_Center_Insight.xlsx'
T=["Contact Center khác Call Center như thế nào?","Một Contact Center trong ngân hàng vận hành như thế nào?","Nhiều Contact Center đang đo sai KPI?","Vì sao nhiều Contact Center luôn quá tải?","Một agent Contact Center xử lý bao nhiêu cuộc gọi mỗi ngày?","Burnout trong Contact Center","QA trong Contact Center hoạt động thế nào?","Vấn đề lớn nhất của QA thủ công","Một Contact Center tốn bao nhiêu chi phí?","Voicebot có thể thay thế agent không?","Vì sao nhiều ngân hàng vẫn muốn khách hàng gọi hotline?","CRM quan trọng thế nào với Contact Center?","Vì sao khách hàng ghét phải lặp lại thông tin?","Omnichannel Contact Center là gì?","Điều gì khiến khách hàng hài lòng nhất khi gọi hotline?","Một lỗi rất phổ biến khi triển khai Contact Center","Tại sao nhiều khách hàng vẫn thích gọi điện?","Speech Analytics đang thay đổi Contact Center","Contact Center là “mỏ vàng dữ liệu”","Contact Center có thể giúp tăng doanh thu","Vì sao nhiều dự án Contact Center thất bại?","AI sẽ thay đổi Contact Center như thế nào?","Tương lai của Contact Center","Bài học lớn nhất từ Contact Center","Phía sau một cuộc gọi hotline: nhìn lại Mùa 1"]
def chapter(n): return 'Nền tảng vận hành' if n<=6 else 'Chất lượng và chi phí' if n<=11 else 'CRM, Omnichannel và trải nghiệm' if n<=17 else 'Dữ liệu, AI và tương lai' if n<=24 else 'Tổng kết'
def slugify(t):
    t=t.replace('đ','d').replace('Đ','D'); t=unicodedata.normalize('NFKD',t)
    t=''.join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r'[^a-z0-9]+','-',t).strip('-')[:70].strip('-')
def sym(ch): return unicodedata.category(ch)[0]=='S' or ch=='•'
def upper_ratio(s):
    L=[c for c in s if c.isalpha()]; return sum(c.isupper() for c in L)/len(L) if L else 0
def convert(text):
    paras=[p.strip() for p in re.split(r'\n\s*\n',text.replace('\r','').strip()) if p.strip()]
    paras=[p for i,p in enumerate(paras) if not(i<3 and p.lower().startswith('contact center insight') and len(p)<100)]
    out=[]
    for p in paras:
        lines=[l.strip() for l in p.split('\n') if l.strip()]
        if '↓' in lines: out.append(('p',' → '.join(l for l in lines if l!='↓'))); continue
        if len(lines)==1 and lines[0] in ('Hook','Nội dung'): continue
        if len(lines)==1 and lines[0]=='Câu hỏi': out.append(('h','Câu hỏi để thảo luận')); continue
        if all(l.startswith('#') for l in lines): continue
        if len(lines)==1:
            l=lines[0]
            if not out and upper_ratio(l)>0.6 and len(l)<170: continue
            if re.match(r'^\d+\.\s+\S',l) and len(l)<130 and not l.endswith(('.','?')): out.append(('h',l)); continue
        for l in lines: out.append(('p',l))
    short=lambda k,x: k=='p' and len(x)<=60 and not sym(x[0]) and not x.endswith(('.','?',':','!','…','"','”'))
    o2=[];i=0
    while i<len(out):
        j=i
        while j<len(out) and short(*out[j]): j+=1
        if j-i>=3: o2.append(('ul',[o[1] for o in out[i:j]])); i=j
        else: o2.append(out[i]); i+=1
    out=o2
    res=[];i=0
    while i<len(out):
        k,x=out[i]
        if k=='p' and sym(x[0]):
            j=i
            while j<len(out) and out[j][0]=='p' and sym(out[j][1][0]): j+=1
            if j-i>=2: res.append(('ul',[o[1] for o in out[i:j]])); i=j; continue
        res.append((k,x)); i+=1
    parts=[]
    for k,x in res:
        parts.append('## '+x if k=='h' else '\n'.join('- '+re.sub(r'^•\s*','',t) for t in x) if k=='ul' else x)
    return '\n\n'.join(parts)
def fix_title(t):
    t=re.sub(r'\s+\?','?',str(t).strip())
    if not t.endswith(('?','.','!')) and re.search(r'^(Vì sao|Tại sao)|như thế nào|không$|ở đâu|bao lâu|thấy gì|là gì',t): t+='?'
    return t
def ch2(n):
    return 'Kiến trúc hệ thống' if n<=3 else 'CRM và tích hợp' if n<=7 else 'Omnichannel và AI' if n<=12 else 'Triển khai và bài học'
def write(season,num,title,pillar,date,pub,kind,label,body):
    slug=slugify(title); d=os.path.join(ROOT,'content','mua-%d'%season); os.makedirs(d,exist_ok=True)
    fm=['---','title: '+title,'slug: '+slug,'series: Contact Center Insights','season: %d'%season,'number: %d'%num,'label: %s'%label,'chapter: '+pillar,'date: '+(date.strftime('%Y-%m-%d') if date else ''),'published: '+('yes' if pub else 'no'),'kind: '+kind,'linkedin: ','---','']
    open(os.path.join(d,'%02d-%s.md'%(num,slug)),'w',encoding='utf-8').write('\n'.join(fm)+'\n'+body+'\n')
wb=load_workbook(XL,read_only=True,data_only=True)
rows=list(wb[wb.sheetnames[0]].iter_rows(values_only=True))[1:]
for r in rows:
    if r[0] is None: continue
    n=int(r[0]); body=str(r[7] or r[6] or '')
    if n==25: body=body.split('\n\n',1)[1] if '\n\n' in body else body
    write(1,n,T[n-1],chapter(n),r[2],str(r[4]).strip()=='Done','recap' if n==25 else 'post',n if n<=24 else '',convert(body))
rows=list(wb[wb.sheetnames[1]].iter_rows(values_only=True))[1:]
for r in rows:
    if not r[3]: continue
    m=re.search(r'S2 #(\d+)',str(r[3])); rec='Recap' in str(r[3])
    n=int(m.group(1)) if m else (99 if rec else 0)
    kind='recap' if rec else 'post' if m else 'intro'
    write(2,n,fix_title(r[5]),'Tổng kết' if rec else ch2(n) if m else 'Giới thiệu Mùa 2',None,True,kind,24+n if m else '',convert(str(r[7] or r[6] or '')))
pat=re.compile(r'\d[\d.,]*\s?%|gấp \d+|\bX\d|\d+\s?(tỷ|triệu)|VietCredit',re.I)
rep=['# Các câu có số liệu hoặc tên khách hàng, nên xem lại nguồn và quyền công bố\n']
for sd in ('mua-1','mua-2'):
    for f in sorted(os.listdir(os.path.join(ROOT,'content',sd))):
        t=open(os.path.join(ROOT,'content',sd,f),encoding='utf-8').read(); hits=[x.strip() for x in re.split(r'(?<=[.!?])\s+|\n',t.split('---',2)[2]) if pat.search(x)]
        if hits: rep.append('\n## '+sd+'/'+f+'\n'+'\n'.join('- '+h[:220] for h in hits[:8]))
open(os.path.join(ROOT,'content','REVIEW.md'),'w',encoding='utf-8').write('\n'.join(rep)+'\n')
print('xong')
