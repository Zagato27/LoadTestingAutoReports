# 🚀 Быстрый старт: AI-интеграция с n8n

## За 5 минут до первого отчета

### Шаг 1: Подготовка (1 мин)

```bash
# Клонируйте репозиторий (если еще не сделали)
cd LoadTestingAutoReports

# Создайте .env из шаблона
cp env.example.txt .env

# Отредактируйте .env (минимум: пароли и URL)
nano .env
```

**Обязательные настройки в .env:**
```bash
POSTGRES_PASSWORD=your_secure_password
PROMETHEUS_URL=http://your-prometheus:9090
GRAFANA_URL=http://your-grafana:3000
```

### Шаг 2: Запуск (2 мин)

```bash
# Автоматическое развертывание
./deploy_ai_service.sh

# Или вручную:
docker-compose -f docker-compose.n8n.yml up -d
```

### Шаг 3: Настройка n8n (2 мин)

1. **Откройте n8n:** http://localhost:5678

2. **Импортируйте workflow:**
   - Settings → Import from File
   - Выберите: `n8n_load_testing_workflow_with_ai.json`

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

4. **Активируйте workflow:**
   - Нажмите кнопку "Active" в правом верхнем углу

### Шаг 4: Тестирование

```bash
# Быстрый тест (без создания отчета)
./test_ai_integration.sh quick

# Полный тест
./test_ai_integration.sh

# Создание реального отчета
curl -X POST http://localhost:5678/webhook/load-testing/report/create \
  -H "Content-Type: application/json" \
  -d '{
    "start": "2025-02-21T11:30",
    "end": "2025-02-21T14:10",
    "service": "NSI"
  }'
```

## 📊 Что происходит при создании отчета

```
1. Webhook получает параметры (start, end, service)
   ↓
2. Копируется шаблон Confluence
   ↓
3. Параллельно выполняется:
   ├─► Загрузка графиков из Grafana
   ├─► Сбор логов из Loki
   └─► AI-анализ метрик (JVM, DB, Kafka, Microservices)
   ↓
4. Все результаты объединяются
   ↓
5. Страница Confluence обновляется одним проходом
   ↓
6. Возвращается ссылка на готовый отчет
```

**Время выполнения:** 3-7 минут (зависит от количества метрик и AI-анализа)

## 🎯 Что включает AI-анализ

AI-сервис автоматически анализирует:

1. **JVM метрики:**
   - Использование памяти (Heap, Non-Heap)
   - CPU нагрузка процессов
   - GC активность

2. **Database метрики:**
   - Активные подключения
   - Времена выполнения запросов
   - Блокировки и deadlocks

3. **Kafka метрики:**
   - Consumer lag
   - Fetch rate
   - Сообщения в очереди

4. **Microservices метрики:**
   - RPS (запросы в секунду)
   - Времена ответа
   - Коды ошибок

**Результат:** Структурированный отчет с выводами, уровнями серьезности проблем и рекомендациями.

## 🔧 Конфигурация метрик

Откройте workflow в n8n и найдите узел **"Get Service Config"**.

Добавьте ваши сервисы:

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
        "grafana_url": "/render/d-solo/dashboard-id/..."
      }
      // ... ваши метрики
    ],
    "logs": [
      {
        "placeholder": "service-name",
        "filter_query": '{namespace="apps"} |= "ERROR"'
      }
      // ... ваши логи
    ]
  },
  // Добавьте другие сервисы...
};
```

## ✅ Проверка работы

### AI-сервис

```bash
# Healthcheck
curl http://localhost:5001/health
# Ожидается: {"status": "healthy"}

# Конфигурация
curl http://localhost:5001/config/check | jq .
# Покажет настройки Prometheus, LLM и т.д.

# Тестовый анализ
curl -X POST http://localhost:5001/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "start": 1708513800000,
    "end": 1708523400000
  }' | jq .
```

### n8n workflow

```bash
# Проверка webhook
curl -X POST http://localhost:5678/webhook/load-testing/report/create \
  -H "Content-Type: application/json" \
  -d '{}' | jq .
# Ожидается: {"status": "error", "message": "Missing required parameters..."}
```

## 📝 Логи и отладка

```bash
# Логи AI-сервиса
docker-compose -f docker-compose.n8n.yml logs -f ai-analyzer

# Логи n8n
docker-compose -f docker-compose.n8n.yml logs -f n8n

# Статус всех сервисов
docker-compose -f docker-compose.n8n.yml ps

# Перезапуск AI-сервиса
docker-compose -f docker-compose.n8n.yml restart ai-analyzer
```

## 🐛 Частые проблемы

### AI-сервис не запускается

```bash
# Проверьте логи
docker-compose -f docker-compose.n8n.yml logs ai-analyzer

# Проверьте конфигурацию
cat AI/config.py

# Пересоберите образ
docker-compose -f docker-compose.n8n.yml build ai-analyzer
docker-compose -f docker-compose.n8n.yml up -d ai-analyzer
```

### AI возвращает "insufficient_data"

```bash
# Проверьте доступность Prometheus
curl http://your-prometheus:9090/api/v1/query?query=up

# Проверьте наличие метрик за период
curl "http://your-prometheus:9090/api/v1/query_range?\
query=jvm_memory_used_bytes&\
start=1708513800&\
end=1708523400&\
step=60"
```

### Workflow не запускается

1. Убедитесь, что workflow **активирован** (кнопка Active в n8n)
2. Проверьте, что credentials настроены
3. Проверьте логи n8n: `docker-compose logs n8n`

## 📚 Документация

- **[AI_INTEGRATION_GUIDE.md](AI_INTEGRATION_GUIDE.md)** - детальное руководство по AI
- **[README_N8N_MIGRATION.md](README_N8N_MIGRATION.md)** - общее руководство по миграции
- **[N8N_MIGRATION_GUIDE.md](N8N_MIGRATION_GUIDE.md)** - расширенная документация

## 🎉 Готово!

После успешной настройки вы можете:

1. **Создавать отчеты через API:**
   ```bash
   curl -X POST http://localhost:5678/webhook/load-testing/report/create \
     -H "Content-Type: application/json" \
     -d '{
       "start": "2025-02-21T11:30",
       "end": "2025-02-21T14:10",
       "service": "NSI"
     }'
   ```

2. **Интегрировать с CI/CD:**
   ```yaml
   # .gitlab-ci.yml
   create_report:
     script:
       - curl -X POST $N8N_URL/webhook/load-testing/report/create \
           -d '{"start": "$START", "end": "$END", "service": "$SERVICE"}'
   ```

3. **Мониторить в n8n:**
   - Executions → История выполнений
   - Просмотр логов каждого узла
   - Retry при ошибках

Удачи! 🚀

