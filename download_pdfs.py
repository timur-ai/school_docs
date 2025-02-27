import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
import re
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def sanitize_filename(filename):
    """
    Очищает имя файла от недопустимых символов
    """
    # Заменяем недопустимые символы на подчеркивание
    invalid_chars = r'[<>:"/\\|?*]'
    filename = re.sub(invalid_chars, '_', filename)
    # Убираем множественные подчеркивания
    filename = re.sub(r'_+', '_', filename)
    # Ограничиваем длину имени файла
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:196] + ext
    return filename

def download_pdf(url, folder='downloaded_pdfs'):
    """
    Скачивает PDF файл по указанному URL
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    try:
        # Настраиваем заголовки для запроса
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        # Получаем имя файла из URL и декодируем его
        filename = unquote(url.split('/')[-1])
        if 'get_file.php' in filename:
            # Извлекаем имя файла из параметра name в URL
            name_match = re.search(r'name=([^&]+)', url)
            if name_match:
                filename = unquote(name_match.group(1))
        
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
            
        # Очищаем имя файла от недопустимых символов
        filename = sanitize_filename(filename)
        filepath = os.path.join(folder, filename)
        
        # Проверяем, существует ли файл
        if os.path.exists(filepath):
            print(f'Файл уже существует: {filename}')
            return True
            
        # Скачиваем файл
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f'Успешно скачан файл: {filename}')
        return True
    except Exception as e:
        print(f'Ошибка при скачивании {url}: {str(e)}')
        return False

def main():
    url = 'https://sch2083.mskobr.ru/info_edu/all_docs/'
    
    try:
        # Настраиваем Edge
        edge_options = Options()
        edge_options.add_argument('--headless')
        edge_options.add_argument('--disable-gpu')
        edge_options.add_argument('--no-sandbox')
        edge_options.add_argument('--disable-dev-shm-usage')
        
        # Инициализируем драйвер
        print("Инициализация браузера...")
        driver = webdriver.Edge(options=edge_options)
        
        # Загружаем страницу
        print("Загружаем страницу...")
        driver.get(url)
        
        # Ждем загрузки контента
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "a")))
        
        # Получаем HTML после загрузки JavaScript
        html_content = driver.page_source
        driver.quit()
        
        # Парсим HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Ищем все ссылки
        links = soup.find_all('a')
        
        pdf_count = 0
        for link in links:
            href = link.get('href')
            if href and '.pdf' in href.lower():
                # Преобразуем относительный URL в абсолютный
                full_url = urljoin(url, href)
                print(f"Найдена ссылка на PDF: {full_url}")
                if download_pdf(full_url):
                    pdf_count += 1
        
        print(f'\nВсего скачано PDF файлов: {pdf_count}')
        
    except Exception as e:
        print(f'Произошла ошибка: {str(e)}')

if __name__ == '__main__':
    main() 