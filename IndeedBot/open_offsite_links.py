import json
from selenium import webdriver
from time import sleep
from random import random
with open('offsite_links.json', 'r') as file:
    offsite_links_dict = json.load(file)

driver = webdriver.Chrome()

for url in offsite_links_dict:
    sleep(1 + random())
    driver.get(url)
    sleep(1 + random())
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
