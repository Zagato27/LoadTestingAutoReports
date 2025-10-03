# n8n Integration

Все файлы, связанные с **n8n workflow** и **AI-интеграцией**, перенесены в директорию:

## 📂 [`n8n_integration/`](n8n_integration/)

### Что там находится:

✅ **n8n workflows** - готовые к импорту workflow файлы  
✅ **AI-микросервис** - Flask REST API для AI-анализа  
✅ **Docker конфигурация** - docker-compose и Dockerfile  
✅ **Скрипты развертывания** - автоматизация установки и тестирования  
✅ **Полная документация** - от быстрого старта до troubleshooting  

---

## 🚀 Быстрый старт

```bash
# Перейдите в директорию
cd n8n_integration

# Следуйте инструкциям
cat START_HERE.md
```

или

```bash
# Автоматическое развертывание
cd n8n_integration
./deploy_ai_service.sh
```

---

## 📚 Документация

Полная документация находится в директории `n8n_integration/`:

- **[START_HERE.md](n8n_integration/START_HERE.md)** ⭐ - начните отсюда
- **[QUICK_START_AI.md](n8n_integration/QUICK_START_AI.md)** - быстрый старт за 5 минут
- **[AI_INTEGRATION_GUIDE.md](n8n_integration/AI_INTEGRATION_GUIDE.md)** - детальное руководство
- **[README.md](n8n_integration/README.md)** - обзор директории

---

## 🎯 Что это дает?

Полная альтернатива Python Flask-сервису:

- **Визуальный workflow** в n8n
- **AI-анализ метрик** через отдельный микросервис
- **Параллельная обработка** Grafana + Loki + AI
- **Docker-контейнеризация** всего стека
- **Автоматизация** развертывания и тестирования

---

## ⚡ Структура проекта

```
LoadTestingAutoReports/
├── app.py                      # Оригинальный Python Flask сервис
├── AI/                         # AI-модуль (используется обоими вариантами)
├── data_collectors/            # Сборщики данных
├── confluence_manager/         # Работа с Confluence
├── n8n_integration/           # ⭐ ВСЁ ДЛЯ n8n ЗДЕСЬ
│   ├── n8n_load_testing_workflow_with_ai.json
│   ├── ai_service_for_n8n.py
│   ├── docker-compose.n8n.yml
│   ├── deploy_ai_service.sh
│   ├── test_ai_integration.sh
│   ├── START_HERE.md
│   └── ... (вся документация)
└── README.md                   # Основной README проекта
```

---

## 📖 Дальнейшие действия

1. Перейдите в `n8n_integration/`
2. Прочитайте `START_HERE.md`
3. Запустите `./deploy_ai_service.sh`
4. Наслаждайтесь! 🎉

---

**Для возврата к Python Flask сервису:** используйте файлы в корне проекта (`app.py`, `update_page.py`, и т.д.)

