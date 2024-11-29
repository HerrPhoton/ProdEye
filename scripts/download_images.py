import os

import requests
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def download_images(query, limit=10):
    """Скачивает изображения по запросу из Google, Bing и Yandex.

    Args:
        query (str): Поисковый запрос
        limit (int): Максимальное количество изображений для скачивания
    """

    # Создаем папку для сохранения изображений
    if not os.path.exists('images'):
        os.makedirs('images')

    # Инициализируем браузер
    driver = webdriver.Chrome()

    # Google Images
    try:
        driver.get(f'https://www.google.com/search?q={query}&tbm=isch')
        for i in range(limit):
            try:
                # Ждем загрузки изображений
                image = WebDriverWait(driver,
                                      10).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'img.rg_i:nth-child({i+1})')))
                image_url = image.get_attribute('src')
                if image_url:
                    response = requests.get(image_url)
                    with open(f'images/google_{i+1}.jpg', 'wb') as f:
                        f.write(response.content)
            except:
                continue

    except Exception as e:
        print(f'Ошибка при скачивании с Google: {e}')

    # Bing Images
    try:
        driver.get(f'https://www.bing.com/images/search?q={query}')
        for i in range(limit):
            try:
                image = WebDriverWait(driver,
                                      10).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'.mimg:nth-child({i+1})')))
                image_url = image.get_attribute('src')
                if image_url:
                    response = requests.get(image_url)
                    with open(f'images/bing_{i+1}.jpg', 'wb') as f:
                        f.write(response.content)
            except:
                continue

    except Exception as e:
        print(f'Ошибка при скачивании с Bing: {e}')

    # Yandex Images
    try:
        driver.get(f'https://yandex.ru/images/search?text={query}')
        for i in range(limit):
            try:
                image = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f'.serp-item__thumb:nth-child({i+1})')))
                image_url = image.get_attribute('src')
                if image_url:
                    if not image_url.startswith('http'):
                        image_url = 'https:' + image_url
                    response = requests.get(image_url)
                    with open(f'images/yandex_{i+1}.jpg', 'wb') as f:
                        f.write(response.content)
            except:
                continue

    except Exception as e:
        print(f'Ошибка при скачивании с Yandex: {e}')

    # Закрываем браузер
    driver.quit()


if __name__ == '__main__':
    download_images("яблоко", 10)
