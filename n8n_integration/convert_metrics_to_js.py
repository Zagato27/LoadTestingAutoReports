#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для конвертации metrics_config.py (Python) в JavaScript формат для n8n workflow
"""

import json
from metrics_config import METRICS_CONFIG

def convert_to_js():
    """Конвертирует Python конфиг в JavaScript формат"""
    
    # Создаем новый конфиг с добавлением необходимых полей
    js_config = {}
    
    for service_name, service_data in METRICS_CONFIG.items():
        js_config[service_name] = {
            "confluence_url": "https://confluence.test.ru",  # Укажите ваш URL
            "page_sample_id": service_data.get("page_sample_id", ""),
            "page_parent_id": service_data.get("page_parent_id", ""),
            "grafana_base_url": "http://0.0.0.0:3000",  # Укажите ваш Grafana URL
            "space_conf": "DPSUPP",  # Confluence space (опционально)
            "metrics": service_data.get("metrics", [])
        }
    
    # Конвертируем в JSON
    js_code = json.dumps(js_config, indent=2, ensure_ascii=False)
    
    # Формируем полный код для n8n
    full_code = f"""const service = $input.first().json.service;

const METRICS_CONFIG = {js_code};

const config = METRICS_CONFIG[service];
if (!config) {{
  throw new Error(`Service ${{service}} not found in config`);
}}

return {{ json: config }};"""
    
    return full_code

def count_metrics():
    """Подсчитывает количество метрик"""
    total = 0
    for service_name, service_data in METRICS_CONFIG.items():
        metrics = service_data.get("metrics", [])
        print(f"\n{service_name}: {len(metrics)} метрик")
        total += len(metrics)
    return total

if __name__ == "__main__":
    print("=" * 60)
    print("Конвертация metrics_config.py → JavaScript для n8n")
    print("=" * 60)
    
    # Подсчет метрик
    total_metrics = count_metrics()
    print(f"\nВсего метрик: {total_metrics}")
    
    # Конвертация
    print("\n" + "=" * 60)
    print("Сгенерированный JavaScript код:")
    print("=" * 60)
    
    js_code = convert_to_js()
    print(js_code)
    
    # Сохранение в файл
    output_file = "n8n_metrics_config.js"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(js_code)
    
    print("\n" + "=" * 60)
    print(f"✅ Код сохранен в файл: {output_file}")
    print("=" * 60)
    
    print("\n📋 Инструкция:")
    print("1. Откройте n8n: http://localhost:5678")
    print("2. Откройте workflow")
    print("3. Найдите узел 'Get Service Config'")
    print(f"4. Скопируйте содержимое {output_file}")
    print("5. Вставьте в поле JavaScript кода")
    print("6. Сохраните workflow")
    
    print("\n⚠️  Не забудьте:")
    print("• Изменить confluence_url на ваш URL")
    print("• Изменить grafana_base_url на ваш Grafana URL")
    print("• Проверить page_sample_id и page_parent_id")

