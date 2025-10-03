# ⚡ Быстрый старт - Изолированный n8n проект

## 🎯 Что это?

Полностью автономная система создания отчетов по нагрузочному тестированию:
- **n8n workflow** - визуальная оркестрация
- **AI-микросервис** - анализ метрик через GigaChat
- **Grafana** - графики метрик
- **Без Loki** - упрощенная версия (только метрики + AI)

---

## 📦 Что внутри?

```
n8n_integration/              # ← ВСЁ ИЗОЛИРОВАННО
├── n8n_workflow_simple.json  # Workflow для импорта
├── ai_service_for_n8n.py     # AI REST API
├── AI/                       # AI-модуль (копия)
├── confluence_manager/       # Confluence (копия)
├── docker-compose.yml        # Docker стек
├── Dockerfile                # AI-сервис
├── requirements.txt          # Python зависимости
└── config.py                 # Настройки
```

**Никаких внешних зависимостей!**

---

## 🚀 Запуск за 5 минут

### 1️⃣ Настройка (.env + config)

```bash
# Создайте .env
cp env.example.txt .env
nano .env
```

Минимальные настройки:
```bash
PROMETHEUS_URL=http://your-prometheus:9090
POSTGRES_PASSWORD=your_password
```

### 2️⃣ Запуск

```bash
# Автоматически
./deploy_ai_service.sh

# Или вручную
docker-compose up -d
```

### 3️⃣ Настройка n8n

1. Откройте http://localhost:5678
2. Import → `n8n_workflow_simple.json`
3. Credentials:
   - Confluence (HTTP Basic Auth)
   - Grafana (HTTP Basic Auth)
4. Activate workflow

### 4️⃣ Тест

```bash
curl -X POST http://localhost:5678/webhook/load-testing/report/create \
  -H "Content-Type: application/json" \
  -d '{
    "start": "2025-02-21T11:30",
    "end": "2025-02-21T14:10",
    "service": "NSI"
  }'
```

---

## 🎯 Архитектура (упрощенная)

```
User → n8n Workflow → AI Service
         ↓              ↓
    Grafana        Prometheus
    Confluence     GigaChat
```

**Поток:**
1. Webhook получает параметры
2. Копирует страницу Confluence
3. Параллельно:
   - Загружает графики Grafana
   - Запускает AI-анализ
4. Объединяет результаты
5. Обновляет страницу
6. Возвращает ссылку на отчет

---

## 📊 AI-анализ

Автоматически анализирует:
- **JVM:** память, CPU, GC
- **Database:** подключения, запросы
- **Kafka:** consumer lag, throughput
- **Microservices:** RPS, response times

**Результат:** Структурированные выводы + рекомендации

---

## 🔧 Команды

```bash
# Развертывание
./deploy_ai_service.sh

# Тестирование
./test_ai_integration.sh quick

# Логи
docker-compose logs -f

# Остановка
docker-compose down
```

---

## ⚠️ Важно

### Что настроить:

1. **AI/config.py** - Prometheus URL, GigaChat credentials
2. **config.py** - Confluence, Grafana логины
3. **Workflow** - метрики в узле "Get Service Config"

### Что НЕ работает:

- ❌ Loki логи (убраны для упрощения)

### Что работает:

- ✅ Grafana метрики
- ✅ AI-анализ
- ✅ Confluence обновление
- ✅ Полная изоляция (все зависимости внутри)

---

## 🐛 Проблемы?

```bash
# AI-сервис недоступен
docker-compose logs ai-analyzer
curl http://localhost:5001/health

# n8n недоступен
docker-compose logs n8n

# AI возвращает ошибки
curl http://localhost:5001/config/check | jq .
```

---

## 📚 Документация

- **README.md** - полная документация
- **AI_INTEGRATION_GUIDE.md** - детальное руководство по AI

---

## ✅ Checklist

- [ ] Настроили `.env`
- [ ] Настроили `AI/config.py`
- [ ] Запустили `docker-compose up -d`
- [ ] Импортировали workflow в n8n
- [ ] Настроили credentials
- [ ] Обновили метрики в workflow
- [ ] Активировали workflow
- [ ] Протестировали

---

## 🎉 Готово!

Теперь система полностью автономна и готова к использованию.

**Следующий шаг:** Создайте первый отчет! 🚀

