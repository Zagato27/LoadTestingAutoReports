#!/bin/bash

###############################################################################
# Скрипт тестирования AI-интеграции с n8n
###############################################################################

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Переменные
N8N_URL="${N8N_URL:-http://localhost:5678}"
AI_SERVICE_URL="${AI_SERVICE_URL:-http://localhost:5001}"
WEBHOOK_PATH="/webhook/load-testing/report/create"

# Счетчики тестов
TESTS_PASSED=0
TESTS_FAILED=0

# Функции для вывода
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1"
    ((TESTS_PASSED++))
}

error() {
    echo -e "${RED}[✗]${NC} $1"
    ((TESTS_FAILED++))
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Тест: Healthcheck AI-сервиса
test_ai_health() {
    info "Тест 1: Проверка здоровья AI-сервиса..."
    
    local response=$(curl -s -w "\n%{http_code}" "${AI_SERVICE_URL}/health" 2>/dev/null || echo "000")
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ] && echo "$body" | grep -q "healthy"; then
        success "AI-сервис здоров"
        return 0
    else
        error "AI-сервис недоступен (HTTP $http_code)"
        return 1
    fi
}

# Тест: Проверка конфигурации AI
test_ai_config() {
    info "Тест 2: Проверка конфигурации AI-сервиса..."
    
    local response=$(curl -s "${AI_SERVICE_URL}/config/check" 2>/dev/null || echo "")
    
    if echo "$response" | grep -q "prometheus_url"; then
        success "Конфигурация AI-сервиса доступна"
        info "  Prometheus URL: $(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('config', {}).get('prometheus_url', 'N/A'))" 2>/dev/null || echo "N/A")"
        info "  LLM Provider: $(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('config', {}).get('llm_provider', 'N/A'))" 2>/dev/null || echo "N/A")"
        return 0
    else
        error "Не удалось получить конфигурацию AI-сервиса"
        return 1
    fi
}

# Тест: AI-анализ (с тестовыми данными)
test_ai_analyze() {
    info "Тест 3: Тестовый AI-анализ..."
    
    local start=$(date -d '1 hour ago' +%s)000
    local end=$(date +%s)000
    
    local payload=$(cat <<EOF
{
  "start": $start,
  "end": $end
}
EOF
)
    
    info "  Период: последний час"
    info "  Запрос AI-анализа (это может занять 1-5 минут)..."
    
    local response=$(curl -s -w "\n%{http_code}" \
        -X POST "${AI_SERVICE_URL}/analyze" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        2>/dev/null || echo "000")
    
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        if echo "$body" | grep -q '"status":"success"'; then
            success "AI-анализ выполнен успешно"
            
            # Проверяем наличие плейсхолдеров
            local placeholders=$(echo "$body" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('data', {}).get('placeholders', {})))" 2>/dev/null || echo "0")
            info "  Количество плейсхолдеров: $placeholders"
            
            return 0
        else
            error "AI-анализ вернул ошибку: $(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin).get('message', 'Unknown error'))" 2>/dev/null || echo "Unknown")"
            return 1
        fi
    else
        error "Ошибка при вызове AI-анализа (HTTP $http_code)"
        return 1
    fi
}

# Тест: Доступность n8n
test_n8n_health() {
    info "Тест 4: Проверка доступности n8n..."
    
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" "$N8N_URL" 2>/dev/null || echo "000")
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "302" ]; then
        success "n8n доступен"
        return 0
    else
        error "n8n недоступен (HTTP $http_code)"
        return 1
    fi
}

# Тест: Webhook n8n (без создания реального отчета)
test_n8n_webhook() {
    info "Тест 5: Проверка webhook n8n (dry-run)..."
    
    # Отправляем запрос с некорректными данными для проверки валидации
    local response=$(curl -s -w "\n%{http_code}" \
        -X POST "${N8N_URL}${WEBHOOK_PATH}" \
        -H "Content-Type: application/json" \
        -d '{}' \
        2>/dev/null || echo "000")
    
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)
    
    # Ожидаем ошибку валидации (400), что подтвердит работу webhook
    if [ "$http_code" = "400" ]; then
        if echo "$body" | grep -q "Missing required parameters"; then
            success "n8n webhook работает (валидация параметров активна)"
            return 0
        fi
    fi
    
    warning "n8n webhook может быть не настроен или workflow не активен"
    info "  Убедитесь, что workflow импортирован и активирован"
    return 0
}

# Тест: Полный цикл (создание отчета) - опционально
test_full_cycle() {
    info "Тест 6: Полный цикл создания отчета (ОПЦИОНАЛЬНО)..."
    
    read -p "Запустить полный тест с созданием реального отчета? (y/n) " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        warning "Пропущен полный тест"
        return 0
    fi
    
    # Запрашиваем параметры
    echo "Введите параметры для теста:"
    read -p "Service name (например, NSI): " service_name
    read -p "Start time (YYYY-MM-DDTHH:MM): " start_time
    read -p "End time (YYYY-MM-DDTHH:MM): " end_time
    
    local payload=$(cat <<EOF
{
  "start": "$start_time",
  "end": "$end_time",
  "service": "$service_name"
}
EOF
)
    
    info "  Создание отчета (это может занять 5-10 минут)..."
    info "  Параметры:"
    info "    Service: $service_name"
    info "    Period: $start_time - $end_time"
    
    local response=$(curl -s -w "\n%{http_code}" \
        -X POST "${N8N_URL}${WEBHOOK_PATH}" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        --max-time 600 \
        2>/dev/null || echo "000")
    
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        if echo "$body" | grep -q '"status":"success"'; then
            success "Отчет создан успешно!"
            
            local page_url=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin).get('page_url', 'N/A'))" 2>/dev/null || echo "N/A")
            info "  Ссылка на отчет: $page_url"
            
            return 0
        else
            error "Ошибка при создании отчета: $(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin).get('message', 'Unknown error'))" 2>/dev/null || echo "Unknown")"
            return 1
        fi
    else
        error "Ошибка при вызове webhook (HTTP $http_code)"
        info "  Проверьте логи n8n для деталей"
        return 1
    fi
}

# Тест: Docker контейнеры
test_docker_status() {
    info "Тест 7: Проверка статуса Docker контейнеров..."
    
    if command -v docker &> /dev/null; then
        local n8n_status=$(docker ps --filter "name=n8n" --format "{{.Status}}" 2>/dev/null || echo "")
        local ai_status=$(docker ps --filter "name=ai-analyzer" --format "{{.Status}}" 2>/dev/null || echo "")
        
        if [ -n "$n8n_status" ] && echo "$n8n_status" | grep -q "Up"; then
            success "Контейнер n8n работает"
        else
            error "Контейнер n8n не найден или не работает"
        fi
        
        if [ -n "$ai_status" ] && echo "$ai_status" | grep -q "Up"; then
            success "Контейнер ai-analyzer работает"
        else
            error "Контейнер ai-analyzer не найден или не работает"
        fi
    else
        warning "Docker не установлен, пропускаем проверку контейнеров"
    fi
}

# Сводка тестов
print_summary() {
    echo ""
    echo "═══════════════════════════════════════════"
    info "РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ"
    echo "═══════════════════════════════════════════"
    success "Пройдено: $TESTS_PASSED"
    if [ $TESTS_FAILED -gt 0 ]; then
        error "Провалено: $TESTS_FAILED"
    else
        success "Провалено: $TESTS_FAILED"
    fi
    echo "═══════════════════════════════════════════"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo ""
        success "ВСЕ ТЕСТЫ ПРОЙДЕНЫ! 🎉"
        echo ""
        info "Система готова к использованию!"
        echo ""
    else
        echo ""
        error "НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ"
        echo ""
        info "Рекомендации:"
        echo "  1. Проверьте логи: docker-compose -f docker-compose.yml logs"
        echo "  2. Убедитесь, что все сервисы запущены: docker-compose -f docker-compose.yml ps"
        echo "  3. Проверьте конфигурацию в AI/config.py и config.py"
        echo "  4. Изучите AI_INTEGRATION_GUIDE.md для troubleshooting"
        echo ""
    fi
}

# Основной процесс
main() {
    echo ""
    info "╔═══════════════════════════════════════════╗"
    info "║  Тестирование AI-интеграции с n8n        ║"
    info "╚═══════════════════════════════════════════╝"
    echo ""
    info "Настройки:"
    info "  n8n URL: $N8N_URL"
    info "  AI Service URL: $AI_SERVICE_URL"
    echo ""
    
    # Запускаем тесты
    test_docker_status
    echo ""
    
    test_ai_health
    echo ""
    
    test_ai_config
    echo ""
    
    test_n8n_health
    echo ""
    
    test_n8n_webhook
    echo ""
    
    test_ai_analyze
    echo ""
    
    test_full_cycle
    echo ""
    
    # Выводим сводку
    print_summary
}

# Обработка аргументов
case "${1:-}" in
    "quick")
        # Быстрая проверка (без AI-анализа и полного цикла)
        info "Быстрая проверка основных компонентов..."
        test_docker_status
        test_ai_health
        test_n8n_health
        print_summary
        ;;
    "ai-only")
        # Только тесты AI-сервиса
        info "Проверка только AI-сервиса..."
        test_ai_health
        test_ai_config
        test_ai_analyze
        print_summary
        ;;
    "help"|"-h"|"--help")
        echo "Использование: $0 [команда]"
        echo ""
        echo "Команды:"
        echo "  (пусто)   - Полный набор тестов"
        echo "  quick     - Быстрая проверка (без AI-анализа)"
        echo "  ai-only   - Только тесты AI-сервиса"
        echo "  help      - Эта справка"
        echo ""
        echo "Переменные окружения:"
        echo "  N8N_URL          - URL n8n (по умолчанию: http://localhost:5678)"
        echo "  AI_SERVICE_URL   - URL AI-сервиса (по умолчанию: http://localhost:5001)"
        ;;
    *)
        main
        ;;
esac

