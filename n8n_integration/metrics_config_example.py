# metrics_config_example.py
# Пример конфигурации метрик для n8n workflow

# ВАЖНО: В n8n эта конфигурация находится в узле "Get Service Config" (JavaScript код)
# Этот файл - для справки и примера структуры данных

METRICS_CONFIG = {
    "NSI": {
        # Confluence настройки
        "confluence_url": "https://confluence.test.ru",
        "page_sample_id": "682908703",  # ID шаблонной страницы
        "page_parent_id": "882999920",  # ID родительской страницы
        
        # Grafana настройки
        "grafana_base_url": "http://0.0.0.0:3000",
        
        # Метрики для отображения
        "metrics": [
            {
                "name": "RPS",
                "grafana_url": "/render/d-solo/XKhgaUpikugieq/k6-load-testing-results?orgId=1&panelId=17&width=1000&height=500&tz=Europe%2FMoscow"
            },
            {
                "name": "ResponseTimeTable",
                "grafana_url": "/render/d-solo/XKhgaUpikugieq/k6-load-testing-results?orgId=1&panelId=67&width=1000&height=900&tz=Europe%2FMoscow"
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
            # Kafka метрики
            {
                "name": "RPSKafka",
                "grafana_url": "/render/d-solo/XKhgaUpikugigf/k6-kafka?orgId=1&panelId=84&width=1000&height=500&tz=Europe%2FMoscow"
            },
            # Core Web Vitals
            {
                "name": "CLS",
                "grafana_url": "/render/d-solo/XKhgaUpikugieq/k6-load-testing-results?orgId=1&panelId=83&width=1000&height=500&tz=Europe%2FMoscow"
            },
            {
                "name": "LCP",
                "grafana_url": "/render/d-solo/XKhgaUpikugieq/k6-load-testing-results?orgId=1&panelId=85&width=1000&height=500&tz=Europe%2FMoscow"
            },
            # Kubernetes метрики
            {
                "name": "global_cpu",
                "grafana_url": "/render/d-solo/e1RXnCbVz/kubernetes-dashboard?orgId=1&panelId=35&width=1000&height=500&tz=Europe%2FMoscow"
            },
            {
                "name": "global_mem",
                "grafana_url": "/render/d-solo/e1RXnCbVz/kubernetes-dashboard?orgId=1&panelId=37&width=1000&height=500&tz=Europe%2FMoscow"
            },
            # Микросервисы метрики
            {
                "name": "micro-registry-nsi_cpu",
                "grafana_url": "/render/d-solo/a164a7f0339f99e89cea5cb47e9be617/kubernetes-compute-resources-workload?orgId=1&panelId=1&width=1000&height=500&tz=Europe%2FMoscow"
            },
            {
                "name": "micro-registry-nsi_mem",
                "grafana_url": "/render/d-solo/a164a7f0339f99e89cea5cb47e9be617/kubernetes-compute-resources-workload?orgId=1&panelId=3&width=1000&height=500&tz=Europe%2FMoscow"
            },
        ]
        
        # ПРИМЕЧАНИЕ: Секция "logs" удалена, так как Loki не используется
    },
    
    # Добавьте другие сервисы по аналогии
    "service_2": {
        "confluence_url": "https://confluence.test.ru",
        "page_sample_id": "682908704",
        "page_parent_id": "652073177",
        "grafana_base_url": "http://0.0.0.0:3000",
        "metrics": [
            {
                "name": "RPMKafka",
                "grafana_url": "/render/d-solo/XKhgaUpikugigf/k6-kafka?orgId=1&panelId=77&width=1000&height=500&tz=Europe%2FMoscow"
            },
        ]
    }
}


# ═══════════════════════════════════════════════════════════════
# КАК ИСПОЛЬЗОВАТЬ В n8n WORKFLOW
# ═══════════════════════════════════════════════════════════════

"""
1. Откройте n8n_workflow_simple.json в n8n
2. Найдите узел "Get Service Config"
3. Скопируйте конфигурацию из этого файла в JavaScript код узла:

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
      // ... остальные метрики
    ]
  }
};

4. В шаблоне Confluence должны быть плейсхолдеры:
   - $$RPS$$ - для метрики RPS
   - $$ResponseTimeTable$$ - для метрики ResponseTimeTable
   - И т.д. для каждой метрики из списка

5. Также добавьте плейсхолдеры для AI-анализа:
   - $$answer_jvm$$ - анализ JVM
   - $$answer_database$$ - анализ БД
   - $$answer_kafka$$ - анализ Kafka
   - $$answer_ms$$ - анализ микросервисов
   - $$final_answer$$ - итоговый анализ
"""

