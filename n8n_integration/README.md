# 🚀 n8n Integration для Load Testing Auto Reports

Эта директория содержит все необходимое для развертывания системы создания отчетов по нагрузочному тестированию на базе **n8n workflow** с **AI-микросервисом**.

---

## 📋 Содержание директории

### 🌟 Workflow и код

| Файл | Описание |
|------|----------|
| **n8n_load_testing_workflow_with_ai.json** | ⭐ Основной workflow с AI-интеграцией |
| **n8n_load_testing_workflow.json** | Базовый workflow (без AI) |
| **ai_service_for_n8n.py** | Flask REST API для AI-анализа |

### 🐳 Docker

| Файл | Описание |
|------|----------|
| **docker-compose.n8n.yml** | Docker Compose для всего стека |
| **Dockerfile.ai_service** | Docker образ AI-сервиса |
| **env.example.txt** | Шаблон переменных окружения |

### 🔧 Скрипты

| Файл | Описание |
|------|----------|
| **deploy_ai_service.sh** | Автоматическое развертывание |
| **test_ai_integration.sh** | Автоматическое тестирование |

### 📚 Документация

| Файл | Для кого |
|------|----------|
| **START_HERE.md** | ⭐ **НАЧНИТЕ ОТСЮДА** |
| **QUICK_START_AI.md** | Быстрый старт за 5 минут |
| **AI_INTEGRATION_GUIDE.md** | Детальное руководство по AI |
| **README_N8N_MIGRATION.md** | Общая миграция на n8n |
| **N8N_MIGRATION_GUIDE.md** | Расширенная документация |
| **README_AI_FILES.md** | Список всех файлов |

---

## 🚀 Быстрый старт

### Шаг 1: Подготовка (1 минута)

```bash
cd n8n_integration

# Создайте .env из шаблона
cp env.example.txt .env

# Отредактируйте .env
nano .env
```

**Обязательные настройки:**
```bash
POSTGRES_PASSWORD=your_secure_password
PROMETHEUS_URL=http://your-prometheus:9090
GRAFANA_URL=http://your-grafana:3000
```

### Шаг 2: Запуск (2 минуты)

```bash
# Сделайте скрипты исполняемыми
chmod +x deploy_ai_service.sh test_ai_integration.sh

# Автоматическое развертывание
./deploy_ai_service.sh
```

### Шаг 3: Настройка n8n (2 минуты)

1. Откройте: **http://localhost:5678**

2. **Import workflow:**
   - Settings → Import from File
   - Выберите: `n8n_load_testing_workflow_with_ai.json`

3. **Настройте Credentials:**
   - Confluence (HTTP Basic Auth)
   - Grafana (HTTP Basic Auth)

4. **Активируйте workflow** (кнопка "Active")

### Шаг 4: Тест

```bash
# Быстрая проверка
./test_ai_integration.sh quick

# Создание отчета
curl -X POST http://localhost:5678/webhook/load-testing/report/create \
  -H "Content-Type: application/json" \
  -d '{
    "start": "2025-02-21T11:30",
    "end": "2025-02-21T14:10",
    "service": "NSI"
  }'
```

---

## 🎯 Архитектура

```
┌──────────┐
│  Клиент  │
└────┬─────┘
     │
     ▼
┌──────────────────────────────┐
│      n8n Workflow            │
│                              │
│  1. Copy Confluence page     │
│  2. Parallel execution:      │
│     ├─ Grafana metrics ─────┐│
│     ├─ Loki logs       ─────┤│
│     └─ AI analysis     ─────┤│
│                             ││
│  3. Merge all results  ◄────┘│
│  4. Update Confluence page   │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│    AI Analyzer Service       │
│    (ai_service_for_n8n.py)   │
│                              │
│  Flask REST API (Port 5001)  │
│                              │
│  Endpoints:                  │
│  - GET  /health              │
│  - GET  /config/check        │
│  - POST /analyze             │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│    ../AI/main.py             │
│    (Existing AI module)      │
│                              │
│  - Prometheus queries        │
│  - GigaChat LLM              │
│  - Domain analysis           │
└──────────────────────────────┘
```

---

## 📊 Что делает система

### Сбор данных (параллельно)

1. **Grafana:**
   - Загружает изображения панелей
   - Прикрепляет как вложения в Confluence
   - Заменяет плейсхолдеры `$$metric_name$$`

2. **Loki:**
   - Собирает логи ERROR за период
   - Сохраняет в `.log` файлы
   - Прикрепляет в Confluence
   - Заменяет плейсхолдеры `$$service_name$$`

3. **AI-анализ:**
   - Загружает метрики из Prometheus
   - Анализирует 4 домена:
     * JVM (память, CPU, GC)
     * Database (подключения, запросы)
     * Kafka (consumer lag, throughput)
     * Microservices (RPS, response times)
   - Генерирует выводы и рекомендации
   - Заменяет плейсхолдеры `$$answer_jvm$$`, `$$answer_database$$`, и т.д.

### Финальное обновление

Все плейсхолдеры заменяются **одним проходом**, страница обновляется и возвращается ссылка на готовый отчет.

---

## 🔧 Управление сервисами

### Развертывание

```bash
./deploy_ai_service.sh          # Полное развертывание
./deploy_ai_service.sh check    # Проверка требований
./deploy_ai_service.sh build    # Сборка образов
./deploy_ai_service.sh start    # Запуск сервисов
./deploy_ai_service.sh stop     # Остановка
./deploy_ai_service.sh restart  # Перезапуск AI-сервиса
./deploy_ai_service.sh logs     # Просмотр логов
./deploy_ai_service.sh clean    # Полная очистка
```

### Тестирование

```bash
./test_ai_integration.sh        # Полный набор тестов (7 проверок)
./test_ai_integration.sh quick  # Быстрая проверка
./test_ai_integration.sh ai-only # Только AI-сервис
```

### Docker Compose

```bash
# Запуск
docker-compose -f docker-compose.n8n.yml up -d

# Статус
docker-compose -f docker-compose.n8n.yml ps

# Логи
docker-compose -f docker-compose.n8n.yml logs -f ai-analyzer
docker-compose -f docker-compose.n8n.yml logs -f n8n

# Остановка
docker-compose -f docker-compose.n8n.yml down

# Полная очистка (с volumes)
docker-compose -f docker-compose.n8n.yml down -v
```

---

## 📝 Конфигурация

### Метрики и логи

Откройте workflow в n8n → узел **"Get Service Config"**

Обновите `METRICS_CONFIG`:

```javascript
const METRICS_CONFIG = {
  "NSI": {
    "confluence_url": "https://confluence.company.com",
    "page_sample_id": "682908703",
    "page_parent_id": "882999920",
    "grafana_base_url": "http://grafana:3000",
    "loki_url": "http://loki:3000/loki/api/v1/query_range",
    "metrics": [
      {
        "name": "RPS",
        "grafana_url": "/render/d-solo/dashboard/..."
      }
      // ... добавьте все ваши метрики
    ],
    "logs": [
      {
        "placeholder": "service-name",
        "filter_query": '{namespace="apps"} |= "ERROR"'
      }
      // ... добавьте все ваши логи
    ]
  }
};
```

### AI-конфигурация

Отредактируйте `../AI/config.py`:

```python
CONFIG = {
    "prometheus": {
        "url": "http://prometheus:9090"
    },
    "llm": {
        "provider": "gigachat",
        "gigachat": {
            "model": "GigaChat-Pro",
            "cert_file": "/app/certs/client.crt",
            "key_file": "/app/certs/client.key",
            # ...
        }
    }
}
```

---

## 🐛 Troubleshooting

### AI-сервис не запускается

```bash
# Логи
docker-compose -f docker-compose.n8n.yml logs ai-analyzer

# Проверка конфигурации
curl http://localhost:5001/config/check | jq .

# Пересборка
docker-compose -f docker-compose.n8n.yml build ai-analyzer
docker-compose -f docker-compose.n8n.yml up -d ai-analyzer
```

### n8n недоступен

```bash
# Логи
docker-compose -f docker-compose.n8n.yml logs n8n

# Перезапуск
docker-compose -f docker-compose.n8n.yml restart n8n

# Проверка портов
netstat -an | grep 5678
```

### AI возвращает "insufficient_data"

```bash
# Проверка Prometheus
curl http://prometheus:9090/api/v1/query?query=up

# Проверка метрик за период
curl "http://prometheus:9090/api/v1/query_range?\
query=jvm_memory_used_bytes&\
start=1708513800&\
end=1708523400&\
step=60" | jq .
```

Больше информации: [AI_INTEGRATION_GUIDE.md](AI_INTEGRATION_GUIDE.md) → раздел Troubleshooting

---

## 📚 Полная документация

1. **[START_HERE.md](START_HERE.md)** ⭐ - начните отсюда
2. **[QUICK_START_AI.md](QUICK_START_AI.md)** - быстрый старт
3. **[AI_INTEGRATION_GUIDE.md](AI_INTEGRATION_GUIDE.md)** - детальное руководство
4. **[README_N8N_MIGRATION.md](README_N8N_MIGRATION.md)** - миграция с Python
5. **[README_AI_FILES.md](README_AI_FILES.md)** - список всех файлов

---

## ✅ Что работает

- ✅ n8n Workflow с 27 узлами
- ✅ AI-микросервис (Flask REST API)
- ✅ Docker контейнеризация
- ✅ Параллельная обработка (Grafana + Loki + AI)
- ✅ Автоматические скрипты развертывания
- ✅ Автоматические тесты
- ✅ Полная документация

---

## 🎉 Готово к использованию!

Откройте **[START_HERE.md](START_HERE.md)** и следуйте инструкциям.

Удачи! 🚀

---

## 📞 Поддержка

- **Быстрый старт:** [QUICK_START_AI.md](QUICK_START_AI.md)
- **Troubleshooting:** [AI_INTEGRATION_GUIDE.md](AI_INTEGRATION_GUIDE.md)
- **Все файлы:** [README_AI_FILES.md](README_AI_FILES.md)

