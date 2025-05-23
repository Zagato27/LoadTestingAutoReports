---

# Load Testing Report AI 

Эта часть проекта предназначена для автоматизированного получения метрик нагрузочного тестирования из [Prometheus](https://prometheus.io/), их агрегации в формате DataFrame с помощью [pandas](https://pandas.pydata.org/), последующего анализа с использованием LLM (например, через API OpenAI) и формирования сводного отчёта по системе. Также предусмотрена возможность обновления страницы в Confluence с итоговым отчётом.

---

## Оглавление

- [Особенности](#особенности)
- [Требования](#требования)
- [Установка](#установка)
- [Конфигурация](#конфигурация)
- [Использование](#использование)
- [Описание кода](#описание-кода)
- [Дополнительно](#дополнительно)

---

## Особенности

- **Получение данных из Prometheus:**  
  Выполняет PromQL-запросы по заданному интервалу времени и получает сырые JSON-данные.

- **Агрегация и обработка данных:**  
  Преобразует полученные метрики в DataFrame с учётом указанных лейблов и выполняет ресемплирование по заданному интервалу.

- **Интеграция с LLM:**  
  Формирует запросы к LLM с включением CSV-данных, полученных из DataFrame, для автоматизированного анализа и формирования отчёта.

- **Работа с промтами:**  
  Читает текстовые шаблоны (промты) из директории `prompts`, что позволяет гибко менять логику анализа для каждого компонента (JVM, ArangoDB, Kafka, Microservices).

- **Объединение отчётов:**  
  На основе индивидуальных ответов для каждой группы метрик формируется сводный отчёт, который можно использовать для дальнейшего анализа.

- **(Опционально) Обновление Confluence:**  
  Реализована (на данный момент закомментирована) возможность обновления страницы Confluence с итоговым отчётом.

---

## Требования

- Python 3.7+
- Зависимости:
  - `requests`
  - `pandas`
  - `openai`
  - `atlassian-python-api`
  - `beautifulsoup4`
  - `getpass`

> **Примечание:** Убедитесь, что файл конфигурации `AI/config.py` присутствует и содержит все необходимые параметры.

---

## Установка

1. **Клонируйте репозиторий:**

   ```bash
   git clone https://github.com/your-username/load-testing-report-generator.git
   cd load-testing-report-generator
   ```

2. **Установите зависимости:**

   Если есть файл `requirements.txt`, выполните:

   ```bash
   pip install -r requirements.txt
   ```

   Либо установите вручную:

   ```bash
   pip install requests pandas openai atlassian-python-api beautifulsoup4
   ```

3. **Структура проекта:**

   ```
   ├── AI
   │   └── config.py         # Файл конфигурации с настройками Prometheus, LLM, запросов и др.
   ├── prompts
   │   ├── jvm_prompt.txt
   │   ├── arangodb_prompt.txt
   │   ├── kafka_prompt.txt
   │   ├── microservices_prompt.txt
   │   └── overall_prompt.txt
   ├── main.py               # Основной скрипт с логикой обработки данных и вызовом LLM
   └── README.md
   ```

---

## Конфигурация

Файл `AI/config.py` должен содержать необходимые настройки, например:

- **Prometheus:**
  - `url` – URL-адрес сервера Prometheus.
  
- **LLM:**
  - `api_key` – API ключ для доступа к модели.
  - `model` – Имя модели (например, `"sonar-deep-research"`).
  - `base_url` – URL для API LLM (например, `"https://api.perplexity.ai"`).

- **Default параметры:**
  - `step` – Шаг для запроса метрик (например, `"1m"` или `"30s"`).
  - `resample_interval` – Интервал ресемплирования данных (например, `"1T"`, `"5T"`).

- **Запросы для различных компонентов:**
  - Подключены секции `queries` с настройками для JVM, ArangoDB, Kafka и Microservices:
    - `promql_queries` – список PromQL-запросов.
    - `label_keys_list` – список списков ключей меток для соответствующих запросов.
    - `labels` – метки, используемые для обозначения полученных DataFrame.

---

## Использование

1. **Подготовка данных:**

   - Убедитесь, что файл конфигурации корректно настроен.
   - Проверьте, что все необходимые промт-файлы находятся в директории `prompts`.

2. **Запуск скрипта:**

   Функция `uploadFromDeepSeek(start_ts, end_ts)` в файле `main.py` объединяет все шаги:
   - Получение данных из Prometheus.
   - Аггрегация и обработка метрик для каждого компонента.
   - Отправка данных в LLM для анализа и формирования отчётов.
   - Формирование итогового сводного отчёта.

   Вы можете запустить основной процесс, вызвав эту функцию, например, через блок `if __name__ == "__main__":` (на данный момент код запуска закомментирован). Пример:

   ```python
   if __name__ == "__main__":
       # Задайте интервалы времени в формате timestamp (в секундах)
       start_ts = 1740126600
       end_ts = 1740136200

       final_report = uploadFromDeepSeek(start_ts, end_ts)
       print("Итоговый отчёт:")
       print(final_report)
   ```

3. **(Опционально) Обновление Confluence:**

   - Функция `update_confluence_page` (в данный момент закомментирована) позволяет обновить страницу в Confluence с итоговым отчётом.
   - Для её использования раскомментируйте код и настройте параметры доступа.

---

## Описание кода

- **Конвертация времени:**  
  `convert_to_timestamp(date_str)` – преобразует строку даты и времени в Unix timestamp.

- **Преобразование шага:**  
  `parse_step_to_seconds(step)` – преобразует строку с указанием шага (например, `"1m"` или `"30s"`) в секунды.

- **Получение данных из Prometheus:**  
  `fetch_prometheus_data()` – отправляет запрос к API Prometheus с параметрами `query_range` и возвращает данные в формате JSON.

- **Агрегация данных в DataFrame:**  
  `fetch_and_aggregate_with_label_keys()` – выполняет несколько PromQL-запросов, обрабатывает полученные данные, строит DataFrame и выполняет ресемплирование.

- **Маркировка DataFrame:**  
  `label_dataframes()` – сопоставляет каждому DataFrame заданную метку для удобства дальнейшего анализа.

- **Вызов LLM для анализа:**  
  `ask_llm_with_labeled_dataframes()` – формирует системное и пользовательское сообщение, объединяет CSV-представление DataFrame и отправляет запрос к LLM. Полученный ответ используется для составления отчёта.

- **Чтение промтов из файла:**  
  `read_prompt_from_file()` – считывает содержимое файла с промтом, учитывая кодировку UTF-8.

- **Основной рабочий процесс:**  
  `uploadFromDeepSeek()` – объединяет все вышеописанные шаги:
  - Чтение конфигурации.
  - Получение и агрегация метрик для компонентов (JVM, ArangoDB, Kafka, Microservices).
  - Получение индивидуальных ответов от LLM.
  - Формирование сводного отчёта на основе шаблона `overall_prompt.txt`.

- **(Закомментирован) Обновление Confluence:**  
  Функция `update_confluence_page()` позволяет обновлять содержимое страницы Confluence, используя библиотеку `atlassian`.

---

## Дополнительно

- **Расширение функционала:**  
  При необходимости можно добавлять новые PromQL-запросы или новые секции анализа, дополняя конфигурационный файл и соответствующие промты.

- **Отладка и логирование:**  
  Рекомендуется добавить обработку ошибок и логирование для удобства мониторинга работы скрипта.

- **Контрибьюции:**  
  Если вы хотите внести улучшения или новые функции – форкайте репозиторий и отправляйте pull request.

---

Этот README даёт общее представление о структуре проекта и его возможностях. Настройте конфигурацию и промты под свои задачи, чтобы начать получать автоматизированные отчёты по нагрузочному тестированию.

