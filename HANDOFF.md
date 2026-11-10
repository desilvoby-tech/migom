# desilvo — HANDOFF

Маркетплейс услуг мастеров по всей Беларуси (аналог redsale.by / youdo / kabanchik). Сайт: https://desilvo.by, кабинет: /app.html. Телефон: +375 (25) 616-01-36. Telegram-бот: @desilvo_bot.

## Что сделано
- Главная (index.html):
  - лента заданий, быстрая форма (Supabase + FormSubmit на почту);
  - «Топ исполнителей» (без демо-анкет), «Последние отзывы» (секция скрыта, пока отзывов нет);
  - FAQ, ссылки на SEO-страницы и «Цены».
- Кабинет (app.html, SPA на hash-роутинге):
  - вход по телефону, код приходит в Telegram; запасной вход по ссылке на email; кнопка Google появляется сама, когда провайдер включён в Supabase;
  - создание задания: 10 категорий с вопросами, можно без входа;
  - лента заданий мастера, отклики, выбор мастера (после выбора открываются контакты), чат с realtime, отметка «выполнено», комиссия;
  - отзывы только после выполненного заказа, ответ мастера;
  - регистрация исполнителя (#reg, 5 шагов) и редактор анкеты: цены от–до, портфолио до 30 фото, опыт, образование, налоговый статус и УНП;
  - публичная анкета (#m-<id>), каталог (#masters, `#masters/<услуга>/<город>`, сортировки; демо-анкеты в конце);
  - админка;
  - свой title вкладки у каждого раздела.
- Telegram-уведомления: мастерам, клиентам, админу.
- SEO:
  - /uslugi/ — 84 страницы «услуга + город» (12 × 7) и хаб;
  - /ceny — цены от–до по анкетам, считаются на лету;
  - sitemap.xml, robots.txt.
- Логотип «клякса-часы»: logo.svg, favicon.svg, favicon-32.png, apple-touch-icon.png, og.png.
- Демо-наполнение: 19 примеров анкет по всем категориям.
  - Флаг `is_demo` в masters и profiles, пометка «Пример анкеты» в каталоге, анкете и на SEO-страницах.
  - Без отзывов, рейтинга, заказов и значков проверки; телефон +375290000000.
  - Удалить все демо-анкеты одним запросом: `delete from auth.users where id in (select id from profiles where is_demo);` (каскадом удалятся profiles и masters).

## Структура (репозиторий desilvoby-tech/migom, ветка main)
- index.html — главная (CSS и JS внутри).
- app.html — кабинет (около 88 КБ, весь JS в последнем `<script>`). Основные функции:
  - `route()`, `vLogin`, `vMe`;
  - мастер: `tMaster`/`tFeed`/`tOffers`/`tJobs`/`tRevs`, `openChat`;
  - задания: `vNew`/`drawNew` (категории в `WCATS`), `vTasks`;
  - анкеты: `vReg`/`drawReg`, `profileEditor`, `vMaster`, `vMasters`;
  - `vAdmin`.
  - Мусор: `vMasterOld`, `vLoginOld`, `masterForm`, `bindMF` — не используются.
- config.js — `window.MIGOM={url,key}` (publishable-ключ, публичный).
- uslugi/*.html — SEO-страницы; s.css — их стили; p.js — живой список мастеров, логотип и favicon.
- ceny.html — страница цен (категории внутри).
- schema.sql — устаревшая первая схема. Актуальная схема — в Supabase.
- Генератор SEO-страниц: claude/gen-uslugi.js в проекте claude.ai «ДЕСИЛВО».

## Как выкладывать
- GitHub Pages из main, домен desilvo.by (DNS у active.by, HTTPS включён). Коммит появляется на сайте через 1–2 минуты.
- gh CLI в облаке не авторизован, поэтому правки идут через web-редактор GitHub в Chrome:
  1. Скачать raw-файл, сделать замены строк с проверкой «нашлось ли».
  2. Вставить текст ClipboardEvent paste в `.cm-content`.
  3. Нажать «Commit changes…», затем «Commit changes».
- Новые и бинарные файлы: страница /upload/main/<папка> + DataTransfer в input[type=file]. PNG можно рисовать прямо на canvas.
- SQL: Supabase SQL Editor → `monaco.editor.getModels()[0].setValue(sql)` → Run. Скрипт выполняется одной транзакцией. Предварительно поставить `translate=no`, иначе ломается.
- Проверка синтаксиса: curl raw → последний `<script>` → `node -e "new Function(src)"`.

## База (Supabase, ref cnrvmcwvxpwdxduwifed)
- Таблицы:
  - profiles — role, name, phone, city, tg_chat_id, tg_code, unp, full_name, is_demo;
  - masters — анкета, флаги проверок, рейтинг и счётчики, jsonb prices/works/education/work_history/achievements, tax_status/verified_tax, is_demo;
  - requests — new / assigned / done / cancelled;
  - offers, reviews (unique request_id), messages, notify_log, login_codes, tg_phones.
- Безопасность:
  - RLS на всех таблицах;
  - security definer: is_admin, is_active_master, request_is_open, choose_master, mark_done, recalc_rating;
  - guard-триггеры guard_master/guard_request/guard_review, обход через `migom.bypass`;
  - column grants: masters.telegram_chat_id скрыт.
- Views: open_requests, public_tasks.
- Storage: бакет `works` (public, 5 МБ, папка = uid).
- Edge function `tg` (verify JWT выключен):
  - вебхук бота, `?setup=1` переустанавливает вебхук;
  - login_start/login_check, phone_start/phone_verify (OTP в Telegram);
  - pg_net-триггер notify_tg.
- Секрет TELEGRAM_BOT_TOKEN — в Supabase Secrets. Админ — desilvo.by@gmail.com.

## Ключевые решения
- Бесплатный стек: GitHub Pages + Supabase free + Telegram (без SMS и Viber).
- Безопасная сделка и онлайн-оплата не нужны, комиссия учитывается вручную.
- Контакты клиента открываются только после выбора мастера. Отзыв — только по выполненному заказу. Никаких фейковых отзывов и рейтингов.
- Секреты и ключи вводит сам владелец.

## Вход через Google — что сделать владельцу
1. Google Cloud Console → APIs & Services → Credentials → Create OAuth client ID (Web application).
2. Authorized redirect URI: https://cnrvmcwvxpwdxduwifed.supabase.co/auth/v1/callback
3. Supabase → Authentication → Sign In / Providers → Google: вставить Client ID и Secret, включить.
4. Supabase → Authentication → URL Configuration: Site URL https://desilvo.by, добавить https://desilvo.by/app.html в Redirect URLs.
5. Кнопка «Войти через Google» появится на странице входа автоматически.

## Что осталось
- Работа с заявками: шаблоны откликов, «временно не брать заявки», статистика мастера, настройки уведомлений, отзывы о клиентах.
- Деньги: баланс, счета на комиссию, ЕРИП.
- Прописать og:image и favicon в HTML SEO-страниц (сейчас вставляются через p.js) и пересобрать их.
- Добавить sitemap в Google Search Console и Яндекс Вебмастер.
- Реальная почта в подвале (info@desilvo.by — заглушка).
- Владельцу проверить вживую вход по телефону и уведомления бота.
- Удалить демо-анкеты, когда появятся реальные мастера.
