# Автоматическое создание отчётов по нагрузочному тестированию в Confluence

Автоматизирует публикацию результатов нагрузочного тестирования: скачивание графиков из Grafana, выгрузку логов из Loki, AI‑аналитику по доменам и обновление страницы Confluence из шаблона в один проход.

## Оглавление
- [Общее описание](#общее-описание)
- [Архитектура и поток данных](#архитектура-и-поток-данных)
- [Компоненты проекта](#компоненты-проекта)
- [Плейсхолдеры шаблона Confluence](#плейсхолдеры-шаблона-confluence)
- [Конфигурация](#конфигурация)
- [Установка и запуск](#установка-и-запуск)
- [Docker](#docker)
- [REST API](#rest-api)
- [Примеры](#примеры)
- [Безопасность и сеть](#безопасность-и-сеть)
- [Устранение неполадок](#устранение-неполадок)

## Общее описание
Сервис поднимает легкий веб‑интерфейс (Flask) для запуска отчёта за заданный интервал и сервис. По конфигурации берутся идентификаторы шаблона и родительской страницы Confluence, создаётся копия шаблона, после чего в неё массово подставляются данные: графики из Grafana, виджеты с логами из Loki и markdown‑блоки с AI‑аналитикой. Один проход по странице позволяет избежать гонок версий и гарантировать целостность результата.

## Архитектура и поток данных
1. UI (`templates/index.html`) или REST вызывает `POST /create_report` с диапазоном времени и именем сервиса.
2. Оркестратор (`update_page.update_report`) копирует шаблон в Confluence и параллельно загружает метрики/логи:
   - метрики: `data_collectors/grafana_collector.uploadFromGrafana` рендерит панели Grafana и прикрепляет изображения к странице;
   - логи: `data_collectors/loki_collector.uploadFromLoki` сохраняет `.log` и прикрепляет как `view-file`‑виджет.
3. После сбора метрик/логов выполняется AI‑аналитика (`AI/main.uploadFromLLM`) по доменам (JVM, Database, Kafka, Microservices) и общий итог.
4. Результаты LLM преобразуются в markdown (`confluence_manager/update_confluence_template.render_llm_markdown`) и вставляются в плейсхолдеры одним вызовом `update_confluence_page_multi`.

## Компоненты проекта
- `app.py` — Flask‑приложение: маршруты `/` (форма), `GET /services` (имена сервисов из `metrics_config.py`), `POST /create_report` (создание отчёта). Конвертация времени: `YYYY-MM-DDTHH:MM` → timestamp в мс.
- `update_page.py` — основной оркестратор: копирование шаблона, параллельная выгрузка метрик/логов, LLM‑часть, мульти‑обновление плейсхолдеров. Есть повторные попытки при конфликте версий страницы.
- `confluence_manager/update_confluence_template.py` — работа с Confluence: `copy_confluence_page`, `update_confluence_page`, `update_confluence_page_multi`, а также форматтер `render_llm_markdown`, который помимо вердикта/доверия/находок/рекомендаций выводит раздел «Пиковая производительность» при наличии данных `peak_performance` [[memory:8657199]].
- `data_collectors/grafana_collector.py` — скачивание изображений панелей Grafana (basic auth), загрузка во вложения Confluence и вставка `<ac:image>`.
- `data_collectors/loki_collector.py` — запрос логов в Loki (`/loki/api/v1/query_range`), сохранение во временный `.log`, загрузка во вложения Confluence и вставка `<ac:structured-macro ac:name="view-file">`.
- `metrics_config.py` — описание сервисов: ID шаблона/родителя Confluence, список метрик (имя → `$$<name>$$` плейсхолдер) и список логов (placeholder + Loki‑фильтр).
- `config.py` — базовые параметры доступа (Confluence/Grafana/Loki).
- `AI/` — подсистема AI и промты; подробности см. `AI/README.md`.

## Плейсхолдеры шаблона Confluence
- **Метрики**: `$$<name>$$` — имя берётся из `METRICS_CONFIG[service].metrics[].name`. На их место вставляются изображения соответствующих панелей Grafana.
- **Логи**: `$$<placeholder>$$` — плейсхолдеры из `METRICS_CONFIG[service].logs[].placeholder`. На их место вставляется виджет просмотра вложенного `.log`.
- **AI‑аналитика**:
  - `$$answer_jvm$$`, `$$answer_database$$`, `$$answer_kafka$$`, `$$answer_ms$$` — доменные markdown‑блоки, если есть данные.
  - `$$answer_llm$$` и `$$final_answer$$` — сводный markdown, формируется из строго валидированного JSON (схема LLMAnalysis). Если строгого JSON нет — фолбэк: публикуется текстовый итог.
  - Если в ответе LLM присутствует `peak_performance` (`{max_rps, max_time, drop_time, method}`), то он выводится отдельным подразделом внутри `$$answer_llm$$`/`$$final_answer$$` [[memory:8657199]].

Пропуск плейсхолдеров не считается ошибкой: отсутствующие значения не ломают отчёт и аккуратно игнорируются.

## Конфигурация
- `config.py` (Confluence/Grafana/Loki):
  - `user`, `password` — учётные данные Confluence;
  - `grafana_login`, `grafana_pass` — доступ к Grafana для рендера изображений;
  - `url_basic` — базовый URL Confluence;
  - `space_conf` — ключ пространства Confluence;
  - `grafana_base_url` — базовый URL Grafana для рендера `/render/d-solo/...`;
  - `loki_url` — endpoint Loki `.../loki/api/v1/query_range`.
- `metrics_config.py` (пер‑сервисная конфигурация):
  - `page_sample_id` — ID шаблонной страницы;
  - `page_parent_id` — ID родительской страницы, куда будет кладться копия;
  - `metrics[]` — список панелей Grafana: `{ name, grafana_url }` → плейсхолдер `$$name$$`;
  - `logs[]` — список логов: `{ placeholder, filter_query }` → плейсхолдер `$$placeholder$$`.
- `AI/config.py` (AI и источник метрик):
  - `prometheus.url` — адрес Prometheus;
  - `metrics_source.type` — `prometheus` или `grafana_proxy`;
  - при `grafana_proxy` — задайте `metrics_source.grafana.{base_url, verify_ssl, auth, prometheus_datasource}`;
  - `llm.provider=gigachat` и секция mTLS (`cert_file`, `key_file`, `verify`, `proxies`, таймауты);
  - доменные `queries` (PromQL), `default_params.step`, `default_params.resample_interval`.

## Установка и запуск
1. Установите Python 3.12+ и зависимости:
   ```bash
   pip install -r requirements.txt
   ```
2. Заполните `config.py`, `metrics_config.py`, `AI/config.py`.
3. Запустите приложение:
   ```bash
   python app.py
   ```
4. Откройте браузер: страница формы по адресу из консоли (по умолчанию `http://localhost:5000/`).
5. Либо вызовите REST `POST /create_report` (см. раздел «REST API»).

## Docker
Сборка и запуск:
```bash
docker build -t load-testing-auto-reports .
docker run --rm -p 5000:5000 \
  -v $(pwd)/AI/config.py:/app/AI/config.py \
  -v $(pwd)/config.py:/app/config.py \
  -v $(pwd)/metrics_config.py:/app/metrics_config.py \
  load-testing-auto-reports
```

## REST API
- `GET /services` — список доступных сервисов из `metrics_config.py`.
- `POST /create_report` — создание отчёта.
  - Тело запроса (JSON):
    ```json
    {
      "start": "2025-02-21T11:30",
      "end": "2025-02-21T14:10",
      "service": "NSI"
    }
    ```
  - Ответ: `{ status: "success" | "error", message: string }`.

## Примеры
- Пример соответствия метрики и плейсхолдера:
  - `metrics_config.py`: `{ "name": "RPS", "grafana_url": "/render/d-solo/...&panelId=17" }`
  - В шаблоне Confluence должен быть плейсхолдер `$$RPS$$`.
- Пример плейсхолдера логов:
  - `logs[].placeholder = "micro-registry-nsi"` → `$$micro-registry-nsi$$` в шаблоне.
- Пример блока AI (итог): будет подставлен в `$$answer_llm$$` и `$$final_answer$$`. Если в JSON LLM есть `peak_performance`, раздел «Пиковая производительность» будет выведен автоматически [[memory:8657199]].

## Безопасность и сеть
- Соединения к Confluence/Grafana/Loki используют простой HTTP(S); проверка сертификатов в некоторых вызовах отключена (`verify=False`). Настройте корпоративные сертификаты там, где это требуется.
- Для GigaChat включается mTLS: укажите `cert_file`, `key_file`, `verify` в `AI/config.py`.
- Не храните реальные пароли в репозитории. Используйте переменные окружения/секреты и монтирование конфигов в контейнер.

## Устранение неполадок
- «Плейсхолдер не найден»: проверьте, что в шаблоне есть `$$<name>$$` и он совпадает с `metrics[].name` или `logs[].placeholder`.
- Конфликт версий Confluence: оркестратор повторит попытку; при массовом редактировании избегайте ручных изменений страницы во время обновления.
- Grafana 401/403: проверьте `grafana_login/grafana_pass` и доступ к `/render/d-solo/...`.
- Loki ошибки: проверьте `loki_url` и корректность `filter_query`.
- LLM «insufficient_data»: означает, что для анализа не хватило данных; проверьте метрики за указанный интервал.

Подсистема AI описана подробно в `AI/README.md`.