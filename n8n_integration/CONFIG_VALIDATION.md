# ⚠️ Проверка конфигурации n8n workflow

## 📋 Анализ параметров

### ✅ Что ЕСТЬ в n8n workflow

#### Узел "Get Service Config" (текущее состояние)
```javascript
const METRICS_CONFIG = {
  "NSI": {
    "confluence_url": "https://confluence.test.ru",     // ✅
    "page_sample_id": "682908703",                      // ✅
    "page_parent_id": "882999920",                      // ✅
    "grafana_base_url": "http://0.0.0.0:3000",         // ✅
    "metrics": [                                        // ✅
      {
        "name": "RPS",
        "grafana_url": "/render/d-solo/..."
      },
      {
        "name": "ResponseTimeTable",
        "grafana_url": "/render/d-solo/..."
      }
    ]
  }
};
```

### ❌ Проблемы

#### 1. МАЛО МЕТРИК (критично!)

**В workflow:** Только 2 метрики (RPS, ResponseTimeTable)

**В metrics_config.py:** 50+ метрик!

**Метрики из полной конфигурации:**
- ✅ ResponseTimeTable
- ✅ RPS
- ❌ RPSGroups
- ❌ ResponseTimeBatch
- ❌ Errors
- ❌ RPSKafka
- ❌ kafkarequest
- ❌ CLS, INP, LCP, FCP, TTFB, FID (Core Web Vitals)
- ❌ global_cpu, global_mem (Kubernetes)
- ❌ nodes_cpu, nodes_mem
- ❌ namespace_cpu, namespace_mem
- ❌ micro-registry-address_cpu/mem
- ❌ И еще 30+ метрик микросервисов

#### 2. Отсутствуют дополнительные параметры

**Из оригинального config.py:**
```python
CONFIG = {
    'user': 'login',                    # ✅ Используется в credentials
    'password': 'pass',                 # ✅ Используется в credentials
    'grafana_login': 'login',           # ✅ Используется в credentials
    'grafana_pass': 'pass',             # ✅ Используется в credentials
    'url_basic': 'https://...',         # ✅ В METRICS_CONFIG как confluence_url
    'space_conf': 'DPSUPP',             # ❌ ОТСУТСТВУЕТ!
    'grafana_base_url': 'http://...',   # ✅ Есть
    'loki_url': 'http://...'            # ❌ Убран (нормально, Loki не используется)
}
```

---

## 🔧 Необходимые исправления

### 1. Добавить ВСЕ метрики в workflow

Откройте `n8n_workflow_simple.json` → узел **"Get Service Config"**

Замените JS код на:

```javascript
const service = $input.first().json.service;

const METRICS_CONFIG = {
  "NSI": {
    "confluence_url": "https://confluence.test.ru",
    "page_sample_id": "682908703",
    "page_parent_id": "882999920",
    "grafana_base_url": "http://0.0.0.0:3000",
    "space_conf": "DPSUPP",  // ← ДОБАВИТЬ!
    "metrics": [
      // Основные метрики
      {
        "name": "ResponseTimeTable",
        "grafana_url": "/render/d-solo/XKhgaUpikugieq/k6-load-testing-results?orgId=1&panelId=67&width=1000&height=900&tz=Europe%2FMoscow"
      },
      {
        "name": "RPS",
        "grafana_url": "/render/d-solo/XKhgaUpikugieq/k6-load-testing-results?orgId=1&panelId=17&width=1000&height=500&tz=Europe%2FMoscow"
      },
      {
        "name": "RPSGroups",
        "grafana_url": "/render/d-solo/XKhgaUpikugieq/k6-load-testing-results?orgId=1&panelId=71&width=2000&height=500&tz=Europe%2FMoscow"
      },
      {
        "name": "ResponseTimeBatch",
        "grafana_url": "/render/d-solo/XKhgaUpikugieq/k6-load-testing-results?orgId=1&panelId=8&width=1000&height=500&tz=Europe%2FMoscow"
      },
      {
        "name": "Errors",
        "grafana_url": "/render/d-solo/XKhgaUpikugieq/k6-load-testing-results?orgId=1&panelId=7&width=1000&height=500&tz=Europe%2FMoscow"
      },
      
      // Kafka метрики
      {
        "name": "RPSKafka",
        "grafana_url": "/render/d-solo/XKhgaUpikugigf/k6-kafka?orgId=1&panelId=84&width=1000&height=500&tz=Europe%2FMoscow&var-DATASOURCE=c821f414-4bcf-4a76-910b-13ccf2d3f9b5"
      },
      {
        "name": "kafkarequest",
        "grafana_url": "/render/d-solo/XKhgaUpikugigf/k6-kafka?orgId=1&panelId=79&width=1000&height=500&tz=Europe%2FMoscow&var-DATASOURCE=c821f414-4bcf-4a76-910b-13ccf2d3f9b5"
      },
      
      // Core Web Vitals
      {
        "name": "CLS",
        "grafana_url": "/render/d-solo/XKhgaUpikugieq/k6-load-testing-results?orgId=1&panelId=83&width=1000&height=500&tz=Europe%2FMoscow"
      },
      {
        "name": "INP",
        "grafana_url": "/render/d-solo/XKhgaUpikugieq/k6-load-testing-results?orgId=1&panelId=84&width=1000&height=500&tz=Europe%2FMoscow"
      },
      {
        "name": "LCP",
        "grafana_url": "/render/d-solo/XKhgaUpikugieq/k6-load-testing-results?orgId=1&panelId=85&width=1000&height=500&tz=Europe%2FMoscow"
      },
      {
        "name": "FCP",
        "grafana_url": "/render/d-solo/XKhgaUpikugieq/k6-load-testing-results?orgId=1&panelId=86&width=1000&height=500&tz=Europe%2FMoscow"
      },
      {
        "name": "TTFB",
        "grafana_url": "/render/d-solo/XKhgaUpikugieq/k6-load-testing-results?orgId=1&panelId=87&width=1000&height=500&tz=Europe%2FMoscow"
      },
      {
        "name": "FID",
        "grafana_url": "/render/d-solo/XKhgaUpikugieq/k6-load-testing-results?orgId=1&panelId=88&width=1000&height=500&tz=Europe%2FMoscow"
      },
      
      // Kubernetes метрики
      {
        "name": "global_cpu",
        "grafana_url": "/render/d-solo/e1RXnCbVz/kubernetes-dashboard?orgId=1&var-datasource=c821f414-4bcf-4a76-910b-13ccf2d3f9b5&var-namespace=All&var-pod=All&var-netface=All&panelId=35&width=1000&height=500&tz=Europe%2FMoscow"
      },
      {
        "name": "global_mem",
        "grafana_url": "/render/d-solo/e1RXnCbVz/kubernetes-dashboard?orgId=1&var-datasource=c821f414-4bcf-4a76-910b-13ccf2d3f9b5&var-namespace=All&var-pod=All&var-netface=All&panelId=37&width=1000&height=500&tz=Europe%2FMoscow"
      },
      {
        "name": "nodes_cpu",
        "grafana_url": "/render/d-solo/e6719396-b09e-48e8-85f5-5aec3e5faa59/sostojanie-klastera-nsi-new?orgId=1&panelId=2&width=1000&height=500&tz=Europe%2FMoscow"
      },
      {
        "name": "nodes_mem",
        "grafana_url": "/render/d-solo/e6719396-b09e-48e8-85f5-5aec3e5faa59/sostojanie-klastera-nsi-new?orgId=1&panelId=3&width=1000&height=500&tz=Europe%2FMoscow"
      },
      {
        "name": "namespace_cpu",
        "grafana_url": "/render/d-solo/e1RXnCbVz/kubernetes-dashboard?orgId=1&var-datasource=c821f414-4bcf-4a76-910b-13ccf2d3f9b5&var-namespace=All&var-pod=All&var-netface=All&panelId=16&width=1000&height=500&tz=Europe%2FMoscow"
      },
      {
        "name": "namespace_mem",
        "grafana_url": "/render/d-solo/e1RXnCbVz/kubernetes-dashboard?orgId=1&var-datasource=c821f414-4bcf-4a76-910b-13ccf2d3f9b5&var-namespace=All&var-pod=All&var-netface=All&panelId=22&width=1000&height=500&tz=Europe%2FMoscow"
      },
      
      // Микросервисы (скопируйте из metrics_config.py все остальные)
      // ... добавьте все micro-* метрики
    ]
  }
};

const config = METRICS_CONFIG[service];
if (!config) {
  throw new Error(`Service ${service} not found in config`);
}

return { json: config };
```

### 2. Скопировать ПОЛНУЮ конфигурацию

**Источник:** `n8n_integration/metrics_config.py`

**Копируйте ВСЕ метрики из:**
```python
METRICS_CONFIG = {
    "NSI": {
        "metrics": [
            # ВСЕ эти метрики нужно скопировать в JavaScript
        ]
    }
}
```

**Используйте скрипт для конвертации:**

```bash
# Откройте metrics_config.py
# Скопируйте секцию "metrics"
# Замените ' на "
# Проверьте синтаксис
```

---

## 🔍 Проверка параметров по узлам

### Узел: "Get Template Page"
```javascript
url: "={{ $('Get Service Config').item.json.confluence_url }}/rest/api/content/..."
```
✅ Использует `confluence_url`

### Узел: "Copy Confluence Page"
```javascript
"space": {
  "key": "{{ $('Get Template Page').item.json.space.key }}"  // ⚠️ Берется из шаблона
}
```
⚠️ **Проблема:** space_conf не используется напрямую, берется из шаблона

**Решение:** Убедитесь, что шаблонная страница находится в правильном space

### Узел: "Prepare Metrics"
```javascript
for (const metric of config.metrics) {
  // Обрабатывает каждую метрику
}
```
✅ Использует список metrics

### Узел: "Download Grafana Image"
```javascript
url: "={{ $json.url }}"  // Формируется из grafana_base_url + grafana_url
```
✅ Работает корректно

---

## 📝 Чек-лист обязательных параметров

### В METRICS_CONFIG должны быть:

- [x] `confluence_url` - URL Confluence
- [x] `page_sample_id` - ID шаблонной страницы
- [x] `page_parent_id` - ID родительской страницы
- [x] `grafana_base_url` - URL Grafana
- [ ] `space_conf` - **ДОБАВИТЬ** (опционально, если нужен)
- [x] `metrics[]` - **ДОПОЛНИТЬ** (сейчас только 2, нужно 50+)

### В n8n Credentials должны быть:

- [x] Confluence credentials (HTTP Basic Auth)
- [x] Grafana credentials (HTTP Basic Auth)

### В шаблоне Confluence должны быть плейсхолдеры:

Для каждой метрики:
- `$$RPS$$`
- `$$ResponseTimeTable$$`
- `$$RPSGroups$$`
- ... и так далее для ВСЕХ метрик

Для AI-анализа:
- `$$answer_jvm$$`
- `$$answer_database$$`
- `$$answer_kafka$$`
- `$$answer_ms$$`
- `$$final_answer$$`

---

## ⚠️ КРИТИЧНО: Обновите метрики!

**Текущее состояние:** 2 метрики  
**Нужно:** 50+ метрик  

**Действия:**
1. Откройте `metrics_config.py`
2. Скопируйте ВСЕ метрики из секции "metrics"
3. Вставьте в n8n узел "Get Service Config"
4. Конвертируйте Python → JavaScript
5. Убедитесь, что в шаблоне Confluence есть соответствующие плейсхолдеры

---

## 🎯 Итоговая проверка

### ✅ Есть и работает:
- Confluence URL
- Page IDs
- Grafana base URL
- Основные 2 метрики
- AI-анализ
- Credentials

### ❌ Нужно добавить:
- **50+ метрик из metrics_config.py**
- `space_conf` (если требуется)
- Проверить плейсхолдеры в шаблоне

### ⚠️ Рекомендации:
1. Скопируйте ПОЛНУЮ конфигурацию метрик
2. Проверьте шаблон Confluence на наличие всех плейсхолдеров
3. Протестируйте с малым набором метрик, затем добавьте все

---

## 🚀 Быстрое решение

```bash
# 1. Откройте файл
cat metrics_config.py | grep -A 2 '"name"'

# 2. Скопируйте ВСЕ метрики в n8n workflow

# 3. Протестируйте
./test_ai_integration.sh
```

---

**Статус:** ⚠️ Требуется обновление метрик!  
**Приоритет:** ВЫСОКИЙ  
**Время:** ~15 минут на копирование всех метрик

