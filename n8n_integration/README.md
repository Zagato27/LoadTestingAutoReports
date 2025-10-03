# 🚀 n8n Integration - Изолированный проект

**Полностью автономная система создания отчетов по нагрузочному тестированию на базе n8n + AI**

## ✨ Особенности

✅ **Полная изоляция** - все зависимости внутри директории  
✅ **Упрощенный workflow** - без Loki (только Grafana + AI)  
✅ **AI-анализ** - JVM, Database, Kafka, Microservices  
✅ **Docker контейнеризация** - docker-compose для всего стека  
✅ **Автоматизация** - скрипты развертывания и тестирования  

---

## 📁 Структура

```
n8n_integration/                    # ← ВСЁ ЗДЕСЬ (изолированно)
├── 🌟 Workflow
│   └── n8n_workflow_simple.json        # Упрощенный workflow (Grafana + AI)
│
├── 💻 AI-сервис
│   ├── ai_service_for_n8n.py           # Flask REST API
│   ├── AI/                             # AI-модуль (копия)
│   ├── confluence_manager/             # Confluence утилиты (копия)
│   └── config.py                       # Базовые настройки
│
├── 🐳 Docker
│   ├── docker-compose.yml              # Docker Compose
│   ├── Dockerfile                      # AI-сервис образ
│   ├── env.example.txt                 # Шаблон .env
│   └── requirements.txt                # Python зависимости
│
├── 🔧 Скрипты
│   ├── deploy_ai_service.sh            # Развертывание
│   └── test_ai_integration.sh          # Тестирование
│
└── 📚 Документация
    └── README.md (этот файл)
```

---

## 🚀 Быстрый старт

### 1. Подготовка (1 минута)

```bash
# Создайте .env
cp env.example.txt .env

# Отредактируйте .env
nano .env
```

**Обязательно настройте:**
```bash
POSTGRES_PASSWORD=your_secure_password
PROMETHEUS_URL=http://your-prometheus:9090
```

### 2. Настройка AI (1 минута)

Отредактируйте `AI/config.py`:

```python
CONFIG = {
    "prometheus": {
        "url": "http://prometheus:9090"
    },
    "llm": {
        "provider": "gigachat",
        "gigachat": {
            "model": "GigaChat-Pro",
            "base_url": "https://gigachat.devices.sberbank.ru/api/v1",
            "cert_file": "/app/certs/client.crt",
            "key_file": "/app/certs/client.key",
            # ...
        }
    },
    # ... остальная конфигурация
}
```

### 3. Запуск (2 минуты)

```bash
# Сделайте скрипты исполняемыми
chmod +x deploy_ai_service.sh test_ai_integration.sh

# Автоматическое развертывание
./deploy_ai_service.sh
```

### 4. Настройка n8n (2 минуты)

1. Откройте: **http://localhost:5678**

2. **Import workflow:**
   - Settings → Import from File
   - Выберите: `n8n_workflow_simple.json`

3. **Настройте Credentials:**
   
   **Confluence:**
   ```
   Тип: HTTP Basic Auth
   ID: confluence-creds
   Username: ваш_логин
   Password: ваш_пароль
   ```
   
   **Grafana:**
   ```
   Тип: HTTP Basic Auth
   ID: grafana-creds
   Username: grafana_login
   Password: grafana_password
   ```

4. **Обновите конфигурацию метрик** в узле "Get Service Config"

5. **Активируйте workflow** (кнопка "Active")

### 5. Тест

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
┌─────────────────────┐
│   n8n Workflow      │
│                     │
│  1. Copy page       │
│  2. Parallel:       │
│     ├─ Grafana ────┐│
│     └─ AI ─────────┤│
│                    ││
│  3. Merge      ◄───┘│
│  4. Update page     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  AI Microservice    │
│  (Flask REST API)   │
│                     │
│  /health            │
│  /analyze           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    ./AI/main.py     │
│                     │
│  - Prometheus       │
│  - GigaChat         │
│  - Analysis         │
└─────────────────────┘
```

**Что убрано по сравнению с оригиналом:**
- ❌ Loki логи
- ❌ Зависимости от родительских директорий

**Что осталось:**
- ✅ Grafana метрики
- ✅ AI-анализ (4 домена)
- ✅ Confluence интеграция
- ✅ Полная изоляция

---

## 📊 AI-анализ

AI автоматически анализирует:

### 1. JVM метрики
- Heap/Non-Heap память
- CPU процессов
- GC активность

### 2. Database метрики
- Активные подключения
- Времена запросов
- Блокировки

### 3. Kafka метрики
- Consumer lag
- Fetch rate
- Throughput

### 4. Microservices метрики
- RPS
- Response times
- Error rates

**Результат:** Структурированный отчет с выводами и рекомендациями

---

## ⚙️ Конфигурация

### Метрики

Откройте workflow в n8n → узел **"Get Service Config"**

```javascript
const METRICS_CONFIG = {
  "NSI": {
    "confluence_url": "https://confluence.company.com",
    "page_sample_id": "682908703",
    "page_parent_id": "882999920",
    "grafana_base_url": "http://grafana:3000",
    "metrics": [
      {
        "name": "RPS",
        "grafana_url": "/render/d-solo/..."
      },
      // ... добавьте все ваши метрики
    ]
  }
};
```

**Примечание:** Секция `logs` удалена (Loki не используется)

---

## 🔧 Управление

### Развертывание

```bash
./deploy_ai_service.sh          # Полное развертывание
./deploy_ai_service.sh check    # Проверка требований
./deploy_ai_service.sh build    # Сборка образов
./deploy_ai_service.sh start    # Запуск сервисов
./deploy_ai_service.sh stop     # Остановка
./deploy_ai_service.sh logs     # Логи AI-сервиса
```

### Тестирование

```bash
./test_ai_integration.sh        # Полный набор тестов
./test_ai_integration.sh quick  # Быстрая проверка
./test_ai_integration.sh ai-only # Только AI-сервис
```

### Docker Compose

```bash
# Запуск
docker-compose up -d

# Статус
docker-compose ps

# Логи
docker-compose logs -f ai-analyzer
docker-compose logs -f n8n

# Остановка
docker-compose down

# Полная очистка
docker-compose down -v
```

---

## 🐛 Troubleshooting

### AI-сервис не запускается

```bash
# Логи
docker-compose logs ai-analyzer

# Проверка конфигурации
curl http://localhost:5001/config/check | jq .

# Пересборка
docker-compose build ai-analyzer
docker-compose up -d ai-analyzer
```

### n8n недоступен

```bash
# Логи
docker-compose logs n8n

# Перезапуск
docker-compose restart n8n
```

### AI возвращает "insufficient_data"

Проблема: Нет метрик в Prometheus за указанный период

**Решение:**
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

---

## 📝 API

### Создание отчета

```bash
POST http://localhost:5678/webhook/load-testing/report/create

Body:
{
  "start": "2025-02-21T11:30",
  "end": "2025-02-21T14:10",
  "service": "NSI"
}
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

### AI-сервис

```bash
# Healthcheck
GET http://localhost:5001/health

# Конфигурация
GET http://localhost:5001/config/check

# Анализ
POST http://localhost:5001/analyze
Body: {"start": 1708513800000, "end": 1708523400000}
```

---

## ✅ Что реализовано

- ✅ n8n Workflow (упрощенный)
- ✅ AI-микросервис (изолированный)
- ✅ Grafana интеграция
- ✅ AI-анализ (4 домена)
- ✅ Docker контейнеризация
- ✅ Скрипты автоматизации
- ✅ Полная изоляция

## ❌ Что убрано

- ❌ Loki логи
- ❌ Зависимости от родительских директорий
- ❌ Сложные workflow с множеством узлов

---

## 🎉 Готово к использованию!

Все зависимости изолированы, проект полностью автономный.

**Следующие шаги:**
1. Настройте `.env`
2. Отредактируйте `AI/config.py`
3. Запустите `./deploy_ai_service.sh`
4. Импортируйте workflow в n8n
5. Создайте первый отчет!

Удачи! 🚀
