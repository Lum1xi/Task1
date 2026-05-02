from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


import time

def parse_product(url: str):

    SINGLE_XPATHS = {
        'full_name': '//h1[contains(@class, "desktop-only-title")]',
        'color': '//span[text()="Колір"]/following-sibling::span/a',
        'memory': '//span[text()="Вбудована пам\'ять"]/../span/a',
        'manufacturer': '//span[text()="Виробник"]/following-sibling::span',
        'price': '//div[contains(@class, "br-pr-price") and contains(@class, "main-price-block")]//div//span',
        'product_code': '//span[text()="Артикул"]/following-sibling::span',
        'reviews_count': '//a[contains(@class, "brackets-reviews")]',
        'screen_diagonal': '//span[text()="Діагональ екрану"]/../span/a',
        'display_resolution': '//span[text()="Роздільна здатність екрану"]/../span/a',
    }

    MULTI_XPATHS = {
        'all_photos': '//div[contains(@class, "product-block-bottom")]//div[contains(@class, "slick-slide")]//img',
        'all_product_details': '//div[@id="br-characteristics"]//div[contains(@class, "br-pr-chr-item")]//div[span]'
    }

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    product_data = {}

    try:
        driver.get(url)


        wait = WebDriverWait(driver, 10)

        try:
            characteristics_tab_xpath = '//span[contains(text(), "Всі характеристики")]/..'
            tab_element = wait.until(EC.element_to_be_clickable((By.XPATH, characteristics_tab_xpath)))
            driver.execute_script("arguments[0].click();", tab_element)
            time.sleep(1)
        except TimeoutException:
            print("Warning: Characteristics tab not found or not clickable.")

        # 1. Збираємо одиночні елементи
        for key, xpath in SINGLE_XPATHS.items():
            try:
                # Змінено на presence_of_element_located
                element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                val = element.text.strip()
                if key == 'reviews_count':
                    import re
                    match = re.search(r'\d+', val)
                    product_data[key] = match.group(0) if match else "0"
                else:
                    product_data[key] = val
            except TimeoutException:
                print(f"Warning: Element '{key}' not found.")
                product_data[key] = "0" if key == 'reviews_count' else None

        try:
            photo_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, MULTI_XPATHS['all_photos'])))
            photos_list = []
            for img in photo_elements:
                src = img.get_attribute('src')
                if src and src not in photos_list:
                    photos_list.append(src)
            product_data['all_photos'] = photos_list
        except TimeoutException:
            print("Warning: Photos not found.")
            product_data['all_photos'] = []

        try:

            detail_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, MULTI_XPATHS['all_product_details'])))
            details_dict = {}
            for i in range(0, len(detail_elements), 2):
                key = detail_elements[i].text.strip()
                val = detail_elements[i+1].text.strip() if i+1 < len(detail_elements) else ""
                if key:
                    details_dict[key] = val
            product_data['all_product_details'] = details_dict
        except TimeoutException:
            print("Warning: Product details not found.")
            product_data['all_product_details'] = {}

        return product_data

    except Exception as e:
        print(f"An critical error occurred: {e}")
        return None

    finally:
        driver.quit()


if __name__ == '__main__':
    test_url = "https://brain.com.ua/ukr/Mobilniy_telefon_Apple_iPhone_15_128GB_Pink-p1044351.html"
    data = parse_product(test_url)
    if data:
        import json
        print(json.dumps(data, indent=4, ensure_ascii=False))
