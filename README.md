# 🔗 Web to Markdown Parser with PDF

Консольное приложение для парсинга веб-сайтов с автоматической конвертацией в Markdown и созданием PDF через Chrome.

## 📋 Возможности

- ✅ Скачивание всего контента сайта (HTML, изображения, CSS, JS)
- ✅ Конвертация HTML в Markdown с сохранением структуры
- ✅ Создание высококачественного PDF через Chrome Print to PDF
- ✅ Прогресс-бары для всех операций
- ✅ Автоматическая организация файлов по папкам

## 🚀 Запуск через Docker

### Вариант 1: Docker Compose (рекомендуется)

```bash
# Сборка и запуск
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d

# Подключиться к контейнеру
docker-compose exec web-parser bash

# Внутри контейнера запустите парсер
python parser.py

# Остановка
docker-compose down
```

### Вариант 2: Обычный Docker

```bash
# Сборка образа
docker build -t md-downloader .

# Запуск контейнера
docker run -it --rm \
  -v "$(pwd)/downloads:/downloads" \
  --shm-size=2g \
  md-downloader

# Для Windows PowerShell
docker run -it --rm `
  -v "${PWD}/downloads:/downloads" `
  --shm-size=2g `
  md-downloader
```

## 💻 Локальный запуск (без Docker)

### Требования

- Python 3.13+
- Google Chrome

### Установка

```bash
# Создать виртуальное окружение
python -m venv .venv

# Активировать (Windows)
.venv\Scripts\activate

# Активировать (Linux/Mac)
source .venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Запуск
python parser.py
```

## 📂 Структура проекта

```
md-downloader/
├── parser.py              # Основной скрипт
├── requirements.txt       # Python зависимости
├── Dockerfile            # Docker конфигурация
├── docker-compose.yml    # Docker Compose конфигурация
├── .dockerignore         # Исключения для Docker
├── .gitignore           # Исключения для Git
└── downloads/           # Папка для скачанных файлов
    └── example.com/
        ├── content.md
        ├── original.html
        ├── page.pdf
        └── assets/
```

## 📦 Результат работы

Для каждого сайта создается папка с:

- **content.md** - Markdown версия с локальными ссылками на изображения
- **original.html** - Оригинальный HTML код страницы
- **page.pdf** - PDF версия страницы (как Print to PDF в Chrome)
- **assets/** - Папка со всеми ресурсами (изображения, CSS, JS)

## 🎯 Использование

```bash
# Запустите программу
python parser.py

# Введите URL (например)
https://example.com

# Или без https://
example.com

# Для выхода введите
exit
```

## 🛠️ Зависимости

- requests - HTTP клиент
- beautifulsoup4 - Парсинг HTML
- markdownify - Конвертация HTML → Markdown
- tqdm - Прогресс-бары
- selenium - Управление браузером
- webdriver-manager - Автоматическая установка ChromeDriver

MIT License
