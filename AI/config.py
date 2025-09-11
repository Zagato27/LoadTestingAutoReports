# config.py

CONFIG = {
    "prometheus": {
        "url": "http://prometheus.apps.url"
    },
    "time_range": {
        # Примерные числа: берем UNIX-время в секундах
        # "start_ts": 1740126463,
        # "end_ts": 1740136370
        "start_ts": "2025-02-21T11:30",
        "end_ts": "2025-02-21T14:10"
    

    },
    "llm": {
        # Используем только прямые REST-вызовы GigaChat по mTLS
        "provider": "gigachat",
        "gigachat": {
            "api_base_url": "https://gigachat.devices.sberbank.ru/api/v1",
            "model": "GigaChat-Pro",
            # Включить mTLS и указать клиентский сертификат/ключ
            "use_mtls": True,
            "cert_file": "",
            "key_file": "",
            # verify: True/False или путь к доверенному корню (НУЦ Минцифры/корп. CA)
            "verify": "",
            # (опционально) прокси, если нужен выход через корпоративный прокси
            "proxies": {
                "https": "",
                "http": ""
            },
            "connect_timeout_sec": 5,
            "request_timeout_sec": 120,
            # отключить preflight GET /models (если сервер требует другую цепочку CA)
            "enable_preflight_models": False
        }
    },
    "default_params": {
        "step": "1m",
        "resample_interval": "10T"
    },
    # Источник метрик: напрямую из Prometheus или через Grafana proxy (без прямого доступа к Prometheus)
    "metrics_source": {
        "type": "prometheus",  # "prometheus" | "grafana_proxy"
        "grafana": {
            "base_url": "http://0.0.0.0:3000",
            "verify_ssl": False,
            "auth": {
                "method": "basic",  # "basic" | "bearer"
                "username": "login",
                "password": "pass",
                "token": ""
            },
            # Идентификация Prometheus-датасорса в Grafana: можно указать любой из id | uid | name
            "prometheus_datasource": {
                "id": None,
                "uid": "",
                "name": ""
            }
        }
    },
    "queries": {
        "jvm": {
            "promql_queries": [
                'sum(jvm_memory_used_bytes{area="heap", application!=""}) by (application, instance)',
                'sum(jvm_memory_used_bytes{area="nonheap", application!=""}) by (application, instance)',
                'sum(jvm_memory_max_bytes{area="heap", application!=""}) by (application, instance)',
                'sum(jvm_memory_max_bytes{area="nonheap", application!=""}) by (application, instance)',
                'sum(jvm_gc_pause_seconds_max{application!=""}) by (application, instance)',
                'sum(jvm_gc_pause_seconds_max{application!=""}) by (application, instance, action, cause)',
                'sum by (application, instance, action, cause) (rate(jvm_gc_pause_seconds_sum{application!=""}[1m])) / '
                'sum by (application, instance, action, cause) (rate(jvm_gc_pause_seconds_count{application!=""}[1m]))',
                'sum by (application, instance) (process_cpu_usage{application!=""})',
                'sum by (application, instance) (jvm_threads_live_threads{application!=""})',
                'sum by (application, instance) (jvm_threads_daemon_threads{application!=""})',
                'sum by (application, instance) (jvm_threads_peak_threads{application!=""})',
                'sum by (application, instance) (jvm_classes_loaded_classes{application!=""})'
            ],
            "label_keys_list": [
                ["application", "instance"],
                ["application", "instance"],
                ["application", "instance"],
                ["application", "instance"],
                ["application", "instance"],
                ["application", "instance", "action", "cause"],
                ["application", "instance", "action", "cause"],
                ["application", "instance"],
                ["application", "instance"],
                ["application", "instance"],
                ["application", "instance"],
                ["application", "instance"]
            ],
            "labels": [
                "JVM: Heap used (bytes) by (application, instance)",
                "JVM: Non-heap used (bytes) by (application, instance) ",
                "JVM: Heap max (bytes) by (application, instance)",
                "JVM: Non-heap max (bytes) by (application, instance)",
                "JVM: GC pause seconds (max) by (application, instance)",
                "JVM: GC pause seconds (max) by (application, instance, action, cause)",
                "JVM: Average GC pause (sum/count) by (application, instance, action, cause)",
                "JVM: Process CPU usage by (application, instance)",
                "JVM: Live threads by (application, instance)",
                "JVM: Daemon threads by (application, instance)",
                "JVM: Peak threads by (application, instance)",
                "JVM: Loaded classes by (application, instance)"
            ]
        },
        "arangodb": {
            "promql_queries": [
                'sum by (pod) (rate(arangodb_http_request_statistics_total_requests_total'
                '{namespace="arangodb", job!~".*replica.*"}[1m]))',
                'sum by (service)(histogram_quantile(0.95, '
                'sum(rate(arangodb_aql_query_time_bucket{job!~".*replica.*"}[5m])) by (le, service)))'
            ],
            "label_keys_list": [
                ["pod"],
                ["service"]
            ],
            "labels": [
                "ArangoDB: sum of HTTP requests (non-replica)",
                "ArangoDB: 95th percentile of AQL query time"
            ]
        },
        "kafka": {
            "promql_queries": [
                'sum(kafka_consumer_fetch_rate{topic !~ "_.+" , topic!~".*searched$", topic!="apps-registry.nsi.document-request"}) by (client_id)',
                'sum by (topic, consumergroup) (kafka_consumergroup_lag{consumergroup!~"apps-apps-micro-registry-incident-AT.*", topic !~ "__.+", topic!~".*searched$", topic!="apps-registry.nsi.document-request"})',
                'NSI_incident_repository_gauge'
                '{application="micro-registry-incident-schedule", repository="KafkaRequest"}'
            ],
            "label_keys_list": [
                ["client_id"],
                ["consumergroup"],
                []
            ],
            "labels": [
                "Kafka: consumer fetch rate by client_id",
                "Kafka: consumergroup lag by topic & group",
                "Kafka: NSI_incident_repository_gauge (KafkaRequest)"
            ]
        },
        "microservices": {
            "promql_queries": [
                'sum by (application) (rate(http_server_requests_seconds_sum{status!~"5.."}[1m]))/sum by (application) (rate(http_server_requests_seconds_count{status!~"5.."}[1m]))',
                'sum by (application) (rate(http_server_requests_seconds_count{}[1m]))'
            ],
            "label_keys_list": [
                ["application"],
                ["application"]
            ],
            "labels": [
                "Microservices: average request time (sec)",
                "Microservices: request count rate (RPS)"
            ]
        }
    }
}