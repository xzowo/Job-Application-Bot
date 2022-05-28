import json
from selenium import webdriver
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=C:\\Users\\anon\\Desktop\\Job-Application-Bot\\IndeedBot\\browserdata")
driver = webdriver.Chrome(chrome_options=options)
URL = "https://my.indeed.com/resume/editor"
driver.get(URL)

ele_list = driver.find_elements(By.XPATH, "//div[starts-with(@aria-label, 'Skills item number ')]")

phrase_dict = {}
word_dict = {}

for ele in ele_list:
    full_str = ele.text

    i = 0
    for c in reversed(full_str):
        if c == '-':
            break
        i += 1

    prefix = full_str[:len(full_str) - i - 1]
    prefix = prefix.replace("\n", "")
    postfix = full_str[len(full_str) - i:]
    postfix = postfix.replace("years", "").replace("year", "").replace("+", "").replace("\n", "").replace(" ", "")
    postfix = postfix.replace("Less", "").replace("than", "")

    if '-' in prefix or ' ' in prefix:
        phrase_dict[prefix] = postfix
    else:
        word_dict[prefix] = postfix

with open("profile_keyword_phrases.json", 'w') as file:
    json.dump(phrase_dict, file)

with open("profile_keyword_words.json", 'w') as file:
    json.dump(word_dict, file)

driver.close()
