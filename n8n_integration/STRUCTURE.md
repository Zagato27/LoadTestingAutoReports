# 📁 Структура n8n_integration

```
n8n_integration/                      # Изолированный проект
│
├── 🌟 Workflow
│   └── n8n_workflow_simple.json     (21K)  # Упрощенный workflow без Loki
│
├── 💻 AI-сервис
│   ├── ai_service_for_n8n.py        (8.4K) # Flask REST API
│   ├── AI/                                  # AI-модуль (изолированная копия)
│   │   ├── main.py                          # Основная логика анализа
│   │   ├── config.py                        # Конфигурация AI
│   │   └── prompts/                         # Промпты для LLM
│   ├── confluence_manager/                  # Confluence утилиты (копия)
│   │   └── update_confluence_template.py
│   ├── config.py                    (652B)  # Базовые настройки
│   ├── metrics_config.py            (14K)   # Полная конфигурация метрик
│   └── metrics_config_example.py    (5.7K)  # Упрощенный пример
│
├── 🐳 Docker
│   ├── docker-compose.yml           (2.1K) # Docker Compose стек
│   ├── Dockerfile                   (1.1K) # AI-сервис образ
│   ├── env.example.txt              (763B) # Шаблон .env
│   └── requirements.txt             (431B) # Python зависимости
│
├── 🔧 Скрипты
│   ├── deploy_ai_service.sh         (9.5K) # Автоматическое развертывание
│   └── test_ai_integration.sh       (13K)  # Автоматическое тестирование
│
└── 📚 Документация
    ├── README.md                    (10K)  # Главная документация
    ├── QUICKSTART.md                (4.7K) # Быстрый старт
    ├── METRICS_CONFIG_GUIDE.md              # Настройка метрик
    └── STRUCTURE.md                         # Этот файл
```

## 📊 Статистика

- **Workflow:** 1 файл (21K)
- **Код:** 1 файл + 2 модуля
- **Docker:** 4 файла (4.4K)
- **Скрипты:** 2 файла (22.5K)
- **Документация:** 3 файла

**Всего:** ~15 файлов + зависимости (AI/, confluence_manager/)

---

## 🎯 Ключевые файлы

| Файл | Назначение |
|------|------------|
| **README.md** | Полная документация |
| **QUICKSTART.md** | Быстрый старт за 5 минут |
| **n8n_workflow_simple.json** | Workflow для импорта в n8n |
| **ai_service_for_n8n.py** | AI REST API (Flask) |
| **docker-compose.yml** | Запуск всего стека |
| **deploy_ai_service.sh** | Автоматическая установка |

---

## ✨ Особенности

✅ **Полная изоляция** - все зависимости внутри  
✅ **Без Loki** - упрощенная версия  
✅ **AI-анализ** - 4 домена (JVM, DB, Kafka, Microservices)  
✅ **Автономность** - не зависит от родительских директорий  

---

## 🚀 Быстрый старт

```bash
# 1. Настройка
cp env.example.txt .env && nano .env

# 2. Запуск
./deploy_ai_service.sh

# 3. Импорт в n8n
# http://localhost:5678 → Import → n8n_workflow_simple.json

# 4. Тест
./test_ai_integration.sh quick
```
