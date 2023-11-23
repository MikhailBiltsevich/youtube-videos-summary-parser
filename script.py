from selenium import webdriver
from selenium.webdriver import  ChromeOptions, ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import json

options = ChromeOptions()
options.add_argument("--headless=new")

driver = webdriver.Chrome(options=options)
driver.get('https://eightify.app/summary?limit=1000')

link_elements = driver.find_elements(By.CSS_SELECTOR, '.summary-list-section li a')

def get_href_attribute(element: WebElement):
    return element.get_attribute('href') 

links = list(map(get_href_attribute, link_elements))

def next_page_click():
    next_page_link = WebDriverWait(driver, 10).until(lambda d : d.find_element(By.CLASS_NAME, 'paginator-list li:last-child'))
    next_page_link.click()

def get_card_info(card: WebElement):
    title = card.find_element(By.CLASS_NAME, 'card-title').text
    ActionChains(driver).move_to_element(card).perform()
    short_summary = WebDriverWait(driver, 5).until(lambda d : card.find_element(By.CLASS_NAME, 'short-summary'))
    return { 'title': title, 'short_summary': short_summary}

def get_cards():
    return WebDriverWait(driver, 10).until(lambda d : d.find_elements(By.CLASS_NAME, 'card'))

data  = []

for link in links:
    driver.get(link)
    category = WebDriverWait(driver, 10).until(lambda d : d.find_element(By.TAG_NAME, 'h1')).text
    print(f'Category: {category}')
    videos = []
    while True:
        cards = get_cards()
        if len(cards) == 0:
            data.append({ 'category': category, 'videos': videos })
            break
        for card in cards:
            card_info = get_card_info(card)
            videos.append(card_info)

        
        next_page_click()

with open('videos-summary.json', 'w') as file:
    json.dump(data, file)