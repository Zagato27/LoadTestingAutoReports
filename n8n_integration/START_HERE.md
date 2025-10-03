# 🎯 НАЧНИТЕ ОТСЮДА

## Реализован вариант 1: Отдельный Python-сервис для AI ✅

Ваш функционал Load Testing Auto Reports успешно перенесен в **n8n workflow** с полной интеграцией **AI-микросервиса**!

---

## 📦 Что создано

### 🌟 Основные файлы

1. **`n8n_load_testing_workflow_with_ai.json`** ⭐
   - Полный workflow с AI-интеграцией
   - 27 узлов, параллельная обработка
   - Готов к импорту в n8n

2. **`ai_service_for_n8n.py`** ⭐
   - REST API для AI-анализа
   - Использует существующий AI/main.py
   - Порт 5001

3. **`docker-compose.n8n.yml`** ⭐
   - Полный стек: n8n + AI + PostgreSQL
   - Готовый к запуску

### 🚀 Скрипты развертывания

4. **`deploy_ai_service.sh`** ⭐
   - Автоматическое развертывание
   - Проверка требований
   - Управление сервисами

5. **`test_ai_integration.sh`** ⭐
   - Автоматические тесты
   - 7 проверок системы
   - Цветной вывод результатов

### 📚 Документация

6. **`QUICK_START_AI.md`** - Старт за 5 минут
7. **`AI_INTEGRATION_GUIDE.md`** - Детальное руководство
8. **`README_N8N_MIGRATION.md`** - Миграция с Python
9. **`N8N_MIGRATION_GUIDE.md`** - Расширенная документация
10. **`README_AI_FILES.md`** - Список всех файлов

### 🐳 Docker

11. **`Dockerfile.ai_service`** - Образ AI-сервиса
12. **`env.example.txt`** - Шаблон переменных

---

## 🚀 Быстрый старт (5 минут)

### Шаг 1: Подготовка

```bash
# Создайте .env
cp env.example.txt .env

# Отредактируйте .env (ОБЯЗАТЕЛЬНО!)
nano .env
```

**Минимальные настройки в .env:**
```bash
POSTGRES_PASSWORD=your_secure_password
PROMETHEUS_URL=http://your-prometheus:9090
GRAFANA_URL=http://your-grafana:3000
```

### Шаг 2: Запуск

```bash
# Сделайте скрипты исполняемыми (если еще не сделали)
chmod +x deploy_ai_service.sh test_ai_integration.sh

# Автоматическое развертывание
./deploy_ai_service.sh
```

### Шаг 3: Настройка n8n

1. Откройте: **http://localhost:5678**

2. **Import workflow:**
   - Settings → Import from File
   - Выберите: `n8n_load_testing_workflow_with_ai.json`

3. **Настройте Credentials:**
   
   **Confluence:**
   - Тип: HTTP Basic Auth
   - ID: `confluence-creds`
   - Username: ваш_логин
   - Password: ваш_пароль

   **Grafana:**
   - Тип: HTTP Basic Auth
   - ID: `grafana-creds`
   - Username: grafana_login
   - Password: grafana_password

4. **Активируйте workflow** (кнопка "Active")

### Шаг 4: Тест

```bash
# Быстрая проверка
./test_ai_integration.sh quick

# Полный тест
./test_ai_integration.sh

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

## 🎯 Архитектура решения

```
┌──────────┐
│  Клиент  │
└────┬─────┘
     │
     ▼
┌──────────────────────┐
│   n8n Workflow       │
│                      │
│  1. Copy page        │
│  2. Parallel:        │
│     ├─ Grafana ─────┐│
│     ├─ Loki    ─────┤│
│     └─ AI ──────────┤│
│                     ││
│  3. Merge all ◄─────┘│
│  4. Update page      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  AI Microservice     │
│  (Flask REST API)    │
│                      │
│  /health             │
│  /analyze            │
│  /config/check       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    AI/main.py        │
│                      │
│  - Prometheus        │
│  - GigaChat          │
│  - Analysis          │
└──────────────────────┘
```

---

## 📊 Что делает AI-анализ

AI-микросервис автоматически анализирует:

### 1. JVM метрики
- Память (Heap, Non-Heap)
- CPU процессов
- GC активность

### 2. Database метрики
- Активные подключения
- Времена запросов
- Блокировки

### 3. Kafka метрики
- Consumer lag
- Fetch rate
- Очереди сообщений

### 4. Microservices метрики
- RPS
- Response times
- Error rates

**Результат:** Structured JSON с выводами, уровнями проблем и рекомендациями

---

## ✅ Что работает

- ✅ Webhook API (замена Flask)
- ✅ Копирование Confluence страниц
- ✅ Загрузка графиков Grafana
- ✅ Сбор логов Loki
- ✅ **AI-анализ метрик**
- ✅ Параллельная обработка
- ✅ Merge результатов
- ✅ Обновление плейсхолдеров
- ✅ Обработка ошибок
- ✅ Docker контейнеризация

---

## 🔧 Что нужно настроить

### 1. Обновите METRICS_CONFIG

Откройте workflow в n8n → узел **"Get Service Config"**

Добавьте ваши метрики из `metrics_config.py`:

```javascript
const METRICS_CONFIG = {
  "NSI": {
    "metrics": [
      { "name": "RPS", "grafana_url": "..." },
      { "name": "ResponseTime", "grafana_url": "..." }
      // ... все ваши метрики
    ],
    "logs": [
      { "placeholder": "service-name", "filter_query": "..." }
      // ... все ваши логи
    ]
  }
};
```

### 2. Проверьте AI/config.py

Убедитесь, что настроены:
- Prometheus URL
- GigaChat credentials
- PromQL queries
- Сертификаты mTLS (если нужны)

---

## 🐛 Troubleshooting

### AI-сервис не запускается

```bash
# Логи
docker-compose -f docker-compose.n8n.yml logs ai-analyzer

# Перезапуск
./deploy_ai_service.sh restart
```

### AI возвращает ошибки

```bash
# Проверка конфигурации
curl http://localhost:5001/config/check | jq .

# Проверка healthcheck
curl http://localhost:5001/health
```

### Workflow не работает

1. Проверьте, что workflow **активирован**
2. Проверьте credentials (Confluence, Grafana)
3. Проверьте логи: `docker-compose logs n8n`

---

## 📚 Документация

| Файл | Описание | Для кого |
|------|----------|----------|
| **QUICK_START_AI.md** | Быстрый старт за 5 мин | Новички |
| **AI_INTEGRATION_GUIDE.md** | Детальное руководство | DevOps |
| **README_N8N_MIGRATION.md** | Общая миграция | Все |
| **N8N_MIGRATION_GUIDE.md** | Расширенная документация | Архитекторы |
| **README_AI_FILES.md** | Список всех файлов | Справка |

---

## 🎉 Следующие шаги

1. ✅ **Запустите систему:**
   ```bash
   ./deploy_ai_service.sh
   ```

2. ✅ **Импортируйте workflow в n8n**

3. ✅ **Настройте credentials**

4. ✅ **Обновите METRICS_CONFIG**

5. ✅ **Протестируйте:**
   ```bash
   ./test_ai_integration.sh
   ```

6. ✅ **Создайте первый отчет!**

---

## 💡 Полезные команды

```bash
# Развертывание
./deploy_ai_service.sh

# Тестирование
./test_ai_integration.sh

# Логи AI
docker-compose -f docker-compose.n8n.yml logs -f ai-analyzer

# Логи n8n
docker-compose -f docker-compose.n8n.yml logs -f n8n

# Остановка
./deploy_ai_service.sh stop

# Полная очистка
./deploy_ai_service.sh clean
```

---

## 🚀 Готово к использованию!

Все файлы созданы, документация готова, скрипты настроены.

**Начните с [QUICK_START_AI.md](QUICK_START_AI.md) для быстрого старта!**

Удачи! 🎉

---

## 📞 Помощь

- Быстрый старт: `QUICK_START_AI.md`
- Troubleshooting: `AI_INTEGRATION_GUIDE.md` (раздел Troubleshooting)
- Полный список файлов: `README_AI_FILES.md`

