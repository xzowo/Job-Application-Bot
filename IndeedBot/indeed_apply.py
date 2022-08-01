from random import random
from time import sleep, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import date, timedelta
from keyword_config import get_response
from process_label_text import process_label_text
from driver_config import APPLY_TIMEOUT, INCLUDE_OPTIONAL_ANSWERS

QUESTION_TEXT_XPATH_STR = ".//span[starts-with(@class, 'fs-unmask')]"

def derive_input_type(item):
    THE_TYPE = ""
    focus_element = None
    button_group = None
    try:
        focus_element = item.find_element(By.XPATH, ".//fieldset[starts-with(@id, 'input-')]")
        button_group = focus_element.find_elements(By.XPATH, ".//input[starts-with(@id, 'input-')]")
        THE_TYPE = "RADIO"
    except:
        print("error finding radiogroup")

        try:
            focus_element = item.find_element(By.XPATH, ".//fieldset[starts-with(@class, 'ia-MultiselectQuestion')]")
            button_group = focus_element.find_elements(By.XPATH, ".//input[starts-with(@id, 'ifl-CheckboxFormField')]")
            THE_TYPE = "CHECKBOX"
        except:
            print("error finding checkboxes")
            try:
                focus_element = item.find_element(By.XPATH, ".//textarea[starts-with(@id, 'input-')]")
                THE_TYPE = "TEXTAREA"
            except:
                print("error finding textarea")
                try:
                    focus_element = item.find_element(By.XPATH, ".//select[starts-with(@id, 'input-')]")
                    select = Select(focus_element)
                    button_group = select.options
                    THE_TYPE = "DROPDOWN"
                except:
                    print("error finding dropdown")
                    try:
                        focus_element = item.find_element(By.XPATH, ".//input[starts-with(@id, 'input-')]")
                        if focus_element.get_attribute('type') == "date":
                            THE_TYPE = "DATE"
                        elif focus_element.get_attribute('type') == "text" or focus_element.get_attribute('type') == "number" or focus_element.get_attribute('type') == "tel":
                            THE_TYPE = "TEXT"
                        else:
                            raise Exception("error finding text, number, or date")
                    except:
                        print("error finding text, number, or date")
    return [focus_element, button_group, THE_TYPE]


def get_input_field_values(FOCUS_ELEMENT, BUTTON_GROUP, INPUT_TYPE):
    ret_list = []
    if INPUT_TYPE == "RADIO" or INPUT_TYPE == "CHECKBOX":
        id_text_list = []
        for button in BUTTON_GROUP:
            if button.is_selected():
                id_text_list.append(button.get_attribute('id'))
        # translate radio button ids into label text
        for button_id_text in id_text_list:
            ret_list.append(FOCUS_ELEMENT.find_element(By.XPATH, ".//label[@for='" + button_id_text + "']").text)

    elif INPUT_TYPE == "TEXTAREA":
        some_str = FOCUS_ELEMENT.text
        if some_str.replace(' ', '').replace('\n', '') != '':
            ret_list.append(some_str)

    elif INPUT_TYPE == "DROPDOWN":
        select = Select(FOCUS_ELEMENT)
        if len(select.all_selected_options) > 0:
            # default no value is technically a selected option
            # don't append it if that's selected
            for op in select.all_selected_options:
                if op.text != '' and op.text != ' ':
                    ret_list.append(op.text)

    elif INPUT_TYPE == "DATE":
        some_str = FOCUS_ELEMENT.get_attribute('value')
        if some_str != '':
            ret_list.append(some_str)

    elif INPUT_TYPE == "TEXT":
        some_str = FOCUS_ELEMENT.get_attribute('value')
        if some_str.replace(' ', '') != '':
            ret_list.append(some_str)

    else:
        ret_list.append("NOT INITIALIZED, TREATING AS A FINISHED ITEM")
        print("unknown type in get_empty_question_items, USING PLACEHOLDER TO IGNORE")

    return ret_list


def resolve_input(driver, item, response):
    global QUESTION_TEXT_XPATH_STR
    DEFAULT_INPUT = 1
    DEFAULT_DATE = date.today() + timedelta(14)
    derived = derive_input_type(item)
    FOCUS_ELEMENT = derived[0]
    BUTTON_GROUP = derived[1]
    if BUTTON_GROUP is not None:
        BUTTON_GROUP = BUTTON_GROUP[::-1]
    INPUT_TYPE = derived[2]

    try:
        question_text = item.find_element(By.XPATH, QUESTION_TEXT_XPATH_STR).text

        print("question_text:", question_text, "resovle_input given RESPONSE:", response)

        if INPUT_TYPE == "RADIO":
            clicked_a_button = False

            # try to find exact match
            for button in BUTTON_GROUP:
                # button does not contain text, but only the id
                button_id_text = button.get_attribute('id')
                answer_text = FOCUS_ELEMENT.find_element(By.XPATH, ".//label[@for='" + button_id_text + "']").text

                if response is not None and response.lower() == answer_text.lower():
                    driver.execute_script("arguments[0].click();", button)
                    clicked_a_button = True
                    break

            if not clicked_a_button:
                for button in BUTTON_GROUP:
                    print(button.text)
                    # button does not contain text, but only the id
                    button_id_text = button.get_attribute('id')
                    answer_text = FOCUS_ELEMENT.find_element(By.XPATH, ".//label[@for='" + button_id_text + "']").text
                    print("ANSWER ITEM:", button_id_text, "ANSWER TEXT:", answer_text)
                    print("RESPONSE:", response)

                    if response is not None and response in answer_text:
                        driver.execute_script("arguments[0].click();", button)
                        clicked_a_button = True
                        break
                    else:

                        processed_text = process_label_text(answer_text)
                        processed_text_list = processed_text.lower().split()
                        response = get_response(processed_text, processed_text_list, INDEXING="DICTIONARY")
                        if response is not None:
                            driver.execute_script("arguments[0].click();", button)
                            clicked_a_button = True
                            break

            if not clicked_a_button:
                for button in BUTTON_GROUP:
                    print(button.text)
                    # button does not contain text, but only the id
                    button_id_text = button.get_attribute('id')
                    answer_text = FOCUS_ELEMENT.find_element(By.XPATH, ".//label[@for='" + button_id_text + "']").text

                if not clicked_a_button:
                    driver.execute_script("arguments[0].click();", BUTTON_GROUP[0])

        elif INPUT_TYPE == "CHECKBOX":
            clicked_a_button = False
            for button in BUTTON_GROUP:
                print(button.text)
                # button does not contain text, but only the id
                button_id_text = button.get_attribute('id')
                answer_text = FOCUS_ELEMENT.find_element(By.XPATH, ".//label[@for='" + button_id_text + "']").text
                print("ANSWER ITEM:", button_id_text, "ANSWER TEXT:", answer_text)
                print("RESPONSE:", response)

                # checkboxes should rely on dictionary indexing only
                if clicked_a_button:
                    response = None

                if response is not None and response in answer_text:
                    driver.execute_script("arguments[0].click();", button)
                    clicked_a_button = True
                else:
                    processed_text = process_label_text(answer_text)
                    processed_text_list = processed_text.lower().split()
                    response = get_response(processed_text, processed_text_list, INDEXING="DICTIONARY")
                    if response is not None:
                        sleep(1 + random())
                        driver.execute_script("arguments[0].click();", button)
                        clicked_a_button = True

            if not clicked_a_button:
                driver.execute_script("arguments[0].click();", BUTTON_GROUP[0])

        elif INPUT_TYPE == "TEXTAREA":
            if response is not None:
                FOCUS_ELEMENT.send_keys(response)
            else:
                FOCUS_ELEMENT.send_keys(DEFAULT_INPUT)

        elif INPUT_TYPE == "DROPDOWN":
            options = BUTTON_GROUP
            try:
                if response is not None:
                    made_selection = False

                    # attempt to find exact match
                    for op in options:
                        print(response, op.text)
                        if response.lower() == op.text.lower():
                            print("clicking:", op.text.lower())
                            op.click()
                            made_selection = True
                            break

                    if not made_selection:
                        for op in options:
                            print(response, op.text)
                            if response.lower() in op.text.lower():
                                print("clicking:", op.text.lower())
                                op.click()
                                made_selection = True
                                break

                    if not made_selection:
                        options[0].click()
                else:
                    options[0].click()
            except Exception as e:
                print(e, "error at trying to select in dropdown")

        elif INPUT_TYPE == "DATE":
            driver.execute_script("arguments[0].click();", FOCUS_ELEMENT)
            FOCUS_ELEMENT.send_keys(DEFAULT_DATE.strftime("%m"))
            sleep(.1)
            FOCUS_ELEMENT.send_keys(DEFAULT_DATE.strftime("%d"))
            sleep(.1)
            FOCUS_ELEMENT.send_keys(DEFAULT_DATE.strftime("%Y"))
            # driver.execute_script("arguments[0].value = arguments[1];", FOCUS_ELEMENT, DEFAULT_DATE)

        elif INPUT_TYPE == "TEXT":
            if response is not None:
                FOCUS_ELEMENT.send_keys(response)
            else:
                FOCUS_ELEMENT.send_keys(DEFAULT_INPUT)

        else:
            print("unknown input type or blank")

    except Exception as e:
        print(e, "error resolving input")


def solve_items(driver, the_items):
    global QUESTION_TEXT_XPATH_STR
    for item in the_items:
        sleep(2 + random())
        question_text = item.find_element(By.XPATH, QUESTION_TEXT_XPATH_STR).text
        processed_text = process_label_text(question_text)

        if "(optional)" in processed_text and not INCLUDE_OPTIONAL_ANSWERS:
            continue
        question_text_list = processed_text.lower().split()
        response = get_response(question_text, question_text_list, INDEXING="TEXT")
        # need to figure out how to differentiate inputs
        resolve_input(driver, item, response)


def get_empty_question_items(question_items):
    empty_question_items = []
    for item in question_items:
        try:
            derived = derive_input_type(item)
            FOCUS_ELEMENT = derived[0]
            BUTTON_GROUP = derived[1]
            INPUT_TYPE = derived[2]

            # questions without an answer list will return [] which is getting appended
            # using placeholder in get_input_field_values to ignore questions without an answer list
            if len(get_input_field_values(FOCUS_ELEMENT, BUTTON_GROUP, INPUT_TYPE)) == 0:
                empty_question_items.append(item)

        except Exception as e:
            print(e, "error get_empty_question_items item")

    return empty_question_items


def solve_questions(driver):
    sleep(2 + random())
    # gather all question items ia-Questions-item
    try:
        base_question_items = driver.find_elements(By.XPATH, "//div[starts-with(@class, 'ia-Questions-item')]")
        empty_question_items = get_empty_question_items(base_question_items)
        solve_items(driver, empty_question_items)
    except Exception as e:
        print(e, "error at aria-invalid")


def apply(driver, job_post):
    # wait until apply button appears
    sleep(6 + random())
    success_applying = False

    try:
        try:
            apply_button = driver.find_element(By.XPATH, ".//div[@id='jobsearch-ViewJobButtons-container']")
        except Exception as e:
            print(e, "apply button")
        sleep(4 + random())
        # try to identify onsite/offsite
        try:
            indeed_button = apply_button.find_element(By.XPATH, ".//*[contains(@class, 'IndeedApplyButton')]")
            if indeed_button.text == "Applied":
                job_post.onsite = True
                return False
        except Exception as e:
            print(e, "not indeed button")
            job_post.onsite = False
            try:
                job_post.href = apply_button.find_element(By.XPATH,
                                                          ".//a[starts-with(@href, 'https://www.indeed.com/applystart')]").get_attribute(
                    'href')
                driver.get(job_post.href)
                print(driver.current_url)
                sleep(10 + random())
                print(driver.current_url)
                job_post.href = driver.current_url
                if "indeed" in driver.current_url:
                    job_post.onsite = True
                    job_post.href = ""
            except Exception as e:
                job_post.onsite = True  # so that it is not appended to offline links
                job_post.href = ""
                print(e, "couldn't find offsite href")
        print(job_post)

        if job_post.onsite:
            try:
                indeed_button.click()
                sleep(4 + random())
            except Exception as e:
                print(e, "clicked indeed apply button error")

            flipping_pages = True
            flipping_page_counter = 0
            MAX_FLIPS = 20

            start_time = time()
            while flipping_pages and flipping_page_counter < MAX_FLIPS and time() - start_time < APPLY_TIMEOUT:
                sleep(4 + random())
                solve_questions(driver)
                solve_questions(driver)  # necessary because some dropdowns clear required fields
                try:
                    sleep(4 + random())
                    continue_button = driver.find_element(By.XPATH,
                                                          "//button[starts-with(@class, 'ia-continueButton')]")
                    driver.execute_script("arguments[0].click();", continue_button)
                    if continue_button.text.lower() == "submit your application":
                        success_applying = True
                        flipping_pages = False
                except Exception as e:
                    print(e, "couldn't find continue button")
                    flipping_pages = False
                flipping_page_counter += 1
        else:
            print("criteria not met: job_post onsite:", job_post.onsite)

    except Exception as e:
        print(e, "base apply")

    return success_applying
