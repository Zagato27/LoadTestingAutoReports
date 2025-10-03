# 📊 Руководство по настройке метрик

## Файлы конфигурации

| Файл | Назначение |
|------|------------|
| **metrics_config.py** | Полный конфиг из оригинального проекта (для справки) |
| **metrics_config_example.py** | Упрощенный пример без Loki |

---

## 🔧 Как настроить метрики в n8n

### 1. Структура конфигурации

```python
METRICS_CONFIG = {
    "NSI": {                            # Имя сервиса
        "confluence_url": "...",        # URL Confluence
        "page_sample_id": "682908703",  # ID шаблона
        "page_parent_id": "882999920",  # ID родителя
        "grafana_base_url": "...",      # URL Grafana
        "metrics": [                    # Список метрик
            {
                "name": "RPS",          # Имя метрики
                "grafana_url": "..."    # URL панели
            }
        ]
    }
}
```

### 2. Где находится конфигурация в n8n?

Откройте workflow → узел **"Get Service Config"** → JavaScript код:

```javascript
const service = $input.first().json.service;
const METRICS_CONFIG = {
  "NSI": {
    "confluence_url": "https://confluence.test.ru",
    "page_sample_id": "682908703",
    "page_parent_id": "882999920",
    "grafana_base_url": "http://grafana:3000",
    "metrics": [
      {
        "name": "RPS",
        "grafana_url": "/render/d-solo/..."
      },
      // ... добавьте ваши метрики сюда
    ]
  }
};

const config = METRICS_CONFIG[service];
if (!config) {
  throw new Error(`Service ${service} not found in config`);
}

return { json: config };
```

### 3. Добавление новой метрики

**Шаг 1:** Получите URL панели Grafana

```
1. Откройте панель в Grafana
2. Share → Link → Copy URL
3. Замените обычный URL на /render/d-solo/...
4. Добавьте параметры: width, height, tz
```

**Пример:**
```
Обычный URL:
https://grafana.company.com/d/XKhgaUpikugieq/dashboard?panelId=17

Render URL:
/render/d-solo/XKhgaUpikugieq/dashboard?orgId=1&panelId=17&width=1000&height=500&tz=Europe%2FMoscow
```

**Шаг 2:** Добавьте в конфиг

```javascript
{
  "name": "MyNewMetric",
  "grafana_url": "/render/d-solo/XKhgaUpikugieq/dashboard?orgId=1&panelId=17&width=1000&height=500&tz=Europe%2FMoscow"
}
```

**Шаг 3:** Добавьте плейсхолдер в шаблон Confluence

```
$$MyNewMetric$$
```

---

## 📋 Типичные метрики

### Производительность

```javascript
{
  "name": "RPS",
  "grafana_url": "/render/d-solo/.../panelId=17..."
},
{
  "name": "ResponseTime",
  "grafana_url": "/render/d-solo/.../panelId=8..."
},
{
  "name": "Errors",
  "grafana_url": "/render/d-solo/.../panelId=7..."
}
```

### Kafka

```javascript
{
  "name": "RPSKafka",
  "grafana_url": "/render/d-solo/.../panelId=84..."
},
{
  "name": "ConsumerLag",
  "grafana_url": "/render/d-solo/.../panelId=79..."
}
```

### Kubernetes

```javascript
{
  "name": "global_cpu",
  "grafana_url": "/render/d-solo/e1RXnCbVz/kubernetes-dashboard?panelId=35..."
},
{
  "name": "global_mem",
  "grafana_url": "/render/d-solo/e1RXnCbVz/kubernetes-dashboard?panelId=37..."
}
```

### Микросервисы

```javascript
{
  "name": "micro-service-name_cpu",
  "grafana_url": "/render/d-solo/.../panelId=1..."
},
{
  "name": "micro-service-name_mem",
  "grafana_url": "/render/d-solo/.../panelId=3..."
}
```

---

## 🎨 Шаблон Confluence

### Создание шаблона

1. Создайте страницу в Confluence
2. Добавьте плейсхолдеры для метрик
3. Добавьте плейсхолдеры для AI-анализа
4. Скопируйте ID страницы в конфиг

### Пример шаблона

```html
<h2>Результаты нагрузочного тестирования</h2>

<h3>Основные метрики</h3>

<h4>RPS (Requests Per Second)</h4>
$$RPS$$

<h4>Response Time</h4>
$$ResponseTimeTable$$

<h4>Errors</h4>
$$Errors$$

<h3>Kafka метрики</h3>
$$RPSKafka$$

<h3>Kubernetes ресурсы</h3>

<h4>CPU</h4>
$$global_cpu$$

<h4>Memory</h4>
$$global_mem$$

<h3>AI-анализ</h3>

<h4>JVM Analysis</h4>
$$answer_jvm$$

<h4>Database Analysis</h4>
$$answer_database$$

<h4>Kafka Analysis</h4>
$$answer_kafka$$

<h4>Microservices Analysis</h4>
$$answer_ms$$

<h4>Overall Findings</h4>
$$final_answer$$
```

---

## 🔄 Миграция из metrics_config.py

Если у вас есть `metrics_config.py` из оригинального проекта:

### 1. Откройте файл

```python
# metrics_config.py
METRICS_CONFIG = {
    "NSI": {
        "metrics": [
            {"name": "RPS", "grafana_url": "..."},
            ...
        ],
        "logs": [...]  # ← это удаляем (Loki не используется)
    }
}
```

### 2. Конвертируйте в JavaScript

```javascript
// В n8n узле "Get Service Config"
const METRICS_CONFIG = {
  "NSI": {
    "confluence_url": "...",
    "page_sample_id": "...",
    "page_parent_id": "...",
    "grafana_base_url": "...",
    "metrics": [
      {"name": "RPS", "grafana_url": "..."},
      // ... скопируйте все метрики
    ]
    // секцию "logs" НЕ копируем (Loki убран)
  }
};
```

### 3. Удалите секцию logs

```diff
- "logs": [
-   {
-     "placeholder": "micro-registry-nsi",
-     "filter_query": '{namespace="apps"} |= "ERROR"'
-   }
- ]
```

---

## ✅ Чек-лист настройки

- [ ] Скопировали метрики из `metrics_config.py`
- [ ] Преобразовали Python → JavaScript
- [ ] Удалили секцию `logs`
- [ ] Обновили URLs (confluence_url, grafana_base_url)
- [ ] Обновили IDs (page_sample_id, page_parent_id)
- [ ] Добавили плейсхолдеры в шаблон Confluence
- [ ] Добавили AI плейсхолдеры ($$answer_jvm$$, и т.д.)
- [ ] Протестировали создание отчета

---

## 🐛 Типичные проблемы

### Метрика не отображается

**Проблема:** Изображение не появляется в отчете

**Решение:**
1. Проверьте, что плейсхолдер в шаблоне точно совпадает: `$$RPS$$`
2. Проверьте URL панели Grafana
3. Проверьте credentials Grafana в n8n

### Неправильный формат URL

**Проблема:** Grafana возвращает ошибку

**Решение:**
```
❌ Неправильно:
https://grafana.com/d/dashboard/name?panelId=17

✅ Правильно:
/render/d-solo/dashboard/name?orgId=1&panelId=17&width=1000&height=500&tz=Europe%2FMoscow
```

### Плейсхолдер не заменяется

**Проблема:** В отчете остается `$$RPS$$`

**Решение:**
1. Проверьте имя в конфиге: `"name": "RPS"`
2. Проверьте плейсхолдер в шаблоне: `$$RPS$$` (без пробелов)
3. Убедитесь, что workflow успешно выполнился

---

## 📚 Дополнительная информация

- **README.md** - основная документация
- **QUICKSTART.md** - быстрый старт
- **metrics_config.py** - полный конфиг (справка)
- **metrics_config_example.py** - упрощенный пример

---

## 🎉 Готово!

После настройки метрик workflow будет автоматически:
1. Загружать изображения панелей из Grafana
2. Прикреплять их к странице Confluence
3. Заменять плейсхолдеры на изображения
4. Добавлять AI-анализ

Удачи! 🚀

