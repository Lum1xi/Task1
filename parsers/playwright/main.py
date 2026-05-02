from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time

def parse_product(url: str):
    """
    Ця функція отримує URL сторінки продукту та парсить дані за допомогою Playwright та словника XPath-виразів.
    """
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

    product_data = {}

    with sync_playwright() as p:
        # headless=False відкриває реальне вікно браузера. Змініть на True, якщо хочете фоновий режим.
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            # Переходимо за URL
            page.goto(url, timeout=60000)

            # --- Вирішення проблеми "Лінивого завантаження" ---
            page.evaluate("window.scrollTo(0, 800);")
            time.sleep(1)
            page.evaluate("window.scrollTo(0, 1500);")
            time.sleep(1)
            tab_xpath = '//a[contains(text(), "Характеристики") or contains(@href, "#characteristics")]'
            try:
                tab = page.wait_for_selector(tab_xpath, timeout=5000)
                tab.click(force=True)  # force=True для кліку навіть якщо елемент частково перекритий
                time.sleep(1)
            except PlaywrightTimeoutError:
                print("Warning: Characteristics tab not found.")
            # 1. Збираємо одиночні елементи
            for key, xpath in SINGLE_XPATHS.items():
                try:
                    # Чекаємо появи елемента в DOM
                    element = page.wait_for_selector(xpath, state='attached', timeout=5000)
                    val = element.inner_text().strip() if element else None
                    if key == 'reviews_count' and val:
                        import re
                        match = re.search(r'\d+', val)
                        product_data[key] = match.group(0) if match else "0"
                    else:
                        product_data[key] = val
                except PlaywrightTimeoutError:
                    print(f"Warning: Element '{key}' not found.")
                    product_data[key] = "0" if key == 'reviews_count' else None

            # 2. Збираємо всі фотографії
            try:
                # Чекаємо хоча б одне фото
                page.wait_for_selector(MULTI_XPATHS['all_photos'], state='attached', timeout=5000)
                photo_elements = page.locator(MULTI_XPATHS['all_photos']).all()
                photos_list = []
                for img in photo_elements:
                    src = img.get_attribute('src')
                    if src and src not in photos_list:
                        photos_list.append(src)
                product_data['all_photos'] = photos_list
            except PlaywrightTimeoutError:
                print("Warning: Photos not found.")
                product_data['all_photos'] = []

            # 3. Збираємо характеристики
            try:

                page.wait_for_selector(MULTI_XPATHS['all_product_details'], state='attached', timeout=5000)
                detail_elements = page.locator(MULTI_XPATHS['all_product_details']).all()
                details_dict = {}
                for i in range(0, len(detail_elements), 2):
                    k = detail_elements[i].inner_text().strip()
                    v = detail_elements[i+1].inner_text().strip() if i+1 < len(detail_elements) else ""
                    if k:
                        details_dict[k] = v
                product_data['all_product_details'] = details_dict

            except PlaywrightTimeoutError:
                print("Warning: Product details not found.")
                product_data['all_product_details'] = {}

            return product_data

        except Exception as e:
            print(f"A critical error occurred: {e}")
            return None
        finally:
            browser.close()

if __name__ == '__main__':
    test_url = "https://brain.com.ua/ukr/Mobilniy_telefon_Apple_iPhone_15_128GB_Pink-p1044351.html"
    data = parse_product(test_url)
    if data:
        import json
        print(json.dumps(data, indent=4, ensure_ascii=False))
