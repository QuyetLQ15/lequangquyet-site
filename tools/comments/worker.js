// Bình luận lequangquyet.com — Cloudflare Worker + D1
// Biến cần có: DB (D1), TURNSTILE_SECRET, ADMIN_PASSWORD (secret); tùy chọn: RESEND_API_KEY (secret)
const ORIGINS = ['https://lequangquyet.com', 'https://www.lequangquyet.com'];
const SLUG_RE = /^[a-z0-9][a-z0-9-]{0,120}$/;

const cors = (req) => {
  const o = req.headers.get('Origin');
  return {
    'Access-Control-Allow-Origin': ORIGINS.includes(o) ? o : ORIGINS[0],
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Vary': 'Origin'
  };
};
const json = (req, data, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', ...cors(req) } });

async function sha256(s) {
  const b = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
  return [...new Uint8Array(b)].map((x) => x.toString(16).padStart(2, '0')).join('');
}
function safeEq(a, b) {
  const x = new TextEncoder().encode(a || ''), y = new TextEncoder().encode(b || '');
  let d = x.length ^ y.length;
  for (let i = 0; i < Math.max(x.length, y.length); i++) d |= (x[i] || 0) ^ (y[i] || 0);
  return d === 0;
}
const isAdmin = (req, env) => {
  const m = (req.headers.get('Authorization') || '').match(/^Bearer (.+)$/);
  return !!(env.ADMIN_PASSWORD && m && safeEq(m[1], env.ADMIN_PASSWORD));
};
const getSetting = async (env, k) => {
  const r = await env.DB.prepare('SELECT v FROM settings WHERE k=?').bind(k).first();
  return r ? r.v : '';
};

async function notify(env, c) {
  try {
    if (!env.RESEND_API_KEY) return;
    const to = await getSetting(env, 'notify_email');
    if (!to) return;
    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + env.RESEND_API_KEY, 'Content-Type': 'application/json' },
      body: JSON.stringify({ from: 'lequangquyet.com <onboarding@resend.dev>', to: [to], subject: c.subject, text: c.text })
    });
  } catch (e) { /* thông báo lỗi không được làm hỏng việc gửi */ }
}

async function postComment(req, env) {
  let d;
  try { d = await req.json(); } catch { return json(req, { error: 'Dữ liệu không hợp lệ.' }, 400); }
  if (d.website) return json(req, { ok: true }); // ô ẩn dành cho bot: giả vờ thành công
  const slug = String(d.slug || ''), name = String(d.name || '').trim(), body = String(d.body || '').trim();
  const email = String(d.email || '').trim();
  if (!SLUG_RE.test(slug)) return json(req, { error: 'Bài viết không hợp lệ.' }, 400);
  if (name.length < 1 || name.length > 60) return json(req, { error: 'Vui lòng nhập tên (tối đa 60 ký tự).' }, 400);
  if (body.length < 2 || body.length > 2000) return json(req, { error: 'Nội dung từ 2 đến 2000 ký tự.' }, 400);
  if (email && (email.length > 120 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))) return json(req, { error: 'Email chưa đúng định dạng.' }, 400);
  if ((body.match(/https?:\/\//gi) || []).length > 2) return json(req, { error: 'Bình luận chứa quá nhiều liên kết.' }, 400);

  const ip = req.headers.get('CF-Connecting-IP') || '';
  const form = new FormData();
  form.append('secret', env.TURNSTILE_SECRET || '');
  form.append('response', String(d.token || ''));
  form.append('remoteip', ip);
  const v = await (await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', { method: 'POST', body: form })).json();
  if (!v.success) return json(req, { error: 'Chưa xác minh được bạn là người thật. Vui lòng thử lại.' }, 400);

  const ipHash = await sha256(ip + '|lqq-salt');
  const recent = await env.DB.prepare("SELECT COUNT(*) n FROM comments WHERE ip_hash=? AND created_at > datetime('now','-10 minutes')").bind(ipHash).first();
  if (recent.n >= 3) return json(req, { error: 'Bạn gửi hơi nhanh, vui lòng thử lại sau ít phút.' }, 429);

  await env.DB.prepare('INSERT INTO comments(slug,name,email,body,status,ip_hash) VALUES(?,?,?,?,?,?)')
    .bind(slug, name, email || null, body, 'pending', ipHash).run();
  await notify(env, { subject: 'Bình luận mới chờ duyệt: ' + name, text: `Bài: ${slug}\nTên: ${name}\nEmail: ${email || '(không để lại)'}\n\n${body}\n\nDuyệt tại: ${new URL(req.url).origin}/admin` });
  return json(req, { ok: true });
}


const INTERESTS = ['Webex Contact Center', 'OmiBot', 'OmiCX', 'OmiQC', 'SIP Trunking/VBN', 'Dịch vụ BPO', 'Khác'];
async function postContact(req, env) {
  let d;
  try { d = await req.json(); } catch { return json(req, { error: 'Dữ liệu không hợp lệ.' }, 400); }
  if (d.website) return json(req, { ok: true });
  const name = String(d.name || '').trim(), phone = String(d.phone || '').trim(), email = String(d.email || '').trim();
  const company = String(d.company || '').trim(), interest = String(d.interest || '').trim(), message = String(d.message || '').trim();
  if (name.length < 1 || name.length > 80) return json(req, { error: 'Vui lòng nhập họ tên.' }, 400);
  if (!/^[0-9+\s.()-]{8,20}$/.test(phone)) return json(req, { error: 'Vui lòng nhập số điện thoại hợp lệ để tôi liên hệ.' }, 400);
  if (email && (email.length > 120 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))) return json(req, { error: 'Email chưa đúng định dạng.' }, 400);
  if (company.length > 100) return json(req, { error: 'Tên công ty quá dài.' }, 400);
  if (interest && !INTERESTS.includes(interest)) return json(req, { error: 'Lựa chọn giải pháp không hợp lệ.' }, 400);
  if (message.length > 1000) return json(req, { error: 'Nội dung tối đa 1000 ký tự.' }, 400);
  if (!d.consent) return json(req, { error: 'Vui lòng đồng ý để tôi lưu thông tin dùng cho việc liên hệ.' }, 400);

  const ip = req.headers.get('CF-Connecting-IP') || '';
  const form = new FormData();
  form.append('secret', env.TURNSTILE_SECRET || '');
  form.append('response', String(d.token || ''));
  form.append('remoteip', ip);
  const v = await (await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', { method: 'POST', body: form })).json();
  if (!v.success) return json(req, { error: 'Chưa xác minh được bạn là người thật. Vui lòng thử lại.' }, 400);

  const ipHash = await sha256(ip + '|lqq-salt');
  const recent = await env.DB.prepare("SELECT COUNT(*) n FROM leads WHERE ip_hash=? AND created_at > datetime('now','-10 minutes')").bind(ipHash).first();
  if (recent.n >= 3) return json(req, { error: 'Bạn gửi hơi nhanh, vui lòng thử lại sau ít phút.' }, 429);

  await env.DB.prepare('INSERT INTO leads(name,phone,email,company,interest,message,ip_hash) VALUES(?,?,?,?,?,?,?)')
    .bind(name, phone, email || null, company || null, interest || null, message || null, ipHash).run();
  await notify(env, {
    subject: 'Yêu cầu tư vấn mới: ' + name,
    text: `Tên: ${name}\nĐiện thoại: ${phone || '-'}\nEmail: ${email || '-'}\nCông ty: ${company || '-'}\nQuan tâm: ${interest || '-'}\n\n${message || '(không có nội dung)'}\n\nXem tại: ${new URL(req.url).origin}/admin`
  });
  return json(req, { ok: true });
}

async function listComments(req, env) {
  const slug = new URL(req.url).searchParams.get('slug') || '';
  if (!SLUG_RE.test(slug)) return json(req, { comments: [] });
  const r = await env.DB.prepare("SELECT id,name,body,created_at FROM comments WHERE slug=? AND status='approved' ORDER BY id ASC LIMIT 200").bind(slug).all();
  return json(req, { comments: r.results });
}

async function admin(req, env, path) {
  if (!isAdmin(req, env)) return json(req, { error: 'Sai mật khẩu.' }, 401);
  if (path === '/api/admin/list') {
    const st = new URL(req.url).searchParams.get('status') || 'pending';
    const q = st === 'all' ? 'SELECT * FROM comments ORDER BY id DESC LIMIT 300' : 'SELECT * FROM comments WHERE status=? ORDER BY id DESC LIMIT 300';
    const r = st === 'all' ? await env.DB.prepare(q).all() : await env.DB.prepare(q).bind(st).all();
    return json(req, { comments: r.results, notify_email: await getSetting(env, 'notify_email') });
  }
  if (path === '/api/admin/leads') {
    const r = await env.DB.prepare('SELECT * FROM leads ORDER BY id DESC LIMIT 300').all();
    return json(req, { leads: r.results });
  }
  if (path === '/api/admin/lead-action' && req.method === 'POST') {
    const d = await req.json();
    const id = parseInt(d.id, 10);
    if (!id) return json(req, { error: 'Thiếu id.' }, 400);
    if (d.action === 'done') await env.DB.prepare("UPDATE leads SET status='done' WHERE id=?").bind(id).run();
    else if (d.action === 'new') await env.DB.prepare("UPDATE leads SET status='new' WHERE id=?").bind(id).run();
    else if (d.action === 'delete') await env.DB.prepare('DELETE FROM leads WHERE id=?').bind(id).run();
    else return json(req, { error: 'Hành động không hợp lệ.' }, 400);
    return json(req, { ok: true });
  }
  if (path === '/api/admin/action' && req.method === 'POST') {
    const d = await req.json();
    const id = parseInt(d.id, 10);
    if (!id) return json(req, { error: 'Thiếu id.' }, 400);
    if (d.action === 'approve') await env.DB.prepare("UPDATE comments SET status='approved' WHERE id=?").bind(id).run();
    else if (d.action === 'reject') await env.DB.prepare("UPDATE comments SET status='rejected' WHERE id=?").bind(id).run();
    else if (d.action === 'delete') await env.DB.prepare('DELETE FROM comments WHERE id=?').bind(id).run();
    else return json(req, { error: 'Hành động không hợp lệ.' }, 400);
    return json(req, { ok: true });
  }
  if (path === '/api/admin/settings' && req.method === 'POST') {
    const d = await req.json();
    const e = String(d.notify_email || '').trim();
    if (e && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e)) return json(req, { error: 'Email không đúng định dạng.' }, 400);
    await env.DB.prepare('INSERT INTO settings(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v').bind('notify_email', e).run();
    return json(req, { ok: true });
  }
  return json(req, { error: 'Không tìm thấy.' }, 404);
}

const ADMIN_HTML = `<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Quản trị bình luận</title>
<style>body{font:16px/1.5 system-ui,sans-serif;max-width:860px;margin:0 auto;padding:20px;color:#12213A;background:#f6f8fb}h1{font-size:22px}.bar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:12px 0}
button,input{font:inherit;padding:8px 12px;border-radius:8px;border:1px solid #c5cedb;background:#fff}button{cursor:pointer}button.on{background:#12213A;color:#fff}
.c{background:#fff;border:1px solid #dde4ee;border-radius:12px;padding:14px;margin:12px 0}.m{font-size:13px;color:#5b6b82;margin-bottom:6px}.b{white-space:pre-wrap;word-break:break-word}
.a button{margin:8px 8px 0 0}.ok{background:#1b7f4b;color:#fff;border-color:#1b7f4b}.no{background:#b42318;color:#fff;border-color:#b42318}.st{font-size:12px;padding:2px 8px;border-radius:99px;background:#eef2f8}</style></head><body>
<h1>Quản trị bình luận</h1><div id="login" class="bar"><input id="pw" type="password" placeholder="Mật khẩu quản trị"><button id="go">Vào</button></div>
<div id="app" hidden><div class="bar" id="tabs"></div><div id="list"></div>
<div class="c"><div class="m">Email nhận thông báo bình luận mới</div><div class="bar"><input id="ne" type="email" style="flex:1;min-width:220px"><button id="sv">Lưu</button></div><div class="m" id="svm"></div></div></div>
<script>
let T=sessionStorage.getItem('t')||'',S='pending';
const $=s=>document.querySelector(s);
async function api(p,o={}){const r=await fetch(p,{...o,headers:{'Content-Type':'application/json',Authorization:'Bearer '+T}});const j=await r.json();if(!r.ok)throw new Error(j.error||'Lỗi');return j}
function el(t,c,x){const e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e}
async function load(){try{if(S==='leads')return loadLeads();const j=await api('/api/admin/list?status='+S);$('#login').hidden=true;$('#app').hidden=false;$('#ne').value=j.notify_email||'';
const tb=$('#tabs');tb.textContent='';[['pending','Chờ duyệt'],['approved','Đã duyệt'],['rejected','Từ chối'],['all','Tất cả'],['leads','Yêu cầu tư vấn']].forEach(([k,v])=>{const b=el('button',k===S?'on':'',v);b.onclick=()=>{S=k;load()};tb.append(b)});
const L=$('#list');L.textContent='';if(!j.comments.length)L.append(el('p','m','Không có bình luận.'));
j.comments.forEach(c=>{const d=el('div','c');const m=el('div','m',c.name+' · '+(c.email||'không để email')+' · bài: '+c.slug+' · '+c.created_at+' UTC ');m.append(el('span','st',c.status));d.append(m,el('div','b',c.body));
const a=el('div','a');[['approve','Duyệt','ok'],['reject','Từ chối',''],['delete','Xóa','no']].forEach(([ac,l,cl])=>{const b=el('button',cl,l);b.onclick=async()=>{if(ac==='delete'&&!confirm('Xóa vĩnh viễn bình luận này?'))return;await api('/api/admin/action',{method:'POST',body:JSON.stringify({id:c.id,action:ac})});load()};a.append(b)});d.append(a);L.append(d)})}
catch(e){T='';sessionStorage.removeItem('t');$('#login').hidden=false;$('#app').hidden=true;alert(e.message)}}
async function tabs(){const tb=$('#tabs');tb.textContent='';[['pending','Chờ duyệt'],['approved','Đã duyệt'],['rejected','Từ chối'],['all','Tất cả'],['leads','Yêu cầu tư vấn']].forEach(([k,v])=>{const b=el('button',k===S?'on':'',v);b.onclick=()=>{S=k;load()};tb.append(b)})}
async function loadLeads(){try{const j=await api('/api/admin/leads');$('#login').hidden=true;$('#app').hidden=false;await tabs();const L=$('#list');L.textContent='';if(!j.leads.length)L.append(el('p','m','Chưa có yêu cầu tư vấn.'));
j.leads.forEach(c=>{const d=el('div','c');const m=el('div','m',c.created_at+' UTC · ');m.append(el('span','st',c.status==='done'?'đã liên hệ':'mới'));d.append(m);
[['Họ tên',c.name],['Điện thoại',c.phone],['Email',c.email],['Công ty',c.company],['Quan tâm',c.interest]].forEach(([k,v])=>{if(v)d.append(el('div','b',k+': '+v))});if(c.message)d.append(el('div','b','Nội dung: '+c.message));
const a=el('div','a');[[c.status==='done'?'new':'done',c.status==='done'?'Đánh dấu chưa liên hệ':'Đã liên hệ','ok'],['delete','Xóa','no']].forEach(([ac,l,cl])=>{const b=el('button',cl,l);b.onclick=async()=>{if(ac==='delete'&&!confirm('Xóa vĩnh viễn yêu cầu này?'))return;await api('/api/admin/lead-action',{method:'POST',body:JSON.stringify({id:c.id,action:ac})});load()};a.append(b)});d.append(a);L.append(d)})}
catch(e){T='';sessionStorage.removeItem('t');$('#login').hidden=false;$('#app').hidden=true;alert(e.message)}}
$('#go').onclick=()=>{T=$('#pw').value;sessionStorage.setItem('t',T);load()};
$('#sv').onclick=async()=>{try{await api('/api/admin/settings',{method:'POST',body:JSON.stringify({notify_email:$('#ne').value})});$('#svm').textContent='Đã lưu.'}catch(e){$('#svm').textContent=e.message}};
if(T)load();
</script></body></html>`;

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const p = url.pathname;
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors(req) });
    try {
      if (p === '/admin') return new Response(ADMIN_HTML, { headers: { 'Content-Type': 'text/html; charset=utf-8', 'X-Robots-Tag': 'noindex', 'Cache-Control': 'no-store' } });
      if (p === '/api/comments' && req.method === 'GET') return await listComments(req, env);
      if (p === '/api/comments' && req.method === 'POST') return await postComment(req, env);
      if (p === '/api/contact' && req.method === 'POST') return await postContact(req, env);
      if (p.startsWith('/api/admin/')) return await admin(req, env, p);
      return json(req, { error: 'Không tìm thấy.' }, 404);
    } catch (e) {
      return json(req, { error: 'Lỗi máy chủ, vui lòng thử lại.' }, 500);
    }
  }
};
