import requests
from bs4 import BeautifulSoup
import re

r = requests.get('https://brain.com.ua/ukr/Mobilniy_telefon_Apple_iPhone_15_128GB_Pink-p1044351.html', headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(r.text, 'html.parser')

print("Gallery container:")
gallery = soup.find('div', class_=re.compile('gallery'))
if gallery:
    print(gallery.get('class'))
    for img in gallery.find_all('img'):
        print(img.get('src') or img.get('data-src'))

print("Any big photos:")
for a in soup.find_all('a', href=re.compile(r'.*?jpg')):
    print(a.get('href'))
