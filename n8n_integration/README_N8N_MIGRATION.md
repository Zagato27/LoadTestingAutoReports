# Миграция Load Testing Auto Reports на n8n

## 📋 Содержание
1. [Обзор](#обзор)
2. [Архитектура](#архитектура)
3. [Быстрый старт](#быстрый-старт)
4. [Детальная настройка](#детальная-настройка)
5. [Использование](#использование)
6. [Troubleshooting](#troubleshooting)

## 🎯 Обзор

Перенесен функционал Python Flask-приложения для автоматического создания отчетов по нагрузочному тестированию в n8n workflow.

### Что было реализовано:

✅ **Полностью перенесено:**
- Прием параметров (start, end, service)
- Копирование шаблонных страниц Confluence
- Загрузка графиков из Grafana
- Сбор логов из Loki
- Обновление плейсхолдеров в Confluence
- Обработка ошибок и валидация

✅ **AI-анализ (отдельный микросервис):**
- Анализ метрик из Prometheus
- Доменные аналитики (JVM, Database, Kafka, Microservices)
- Итоговые выводы и рекомендации
- Форматирование в markdown для Confluence

## 🏗️ Архитектура

```
┌──────────────┐
│   Клиент     │
│ (REST API)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│              │     │              │
│     n8n      │────▶│ AI Analyzer  │
│   Workflow   │     │  Microservice│
│              │     │              │
└──────┬───────┘     └──────┬───────┘
       │                    │
       │                    │
       ▼                    ▼
┌──────────────┐     ┌──────────────┐
│  Confluence  │     │ Prometheus/  │
│   + Grafana  │     │   GigaChat   │
│   + Loki     │     │              │
└──────────────┘     └──────────────┘
```

### Компоненты:

1. **n8n Workflow** (`n8n_load_testing_workflow.json`)
   - Оркестрация всего процесса
   - Работа с Confluence, Grafana, Loki
   - Обновление страниц

2. **AI Analyzer Microservice** (`ai_service_for_n8n.py`)
   - Анализ метрик через LLM
   - Генерация выводов и рекомендаций
   - REST API для интеграции с n8n

## 🚀 Быстрый старт

### Вариант 1: Docker Compose (рекомендуется)

```bash
# 1. Клонируйте репозиторий
git clone <repo_url>
cd LoadTestingAutoReports

# 2. Подготовьте конфигурацию
cp env.example.txt .env
# Отредактируйте .env файл

# 3. Запустите стек
docker-compose -f docker-compose.n8n.yml up -d

# 4. Откройте n8n
open http://localhost:5678

# 5. Импортируйте workflow
# В n8n: Settings → Import from File → выберите n8n_load_testing_workflow.json
```

### Вариант 2: Ручная установка

```bash
# 1. Установите n8n
npm install n8n -g

# 2. Запустите n8n
n8n start

# 3. В другом терминале запустите AI-сервис
python ai_service_for_n8n.py

# 4. Импортируйте workflow в n8n UI
```

## ⚙️ Детальная настройка

### 1. Настройка n8n Credentials

После импорта workflow настройте credentials:

#### Confluence Credentials
```
Тип: HTTP Basic Auth
Name: Confluence Credentials
Username: ваш_логин
Password: ваш_пароль_или_токен
```

#### Grafana Credentials
```
Тип: HTTP Basic Auth  
Name: Grafana Credentials
Username: grafana_login
Password: grafana_password
```

### 2. Настройка конфигурации метрик

Откройте узел **"Get Service Config"** в workflow и обновите `METRICS_CONFIG`:

```javascript
const METRICS_CONFIG = {
  "NSI": {
    "confluence_url": "https://confluence.sberbank.ru",
    "page_sample_id": "682908703",  // ID шаблона
    "page_parent_id": "882999920",   // ID родительской страницы
    "grafana_base_url": "http://grafana.url:3000",
    "loki_url": "http://loki.url/loki/api/v1/query_range",
    "metrics": [
      {
        "name": "RPS",
        "grafana_url": "/render/d-solo/XKhgaUpikugieq/k6-load-testing-results?orgId=1&panelId=17&width=1000&height=500&tz=Europe%2FMoscow"
      },
      {
        "name": "ResponseTimeTable",
        "grafana_url": "/render/d-solo/XKhgaUpikugieq/k6-load-testing-results?orgId=1&panelId=67&width=1000&height=900&tz=Europe%2FMoscow"
      }
      // ... добавьте остальные метрики из metrics_config.py
    ],
    "logs": [
      {
        "placeholder": "micro-registry-nsi",
        "filter_query": '{namespace=~"apps", service_name=~"micro-registry-nsi"} |= "ERROR"'
      }
      // ... добавьте остальные логи
    ]
  },
  // Добавьте другие сервисы по аналогии
  "service_2": {
    // ...
  }
};
```

### 3. Настройка AI Analyzer

Убедитесь, что файлы `AI/config.py` и `config.py` содержат правильные настройки:

```python
# AI/config.py
CONFIG = {
    "prometheus": {
        "url": "http://prometheus:9090"
    },
    "metrics_source": {
        "type": "prometheus"  # или "grafana_proxy"
    },
    "llm": {
        "provider": "gigachat",
        "gigachat": {
            "model": "GigaChat-Pro",
            "base_url": "https://gigachat.devices.sberbank.ru/api/v1",
            "cert_file": "/app/certs/client.crt",
            "key_file": "/app/certs/client.key",
            # ... другие настройки
        }
    }
}
```

### 4. Интеграция AI-сервиса в n8n

В workflow уже добавлены узлы для AI, но вам нужно:

1. Откройте workflow в n8n
2. Найдите узел "Call AI Analyzer" (или создайте новый HTTP Request узел)
3. Настройте:
   ```
   Method: POST
   URL: http://ai-analyzer:5001/analyze
   Body: JSON
   {
     "start": {{ $('Parse Input').item.json.start_timestamp }},
     "end": {{ $('Parse Input').item.json.end_timestamp }}
   }
   ```

## 📊 Использование

### REST API

#### Создание отчета

```bash
curl -X POST http://localhost:5678/webhook/load-testing/report/create \
  -H "Content-Type: application/json" \
  -d '{
    "start": "2025-02-21T11:30",
    "end": "2025-02-21T14:10",
    "service": "NSI"
  }'
```

**Успешный ответ:**
```json
{
  "status": "success",
  "message": "Report created successfully",
  "page_id": "123456789",
  "page_url": "https://confluence.../viewpage.action?pageId=123456789",
  "service": "NSI",
  "start": 1708513800000,
  "end": 1708523400000
}
```

**Ответ при ошибке:**
```json
{
  "status": "error",
  "message": "Missing required parameters: start, end, service"
}
```

### Проверка AI-сервиса

```bash
# Healthcheck
curl http://localhost:5001/health

# Проверка конфигурации
curl http://localhost:5001/config/check

# Тестовый анализ
curl -X POST http://localhost:5001/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "start": 1708513800000,
    "end": 1708523400000
  }'
```

## 🔧 Troubleshooting

### n8n не запускается

```bash
# Проверьте логи
docker-compose -f docker-compose.n8n.yml logs n8n

# Проверьте порты
netstat -an | grep 5678

# Пересоздайте контейнер
docker-compose -f docker-compose.n8n.yml up -d --force-recreate n8n
```

### AI-сервис не отвечает

```bash
# Проверьте логи
docker-compose -f docker-compose.n8n.yml logs ai-analyzer

# Проверьте healthcheck
curl http://localhost:5001/health

# Проверьте конфигурацию
curl http://localhost:5001/config/check
```

### Ошибки при загрузке из Grafana

1. **401 Unauthorized:**
   - Проверьте credentials в n8n
   - Убедитесь, что используется правильный логин/пароль

2. **404 Not Found:**
   - Проверьте URL панелей в METRICS_CONFIG
   - Убедитесь, что панели существуют

3. **Timeout:**
   - Проверьте доступность Grafana
   - Увеличьте timeout в настройках HTTP Request узла

### Ошибки при работе с Confluence

1. **Плейсхолдер не найден:**
   - Проверьте, что в шаблоне есть `$$название$$`
   - Проверьте точное совпадение имен метрик

2. **Конфликт версий:**
   - n8n автоматически повторяет попытку
   - Убедитесь, что страница не редактируется вручную во время обновления

3. **Изображения не отображаются:**
   - Проверьте, что файлы загружены как вложения
   - Проверьте синтаксис `<ac:image>` тега

### Ошибки AI-анализа

1. **"insufficient_data":**
   - Проверьте наличие метрик в Prometheus за указанный период
   - Проверьте PromQL запросы в AI/config.py

2. **Timeout при вызове LLM:**
   - Увеличьте таймауты в AI/config.py
   - Проверьте доступность GigaChat API
   - Проверьте mTLS сертификаты

3. **Ошибки парсинга JSON:**
   - Обновите промпты в `AI/prompts/`
   - Проверьте, что модель возвращает валидный JSON

## 📈 Мониторинг и логи

### n8n

```bash
# Логи выполнения
# UI: Executions → выберите workflow → View execution

# Логи контейнера
docker-compose -f docker-compose.n8n.yml logs -f n8n
```

### AI Analyzer

```bash
# Логи контейнера
docker-compose -f docker-compose.n8n.yml logs -f ai-analyzer

# Статус
curl http://localhost:5001/health
```

## 🔄 Миграция с Python сервиса

### Переключение трафика

1. **Тестирование:**
   ```bash
   # Старый сервис
   curl http://old-service:5000/create_report

   # Новый n8n workflow
   curl http://n8n:5678/webhook/load-testing/report/create
   ```

2. **Параллельный запуск:**
   - Запустите оба сервиса параллельно
   - Переключайте клиентов постепенно
   - Сравнивайте результаты

3. **Полное переключение:**
   - Обновите DNS/балансировщик
   - Остановите старый сервис
   - Мониторьте ошибки

### Откат (если нужно)

```bash
# Вернитесь к старому сервису
docker-compose up -d

# Или через балансировщик переключите трафик обратно
```

## 📝 Дополнительные материалы

- [N8N_MIGRATION_GUIDE.md](N8N_MIGRATION_GUIDE.md) - детальное руководство
- [ai_service_for_n8n.py](ai_service_for_n8n.py) - код AI-микросервиса
- [n8n_load_testing_workflow.json](n8n_load_testing_workflow.json) - workflow
- [docker-compose.n8n.yml](docker-compose.n8n.yml) - Docker Compose конфигурация

## 🤝 Поддержка

При возникновении вопросов или проблем:
1. Проверьте [Troubleshooting](#troubleshooting)
2. Изучите логи сервисов
3. Обратитесь к команде разработки

## 📄 Лицензия

Внутренний проект компании.

