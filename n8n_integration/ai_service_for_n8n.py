"""
AI Analyzer Microservice для интеграции с n8n workflow

Этот микросервис предоставляет REST API для AI-анализа метрик
и может быть вызван из n8n через HTTP Request узел.
"""

from flask import Flask, request, jsonify
from AI.main import uploadFromLLM
from confluence_manager.update_confluence_template import render_llm_markdown
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/health', methods=['GET'])
def health():
    """Проверка здоровья сервиса"""
    return jsonify({"status": "healthy"}), 200


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Анализирует метрики за указанный период
    
    Входные параметры (JSON):
    {
        "start": 1708513800000,  // timestamp в миллисекундах
        "end": 1708523400000     // timestamp в миллисекундах
    }
    
    Выходные данные (JSON):
    {
        "status": "success",
        "data": {
            "jvm": "markdown текст",
            "database": "markdown текст",
            "kafka": "markdown текст",
            "microservices": "markdown текст",
            "final": "markdown текст",
            "placeholders": {
                "$$answer_jvm$$": "html для confluence",
                "$$answer_database$$": "html для confluence",
                ...
            }
        }
    }
    """
    try:
        data = request.json
        
        # Валидация входных данных
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        start = data.get('start')
        end = data.get('end')
        
        if not start or not end:
            return jsonify({
                "status": "error",
                "message": "Missing required parameters: start, end"
            }), 400
        
        # Конвертируем из миллисекунд в секунды для uploadFromLLM
        start_ts = float(start) / 1000.0
        end_ts = float(end) / 1000.0
        
        logger.info(f"Starting AI analysis for period: {start_ts} - {end_ts}")
        
        # Вызываем AI-анализ
        results = uploadFromLLM(start_ts, end_ts)
        
        # Подготавливаем плейсхолдеры для Confluence
        placeholders = {}
        
        # Доменные разделы
        if results.get("jvm"):
            placeholders["$$answer_jvm$$"] = results["jvm"]
        
        if results.get("database"):
            placeholders["$$answer_database$$"] = results["database"]
        
        if results.get("kafka"):
            placeholders["$$answer_kafka$$"] = results["kafka"]
        
        if results.get("ms"):
            placeholders["$$answer_ms$$"] = results["ms"]
        
        # Итоговый раздел - используем структурированный markdown если есть
        final_struct = results.get("final_parsed")
        if isinstance(final_struct, dict) and final_struct:
            md = render_llm_markdown(final_struct)
            if md.strip():
                placeholders["$$answer_llm$$"] = md
                placeholders["$$final_answer$$"] = md
        else:
            # Фолбэк: текстовый ответ
            final_text = results.get("final")
            if isinstance(final_text, str) and final_text.strip():
                md_fallback = f"### Итог LLM\n\n{final_text}"
                placeholders["$$final_answer$$"] = md_fallback
                placeholders["$$answer_llm$$"] = md_fallback
        
        # Структурированные данные для всех доменов
        structured_data = {
            "jvm_parsed": results.get("jvm_parsed"),
            "database_parsed": results.get("database_parsed"),
            "kafka_parsed": results.get("kafka_parsed"),
            "ms_parsed": results.get("ms_parsed"),
            "final_parsed": results.get("final_parsed")
        }
        
        logger.info("AI analysis completed successfully")
        
        return jsonify({
            "status": "success",
            "data": {
                "raw_results": results,
                "placeholders": placeholders,
                "structured": structured_data
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error during AI analysis: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"AI analysis failed: {str(e)}"
        }), 500


@app.route('/analyze/domain/<domain>', methods=['POST'])
def analyze_domain(domain):
    """
    Анализирует конкретный домен (jvm, database, kafka, microservices)
    
    Полезно для частичного анализа или переанализа одного домена
    """
    try:
        data = request.json
        start = data.get('start')
        end = data.get('end')
        
        if not start or not end:
            return jsonify({
                "status": "error",
                "message": "Missing required parameters: start, end"
            }), 400
        
        start_ts = float(start) / 1000.0
        end_ts = float(end) / 1000.0
        
        logger.info(f"Analyzing domain '{domain}' for period: {start_ts} - {end_ts}")
        
        # Запускаем полный анализ (можно оптимизировать для конкретного домена)
        results = uploadFromLLM(start_ts, end_ts)
        
        # Возвращаем результат только для запрошенного домена
        domain_map = {
            "jvm": ("jvm", "jvm_parsed"),
            "database": ("database", "database_parsed"),
            "kafka": ("kafka", "kafka_parsed"),
            "microservices": ("ms", "ms_parsed")
        }
        
        if domain not in domain_map:
            return jsonify({
                "status": "error",
                "message": f"Unknown domain: {domain}. Available: jvm, database, kafka, microservices"
            }), 400
        
        text_key, parsed_key = domain_map[domain]
        
        return jsonify({
            "status": "success",
            "data": {
                "domain": domain,
                "text": results.get(text_key),
                "parsed": results.get(parsed_key)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error analyzing domain {domain}: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"Domain analysis failed: {str(e)}"
        }), 500


@app.route('/config/check', methods=['GET'])
def check_config():
    """
    Проверяет конфигурацию AI-модуля
    
    Полезно для диагностики проблем с подключением к Prometheus, GigaChat и т.д.
    """
    try:
        from AI.config import CONFIG
        
        config_status = {
            "prometheus_url": CONFIG.get("prometheus", {}).get("url"),
            "metrics_source_type": CONFIG.get("metrics_source", {}).get("type"),
            "llm_provider": CONFIG.get("llm", {}).get("provider"),
            "gigachat_model": CONFIG.get("llm", {}).get("gigachat", {}).get("model"),
            "step": CONFIG.get("default_params", {}).get("step"),
            "resample_interval": CONFIG.get("default_params", {}).get("resample_interval")
        }
        
        return jsonify({
            "status": "success",
            "config": config_status
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Config check failed: {str(e)}"
        }), 500


if __name__ == '__main__':
    import os
    
    # Настройки из переменных окружения или дефолтные
    host = os.getenv('AI_SERVICE_HOST', '0.0.0.0')
    port = int(os.getenv('AI_SERVICE_PORT', 5001))
    debug = os.getenv('AI_SERVICE_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting AI Analyzer Service on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)

