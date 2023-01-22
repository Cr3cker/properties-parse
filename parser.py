from bs4 import BeautifulSoup
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import re


class Parser:
    def __init__(self) -> None:
        '''Initialize the class'''
        self.url = 'https://lemberg.sk/ru/for-rent/'
        self.properties = []
        self.path = "/opt/WebDriver/bin/chromedriver"
        # This is a list of options for the Chrome driver
        self.opts = [
            "start-maximized",
            "disable-infobars",
            "--disable-extensions",
            "--headless"
        ]

    def get_all_props(self) -> BeautifulSoup:
        '''Get all properties from the website'''
        options = webdriver.ChromeOptions()
        # Here we add the options to the Chrome driver
        options.add_argument(self.opts[0])
        options.add_argument(self.opts[1])
        options.add_argument(self.opts[2])
        options.add_argument(self.opts[3])

        # Here we initialize the Chrome driver
        service = Service(self.path)
        driver = webdriver.Chrome(options=options, service=service)
        driver.get(self.url)

        # Here we find the button to click to load more properties
        button = driver.find_element(By.XPATH, '//*[@id="mse2_mfilter"]/div[4]/button')
        button.send_keys("\n")
        time.sleep(1)

        # Here we get the content of the page   
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        return soup

    def get_content(self, soup: BeautifulSoup) -> None:
        '''Get the content from the website'''
        links = []
        actual = []
        items = soup.find_all('div', class_='product-item')

        # Here we create regex patterns to match the content
        price_pattern = re.compile(r'\d{1,3}(?:\s\d{3})*(?:\.\d{2})?€')
        rooms_pattern = re.compile(r'Комнат:(.*)')
        city_pattern = re.compile(r'Город:([a-zA-Z]+)')
        area_pattern = re.compile(r'(\d{1,3}(?:\.\d{2})?) m2')
        parking_pattern = re.compile(r'Паркинг:([Есть паркинг Без паркинга]*)')
        saletype_pattern = re.compile(r'Продажа|Аренда')

        # Extract the links from the website
        link_items = soup.find_all('div', class_='product-item-cover')
        for link in link_items:
            links.append({'link': 'https://lemberg.sk/ru/' + link.find('a').get('href')})

        # Exttact the actuality of the properties
        actuality = soup.find_all('div', class_='product-sticker')
        for act in actuality:
            actual.append(act.text)
        actual.insert(0, 'Актуальное')

        # Check if the property is actual and extract the content from the website
        accepted = ['Актуальное', 'Акция']
        for item in items:
            string = item.find('div', class_='product-item-body').get_text(strip=True)
            if actual[items.index(item)] in accepted:
                self.properties.append({
                        'id': len(self.properties) + 1,
                        'title': string.replace('\n', '').split('Аренда')[0],
                        'saletype': saletype_pattern.findall(string)[0],
                        'city': city_pattern.findall(string)[0].strip() if city_pattern.findall(string) else 'Нет данных',
                        'rooms': rooms_pattern.findall(string)[0] if rooms_pattern.findall(string) else 'Нет данных',
                        'area': area_pattern.findall(string)[0].split('.')[0] if area_pattern.findall(string) else 'Нет данных',
                        'price': price_pattern.findall(string)[0].replace(' ', '') if price_pattern.findall(string) else 'Нет данных',
                        'parking': parking_pattern.findall(string)[0] if parking_pattern.findall(string) else 'Нет данных',
                        'link': links[items.index(item)]['link']
                    })

    # Add a method to save the content to a file
    def save_content(self) -> None:
        '''Save the content to a csv file'''
        with open('static/properties.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'title', 'saletype', 'city', 'rooms', 'area', 'price', 'parking', 'link'])
            for prop in self.properties:
                writer.writerow([prop['id'], prop['title'], prop['saletype'], prop['city'], prop['rooms'], prop['area'], prop['price'], prop['parking'], prop['link']])

    # Add a method to run the whole process
    def run(self) -> None:
        '''Run the parser'''
        soup = self.get_all_props()
        self.get_content(soup)
        self.save_content()

        return self.properties

p = Parser()
p.run()
