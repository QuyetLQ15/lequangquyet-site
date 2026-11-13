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

var sl=$('slider');
if(sl){var tr=sl.querySelector('.sl-track'),cs=tr.querySelectorAll('.sl-card'),dt=sl.querySelector('.sl-dots'),hold=false,tm;
cs.forEach(function(){dt.appendChild(document.createElement('i'))});var ds=dt.children;
function step(){var c=cs[1]?cs[1].offsetLeft-cs[0].offsetLeft:tr.clientWidth;return c}
function cur(){return Math.min(cs.length-1,Math.round(tr.scrollLeft/step()))}
function mark(){var k=cur();for(var i=0;i<ds.length;i++)ds[i].classList.toggle('on',i===k)}
function go(d){var atEnd=tr.scrollLeft+tr.clientWidth>=tr.scrollWidth-4;if(d>0&&atEnd){tr.scrollTo({left:0,behavior:rm?'auto':'smooth'})}else{tr.scrollBy({left:d*step(),behavior:rm?'auto':'smooth'})}}
sl.querySelector('.prev').addEventListener('click',function(){go(-1)});sl.querySelector('.next').addEventListener('click',function(){go(1)});
tr.addEventListener('scroll',function(){clearTimeout(tm);tm=setTimeout(mark,60)},{passive:true});mark();
['mouseenter','focusin','touchstart'].forEach(function(e){sl.addEventListener(e,function(){hold=true})});
['mouseleave','focusout','touchend'].forEach(function(e){sl.addEventListener(e,function(){hold=false})});
if(!rm){setInterval(function(){if(!hold&&!document.hidden)go(1)},5000)}}
})();
