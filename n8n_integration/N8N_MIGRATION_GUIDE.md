# Руководство по миграции на n8n

## Обзор

Создан n8n workflow для переноса функционала Python-сервиса создания отчетов по нагрузочному тестированию.

## Что реализовано в workflow

### ✅ Базовый функционал (готов)
1. **Прием параметров через Webhook**
   - Endpoint: `POST /load-testing/report/create`
   - Параметры: `start`, `end`, `service`
   - Валидация входных данных

2. **Работа с Confluence**
   - Получение шаблонной страницы
   - Копирование страницы
   - Обновление плейсхолдеров

3. **Загрузка метрик из Grafana**
   - Скачивание изображений панелей
   - Загрузка вложений в Confluence
   - Замена плейсхолдеров типа `$$RPS$$`

4. **Сбор логов из Loki**
   - Запрос логов по фильтру
   - Сохранение в `.log` файл
   - Загрузка в Confluence как вложение

5. **Обработка ответов**
   - Успешный ответ с ссылкой на страницу
   - Обработка ошибок

### ⚠️ Требует доработки

**AI-анализ метрик (GigaChat/LLM)**
- В Python-сервисе используется сложная логика AI-анализа:
  - Загрузка метрик из Prometheus
  - Анализ по доменам (JVM, Database, Kafka, Microservices)
  - Генерация итоговых выводов
  - Форматирование в markdown

**Варианты реализации в n8n:**

#### Вариант 1: Отдельный Python-сервис для AI
```
n8n → Python AI Service → n8n
```
Плюсы:
- Сохраняется вся логика AI
- Легко поддерживать
- Можно использовать существующий код

Минусы:
- Нужен дополнительный сервис

#### Вариант 2: n8n + Code узлы с LangChain
```
n8n (Code nodes с GigaChat API)
```
Плюсы:
- Все в одном workflow
- Нативная интеграция

Минусы:
- Нужно переписать логику
- Сложнее отлаживать

#### Вариант 3: Гибридный
```
n8n → Docker контейнер с Python AI → n8n
```
Плюсы:
- Изолированность
- Простота деплоя

## Инструкция по настройке

### 1. Импорт workflow в n8n

```bash
# Скопируйте файл n8n_load_testing_workflow.json
# В n8n: Settings → Import from File → Выберите файл
```

### 2. Настройка Credentials

#### Confluence Credentials
```
Тип: HTTP Basic Auth
ID: confluence-creds
Username: ваш_логин
Password: ваш_пароль_или_токен
```

#### Grafana Credentials  
```
Тип: HTTP Basic Auth
ID: grafana-creds
Username: ваш_логин_grafana
Password: ваш_пароль_grafana
```

### 3. Настройка конфигурации

В узле **"Get Service Config"** обновите METRICS_CONFIG:

```javascript
const METRICS_CONFIG = {
  "NSI": {
    "confluence_url": "https://confluence.sberbank.ru",
    "page_sample_id": "682908703",
    "page_parent_id": "882999920",
    "grafana_base_url": "http://grafana.url:3000",
    "loki_url": "http://loki.url/loki/api/v1/query_range",
    "metrics": [
      {
        "name": "RPS",
        "grafana_url": "/render/d-solo/..."
      }
      // ... добавьте все метрики из metrics_config.py
    ],
    "logs": [
      {
        "placeholder": "micro-registry-nsi",
        "filter_query": '{namespace=~"apps"} |= "ERROR"'
      }
      // ... добавьте все логи
    ]
  }
  // ... добавьте другие сервисы
};
```

### 4. Тестирование

```bash
# Тестовый запрос
curl -X POST http://your-n8n.url/webhook/load-testing/report/create \
  -H "Content-Type: application/json" \
  -d '{
    "start": "2025-02-21T11:30",
    "end": "2025-02-21T14:10",
    "service": "NSI"
  }'
```

Ожидаемый ответ:
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

## Добавление AI-анализа

### Рекомендуемый подход: Python микросервис

1. **Создайте отдельный микросервис** `ai_analyzer_service.py`:

```python
from flask import Flask, request, jsonify
from AI.main import uploadFromLLM

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    start_ts = data['start'] / 1000  # конвертируем из мс
    end_ts = data['end'] / 1000
    
    results = uploadFromLLM(start_ts, end_ts)
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

2. **Добавьте в n8n новый узел HTTP Request**:

```
Position: После "Copy Confluence Page"
URL: http://ai-service:5001/analyze
Method: POST
Body: 
{
  "start": {{ $('Parse Input').item.json.start_timestamp }},
  "end": {{ $('Parse Input').item.json.end_timestamp }}
}
```

3. **Обработайте результат AI**:

Добавьте узел Code для обработки AI-ответа и замены плейсхолдеров:
- `$$answer_jvm$$`
- `$$answer_database$$`
- `$$answer_kafka$$`
- `$$answer_ms$$`
- `$$final_answer$$`

## Сравнение с текущим Python сервисом

| Функция | Python сервис | n8n workflow | Статус |
|---------|---------------|--------------|--------|
| Веб-интерфейс | Flask + HTML | Webhook | ✅ |
| Копирование страницы Confluence | ✅ | ✅ | ✅ |
| Загрузка метрик Grafana | ✅ | ✅ | ✅ |
| Сбор логов Loki | ✅ | ✅ | ✅ |
| AI-анализ | ✅ | ⚠️ | Требует AI-сервиса |
| Обновление плейсхолдеров | ✅ | ✅ | ✅ |
| Параллельная обработка | ThreadPoolExecutor | n8n native | ✅ |
| Retry логика | ✅ | n8n native | ✅ |

## Преимущества n8n решения

1. **Визуализация**: Наглядный граф выполнения
2. **Мониторинг**: Встроенные логи и история выполнений
3. **Масштабируемость**: Легко добавлять новые узлы
4. **Повторное использование**: Можно создать sub-workflows
5. **Обработка ошибок**: Встроенная retry-логика
6. **Вебхуки**: Нативная поддержка, не нужен Flask

## Следующие шаги

1. ✅ Импортируйте workflow в n8n
2. ✅ Настройте credentials
3. ✅ Обновите конфигурацию метрик
4. ⚠️ Решите, как интегрировать AI:
   - Микросервис (рекомендуется)
   - Code узлы в n8n
   - Внешний API
5. ⚠️ Протестируйте на тестовых данных
6. ⚠️ Добавьте обработку ошибок
7. ⚠️ Настройте алерты и мониторинг

## Troubleshooting

### Ошибка "Service not found"
Проверьте, что имя сервиса в запросе совпадает с ключом в METRICS_CONFIG

### Ошибка 401 при запросе к Confluence
Проверьте credentials, возможно нужен токен вместо пароля

### Изображения не загружаются из Grafana
- Проверьте доступность Grafana URL
- Убедитесь, что панели существуют
- Проверьте credentials

### Логи не найдены в Loki
- Проверьте filter_query
- Убедитесь, что логи есть за указанный период
- Проверьте формат временных меток

## Контакты

Для вопросов по миграции или проблем с настройкой обращайтесь к команде разработки.

