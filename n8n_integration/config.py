# config.py для n8n_integration
# Базовые настройки для работы с Confluence и Grafana

CONFIG = {
    # Confluence
    'user': 'your_confluence_login',
    'password': 'your_confluence_password_or_token',
    'url_basic': 'https://confluence.company.com',
    'space_conf': 'YOUR_SPACE_KEY',
    
    # Grafana
    'grafana_login': 'your_grafana_login',
    'grafana_pass': 'your_grafana_password',
    'grafana_base_url': 'http://grafana:3000',
}

# Примечание: В production используйте переменные окружения
# вместо хранения паролей в этом файле!

