/* qa-fix (27.11.2026): замечания проверки. Чтобы отключить — удалить блок qa-fix в конце config.js */
(function(){
  /* телефон: шапка кабинета в две строки, без второй кнопки «Создать задание» */
  if(document.querySelector('header .nav>a.btn[href="#new"]')){
    var st=document.createElement("style");
    st.textContent='@media(max-width:560px){header .nav{gap:6px 10px;padding:8px 12px;justify-content:space-between}header .nav .logo{flex:1 0 60%;order:-2}header #logout{order:-1}header .nav .sp,header .nav>a.btn[href="#new"]{display:none}header .nav a.l{font-size:.82rem;line-height:1.2;padding:6px 0}}';
    document.head.appendChild(st);
  }
  /* поиск: «починить кран» → ищем по слову «кран», если по всей фразе ничего нет */
  if(typeof window.dsSearch!=="function") return;
  var SKIP=/^(починить|почините|починка|отремонтировать|ремонт|исправить|сделать|нужен|нужна|нужно|надо|мне|помогите|заказать|вызвать)$/;
  var orig=window.dsSearch;
  window.dsSearch=function(qs,fuzzy){
    var r=orig(qs,fuzzy); if(r.length) return r;
    var rest=qs.filter(function(w){return !SKIP.test(w)});
    return rest.length&&rest.length<qs.length?orig(rest,fuzzy):r;
  };
})();
