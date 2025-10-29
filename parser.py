#!/usr/bin/env python3
"""
Web to Markdown Parser
Парсит веб-сайты и конвертирует их в Markdown с сохранением всех вложений
"""

import os
import re
import hashlib
from urllib.parse import urljoin, urlparse, unquote
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from tqdm import tqdm


class WebToMarkdownParser:
    def __init__(self, base_dir="D:\\Downloads\\MD downloads"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def sanitize_filename(self, name):
        """Очищает имя файла от недопустимых символов"""
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        name = name.strip('. ')
        return name[:200] if name else 'unnamed'

    def get_site_folder_name(self, url):
        """Создает имя папки на основе URL"""
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        path = parsed.path.strip('/').replace('/', '_')

        if path:
            folder_name = f"{domain}_{path}"
        else:
            folder_name = domain

        return self.sanitize_filename(folder_name)

    def download_file(self, url, save_path):
        """Скачивает файл с прогресс-баром"""
        try:
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            with open(save_path, 'wb') as f:
                if total_size == 0:
                    f.write(response.content)
                else:
                    with tqdm(total=total_size, unit='B', unit_scale=True,
                              desc=save_path.name, leave=False) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
            return True
        except Exception as e:
            print(f"\n⚠️  Ошибка загрузки {url}: {e}")
            return False

    def get_file_extension(self, url, content_type=None):
        """Определяет расширение файла"""
        parsed = urlparse(url)
        path = unquote(parsed.path)

        if '.' in path:
            ext = os.path.splitext(path)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico',
                       '.css', '.js', '.pdf', '.mp4', '.webm']:
                return ext

        if content_type:
            ext_map = {
                'image/jpeg': '.jpg',
                'image/png': '.png',
                'image/gif': '.gif',
                'image/svg+xml': '.svg',
                'image/webp': '.webp',
                'text/css': '.css',
                'application/javascript': '.js',
                'application/pdf': '.pdf',
            }
            return ext_map.get(content_type, '')

        return ''

    def download_resource(self, url, base_url, assets_dir, resource_type='image'):
        """Скачивает ресурс (изображение, CSS, JS и т.д.)"""
        try:
            full_url = urljoin(base_url, url)

            # Проверяем, не является ли это data URI
            if full_url.startswith('data:'):
                return None

            # Создаем уникальное имя файла
            url_hash = hashlib.md5(full_url.encode()).hexdigest()[:8]

            # Пытаемся получить оригинальное имя файла
            parsed = urlparse(full_url)
            original_name = os.path.basename(unquote(parsed.path))

            if not original_name or '.' not in original_name:
                response = self.session.head(full_url, timeout=10)
                content_type = response.headers.get('content-type', '').split(';')[0]
                ext = self.get_file_extension(full_url, content_type)
                filename = f"{resource_type}_{url_hash}{ext}"
            else:
                name, ext = os.path.splitext(original_name)
                filename = f"{self.sanitize_filename(name)}_{url_hash}{ext}"

            save_path = assets_dir / filename

            if save_path.exists():
                return filename

            if self.download_file(full_url, save_path):
                return filename

        except Exception as e:
            print(f"\n⚠️  Не удалось скачать {url}: {e}")

        return None

    def process_html_to_markdown(self, html_content, base_url, assets_dir):
        """Конвертирует HTML в Markdown с обработкой вложений"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Создаем папку для ассетов
        assets_dir.mkdir(exist_ok=True)

        # Обрабатываем изображения
        images = soup.find_all('img')
        print(f"📷 Найдено изображений: {len(images)}")

        for img in tqdm(images, desc="Загрузка изображений", unit="img"):
            src = img.get('src') or img.get('data-src')
            if src:
                filename = self.download_resource(src, base_url, assets_dir, 'image')
                if filename:
                    img['src'] = f"assets/{filename}"
                    # Сохраняем alt текст
                    if not img.get('alt'):
                        img['alt'] = filename

        # Обрабатываем ссылки на CSS
        css_links = soup.find_all('link', rel='stylesheet')
        print(f"🎨 Найдено CSS файлов: {len(css_links)}")

        for link in tqdm(css_links, desc="Загрузка CSS", unit="file", leave=False):
            href = link.get('href')
            if href:
                filename = self.download_resource(href, base_url, assets_dir, 'css')
                if filename:
                    link['href'] = f"assets/{filename}"

        # Обрабатываем скрипты
        scripts = soup.find_all('script', src=True)
        print(f"📜 Найдено JS файлов: {len(scripts)}")

        for script in tqdm(scripts, desc="Загрузка JS", unit="file", leave=False):
            src = script.get('src')
            if src:
                filename = self.download_resource(src, base_url, assets_dir, 'js')
                if filename:
                    script['src'] = f"assets/{filename}"

        # Конвертируем в Markdown
        markdown_content = md(str(soup), heading_style="ATX")

        return markdown_content

    def parse_website(self, url):
        """Основная функция парсинга сайта"""
        print(f"\n🌐 Начинаем парсинг: {url}")

        try:
            # Загружаем страницу
            print("📥 Загрузка HTML...")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = response.apparent_encoding

            # Создаем папку для сайта
            folder_name = self.get_site_folder_name(url)
            site_dir = self.base_dir / folder_name
            site_dir.mkdir(exist_ok=True)

            assets_dir = site_dir / 'assets'

            print(f"📁 Сохранение в: {site_dir}")

            # Конвертируем HTML в Markdown
            print("🔄 Конвертация в Markdown...")
            markdown_content = self.process_html_to_markdown(
                response.text,
                url,
                assets_dir
            )

            # Сохраняем Markdown
            md_file = site_dir / 'content.md'
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(f"# {url}\n\n")
                f.write(f"Сохранено: {Path.cwd()}\n\n")
                f.write("---\n\n")
                f.write(markdown_content)

            # Сохраняем оригинальный HTML
            html_file = site_dir / 'original.html'
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(response.text)

            print(f"\n✅ Готово! Сохранено в: {site_dir}")
            print(f"   📄 Markdown: content.md")
            print(f"   🌐 HTML: original.html")
            print(f"   📂 Ассеты: assets/")

        except requests.exceptions.RequestException as e:
            print(f"\n❌ Ошибка загрузки страницы: {e}")
        except Exception as e:
            print(f"\n❌ Произошла ошибка: {e}")


def main():
    print("=" * 60)
    print("  🔗 Web to Markdown Parser")
    print("=" * 60)

    parser = WebToMarkdownParser()

    while True:
        url = input("\n🔗 Введите URL для парсинга (или 'exit' для выхода): ").strip()

        if url.lower() in ['exit', 'quit', 'q']:
            print("👋 До свидания!")
            break

        if not url:
            print("⚠️  URL не может быть пустым")
            continue

        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        parser.parse_website(url)


if __name__ == "__main__":
    main()