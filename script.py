from selenium import webdriver
from selenium.webdriver import  ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import json
import  multiprocessing

options = ChromeOptions()
options.add_argument("--headless=new")
# options.add_argument("--start-maximized")
# options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)


def get_href_attribute(element: WebElement):
    return element.get_attribute('href')

def is_next_page_link_enabled():
    next_page_link = WebDriverWait(driver, 10).until(lambda d : d.find_element(By.CLASS_NAME, 'paginator-list li:last-child'))
    return next_page_link.get_attribute('class').find('paginator-page__disabled') == -1

def next_page_click():
    next_page_link = WebDriverWait(driver, 10).until(lambda d : d.find_element(By.CLASS_NAME, 'paginator-list li:last-child'))
    next_page_link.click()

def get_category_links():
    driver.get('https://eightify.app/summary')
    category_links = []

    while True:
        link_elements = []
        try:
            link_elements = driver.find_elements(By.CSS_SELECTOR, '.summary-list-section > ul li a')
        except:
            print('Categories not found!')
        links = list(map(get_href_attribute, link_elements))
        category_links = category_links + links
        if is_next_page_link_enabled() == False:
            break
        next_page_click()
    return category_links

def parse_video(link):
    video = {}
    tmp_driver = webdriver.Chrome(options=options)
    tmp_driver.get(link)
    print(tmp_driver.current_url)
    video['title'] = WebDriverWait(tmp_driver, 10).until(lambda d : d.find_element(By.TAG_NAME, 'h1')).text
    video['summary_url'] = tmp_driver.current_url
    video['summary'] = ''
    try:
        video['summary'] = WebDriverWait(tmp_driver, 10).until(lambda d : d.find_element(By.CLASS_NAME, 'tldr')).text.replace('TLDR ', '', 1)
    except:
        print('Summary not found')
    return video

def parse_category_by_link(link: str):
    parsed = {}
    driver.get(link)
    category_title = WebDriverWait(driver, 10).until(lambda d : d.find_element(By.TAG_NAME, 'h1')).text
    category_description = WebDriverWait(driver, 10).until(lambda d : d.find_element(By.CLASS_NAME, 'article')).text
    parsed['title'] = category_title
    parsed['description'] = category_description
    parsed['videos'] = []
    summary_links = []
    while True:
        summary_link_elements = []
        try:
            summary_link_elements = WebDriverWait(driver, 10).until(lambda d : d.find_elements(By.CLASS_NAME, 'card-title a'))
        except:
            print('Videos not found!')
        links = list(map(get_href_attribute, summary_link_elements))
        summary_links = summary_links + links
        if is_next_page_link_enabled() == False or len(links) == 0:
            break
        next_page_click()

    with multiprocessing.Pool(1) as pool:
        parsed_videos = pool.map(parse_video, summary_links)
        for parsed_video in enumerate(parsed_videos):
            parsed['videos'].append(parsed_video)
            print(f"{len(parsed['videos'])}/{len(summary_links)}")

    with open(f'{parsed["title"]}.json', 'w') as file:
        json.dump(parsed, file, indent=2)

print('Getting category links')
category_links = get_category_links()
print('End of getting category links')
for link in category_links:
    print(f'Category: {link}')
    parse_category_by_link(link)