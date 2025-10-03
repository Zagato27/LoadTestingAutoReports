# 📁 Структура директории n8n_integration

```
n8n_integration/
│
├── 🌟 Основные файлы
│   ├── n8n_load_testing_workflow_with_ai.json  (29K)  ⭐ Workflow с AI
│   ├── n8n_load_testing_workflow.json          (23K)     Базовый workflow
│   ├── ai_service_for_n8n.py                   (8.4K) ⭐ AI REST API
│   │
├── 🐳 Docker
│   ├── docker-compose.n8n.yml                  (2.2K) ⭐ Docker Compose
│   ├── Dockerfile.ai_service                   (918B)    Docker образ
│   ├── env.example.txt                         (763B)    Шаблон .env
│   │
├── 🔧 Скрипты
│   ├── deploy_ai_service.sh                    (9.6K) ⭐ Развертывание
│   ├── test_ai_integration.sh                  (13K)  ⭐ Тестирование
│   │
└── 📚 Документация
    ├── README.md                               (11K)  ⭐ Главный README
    ├── START_HERE.md                           (9.1K) ⭐ Точка входа
    ├── QUICK_START_AI.md                       (7.8K)    Быстрый старт
    ├── AI_INTEGRATION_GUIDE.md                 (17K)     Детальное руководство
    ├── README_N8N_MIGRATION.md                 (12K)     Миграция
    ├── N8N_MIGRATION_GUIDE.md                  (8.4K)    Расширенная док
    └── README_AI_FILES.md                      (13K)     Список файлов
```

## 📊 Итого

- **Workflows:** 2 файла (52K)
- **Код:** 1 файл (8.4K)
- **Docker:** 3 файла (3.9K)
- **Скрипты:** 2 файла (22.6K)
- **Документация:** 7 файлов (78.3K)

**Всего:** 15 файлов (~165K)

---

## 🎯 С чего начать?

1. **[START_HERE.md](START_HERE.md)** ⭐
2. **[QUICK_START_AI.md](QUICK_START_AI.md)**
3. **[README.md](README.md)**

---

## 🚀 Быстрые команды

```bash
# Развертывание
./deploy_ai_service.sh

# Тестирование
./test_ai_integration.sh

# Логи
docker-compose -f docker-compose.n8n.yml logs -f
```
