(function(){
var API='https://lqq-comment.quyet-lequang95.workers.dev',SITEKEY='0x4AAAAAAGDBIjaRiq60acLU';
var box=document.getElementById('binh-luan');if(!box)return;
var m=location.pathname.match(/\/blog\/([a-z0-9-]+)\/?$/);if(!m)return;
var slug=m[1];
function el(t,c,x){var e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e}
var list=box.querySelector('.cmt-list'),form=box.querySelector('form'),msg=box.querySelector('.cmt-msg'),cnt=box.querySelector('.cmt-count');
function fmt(s){var d=new Date(s.replace(' ','T')+'Z');return isNaN(d)?'':d.toLocaleDateString('vi-VN')}
function load(){fetch(API+'/api/comments?slug='+encodeURIComponent(slug)).then(function(r){return r.json()}).then(function(j){
 list.textContent='';var a=j.comments||[];cnt.textContent=a.length?'('+a.length+')':'';
 if(!a.length){list.appendChild(el('p','cmt-empty','Chưa có bình luận nào. Hãy là người đầu tiên chia sẻ góc nhìn của mình.'));return}
 a.forEach(function(c){var d=el('div','cmt-item');var h=el('div','cmt-h');h.appendChild(el('strong',null,c.name));h.appendChild(el('time',null,fmt(c.created_at)));d.appendChild(h);d.appendChild(el('p',null,c.body));list.appendChild(d)})
}).catch(function(){list.textContent=''})}
var wid=null,tsLoaded=false;
function loadTS(){if(tsLoaded)return;tsLoaded=true;var s=document.createElement('script');s.src='https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';s.async=true;s.onload=function(){wid=turnstile.render(box.querySelector('.cmt-ts'),{sitekey:SITEKEY})};document.head.appendChild(s)}
form.addEventListener('focusin',loadTS,{once:true});
form.addEventListener('submit',function(e){e.preventDefault();msg.className='cmt-msg';msg.textContent='';
 var f=new FormData(form),tok=window.turnstile&&wid!==null?turnstile.getResponse(wid):'';
 if(!tok){msg.classList.add('err');msg.textContent='Vui lòng chờ hộp xác minh hiện dấu tick rồi gửi lại.';return}
 var btn=form.querySelector('button');btn.disabled=true;
 fetch(API+'/api/comments',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({slug:slug,name:f.get('name'),email:f.get('email'),body:f.get('body'),website:f.get('website'),token:tok})})
 .then(function(r){return r.json().then(function(j){return{ok:r.ok,j:j}})}).then(function(x){
  if(x.ok){form.reset();msg.classList.add('ok');msg.textContent='Cảm ơn bạn! Bình luận sẽ hiển thị sau khi tôi duyệt.'}
  else{msg.classList.add('err');msg.textContent=x.j.error||'Chưa gửi được, vui lòng thử lại.'}
  if(window.turnstile&&wid!==null)turnstile.reset(wid)})
 .catch(function(){msg.classList.add('err');msg.textContent='Mất kết nối, vui lòng thử lại.'})
 .then(function(){btn.disabled=false})});
load();
})();
