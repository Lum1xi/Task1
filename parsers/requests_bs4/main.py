import requests
from bs4 import BeautifulSoup
import re


def parse_product(url: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        product_data = {}

        # 1. Назва
        h1 = soup.find('h1')
        product_data['full_name'] = h1.text.strip() if h1 else None

        # 2. Ціна
        price_elem = soup.select_one('.br-pr-price.main-price-block span')
        product_data['price'] = price_elem.text.strip() if price_elem else None

        # 3. Відгуки
        reviews_elem = soup.select_one('.brackets-reviews')
        if reviews_elem:
            reviews_text = reviews_elem.text.strip()
            match = re.search(r'\d+', reviews_text)
            product_data['reviews_count'] = match.group(0) if match else "0"
        else:
            product_data['reviews_count'] = "0"

        def get_detail_by_label(label_text):
            label = soup.find('span', string=re.compile(label_text))
            if label:
                val_elem = label.find_next_sibling('span')
                return val_elem.text.strip() if val_elem else None
            return None

        product_data['color'] = get_detail_by_label('Колір')
        product_data['memory'] = get_detail_by_label("Вбудована пам'ять")
        product_data['manufacturer'] = get_detail_by_label('Виробник')
        product_data['product_code'] = get_detail_by_label('Артикул')
        product_data['screen_diagonal'] = get_detail_by_label('Діагональ екрану')
        product_data['display_resolution'] = get_detail_by_label('Роздільна здатність екрану')

        photos_list = []

        for img in soup.select('.product-block-bottom img, .br-pr-gallery img'):
            src = img.get('src') or img.get('data-src') or img.get('data-lazy')
            if src and ('img.brain.com.ua' in src or src.endswith('.jpg')) and not src.startswith('data:image'):
                if src not in photos_list:
                    photos_list.append(src)

        for a in soup.select('.br-pr-gallery a'):
            href = a.get('href') or a.get('data-zoom-image')
            if href and (href.endswith('.jpg') or href.endswith('.png')):
                if href not in photos_list:
                    photos_list.append(href)

        product_data['all_photos'] = photos_list

        if not product_data.get('all_photos'):
            fallback_img = soup.select_one('img#product_main_image')
            if fallback_img:
                src = fallback_img.get('src') or fallback_img.get('data-src') or fallback_img.get('data-lazy')
                if src:
                    product_data['all_photos'] = [src]

        # 3. Збираємо характеристики
        details_dict = {}
        for item in soup.select('#br-characteristics .br-pr-chr-item'):
            spans = item.find_all('span')

            for i in range(0, len(spans) - 1, 2):
                k_elem = spans[i]
                v_elem = spans[i + 1]

                if k_elem and v_elem:
                    k = k_elem.get_text(strip=True)
                    v = v_elem.get_text(strip=True)
                    v = re.sub(r'\s+', ' ', v)
                    k = k.rstrip(':')

                    if k and len(k) < 150:
                        details_dict[k] = v
        product_data['all_product_details'] = details_dict

        return product_data

    except Exception as e:
        print(f"An error occurred during requests_bs4 parsing: {e}")
        return None


if __name__ == '__main__':
    test_url = "https://brain.com.ua/ukr/Mobilniy_telefon_Apple_iPhone_15_128GB_Pink-p1044351.html"
    data = parse_product(test_url)
    if data:
        import json

        print(json.dumps(data, indent=4, ensure_ascii=False))
