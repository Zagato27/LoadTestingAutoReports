# metrics_config.py

METRICS_CONFIG = {
    "NSI": {
        "page_sample_id": "682908703",  # Шаблон страницы Confluence для NSI
        "page_parent_id": "882999920",  # Страница Confluence для складирования готовых отчетов
        "metrics": [
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
            
            
            
            
            {
                "name": "RPSKafka",
                "grafana_url": "/render/d-solo/XKhgaUpikugigf/k6-kafka?orgId=1&panelId=84&width=1000&height=500&tz=Europe%2FMoscow&var-DATASOURCE=c821f414-4bcf-4a76-910b-13ccf2d3f9b5"             
            },
            {
                "name": "kafkarequest",
                "grafana_url": "/render/d-solo/XKhgaUpikugigf/k6-kafka?orgId=1&panelId=79&width=1000&height=500&tz=Europe%2FMoscow&var-DATASOURCE=c821f414-4bcf-4a76-910b-13ccf2d3f9b5"      
            },
            
            
            
            
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
            
            
            
            {
                "name": "micro-registry-address_cpu",
                "grafana_url": "/render/d-solo/a164a7f0339f99e89cea5cb47e9be617/kubernetes-compute-resources-workload?orgId=1&var-datasource=c821f414-4bcf-4a76-910b-13ccf2d3f9b5&var-cluster=&var-namespace=apps&var-type=deployment&var-workload=micro-registry-address&panelId=1&width=1000&height=500&tz=Europe%2FMoscow"
            },
            {
                "name": "micro-registry-address_mem",
                "grafana_url": "/render/d-solo/a164a7f0339f99e89cea5cb47e9be617/kubernetes-compute-resources-workload?orgId=1&var-datasource=c821f414-4bcf-4a76-910b-13ccf2d3f9b5&var-cluster=&var-namespace=apps&var-type=deployment&var-workload=micro-registry-address&panelId=3&width=1000&height=500&tz=Europe%2FMoscow"
            },
            {
                "name": "micro-registry-nsi_cpu",
                "grafana_url": "/render/d-solo/a164a7f0339f99e89cea5cb47e9be617/kubernetes-compute-resources-workload?orgId=1&var-datasource=c821f414-4bcf-4a76-910b-13ccf2d3f9b5&var-cluster=&var-namespace=apps&var-type=deployment&var-workload=micro-registry-nsi&panelId=1&width=1000&height=500&tz=Europe%2FMoscow"
            },
            {
                "name": "micro-registry-nsi_mem",
                "grafana_url": "/render/d-solo/a164a7f0339f99e89cea5cb47e9be617/kubernetes-compute-resources-workload?orgId=1&var-datasource=c821f414-4bcf-4a76-910b-13ccf2d3f9b5&var-cluster=&var-namespace=apps&var-type=deployment&var-workload=micro-registry-nsi&panelId=3&width=1000&height=500&tz=Europe%2FMoscow"
            },
            {
                "name": "micro-address-search-node_cpu",
                "grafana_url": "/render/d-solo/a164a7f0339f99e89cea5cb47e9be617/kubernetes-compute-resources-workload?orgId=1&var-datasource=c821f414-4bcf-4a76-910b-13ccf2d3f9b5&var-cluster=&var-namespace=apps&var-type=statefulset&var-workload=micro-address-search-node&panelId=1&width=1000&height=500&tz=Europe%2FMoscow"
            },
            {
                "name": "micro-address-search-node_mem",
                "grafana_url": "/render/d-solo/a164a7f0339f99e89cea5cb47e9be617/kubernetes-compute-resources-workload?orgId=1&var-datasource=c821f414-4bcf-4a76-910b-13ccf2d3f9b5&var-cluster=&var-namespace=apps&var-type=statefulset&var-workload=micro-address-search-node&panelId=3&width=1000&height=500&tz=Europe%2FMoscow"
            },
            {
                "name": "micro-registry-incident_cpu",
                "grafana_url": "/render/d-solo/a164a7f0339f99e89cea5cb47e9be617/kubernetes-compute-resources-workload?orgId=1&var-datasource=c821f414-4bcf-4a76-910b-13ccf2d3f9b5&var-cluster=&var-namespace=apps&var-type=deployment&var-workload=micro-registry-incident&panelId=1&width=1000&height=500&tz=Europe%2FMoscow"
            },
            {
                "name": "micro-registry-incident_mem",
                "grafana_url": "/render/d-solo/a164a7f0339f99e89cea5cb47e9be617/kubernetes-compute-resources-workload?orgId=1&var-datasource=c821f414-4bcf-4a76-910b-13ccf2d3f9b5&var-cluster=&var-namespace=apps&var-type=deployment&var-workload=micro-registry-incident&panelId=3&width=1000&height=500&tz=Europe%2FMoscow"
            },
            {
                "name": "micro-address-search-node-kafka_cpu",
                "grafana_url": "/render/d-solo/a164a7f0339f99e89cea5cb47e9be617/kubernetes-compute-resources-workload?orgId=1&var-datasource=c821f414-4bcf-4a76-910b-13ccf2d3f9b5&var-cluster=&var-namespace=apps&var-type=statefulset&var-workload=micro-address-search-node-kafka&panelId=1&width=1000&height=500&tz=Europe%2FMoscow"
            },
            {
                "name": "micro-address-search-node-kafka_mem",
                "grafana_url": "/render/d-solo/a164a7f0339f99e89cea5cb47e9be617/kubernetes-compute-resources-workload?orgId=1&var-datasource=c821f414-4bcf-4a76-910b-13ccf2d3f9b5&var-cluster=&var-namespace=apps&var-type=statefulset&var-workload=micro-address-search-node-kafka&panelId=3&width=1000&height=500&tz=Europe%2FMoscow"
            },
            {
                "name": "micro-address-search-node-custom_cpu",
                "grafana_url": "/render/d-solo/a164a7f0339f99e89cea5cb47e9be617/kubernetes-compute-resources-workload?orgId=1&var-datasource=c821f414-4bcf-4a76-910b-13ccf2d3f9b5&var-cluster=&var-namespace=apps&var-type=statefulset&var-workload=micro-address-search-node-custom&panelId=1&width=1000&height=500&tz=Europe%2FMoscow"
            },
            {
                "name": "micro-address-search-node-custom_mem",
                "grafana_url": "/render/d-solo/a164a7f0339f99e89cea5cb47e9be617/kubernetes-compute-resources-workload?orgId=1&var-datasource=c821f414-4bcf-4a76-910b-13ccf2d3f9b5&var-cluster=&var-namespace=apps&var-type=statefulset&var-workload=micro-address-search-node-custom&panelId=3&width=1000&height=500&tz=Europe%2FMoscow"
            },
             {
                "name": "micro-registry-incident-schedule_cpu",
                "grafana_url": "/render/d-solo/a164a7f0339f99e89cea5cb47e9be617/kubernetes-compute-resources-workload?orgId=1&var-datasource=c821f414-4bcf-4a76-910b-13ccf2d3f9b5&var-cluster=&var-namespace=apps&var-type=deployment&var-workload=micro-registry-incident-schedule&panelId=1&width=1000&height=500&tz=Europe%2FMoscow"
            },
            {
                "name": "micro-registry-incident-schedule_mem",
                "grafana_url": "/render/d-solo/a164a7f0339f99e89cea5cb47e9be617/kubernetes-compute-resources-workload?orgId=1&var-datasource=c821f414-4bcf-4a76-910b-13ccf2d3f9b5&var-cluster=&var-namespace=apps&var-type=deployment&var-workload=micro-registry-incident-schedule&panelId=3&width=1000&height=500&tz=Europe%2FMoscow"
            },
        ],
        "logs": [
            {
                "placeholder": "micro-address-search-node",
                "filter_query": '{namespace=~"apps", service_name=~"micro-address-search-node"} |= "ERROR"'
            },
            {
                "placeholder": "micro-registry-address",
                "filter_query": '{namespace=~"apps", service_name=~"micro-registry-address"} |= "ERROR"'
            },
            {
                "placeholder": "micro-registry-nsi",
                "filter_query": '{namespace=~"apps", service_name=~"micro-registry-nsi"} |= "ERROR"'
            },
            {
                "placeholder": "micro-address-search-node-kafka",
                "filter_query": '{namespace=~"apps", service_name=~"micro-address-search-node-kafka"} |= "ERROR"'
            },
            {
                "placeholder": "micro-address-search-node-custom",
                "filter_query": '{namespace=~"apps", service_name=~"micro-address-search-node-custom"} |= "ERROR"'
            },
            {
                "placeholder": "micro-registry-incident-schedule",
                "filter_query": '{namespace=~"apps", service_name=~"micro-registry-incident-schedule"} |= "ERROR"'
            },
            {
                "placeholder": "micro-registry-incident",
                "filter_query": '{namespace=~"apps", service_name=~"micro-registry-incident"} |= "ERROR"'
            }
        ]

    },
    "service_2": { # Сокращенное наименование СПО на английском например INP, PAIP, RUIP, нужно также ввести название в СПО в шаблон веб страницы(templates\index.html)
        "page_sample_id": "682908704",  # Шаблон страницы Confluence для service_2
        "page_parent_id": "652073177",  # Страница Confluence для складирования готовых отчетов
        "metrics": [
            {
                "name": "RPMKafka",
                "grafana_url": "/render/d-solo/XKhgaUpikugigf/k6-kafka?orgId=1&panelId=77&width=1000&height=500&tz=Europe%2FMoscow"
            },
            {
                "name": "RPMTypes",
                "grafana_url": "/render/d-solo/XKhgaUpikugigf/k6-kafka?orgId=1&panelId=78&width=1000&height=500&tz=Europe%2FMoscow"
            },
            {
                "name": "ResponseTimeTypes",
                "grafana_url": "/render/d-solo/XKhgaUpikugigf/k6-kafka?orgId=1&panelId=76&width=1000&height=500&tz=Europe%2FMoscow"
            },
            {
                "name": "kafkarequest",
                "grafana_url": "/render/d-solo/XKhgaUpikugigf/k6-kafka?orgId=1&panelId=79&width=1000&height=500&tz=Europe%2FMoscow"
            }
        ],
        "logs": [
            {
                "placeholder": "micro-address-search-node",
                "filter_query": '{namespace=~"apps", service_name=~"micro-address-search-node"} |= "ERROR"'
            },
            {
                "placeholder": "micro-registry-incident",
                "filter_query": '{namespace=~"apps", service_name=~"micro-registry-incident"} |= "ERROR"'
            }
        ]
    }
}
