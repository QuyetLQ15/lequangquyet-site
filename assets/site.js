(function(){var rm=matchMedia('(prefers-reduced-motion:reduce)').matches,$=function(i){return document.getElementById(i)};
var tt=$('totop');
if(tt){addEventListener('scroll',function(){tt.classList.toggle('show',scrollY>400)},{passive:true});
tt.addEventListener('click',function(){scrollTo({top:0,behavior:rm?'auto':'smooth'})});}
var bg=$('burger'),mn=$('menu'),cb=$('cbtn'),cp=$('cpop');
function setC(o){if(!cp)return;cp.hidden=!o;cb.setAttribute('aria-expanded',o)}
function setM(o){if(!mn)return;mn.classList.toggle('open',o);bg.setAttribute('aria-expanded',o)}
if(cb)cb.addEventListener('click',function(e){e.stopPropagation();setC(cp.hidden);setM(false)});
if(bg)bg.addEventListener('click',function(e){e.stopPropagation();setM(!mn.classList.contains('open'));setC(false)});
document.addEventListener('click',function(e){if(cp&&!cp.contains(e.target))setC(false);if(mn&&!mn.contains(e.target))setM(false)});
document.addEventListener('keydown',function(e){if(e.key==='Escape'){setC(false);setM(false)}});
if(mn)mn.addEventListener('click',function(e){if(e.target.tagName==='A')setM(false)});
document.querySelectorAll('[data-copy]').forEach(function(b){b.addEventListener('click',function(){
var t=b.dataset.copy,done=function(){var o=b.textContent;b.textContent='Đã sao chép';setTimeout(function(){b.textContent=o},1800)};
if(navigator.clipboard){navigator.clipboard.writeText(t).then(done)}else{var i=document.createElement('input');i.value=t;document.body.appendChild(i);i.select();document.execCommand('copy');i.remove();done()}})});
var q=$('q'),chips=document.querySelectorAll('.blog .chips button'),cur='all';
function norm(s){return s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/đ/g,'d').toLowerCase()}
function apply(){var t=q?norm(q.value.trim()):'',n=0;
document.querySelectorAll('.blog .posts li').forEach(function(li){var ok=(cur==='all'||li.dataset.t===cur)&&(!t||norm(li.textContent).indexOf(t)>-1);li.hidden=!ok;if(ok)n++});
document.querySelectorAll('.blog h3.season').forEach(function(h){h.hidden=!h.nextElementSibling.querySelector('li:not([hidden])')});
var c=$('cnt');if(c)c.textContent=n+' bài viết';var z=$('none');if(z)z.hidden=n>0}
if(q){q.addEventListener('input',apply);chips.forEach(function(b){b.addEventListener('click',function(){cur=b.dataset.f;chips.forEach(function(x){x.setAttribute('aria-pressed',x===b)});apply()})})}
var ac=document.querySelectorAll('.actchips button');
ac.forEach(function(b){b.addEventListener('click',function(){ac.forEach(function(x){x.setAttribute('aria-pressed',x===b)});var f=b.dataset.f;
document.querySelectorAll('.actlist .act').forEach(function(a){a.hidden=f!=='all'&&a.dataset.t!==f})})});

var sp=$('spot');
if(sp){var ss=sp.querySelectorAll('.spot-slide'),tb=sp.querySelectorAll('.spot-tabs button'),ix=0,tm,DUR=6500;
sp.style.setProperty('--dur',DUR+'ms');
function show(n){ix=(n+ss.length)%ss.length;ss.forEach(function(s,i){s.classList.toggle('on',i===ix)});tb.forEach(function(b,i){b.classList.toggle('on',i===ix);b.setAttribute('aria-selected',i===ix)});if(!rm)restart()}
function restart(){clearTimeout(tm);sp.classList.remove('run');void sp.offsetWidth;if(rm)return;sp.classList.add('run');tm=setTimeout(function(){if(sp.classList.contains('hold')||document.hidden){restart()}else{show(ix+1)}},DUR)}
tb.forEach(function(b,i){b.addEventListener('click',function(){show(i)})});
sp.addEventListener('keydown',function(e){if(e.key==='ArrowRight')show(ix+1);if(e.key==='ArrowLeft')show(ix-1)});
sp.addEventListener('mouseenter',function(){sp.classList.add('hold')});sp.addEventListener('mouseleave',function(){sp.classList.remove('hold')});
sp.addEventListener('focusin',function(e){try{if(e.target.matches(':focus-visible'))sp.classList.add('hold')}catch(x){}});sp.addEventListener('focusout',function(){sp.classList.remove('hold')});
restart()}

function toast(m){var o=document.querySelector('.toast');if(o)o.remove();var d=document.createElement('div');d.className='toast';d.setAttribute('role','status');d.textContent=m;document.body.appendChild(d);setTimeout(function(){d.remove()},3200)}
var fine=matchMedia('(hover:hover) and (pointer:fine)');
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href^="tel:"]');if(!a||!fine.matches)return;e.preventDefault();var n='0587793865',ok=function(){toast('Đã sao chép số 0587 793 865. Nhắn Zalo sẽ nhanh hơn nếu anh/chị đang dùng máy tính.')};
if(navigator.clipboard){navigator.clipboard.writeText(n).then(ok,function(){toast('Số điện thoại: 0587 793 865')})}else{toast('Số điện thoại: 0587 793 865')}});

var mainEl=document.querySelector('main');if(mainEl){if(!mainEl.id)mainEl.id='main';mainEl.setAttribute('tabindex','-1')}
var ml=[].slice.call(document.querySelectorAll('#menu a'));
function curMenu(a){ml.forEach(function(x){if(x===a)x.setAttribute('aria-current','true');else x.removeAttribute('aria-current')})}
var pth=location.pathname.replace(/index\.html$/,''),pageLink=null;
ml.forEach(function(a){var u=new URL(a.href,location.href),up=u.pathname.replace(/index\.html$/,'');if(!u.hash&&up.length>1&&pth.indexOf(up)===0)pageLink=a});
if(pageLink){curMenu(pageLink)}
else{var map=[];ml.forEach(function(a){var u=new URL(a.href,location.href),id='';if(u.hash&&u.pathname.replace(/index\.html$/,'')===pth)id=u.hash.slice(1);else if(!u.hash){id=u.pathname.split('/').filter(Boolean).pop()||''}var sec=id&&document.getElementById(id);if(sec&&sec.tagName==='SECTION')map.push({a:a,s:sec})});
map.sort(function(x,y){return x.s.offsetTop-y.s.offsetTop});
if(map.length){var tk=false;function spy(){tk=false;var best=null,line=innerHeight*.35;
if(scrollY<200){curMenu(null);return}
if(innerHeight+scrollY>=document.documentElement.scrollHeight-4){curMenu(map[map.length-1].a);return}
map.forEach(function(m){if(m.s.getBoundingClientRect().top<=line)best=m.a});curMenu(best)}
addEventListener('scroll',function(){if(!tk){tk=true;requestAnimationFrame(spy)}},{passive:true});spy()}}
})();
