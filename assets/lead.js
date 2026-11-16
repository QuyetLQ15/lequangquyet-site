(function(){
var API='https://lqq-comment.quyet-lequang95.workers.dev',SITEKEY='0x4AAAAAAGDBIjaRiq60acLU';
var form=document.getElementById('lien-he-form');if(!form)return;
var msg=form.querySelector('.lead-msg'),wid=null,loaded=false;
var ck=form.querySelector('[name=consent]'),btn=form.querySelector('button');
function sync(){btn.disabled=!ck.checked}
ck.addEventListener('change',sync);sync();
function loadTS(){if(loaded)return;loaded=true;var s=document.createElement('script');s.src='https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';s.async=true;s.onload=function(){wid=turnstile.render(form.querySelector('.lead-ts'),{sitekey:SITEKEY})};document.head.appendChild(s)}
form.addEventListener('focusin',loadTS,{once:true});
form.addEventListener('submit',function(e){e.preventDefault();msg.className='lead-msg';msg.textContent='';
 var f=new FormData(form),tok=window.turnstile&&wid!==null?turnstile.getResponse(wid):'';
 if(!tok){msg.classList.add('err');msg.textContent='Vui lòng chờ hộp xác minh hiện dấu tick rồi gửi lại.';return}
 if(!ck.checked){msg.classList.add('err');msg.textContent='Vui lòng tick đồng ý sử dụng thông tin để gửi.';return}
 btn.disabled=true;
 fetch(API+'/api/contact',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:f.get('name'),phone:f.get('phone'),email:f.get('email'),company:f.get('company'),interest:f.get('interest'),message:f.get('message'),consent:f.get('consent')==='on',website:f.get('website'),token:tok})})
 .then(function(r){return r.json().then(function(j){return{ok:r.ok,j:j}})}).then(function(x){
  if(x.ok){form.reset();msg.classList.add('ok');msg.textContent='Cảm ơn anh/chị! Tôi đã nhận được thông tin và sẽ liên hệ lại sớm.'}
  else{msg.classList.add('err');msg.textContent=x.j.error||'Chưa gửi được, vui lòng thử lại.'}
  if(window.turnstile&&wid!==null)turnstile.reset(wid)})
 .catch(function(){msg.classList.add('err');msg.textContent='Mất kết nối, vui lòng thử lại.'})
 .then(sync)});
})();
