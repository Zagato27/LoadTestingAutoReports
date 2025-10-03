# Руководство по интеграции AI-сервиса с n8n

## 📋 Содержание
1. [Архитектура](#архитектура)
2. [Установка AI-сервиса](#установка-ai-сервиса)
3. [Настройка в n8n](#настройка-в-n8n)
4. [Тестирование](#тестирование)
5. [Troubleshooting](#troubleshooting)

## 🏗️ Архитектура

```
┌─────────────────┐
│   n8n Workflow  │
│                 │
│  1. Copy page   │
│  2. Start parallel:
│     ├─ Grafana  │──┐
│     ├─ Loki     │──┤
│     └─ AI       │──┤
│                 │  │
│  3. Merge all   │◄─┘
│  4. Update page │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  AI Microservice│
│                 │
│  Flask REST API │
│  Port: 5001     │
│                 │
│  /analyze       │
│  /health        │
│  /config/check  │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   AI/main.py    │
│                 │
│  - Prometheus   │
│  - GigaChat     │
│  - Analysis     │
└─────────────────┘
```

## 📦 Установка AI-сервиса

### Вариант 1: Docker (рекомендуется)

#### 1. Подготовьте конфигурацию

Убедитесь, что файлы конфигурации настроены:

**AI/config.py:**
```python
CONFIG = {
    "prometheus": {
        "url": "http://prometheus.company.com:9090"
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
            "verify": "/app/certs/ca.crt",
            "request_timeout_sec": 120,
            "generation": {
                "temperature": 0.2,
                "top_p": 0.9,
                "max_tokens": 1200,
                "force_json_in_prompt": True
            }
        }
    },
    "default_params": {
        "step": "1m",
        "resample_interval": "1min"
    },
    "queries": {
        "jvm": {
            "promql_queries": [
                'jvm_memory_used_bytes{area="heap"}',
                'process_cpu_usage'
            ],
            "label_keys_list": [
                ["application", "instance"],
                ["application", "instance"]
            ],
            "labels": ["Heap Memory Used", "CPU Usage"]
        },
        "database": {
            "promql_queries": [
                'hikaricp_connections_active',
                'hikaricp_connections_pending'
            ],
            "label_keys_list": [
                ["pool", "application"],
                ["pool", "application"]
            ],
            "labels": ["Active Connections", "Pending Connections"]
        },
        "kafka": {
            "promql_queries": [
                'kafka_consumer_lag',
                'kafka_consumer_fetch_rate'
            ],
            "label_keys_list": [
                ["consumer_group", "topic"],
                ["consumer_group", "topic"]
            ],
            "labels": ["Consumer Lag", "Fetch Rate"]
        },
        "microservices": {
            "promql_queries": [
                'http_server_requests_seconds_count',
                'http_server_requests_seconds_sum'
            ],
            "label_keys_list": [
                ["application", "uri", "method"],
                ["application", "uri", "method"]
            ],
            "labels": ["Request Count", "Response Time Sum"]
        }
    }
}
```

#### 2. Подготовьте сертификаты (если используется mTLS)

```bash
mkdir -p certs
# Скопируйте ваши сертификаты
cp /path/to/client.crt certs/
cp /path/to/client.key certs/
cp /path/to/ca.crt certs/
```

#### 3. Запустите через Docker Compose

```bash
# Запустите весь стек (n8n + AI-сервис)
docker-compose -f docker-compose.n8n.yml up -d

# Проверьте статус
docker-compose -f docker-compose.n8n.yml ps

# Проверьте логи AI-сервиса
docker-compose -f docker-compose.n8n.yml logs -f ai-analyzer
```

#### 4. Проверьте работу AI-сервиса

```bash
# Healthcheck
curl http://localhost:5001/health
# Ожидаемый ответ: {"status": "healthy"}

# Проверка конфигурации
curl http://localhost:5001/config/check
# Покажет текущие настройки Prometheus, LLM и т.д.
```

### Вариант 2: Локальный запуск (для разработки)

```bash
# 1. Установите зависимости
pip install -r requirements.txt

# 2. Настройте переменные окружения (опционально)
export AI_SERVICE_HOST=0.0.0.0
export AI_SERVICE_PORT=5001
export AI_SERVICE_DEBUG=true

# 3. Запустите сервис
python ai_service_for_n8n.py

# Сервис будет доступен на http://localhost:5001
```

## ⚙️ Настройка в n8n

### 1. Импорт обновленного workflow

```bash
# Используйте новый файл с AI-интеграцией
# В n8n: Settings → Import from File → 
# Выберите: n8n_load_testing_workflow_with_ai.json
```

### 2. Проверьте узел "Call AI Analyzer"

Откройте workflow в n8n и найдите узел **"Call AI Analyzer"**:

**Настройки узла:**
- **Method:** POST
- **URL:** `http://ai-analyzer:5001/analyze` (если через Docker)
  - Для локального: `http://localhost:5001/analyze`
  - Для продакшена: `http://your-ai-service.company.com:5001/analyze`
- **Body:** JSON
```json
{
  "start": {{ $('Parse Input').item.json.start_timestamp }},
  "end": {{ $('Parse Input').item.json.end_timestamp }}
}
```
- **Timeout:** 300000 (5 минут)

### 3. Архитектура workflow с AI

Workflow выполняется параллельно:

```
Copy Page
   ├─► Metrics (Grafana) ──┐
   ├─► Logs (Loki)      ──┤
   └─► AI Analysis      ──┤
                          │
                          ▼
                    Merge All
                          │
                          ▼
                  Update Page (один проход)
```

### 4. Структура AI-ответа

AI-сервис возвращает:

```json
{
  "status": "success",
  "data": {
    "raw_results": {
      "jvm": "текст анализа JVM",
      "database": "текст анализа DB",
      "kafka": "текст анализа Kafka",
      "ms": "текст анализа Microservices",
      "final": "итоговый вывод"
    },
    "placeholders": {
      "$$answer_jvm$$": "<h3>JVM Analysis</h3><p>...</p>",
      "$$answer_database$$": "<h3>Database Analysis</h3><p>...</p>",
      "$$answer_kafka$$": "<h3>Kafka Analysis</h3><p>...</p>",
      "$$answer_ms$$": "<h3>Microservices Analysis</h3><p>...</p>",
      "$$answer_llm$$": "<h3>Overall Findings</h3><p>...</p>",
      "$$final_answer$$": "<h3>Final Recommendations</h3><p>...</p>"
    },
    "structured": {
      "jvm_parsed": {
        "verdict": "acceptable",
        "confidence": 0.85,
        "findings": [...],
        "recommended_actions": [...]
      },
      ...
    }
  }
}
```

## 🧪 Тестирование

### 1. Тест AI-сервиса независимо

```bash
# Простой тест анализа
curl -X POST http://localhost:5001/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "start": 1708513800000,
    "end": 1708523400000
  }' | jq .

# Ожидаемый ответ:
# {
#   "status": "success",
#   "data": {
#     "placeholders": { ... },
#     ...
#   }
# }
```

### 2. Тест конкретного домена

```bash
# Анализ только JVM
curl -X POST http://localhost:5001/analyze/domain/jvm \
  -H "Content-Type: application/json" \
  -d '{
    "start": 1708513800000,
    "end": 1708523400000
  }' | jq .
```

### 3. Полный тест через n8n

```bash
# Вызов полного workflow
curl -X POST http://localhost:5678/webhook/load-testing/report/create \
  -H "Content-Type: application/json" \
  -d '{
    "start": "2025-02-21T11:30",
    "end": "2025-02-21T14:10",
    "service": "NSI"
  }' | jq .

# Ожидаемый ответ:
# {
#   "status": "success",
#   "message": "Report created successfully",
#   "page_id": "123456789",
#   "page_url": "https://confluence.../viewpage.action?pageId=123456789",
#   ...
# }
```

### 4. Проверка результата в Confluence

1. Откройте ссылку из `page_url`
2. Проверьте наличие разделов:
   - Графики из Grafana
   - Логи из Loki
   - **AI-анализ:**
     - $$answer_jvm$$ → Анализ JVM
     - $$answer_database$$ → Анализ БД
     - $$answer_kafka$$ → Анализ Kafka
     - $$answer_ms$$ → Анализ микросервисов
     - $$final_answer$$ → Итоговые выводы

## 🔧 Troubleshooting

### AI-сервис не запускается

**Проблема:** `ModuleNotFoundError: No module named 'AI'`

**Решение:**
```bash
# Проверьте структуру директорий
ls -la AI/
# Должны быть: __init__.py, main.py, config.py, prompts/

# Пересоберите контейнер
docker-compose -f docker-compose.n8n.yml build ai-analyzer
docker-compose -f docker-compose.n8n.yml up -d ai-analyzer
```

**Проблема:** Ошибка сертификатов mTLS

**Решение:**
```bash
# Проверьте наличие сертификатов
docker-compose -f docker-compose.n8n.yml exec ai-analyzer ls -la /app/certs/

# Проверьте права доступа
docker-compose -f docker-compose.n8n.yml exec ai-analyzer cat /app/certs/client.crt

# Если файлы не смонтированы, проверьте docker-compose.n8n.yml:
# volumes:
#   - ./certs:/app/certs:ro
```

### AI-анализ возвращает ошибку

**Проблема:** `"status": "error", "message": "AI analysis failed: ..."`

**Диагностика:**
```bash
# Проверьте логи
docker-compose -f docker-compose.n8n.yml logs ai-analyzer | tail -100

# Проверьте конфигурацию
curl http://localhost:5001/config/check | jq .

# Проверьте доступность Prometheus
docker-compose -f docker-compose.n8n.yml exec ai-analyzer \
  curl -v http://prometheus:9090/api/v1/query?query=up

# Проверьте доступность GigaChat
docker-compose -f docker-compose.n8n.yml exec ai-analyzer \
  python -c "from AI.main import _gigachat_preflight; _gigachat_preflight({})"
```

**Проблема:** Timeout при вызове AI

**Решение:**
```bash
# Увеличьте timeout в n8n узле "Call AI Analyzer"
# Options → Timeout → 600000 (10 минут)

# Или в AI/config.py увеличьте:
# "request_timeout_sec": 300
```

### AI-плейсхолдеры не заменяются

**Проблема:** В Confluence остаются `$$answer_jvm$$` без замены

**Диагностика:**
```bash
# Проверьте, что AI-сервис вернул placeholders
# В n8n посмотрите выполнение узла "Process AI Results"
# Должен быть массив с placeholder и replacement

# Проверьте в шаблоне Confluence наличие плейсхолдеров
# Они должны точно совпадать: $$answer_jvm$$ (без пробелов)
```

**Решение:**
1. Откройте шаблонную страницу в Confluence
2. Убедитесь, что плейсхолдеры присутствуют:
   ```
   <h2>JVM Analysis</h2>
   $$answer_jvm$$
   
   <h2>Database Analysis</h2>
   $$answer_database$$
   
   <h2>Kafka Analysis</h2>
   $$answer_kafka$$
   
   <h2>Microservices Analysis</h2>
   $$answer_ms$$
   
   <h2>Final Recommendations</h2>
   $$final_answer$$
   ```
3. Сохраните и повторите запуск workflow

### Недостаточно данных для анализа

**Проблема:** `"verdict": "insufficient_data"`

**Причины и решения:**

1. **Нет метрик в Prometheus:**
```bash
# Проверьте наличие метрик за период
curl "http://prometheus:9090/api/v1/query_range?\
query=jvm_memory_used_bytes&\
start=1708513800&\
end=1708523400&\
step=60" | jq .
```

2. **Неправильные PromQL запросы:**
```python
# Проверьте AI/config.py → queries
# Убедитесь, что имена метрик совпадают с Prometheus
```

3. **Слишком короткий период:**
```bash
# Используйте период минимум 10-15 минут
# start и end должны отличаться минимум на 600000 мс (10 мин)
```

### Проблемы с производительностью

**Проблема:** AI-анализ занимает > 5 минут

**Оптимизация:**

1. **Уменьшите step в AI/config.py:**
```python
"default_params": {
    "step": "2m",  # вместо "1m"
    "resample_interval": "2min"
}
```

2. **Ограничьте топ-N серий:**
```python
# В AI/main.py функция uploadFromLLM:
top_n=10  # вместо 15
```

3. **Используйте кеширование (будущая оптимизация):**
```python
# Добавьте Redis для кеширования результатов анализа
# за одинаковые периоды
```

## 📊 Мониторинг AI-сервиса

### Метрики для отслеживания

```bash
# Проверка здоровья каждые 30 сек
watch -n 30 'curl -s http://localhost:5001/health | jq .'

# Логи в реальном времени
docker-compose -f docker-compose.n8n.yml logs -f --tail=100 ai-analyzer

# Использование ресурсов
docker stats ai-analyzer
```

### Алерты (для Prometheus)

Если у вас настроен Prometheus, добавьте алерты:

```yaml
# prometheus_alerts.yml
groups:
  - name: ai_service
    interval: 30s
    rules:
      - alert: AIServiceDown
        expr: up{job="ai-analyzer"} == 0
        for: 1m
        annotations:
          summary: "AI Analyzer service is down"
      
      - alert: AIServiceSlowResponse
        expr: http_request_duration_seconds{job="ai-analyzer"} > 300
        for: 5m
        annotations:
          summary: "AI Analyzer responses are slow (>5min)"
```

## 🚀 Оптимизация для продакшена

### 1. Масштабирование

```yaml
# docker-compose.n8n.yml
services:
  ai-analyzer:
    # ...
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### 2. Балансировка нагрузки

```nginx
# nginx.conf
upstream ai_backend {
    server ai-analyzer-1:5001;
    server ai-analyzer-2:5001;
    server ai-analyzer-3:5001;
}

server {
    location /ai/ {
        proxy_pass http://ai_backend/;
        proxy_timeout 600s;
    }
}
```

### 3. Кеширование результатов

```python
# Добавьте в ai_service_for_n8n.py
import redis
import hashlib
import json

redis_client = redis.Redis(host='redis', port=6379, db=0)

def get_cache_key(start, end):
    return f"ai_analysis:{start}:{end}"

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    start = data.get('start')
    end = data.get('end')
    
    # Проверяем кеш
    cache_key = get_cache_key(start, end)
    cached = redis_client.get(cache_key)
    if cached:
        logger.info(f"Returning cached result for {cache_key}")
        return jsonify(json.loads(cached)), 200
    
    # Выполняем анализ
    results = uploadFromLLM(start/1000, end/1000)
    
    # Кешируем на 1 час
    redis_client.setex(cache_key, 3600, json.dumps(results))
    
    return jsonify({"status": "success", "data": results}), 200
```

## 📚 Дополнительные ресурсы

- [AI/README.md](AI/README.md) - документация AI-модуля
- [ai_service_for_n8n.py](ai_service_for_n8n.py) - исходный код сервиса
- [N8N_MIGRATION_GUIDE.md](N8N_MIGRATION_GUIDE.md) - общее руководство
- [README_N8N_MIGRATION.md](README_N8N_MIGRATION.md) - быстрый старт

## 🤝 Поддержка

При возникновении проблем:
1. Проверьте раздел [Troubleshooting](#troubleshooting)
2. Изучите логи: `docker-compose logs ai-analyzer`
3. Проверьте конфигурацию: `curl http://localhost:5001/config/check`
4. Обратитесь к команде разработки с логами и описанием проблемы

