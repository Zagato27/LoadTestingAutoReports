#!/bin/bash

###############################################################################
# Скрипт развертывания AI-сервиса для n8n Load Testing Auto Reports
###############################################################################

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для красивого вывода
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка наличия необходимых команд
check_requirements() {
    info "Проверка требований..."
    
    local missing_tools=()
    
    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        missing_tools+=("docker-compose")
    fi
    
    if ! command -v curl &> /dev/null; then
        missing_tools+=("curl")
    fi
    
    if [ ${#missing_tools[@]} -gt 0 ]; then
        error "Не установлены следующие инструменты: ${missing_tools[*]}"
        exit 1
    fi
    
    success "Все требования выполнены"
}

# Проверка конфигурации
check_config() {
    info "Проверка конфигурации..."
    
    if [ ! -f "AI/config.py" ]; then
        error "Не найден файл AI/config.py"
        exit 1
    fi
    
    if [ ! -f "config.py" ]; then
        error "Не найден файл config.py"
        exit 1
    fi
    
    if [ ! -f "ai_service_for_n8n.py" ]; then
        error "Не найден файл ai_service_for_n8n.py"
        exit 1
    fi
    
    success "Конфигурация в порядке"
}

# Создание .env файла если его нет
setup_env() {
    if [ ! -f ".env" ]; then
        info "Создание .env файла из шаблона..."
        
        if [ -f "env.example.txt" ]; then
            cp env.example.txt .env
            warning "Создан .env из шаблона. ОБЯЗАТЕЛЬНО отредактируйте его перед запуском!"
            info "Откройте .env и настройте:"
            echo "  - POSTGRES_PASSWORD"
            echo "  - PROMETHEUS_URL"
            echo "  - GRAFANA_URL"
            echo "  - N8N_BASIC_AUTH_PASSWORD"
            read -p "Нажмите Enter после редактирования .env..."
        else
            error "Не найден файл env.example.txt"
            exit 1
        fi
    else
        success ".env файл уже существует"
    fi
}

# Проверка сертификатов (если используется mTLS)
check_certificates() {
    info "Проверка сертификатов для mTLS..."
    
    if [ -d "certs" ]; then
        if [ -f "certs/client.crt" ] && [ -f "certs/client.key" ]; then
            success "Сертификаты найдены"
        else
            warning "Директория certs существует, но не найдены client.crt или client.key"
            info "Если вы используете mTLS для GigaChat, поместите сертификаты в директорию certs/"
        fi
    else
        warning "Директория certs не найдена"
        info "Если вы используете mTLS для GigaChat, создайте директорию certs/ и поместите туда сертификаты"
    fi
}

# Сборка Docker образов
build_images() {
    info "Сборка Docker образов..."
    
    docker-compose -f docker-compose.n8n.yml build ai-analyzer
    
    success "Образы собраны"
}

# Запуск сервисов
start_services() {
    info "Запуск сервисов..."
    
    docker-compose -f docker-compose.n8n.yml up -d
    
    success "Сервисы запущены"
}

# Проверка работы сервисов
check_services() {
    info "Ожидание запуска сервисов (30 секунд)..."
    sleep 30
    
    info "Проверка n8n..."
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:5678 | grep -q "200\|302"; then
        success "n8n доступен на http://localhost:5678"
    else
        warning "n8n может быть еще не готов, попробуйте позже"
    fi
    
    info "Проверка AI-сервиса..."
    local ai_health=$(curl -s http://localhost:5001/health 2>/dev/null || echo "")
    if echo "$ai_health" | grep -q "healthy"; then
        success "AI-сервис работает на http://localhost:5001"
        
        # Проверяем конфигурацию
        info "Проверка конфигурации AI-сервиса..."
        curl -s http://localhost:5001/config/check | python3 -m json.tool 2>/dev/null || true
    else
        error "AI-сервис недоступен"
        info "Проверьте логи: docker-compose -f docker-compose.n8n.yml logs ai-analyzer"
        exit 1
    fi
}

# Вывод информации для следующих шагов
print_next_steps() {
    echo ""
    success "Развертывание завершено!"
    echo ""
    info "Следующие шаги:"
    echo ""
    echo "1. Откройте n8n: http://localhost:5678"
    echo "   Логин: admin (если настроили в .env)"
    echo "   Пароль: смотрите в .env (N8N_BASIC_AUTH_PASSWORD)"
    echo ""
    echo "2. Импортируйте workflow:"
    echo "   Settings → Import from File → n8n_load_testing_workflow_with_ai.json"
    echo ""
    echo "3. Настройте Credentials в n8n:"
    echo "   - Confluence (HTTP Basic Auth)"
    echo "   - Grafana (HTTP Basic Auth)"
    echo ""
    echo "4. Обновите конфигурацию метрик в узле 'Get Service Config'"
    echo ""
    echo "5. Протестируйте workflow:"
    echo '   curl -X POST http://localhost:5678/webhook/load-testing/report/create \'
    echo '     -H "Content-Type: application/json" \'
    echo '     -d '"'"'{'
    echo '       "start": "2025-02-21T11:30",'
    echo '       "end": "2025-02-21T14:10",'
    echo '       "service": "NSI"'
    echo '     }'"'"
    echo ""
    info "Полезные команды:"
    echo "  - Логи AI-сервиса: docker-compose -f docker-compose.n8n.yml logs -f ai-analyzer"
    echo "  - Логи n8n: docker-compose -f docker-compose.n8n.yml logs -f n8n"
    echo "  - Статус сервисов: docker-compose -f docker-compose.n8n.yml ps"
    echo "  - Остановка: docker-compose -f docker-compose.n8n.yml down"
    echo ""
    info "Документация:"
    echo "  - AI_INTEGRATION_GUIDE.md - детальное руководство по AI"
    echo "  - README_N8N_MIGRATION.md - общее руководство"
    echo ""
}

# Основной процесс
main() {
    echo ""
    info "=== Развертывание AI-сервиса для n8n ==="
    echo ""
    
    check_requirements
    check_config
    setup_env
    check_certificates
    
    echo ""
    read -p "Продолжить развертывание? (y/n) " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        info "Развертывание отменено"
        exit 0
    fi
    
    build_images
    start_services
    check_services
    print_next_steps
}

# Обработка аргументов
case "${1:-}" in
    "check")
        check_requirements
        check_config
        check_certificates
        ;;
    "build")
        build_images
        ;;
    "start")
        start_services
        ;;
    "test")
        check_services
        ;;
    "logs")
        docker-compose -f docker-compose.n8n.yml logs -f ai-analyzer
        ;;
    "stop")
        info "Остановка сервисов..."
        docker-compose -f docker-compose.n8n.yml down
        success "Сервисы остановлены"
        ;;
    "restart")
        info "Перезапуск сервисов..."
        docker-compose -f docker-compose.n8n.yml restart ai-analyzer
        success "AI-сервис перезапущен"
        ;;
    "clean")
        warning "Это удалит все контейнеры, образы и volumes!"
        read -p "Продолжить? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose -f docker-compose.n8n.yml down -v --rmi all
            success "Очистка завершена"
        fi
        ;;
    "help"|"-h"|"--help")
        echo "Использование: $0 [команда]"
        echo ""
        echo "Команды:"
        echo "  (пусто)  - Полное развертывание"
        echo "  check    - Проверка требований и конфигурации"
        echo "  build    - Сборка Docker образов"
        echo "  start    - Запуск сервисов"
        echo "  test     - Проверка работы сервисов"
        echo "  logs     - Просмотр логов AI-сервиса"
        echo "  stop     - Остановка сервисов"
        echo "  restart  - Перезапуск AI-сервиса"
        echo "  clean    - Полная очистка (контейнеры + образы + volumes)"
        echo "  help     - Эта справка"
        ;;
    *)
        main
        ;;
esac

