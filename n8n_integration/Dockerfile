# Dockerfile для изолированного AI-сервиса

FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код (все зависимости внутри директории)
COPY AI/ ./AI/
COPY confluence_manager/ ./confluence_manager/
COPY ai_service_for_n8n.py .

# Создаем директорию для временных файлов
RUN mkdir -p /app/data_collectors/temporary_files

# Создаем пользователя для запуска (безопасность)
RUN useradd -m -u 1000 aiservice && \
    chown -R aiservice:aiservice /app

USER aiservice

# Открываем порт
EXPOSE 5001

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5001/health')"

# Запускаем сервис
CMD ["python", "ai_service_for_n8n.py"]

