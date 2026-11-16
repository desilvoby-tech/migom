/* Cookie-согласие и Яндекс.Метрика (16.11.2026). Метрика загружается только после «Принять». */
(function(){
var K="ck_consent",ID=114221965;
function get(){try{return localStorage.getItem(K)}catch(e){return null}}
function put(v){try{localStorage.setItem(K,v);localStorage.setItem("ck_ok","1")}catch(e){}}
function load(){if(window.__ymOn)return;window.__ymOn=1;
(function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};m[i].l=1*new Date();for(var j=0;j<document.scripts.length;j++){if(document.scripts[j].src===r){return;}}k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})(window,document,"script","https://mc.yandex.ru/metrika/tag.js?id="+ID,"ym");
ym(ID,"init",{ssr:true,clickmap:true,trackLinks:true,accurateTrackBounce:true,webvisor:true,trackHash:true});}
function kill(){var o=document.querySelectorAll(".ckb");for(var i=0;i<o.length;i++)o[i].remove()}
function banner(){kill();if(document.querySelector(".ckc"))return;
var d=document.createElement("div");d.className="ckc";d.setAttribute("role","dialog");d.setAttribute("aria-label","Согласие на cookie");
d.innerHTML='<p>Мы используем необходимые cookie и хранилище браузера для работы сайта: вход, черновики, настройки. С вашего согласия подключим Яндекс.Метрику — обезличенную статистику посещений. <a href="/politika#cookie">Подробнее</a></p><div class="b"><button type="button" class="ok">Принять</button><button type="button" class="no">Отклонить</button></div>';
var st=document.createElement("style");st.textContent='.ckc{position:fixed;left:12px;right:12px;bottom:12px;z-index:10000;max-width:780px;margin:0 auto;background:#141B2D;color:#eef2f7;border-radius:14px;padding:14px 16px;display:flex;gap:14px;align-items:center;box-shadow:0 10px 30px rgba(0,0,0,.25);font:14px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}.ckc p{margin:0;flex:1}.ckc a{color:#9BE07E}.ckc .b{display:flex;gap:8px;flex:none}.ckc button{border:0;border-radius:10px;padding:9px 16px;font:700 14px system-ui,sans-serif;cursor:pointer}.ckc .ok{background:#4BAE2F;color:#fff}.ckc .no{background:#2A3550;color:#eef2f7}@media(max-width:600px){.ckc{flex-direction:column;align-items:stretch}.ckc .b button{flex:1}}';
d.appendChild(st);
d.querySelector(".ok").onclick=function(){put("yes");d.remove();load()};
d.querySelector(".no").onclick=function(){put("no");d.remove()};
document.body.appendChild(d)}
window.DS_COOKIES=function(){try{localStorage.removeItem(K)}catch(e){}banner()};
var v=get();
if(v==="yes")load();
else if(v!=="no"){if(document.body)banner();else document.addEventListener("DOMContentLoaded",banner)}
setTimeout(kill,800);setTimeout(kill,2500);
})();
