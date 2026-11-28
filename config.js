// Настройки подключения к Supabase.
// Вставьте в key ключ "anon public" (или "publishable") из Supabase: Project Settings -> API Keys.
window.MIGOM = {
  url: "https://api.desilvo.by",
  key: "sb_publishable_DlHP4iYq9B2nmeEo-IU-LY_stINl2i2",
  yandex: true,   // включить после настройки функции oauth
  mailru: true
};
/* qa-fix (27.11.2026): замечания проверки. Чтобы отключить — удалить этот блок. */
document.addEventListener("DOMContentLoaded",function(){var s=document.createElement("script");s.src="/qa-fix.js?v=2";document.head.appendChild(s)});
