# 🐛 Fix Tracker — Сгенерировано METAai

**Дата**: 2026-04-28 04:12
**Всего issues**: 52

## METAai

| # | Severity | Category | Description | Fix |
|---|----------|----------|-------------|-----|
| 1 | 🔴 CRITICAL | Code Review | Отсутствует определение `BUNDLE_CONTENTS` в коде, что вызове | — |
| 2 | 🔴 CRITICAL | Code Review | Потенциальная гонка условий в rate limiting механизме из-за  | — |
| 3 | 🔴 CRITICAL | Code Review | Отсутствует определение `BUNDLE_CONTENTS` в коде, что вызове | — |
| 4 | 🔴 CRITICAL | Code Review | Потенциальная race condition в rate limiting с использование | — |
| 5 | 🔴 CRITICAL | Code Review | Отсутствие проверки лимитов на количество активных подписок  | — |
| 6 | 🔴 CRITICAL | Code Review | Отсутствует определение `BUNDLE_CONTENTS` в коде, что вызове | — |
| 7 | 🔴 CRITICAL | Code Review | Потенциальная race condition в rate limiting с использование | — |
| 8 | 🔴 CRITICAL | Code Review | Отсутствует определение `BUNDLE_CONTENTS` в коде, что вызове | — |
| 9 | 🔴 CRITICAL | Code Review | Потенциальная race condition в rate limiting с использование | — |
| 10 | 🔴 CRITICAL | Code Review | Отсутствие проверки лимита на количество активных подписок у | — |
| 11 | 🔴 CRITICAL | Строки 146-147 | Использовать защищенное логирование, не выводить чувствитель | 🟠 HIGH |
| 12 | 🟠 HIGH | `create_invoice` method (lines 108-125) | Использовать потокобезопасный кэш (Redis) с атомарными опера | 🔴 CRITICAL |
| 13 | 🟠 HIGH | Блоки try/except | Использовать генерические сообщения об ошибках | 🟡 MEDIUM |
| 14 | 🟠 HIGH | Строка 190 (`payload = f"{req.plan_id}:{user.id}:{payment.id}"`) | Использовать криптографически защищенное формирование payloa | 🟡 MEDIUM |
| 15 | 🔴 CRITICAL | Code Review | Потенциальная утечка секретов в `WEBAPP_URL` без проверки бе | — |
| 16 | 🔴 CRITICAL | Code Review | Отсутствие обработки исключений в некоторых асинхронных мето | — |
| 17 | 🔴 CRITICAL | Code Review | Потенциальная утечка секретов в `WEBAPP_URL` без проверки бе | — |
| 18 | 🔴 CRITICAL | Code Review | Отсутствие обработки исключений в некоторых асинхронных мето | — |
| 19 | 🔴 CRITICAL | lines 200-250 | Использовать параметризованные запросы | 🟠 HIGH |
| 20 | 🟠 HIGH | lines 13-14 | Использовать vault/secret manager | 🟡 MEDIUM |
| 21 | 🟠 HIGH | `_is_admin()` | Реализовать многофакторную проверку | 🟡 MEDIUM |

## ONYX

| # | Severity | Category | Description | Fix |
|---|----------|----------|-------------|-----|
| 1 | 🔴 CRITICAL | Code Review | Незащищенное кэширование rate limiting в памяти процесса — р | — |
| 2 | 🔴 CRITICAL | Code Review | Отсутствие проверки лимита платежей для предотвращения злоуп | — |
| 3 | 🔴 CRITICAL | Code Review | Прямое внедрение зависимостей в методе `create_invoice` (имп | — |
| 4 | 🔴 CRITICAL | Code Review | Потенциальная гонка условий (race condition) при обновлении  | — |
| 5 | 🔴 CRITICAL | Code Review | Отсутствие обработки ошибок при работе с базой данных может  | — |
| 6 | 🔴 CRITICAL | Code Review | Потенциальная уязвимость безопасности в `validate_init_data( | — |
| 7 | 🔴 CRITICAL | Code Review | Потенциальная уязвимость в `get_user_from_init_data()`: нет  | — |
| 8 | 🔴 CRITICAL | Code Review | Отсутствие обработки race condition при создании пользовател | — |
| 9 | 🔴 CRITICAL | Code Review | Отсутствие валидации входных параметров в `create_invoice_li | — |

## Sylectus

| # | Severity | Category | Description | Fix |
|---|----------|----------|-------------|-----|
| 1 | 🔴 CRITICAL | Code Review | Хардкодированный приватный ключ и секрет в коде — КРАЙНЕ ОПА | — |
| 2 | 🔴 CRITICAL | Code Review | Отсутствие проверки прав доступа перед записью в .env файл | — |
| 3 | 🔴 CRITICAL | Code Review | Прямое использование root-доступа без необходимости | — |
| 4 | 🔴 CRITICAL | Code Review | Отсутствие проверки существования пользователя перед обновле | — |
| 5 | 🔴 CRITICAL | Code Review | В `handle_bid_callback()` отсутствует обработка сценария, ко | — |
| 6 | 🔴 CRITICAL | Code Review | Потенциальная утечка соединений с базой данных в методах с ` | — |
| 7 | 🔴 CRITICAL | Code Review | Потенциальная уязвимость безопасности в `verify_webhook()`:  | — |
| 8 | 🔴 CRITICAL | Code Review | Отсутствие обработки исключений при парсинге JSON в `parse_w | — |
| 9 | 🔴 CRITICAL | Code Review | Небезопасное поведение при отсутствии ключа шифрования: функ | — |
| 10 | 🔴 CRITICAL | Code Review | Потенциальная гонка условий в `activate_subscription()` при  | — |
| 11 | 🔴 CRITICAL | Code Review | Отсутствие проверки максимального лимита очков при списании/ | — |
| 12 | 🔴 CRITICAL | Code Review | Отсутствие проверки существования пользователя перед обновле | — |

## backend

| # | Severity | Category | Description | Fix |
|---|----------|----------|-------------|-----|
| 1 | 🔴 CRITICAL | Code Review | Потенциальная уязвимость безопасности в `validate_init_data( | — |
| 2 | 🔴 CRITICAL | Code Review | Потенциальная уязвимость в `get_user_from_init_data()`: нет  | — |
| 3 | 🔴 CRITICAL | Code Review | Отсутствие обработки race condition при создании пользовател | — |
| 4 | 🔴 CRITICAL | Code Review | Небезопасное кэширование rate limiting в памяти процесса (`c | — |
| 5 | 🔴 CRITICAL | Code Review | Отсутствие проверки максимальной длины payload может привест | — |
| 6 | 🔴 CRITICAL | Code Review | Прямое внедрение настроек провайдера платежей без валидации | — |
| 7 | 🔴 CRITICAL | Code Review | Потенциальная гонка условий при обновлении статуса подписки. | — |
| 8 | 🔴 CRITICAL | Code Review | Отсутствие обработки ошибок при работе с базой данных может  | — |
| 9 | 🔴 CRITICAL | Code Review | Отсутствие валидации входных параметров в `create_invoice_li | — |
| 10 | 🔴 CRITICAL | Code Review | Потенциальная утечка секретов: `provider_token` может быть н | — |

