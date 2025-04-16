# Pollster 📝  
**Современная платформа для создания и прохождения опросов на Django**  

[![Лицензия: MIT](https://img.shields.io/badge/Лицензия-MIT-blue.svg)](https://opensource.org/licenses/MIT)  
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-green.svg)](https://python.org)  
[![Django 4.0+](https://img.shields.io/badge/Django-4.0+-green.svg)](https://djangoproject.com)  
[![MySQL 8.0+](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://mysql.com)  

## 🔥 Основные возможности  
- Создание опросов с различными типами вопросов  
- Гибкая система авторизации пользователей  
- Адаптивный интерфейс для всех устройств  
- Интеграция с RabbitMQ для асинхронных задач  
- Защита от спама с помощью PoW (Proof of Work)  
- Экспорт результатов в различные форматы  

## 🚀 Быстрый старт  

### Предварительные требования  
- Python 3.9+  
- MySQL 8.0+  
- Docker (опционально)  

### Установка (обычный способ)  
```bash  
git clone https://github.com/Seigneurs-Team/pollster/
cd pollster/src  
pip install -r requirements.txt  
python3 -m app.manage runserver  
```  

### Запуск через Docker  
```bash  
docker-compose up  
```  

## 🗂 Структура проекта  
```  
───src
    ├───app
    │   ├───change_settings_of_user
    │   │   └───migrations
    │   ├───common_static
    │   │   ├───css
    │   │   ├───img
    │   │   └───scripts
    │   ├───components
    │   ├───create_new_account_page
    │   │   ├───migrations
    │   │   └───templates
    │   ├───create_poll_page
    │   │   ├───migrations
    │   │   └───templates
    │   ├───delete_account
    │   │   └───migrations
    │   ├───delete_poll
    │   │   └───migrations
    │   ├───log_out
    │   │   └───migrations
    │   ├───main_page
    │   │   ├───migrations
    │   │   └───templates
    │   ├───passing_poll_page
    │   │   ├───migrations
    │   │   └───templates
    │   ├───pollster
    │   ├───profile_page
    │   │   ├───migrations
    │   │   └───templates
    │   └───sign_in_page
    │       ├───migrations
    │       └───templates
    ├───authentication
    ├───Configs
    ├───databases
    ├───Dionysus
    ├───PoW
    └───Tools_for_rabbitmq
```  



## 🤝 Как внести свой вклад  
1. Форкните репозиторий  
2. Создайте ветку для своей фичи (`git checkout -b feature/amazing-feature`)  
3. Сделайте коммит изменений (`git commit -m 'Add some amazing feature'`)  
4. Запушьте в свой форк (`git push origin feature/amazing-feature`)  
5. Откройте Pull Request  

## 📄 Лицензия  
Этот проект распространяется под лицензией MIT - подробности см. в файле [LICENSE](LICENSE).  

---  
**Разработано с ❤️ командой Pollster - делаем сбор мнений простым и удобным!**  
