from confluence_manager.update_confluence_template import copy_confluence_page, update_confluence_page
from AI.main import uploadFromDeepSeek

from concurrent.futures import ThreadPoolExecutor, as_completed
from data_collectors.grafana_collector import uploadFromGrafana
from data_collectors.loki_collector import uploadFromLoki
from config import CONFIG  # Импорт базовой конфигурации
from metrics_config import METRICS_CONFIG  # Импорт конфигурации метрик
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime  # если ещё не импортирован
import traceback  # для детального вывода ошибок (опционально)


def update_report(start, end, service):
    # Получение параметров из `config.py`
    user = CONFIG['user']
    password = CONFIG['password']
    grafana_login = CONFIG['grafana_login']
    grafana_pass = CONFIG['grafana_pass']
    url_basic = CONFIG['url_basic']
    space_conf = CONFIG['space_conf']
    grafana_base_url = CONFIG['grafana_base_url']
    loki_url = CONFIG['loki_url']

    
    # Получаем конфигурацию сервиса и проверяем наличие метрик
    service_config = METRICS_CONFIG.get(service)
    if not service_config:
        raise ValueError(f"Конфигурация для сервиса '{service}' не найдена.")
    
    # Получаем `page_sample_id` и `page_parent_id` из конфигурации сервиса
    page_parent_id = service_config["page_parent_id"]
    page_sample_id = service_config["page_sample_id"]
    copy_page_id = copy_confluence_page(url_basic, user, password, page_sample_id, page_parent_id)
   

    # Список задач для обновлений
    tasks = []
    
                
    # Добавим функцию обновления с повторными попытками
    def update_with_retry(url, username, password, page_id, data_to_find, replace_text, max_attempts=3):
        for attempt in range(max_attempts):
            try:
                return update_confluence_page(url, username, password, page_id, data_to_find, replace_text)
            except Exception as e:
                if "Attempted to update stale data" in str(e) and attempt < max_attempts-1:
                    print(f"Попытка {attempt+1} не удалась, повторяем через 1 секунду...")
                    time.sleep(1)  # Небольшая задержка перед повторной попыткой
                else:
                    raise e

    # Основной код с разделением параллельных и последовательных операций
    metrics_logs_tasks = []

    with ThreadPoolExecutor() as executor:
        # Добавляем задачи для каждой метрики, указанной для выбранного сервиса
        for metric in service_config["metrics"]:
            # Формируем полный URL для метрики с учетом базового URL Grafana и временного диапазона
            grafana_url = f"{grafana_base_url}{metric['grafana_url']}&from={start}&to={end}"
            name = metric['name']

            # Добавляем задачу для загрузки метрики и обновления Confluence
            metrics_logs_tasks.append(executor.submit(
                update_confluence_page,
                url_basic, user, password, copy_page_id,
                f"$${name}$$",
                uploadFromGrafana(user, password, url_basic, space_conf, copy_page_id, [[name, grafana_url]], service, grafana_login, grafana_pass)
            ))

        # Добавление задач для логов, если они есть в конфигурации сервиса
        for log in service_config.get("logs", []):
            placeholder = log["placeholder"]
            filter_query = log["filter_query"]

            metrics_logs_tasks.append(executor.submit(
                update_confluence_page,
                url_basic, user, password, copy_page_id,
                f"$${placeholder}$$",
                uploadFromLoki(loki_url, start, end, filter_query, user, password, url_basic, copy_page_id, service, placeholder)
            ))
        
        # Обработка результатов метрик и логов
        for future in as_completed(metrics_logs_tasks):
            try:
                result = future.result()
                print(f"Метрика/лог обновлены: {result}")
            except Exception as e:
                print(f"Ошибка при обновлении метрики/лога: {e}")

    # Получаем результаты DeepSeek и обновляем их последовательно
    results = uploadFromDeepSeek(start/1000, end/1000)

    # Последовательное обновление для предотвращения конфликтов версий
    try:
        print("Обновление данных DeepSeek...")
        
        # Последовательно обновляем каждый раздел с повторными попытками
        update_with_retry(url_basic, user, password, copy_page_id, "$$final_answer$$", results["final"])
        print("✓ Итоговый ответ обновлен")
        
        update_with_retry(url_basic, user, password, copy_page_id, "$$answer_jvm$$", results["jvm"])
        print("✓ JVM обновлен")
        
        update_with_retry(url_basic, user, password, copy_page_id, "$$answer_arangodb$$", results["arangodb"])
        print("✓ ArangoDB обновлен")
        
        update_with_retry(url_basic, user, password, copy_page_id, "$$answer_kafka$$", results["kafka"])
        print("✓ Kafka обновлен")
        
        update_with_retry(url_basic, user, password, copy_page_id, "$$answer_ms$$", results["ms"])
        print("✓ Microservices обновлен")
        
        print("Все данные DeepSeek успешно обновлены")
    except Exception as e:
        print(f"Ошибка при последовательном обновлении данных DeepSeek: {e}")

