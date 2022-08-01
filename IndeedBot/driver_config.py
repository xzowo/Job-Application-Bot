from random import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep

DEBUG_MODE = False
REMOTE_JOB = True


options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=C:\\Users\\anon\\Desktop\\Job-Application-Bot\\IndeedBot\\browserdata")
driver = webdriver.Chrome(chrome_options=options)

options2 = webdriver.ChromeOptions()
options2.add_argument("user-data-dir=C:\\Users\\anon\\Desktop\\Job-Application-Bot\\IndeedBot\\browserdata2")
driver2 = webdriver.Chrome(chrome_options=options2)

SEARCH_URL = ""
driver.get(SEARCH_URL)
sleep(10 + random()) # need to wait for the page to load

if REMOTE_JOB:
    # indeed has a unique hash for remote jobs... need to click it manually
    remote_button = driver.find_element(By.XPATH, "//button[@id='filter-remotejob']")
    remote_button2 = remote_button.find_element(By.XPATH, "..//a[@class='yosegi-FilterPill-dropdownListItemLink']")
    driver.execute_script("arguments[0].click();", remote_button2)
    sleep(4 + random())

POTENTIAL_WAIT_TIME = 3
WAIT_TIME = 10
wait = WebDriverWait(driver, WAIT_TIME)
short_wait = WebDriverWait(driver, WAIT_TIME / 2)
RATING_LOWER_BOUND = 2.6
APPLY_TIMEOUT = 400.0
INCLUDE_OPTIONAL_ANSWERS = False
ALLOWED_STRIKES = 3
USING_OMISSION_DICT = True
OMIT_CONTRACT_JOBS = True

AMOUNT_OF_PGS_TO_SCAN = 1
