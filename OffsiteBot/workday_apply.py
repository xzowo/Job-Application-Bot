from random import random
from time import sleep, time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import date, timedelta
from keyword_config import get_response, cred_dict, RESUME_PATH
from process_label_text import process_label_text
from selenium.webdriver.common.action_chains import ActionChains


def slow_type(element, text, delay=0.05):
    text = str(text)  # to ensure that default input such as int or float is iterable
    for character in text:
        element.send_keys(character)
        sleep(delay + (random() / 3.0))


# exists due to information not being readily available on the page. dropdown and multiinput will use this late
# and when data modification is necessary
def get_button_group_dropdown(focus_element, driver):
    button_group = None
    try:
        print("CLICKING DROPDOWN")
        root_button = focus_element.find_element(By.XPATH, ".//button[@aria-haspopup='listbox']")
        driver.execute_script("arguments[0].click();", root_button)
        sleep(4 + random())

        root_button2 = focus_element.find_element(By.XPATH, ".//button[@aria-haspopup='listbox']")
        print("is dropdown expanded?", root_button2.get_attribute('aria-expanded'))
        listbox_ul_id = root_button2.get_attribute('aria-controls')
        listbox_ul = driver.find_element(By.XPATH, ".//ul[@id='" + listbox_ul_id + "']")
        button_group = listbox_ul.find_elements(By.TAG_NAME, "li")  # can just click elements
    except Exception as e:
        print(e, "get_button_group error finding dropdown")
    sleep(1 + random())
    return button_group


def get_button_group_multi(focus_element, driver):
    button_group = None
    try:
        prompt_search_button = focus_element.find_element(By.XPATH,
                                                          ".//div[@data-automation-id='multiselectInputContainer']")
        prompt_search_button.click()
        sleep(10 + random())
        button_group = driver.find_elements(By.XPATH, ".//div[@data-automation-id='promptLeafNode']")
    except Exception as e:
        print(e, "get_button_group error finding multiinput")
    sleep(1 + random())
    return button_group


# should probably not try to assign button group yet, only assign when attempting to assign values.
# this is due to listbox information not being readily available on the page.
# it is mandatory to click to get info from the popup
def derive_input_type(item, driver):
    focus_element = None
    button_group = None
    THE_TYPE = ""
    # formfield- contains dropdown, text, radio, or checkbox
    try:
        focus_element = item
        try:
            item.find_element(By.XPATH, ".//button[@aria-haspopup='listbox']")
            THE_TYPE = "DROPDOWN"
        except:
            # print("derive error finding dropdown")
            try:
                button_group = focus_element.find_elements(By.XPATH, ".//input[@type='text']")
                if len(button_group) == 0:
                    raise Exception("")
                THE_TYPE = "TEXT"
            except:
                # print("derive error finding text inputs")
                try:
                    button_group = focus_element.find_elements(By.XPATH, ".//input[@type='radio']")
                    if len(button_group) == 0:
                        raise Exception("")
                    THE_TYPE = "RADIO"
                except:
                    # print("derive error finding radio inputs")
                    try:
                        button_group = focus_element.find_elements(By.XPATH, ".//input[@type='checkbox']")
                        if len(button_group) == 0:
                            raise Exception("")
                        THE_TYPE = "CHECKBOX"
                    except:
                        pass
                        # print("derive error finding checkbox inputs")
        if THE_TYPE == "":
            raise Exception("derive error finding dropdown, radio, checkbox, or text inputs")
    except Exception as e:
        print(e)
        try:
            focus_element = item.find_element(By.TAG_NAME, "textarea")
            THE_TYPE = "TEXTAREA"
        except:
            # print("derive error finding textarea input")
            try:
                item.find_element(By.XPATH, ".//div[@data-automation-id='dateInputWrapper']")
                focus_element = item
                THE_TYPE = "DATE"
            except:
                # print("derive error finding date")
                try:
                    item.find_element(By.XPATH, ".//div[@data-automation-id='multiSelectContainer']")
                    focus_element = item
                    THE_TYPE = "MULTIINPUT"
                except:
                    print("derive error finding multiinput, or unknown type")
    return [focus_element, button_group, THE_TYPE]


def is_input_field_empty(FOCUS_ELEMENT, BUTTON_GROUP, INPUT_TYPE, driver):
    ret_list = []
    if INPUT_TYPE == "RADIO" or INPUT_TYPE == "CHECKBOX":
        id_text_list = []
        for button in BUTTON_GROUP:
            if button.get_attribute('aria-checked') == 'true':
                id_text_list.append(button.get_attribute('id'))
        # translate radio button ids into label text
        for button_id_text in id_text_list:
            ret_list.append(FOCUS_ELEMENT.find_element(By.XPATH, ".//label[@for='" + button_id_text + "']").text)

    elif INPUT_TYPE == "TEXTAREA":
        some_str = FOCUS_ELEMENT.text
        if some_str.replace(' ', '').replace('\n', '') != '':
            ret_list.append(some_str)

    elif INPUT_TYPE == "DROPDOWN":
        dropdown = FOCUS_ELEMENT.find_element(By.XPATH, ".//button[@aria-haspopup='listbox']")
        if dropdown.get_attribute('value') != "":
            ret_list.append(dropdown.text)

    elif INPUT_TYPE == "MULTIINPUT":
        try:
            multi_item = FOCUS_ELEMENT.find_element(By.XPATH, ".//div[starts-with(@id, 'pill-')]")
            ret_list.append(multi_item.text)
        except:
            print("couldnt find multiitem")

    elif INPUT_TYPE == "DATE":
        mm_ele = FOCUS_ELEMENT.find_element(By.XPATH, ".//input[@aria-label='Month']")
        dd_ele = FOCUS_ELEMENT.find_element(By.XPATH, ".//input[@aria-label='Day']")
        yyyy_ele = FOCUS_ELEMENT.find_element(By.XPATH, ".//input[@aria-label='Year']")
        mm_str = mm_ele.text
        dd_str = dd_ele.text
        yyyy_str = yyyy_ele.text

        # all strings must be numeric to be considered selected
        if mm_str.isnumeric() and dd_str.isnumeric() and yyyy_str.isnumeric():
            ret_list.append(mm_str + "//" + dd_str + "//" + yyyy_str)

    elif INPUT_TYPE == "TEXT":
        some_str = BUTTON_GROUP[0].get_attribute('value')
        if some_str is not None and some_str.replace(' ', '') != '':
            ret_list.append(some_str)

    else:
        ret_list.append("NOT INITIALIZED, TREATING AS A FINISHED ITEM")
        print("unknown type in get_empty_question_items, USING PLACEHOLDER TO IGNORE")

    print("is_input_field_empty:", ret_list)
    if len(ret_list) == 0:
        return True
    return False


def resolve_input(driver, item, response):
    DEFAULT_INPUT = 1
    DEFAULT_DATE = date.today()
    derived = derive_input_type(item, driver)
    FOCUS_ELEMENT = derived[0]
    BUTTON_GROUP = derived[1]
    INPUT_TYPE = derived[2]

    if INPUT_TYPE == "DROPDOWN":
        BUTTON_GROUP = get_button_group_dropdown(FOCUS_ELEMENT, driver)
    elif INPUT_TYPE == "MULTIINPUT":
        BUTTON_GROUP = get_button_group_multi(FOCUS_ELEMENT, driver)

    if BUTTON_GROUP is not None:
        BUTTON_GROUP = BUTTON_GROUP[::-1]

    print("resolve_input function given:", response, "\nFocus element:", FOCUS_ELEMENT.text, BUTTON_GROUP, INPUT_TYPE)
    try:
        question_text = ""
        try:
            question_text = item.find_element(By.XPATH, ".//label[starts-with(@for, 'input-')]").text
        except:
            # where date is different
            try:
                question_text = item.find_element(By.XPATH, ".//label[starts-with(@id, 'label-')]").text
            except:
                print("question text error")

        if INPUT_TYPE == "RADIO":
            clicked_a_button = False
            if response is not None:

                if not clicked_a_button:
                    for button in BUTTON_GROUP:
                        print(button.text)
                        # button does not contain text, but only the id
                        button_id_text = button.get_attribute('id')
                        answer_text = FOCUS_ELEMENT.find_element(By.XPATH,
                                                                 ".//label[@for='" + button_id_text + "']").text
                        print(button_id_text, answer_text)
                        print("RESPONSE:", response)

                        if response.lower() == answer_text.lower():
                            driver.execute_script("arguments[0].click();", button)
                            clicked_a_button = True
                            break

            if not clicked_a_button:
                for button in BUTTON_GROUP:
                    print(button.text)
                    # button does not contain text, but only the id
                    button_id_text = button.get_attribute('id')
                    answer_text = FOCUS_ELEMENT.find_element(By.XPATH, ".//label[@for='" + button_id_text + "']").text
                    print(button_id_text, answer_text)
                    print("RESPONSE:", response)

                    if response is not None and response in answer_text:
                        driver.execute_script("arguments[0].click();", button)
                        clicked_a_button = True
                        break
                    elif response is not None and response.lower() in answer_text.lower():
                        driver.execute_script("arguments[0].click();", button)
                        clicked_a_button = True
                        break
                    else:
                        if "disability" in process_label_text(question_text).lower() and "Yes" in answer_text:
                            continue
                        if "veteran" in process_label_text(question_text).lower() and "Yes" in answer_text:
                            continue

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

                    if "Do you have experience in " in question_text and "Yes" in answer_text:
                        driver.execute_script("arguments[0].click();", button)
                        clicked_a_button = True
                    elif " degree?" in question_text and "Yes" in answer_text:
                        driver.execute_script("arguments[0].click();", button)
                        clicked_a_button = True

                if not clicked_a_button:
                    driver.execute_script("arguments[0].click();", BUTTON_GROUP[0])

        elif INPUT_TYPE == "CHECKBOX":
            clicked_a_button = False
            for button in BUTTON_GROUP:
                print(button.text)
                # button does not contain text, but only the id
                button_id_text = button.get_attribute('id')
                answer_text = FOCUS_ELEMENT.find_element(By.XPATH, ".//label[@for='" + button_id_text + "']").text
                print(button_id_text, answer_text)
                print("RESPONSE:", response)

                # checkboxes should rely on dictionary indexing only
                if clicked_a_button:
                    response = None

                if response is not None and response.lower() in answer_text.lower():
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
                FOCUS_ELEMENT.click()
                FOCUS_ELEMENT.clear()
                slow_type(FOCUS_ELEMENT, response)
                FOCUS_ELEMENT.sendKeys(Keys.TAB)
            else:
                FOCUS_ELEMENT.click()
                FOCUS_ELEMENT.clear()
                slow_type(FOCUS_ELEMENT, DEFAULT_INPUT)
                FOCUS_ELEMENT.sendKeys(Keys.TAB)

        elif INPUT_TYPE == "TEXT":
            if response is not None:
                BUTTON_GROUP[0].click()
                BUTTON_GROUP[0].clear()
                slow_type(BUTTON_GROUP[0], response)
                BUTTON_GROUP[0].sendKeys(Keys.TAB)
            else:
                BUTTON_GROUP[0].click()
                BUTTON_GROUP[0].clear()
                slow_type(BUTTON_GROUP[0], DEFAULT_INPUT)
                BUTTON_GROUP[0].sendKeys(Keys.TAB)

        elif INPUT_TYPE == "DROPDOWN":
            options = BUTTON_GROUP
            print("REACHED DROPDOWN INPUTTING, response:", response)
            try:
                if response is not None:
                    made_selection = False

                    # attempt to find exact match
                    for op in options:
                        print(response, op.text)
                        if response.lower() == op.text.lower():
                            driver.execute_script("arguments[0].click();", op)
                            made_selection = True
                            break

                    if not made_selection:
                        for op in options:
                            print(response, op.text)
                            if response.lower() in op.text.lower():
                                driver.execute_script("arguments[0].click();", op)
                                made_selection = True
                                break

                    if not made_selection:
                        driver.execute_script("arguments[0].click();", options[0])
                        made_selection = True

                else:
                    driver.execute_script("arguments[0].click();", options[0])
                    made_selection = True
            except Exception as e:
                print(e, "error at trying to select in dropdown")

        elif INPUT_TYPE == "MULTIINPUT":
            # can be expressed as a tree
            # sometimes, the depth is deeper than one
            # very finicky. selenium locators have issues finding promptLeafNodes on the end leafs
            # the only thing that is reliable, is simulating keys with actions
            # clicking in a lower width window is unreliable
            # is the tree depth greater than 1? check if the menu still exists
            reached_end_leaf = False
            actions = ActionChains(driver)
            while not reached_end_leaf:
                try:
                    multi_buttons = driver.find_elements(By.XPATH, "//div[@data-automation-id='promptLeafNode']")
                    print("MULTI_BUTTONS:", multi_buttons)
                    if len(multi_buttons) > 0:
                        actions.send_keys(Keys.DOWN).perform()
                        sleep(1)
                        actions.send_keys(Keys.ENTER).perform()
                        sleep(1)
                    else:
                        reached_end_leaf = True
                        actions.send_keys(Keys.DOWN).perform()
                        sleep(1)
                        actions.send_keys(Keys.ENTER).perform()
                        sleep(1)
                        break
                except Exception as e:
                    print(e, "tree dive error")
                sleep(4 + random())

        elif INPUT_TYPE == "DATE":
            driver.execute_script("arguments[0].click();", FOCUS_ELEMENT)
            sleep(1)  # /..//div[@data-automation-id='spinnerDisplay']
            mm_ele = FOCUS_ELEMENT.find_element(By.XPATH, ".//input[@aria-label='Month']")
            driver.execute_script("arguments[0].click();", mm_ele)
            sleep(1)
            mm_ele.send_keys(DEFAULT_DATE.strftime("%m"))
            sleep(1)
            dd_ele = FOCUS_ELEMENT.find_element(By.XPATH, ".//input[@aria-label='Day']")
            driver.execute_script("arguments[0].click();", dd_ele)
            sleep(1)
            dd_ele.send_keys(DEFAULT_DATE.strftime("%d"))
            sleep(1)
            yyyy_ele = FOCUS_ELEMENT.find_element(By.XPATH, ".//input[@aria-label='Year']")
            driver.execute_script("arguments[0].click();", yyyy_ele)
            sleep(1)
            yyyy_ele.send_keys(DEFAULT_DATE.strftime("%Y"))
            sleep(1)

        else:
            print("unknown input type or blank")

    except Exception as e:
        print(e, "error resolving input")


def solve_items(driver, the_items):
    for item in the_items:
        sleep(2 + random())
        question_text = ""
        try:
            question_text = item.find_element(By.XPATH, ".//label[starts-with(@for, 'input-')]").text
        except:
            # where date is different
            try:
                question_text = item.find_element(By.XPATH, ".//label[starts-with(@id, 'label-')]").text
            except:
                print("question text error")

        processed_text = process_label_text(question_text)

        question_text_list = processed_text.lower().split()
        response = get_response(question_text, question_text_list, INDEXING="TEXT")
        # need to figure out how to differentiate inputs
        resolve_input(driver, item, response)


def get_empty_question_items(question_items):
    empty_question_items = []
    for item in question_items:
        try:
            derived = derive_input_type(item, driver)
            FOCUS_ELEMENT = derived[0]
            BUTTON_GROUP = derived[1]
            INPUT_TYPE = derived[2]
            print(FOCUS_ELEMENT.text, BUTTON_GROUP, INPUT_TYPE)
            # questions without an answer list will return [] which is getting appended
            # using placeholder in get_input_field_values to ignore questions without an answer list
            if is_input_field_empty(FOCUS_ELEMENT, BUTTON_GROUP, INPUT_TYPE, driver):
                empty_question_items.append(item)

        except Exception as e:
            print(e, "error get_empty_question_items item")
    display_list = []
    for item in empty_question_items:
        display_list.append(item.text)
    print("empty q items:", display_list)
    return empty_question_items


def get_required_question_items(question_items):
    req_question_items = []
    for item in question_items:
        try:
            item_label = item.find_element(By.XPATH, ".//abbr[@title='required']")
            req_question_items.append(item)
        except Exception as e:
            print("couldn't find required for item\n")
    return req_question_items


def solve_questions(driver):
    sleep(2 + random())
    # gather all question items data-automation-id
    try:
        base_question_items = driver.find_elements(By.XPATH, "//div[starts-with(@data-automation-id, 'formField-')]")
        required_question_items = get_required_question_items(base_question_items)
        empty_question_items = get_empty_question_items(required_question_items)
        solve_items(driver, empty_question_items)
    except Exception as e:
        print(e, "error at aria-invalid")


# returns True on login
def login(driver, EMAIL, PASSWORD):
    sleep(5 + random())
    try:
        email_input = driver.find_element(By.XPATH, "//input[@data-automation-id='email']")
        password_input = driver.find_element(By.XPATH, "//input[@data-automation-id='password']")
        email_input.send_keys(EMAIL)
        password_input.send_keys(PASSWORD)
        sleep(.3)
        submit_button = driver.find_element(By.XPATH, "//div[@data-automation-id='noCaptchaWrapper']")
        submit_button.click()
        # check to see if continue button exists
        sleep(20 + random())
        driver.find_element(By.XPATH, "//button[@data-automation-id='bottom-navigation-next-button']")
    except Exception as e:
        print(e, "error at login, attempting create acc")

        try:
            sleep(1 + random())
            create_acc_button = driver.find_element(By.XPATH, "//button[@data-automation-id='createAccountLink']")
            create_acc_button.click()
            sleep(1 + random())

            email_input = driver.find_element(By.XPATH, "//input[@data-automation-id='email']")
            password_input = driver.find_element(By.XPATH, "//input[@data-automation-id='password']")
            verify_password_input = driver.find_element(By.XPATH, "//input[@data-automation-id='verifyPassword']")
            try:
                create_acc_checkbox = driver.find_element(By.XPATH,
                                                          "//input[@data-automation-id='createAccountCheckbox']")
                create_acc_checkbox.click()
            except:
                print("create acc checkbox not found")

            email_input.send_keys(EMAIL)
            password_input.send_keys(PASSWORD)
            verify_password_input.send_keys(PASSWORD)
            sleep(1 + random())
            submit_button = driver.find_element(By.XPATH, "//div[@data-automation-id='noCaptchaWrapper']")
            submit_button.click()
            # check to see if continue button exists
            sleep(20 + random())
            driver.find_element(By.XPATH, "//button[@data-automation-id='bottom-navigation-next-button']")
            # on some websites, it requires email verification
            alert_msg = driver.find_element(By.XPATH, "//button[@data-automation-id='alertMessage']")
            if "An email has been sent to you. Please verify your account." in alert_msg.text:
                # need to login to email and press verify
                print("Need to click verification link")
                return False

        except Exception as e:
            print(e, "login form detection issue")
            return False
    return True


def apply(driver):
    # wait until apply button appears
    sleep(6 + random())
    applied = False
    APPLY_TIMEOUT = 600

    try:
        err_msg = driver.find_element(By.XPATH, "//span[@data-automation-id='errorMessage']")
        if err_msg.text.lower() == "the page you are looking for does not exist":
            applied = True
            print("Page does not exist")
            return applied
        else:
            print("page seems valid, but has error message")
    except Exception as e:
        print("page seems valid")

    try:
        try:
            apply_button = driver.find_element(By.XPATH, "//a[@data-automation-id='adventureButton']")
            driver.execute_script("arguments[0].click();", apply_button)
            sleep(4 + random())
        except Exception as e:
            print(e, "apply button")
            return applied

        try:
            autofill_w_resume_button = driver.find_element(By.XPATH, "//a[@data-automation-id='autofillWithResume']")
            autofill_w_resume_button.click()
        except Exception as e:
            print(e, "autofill w resume button")
            return applied

        # sometimes login isn't neccessary to apply for a job
        login_status = login(driver, cred_dict['email'], cred_dict['password'])
        print("login status:", login_status)

        try:
            driver.find_element(By.XPATH, "//div[@data-automation-id='alreadyApplied']")
            applied = True
            return applied
        except:
            print("couldnt find already applied")

        try:
            select_file = driver.find_element(By.XPATH, "//input[@data-automation-id='file-upload-input-ref']")
            select_file.send_keys(RESUME_PATH)
            # takes a moment to upload
            sleep(5 + random())
        except Exception as e:
            print("select file issue")

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
                                                      "//button[@data-automation-id='bottom-navigation-next-button']")

                if "submit" in continue_button.text.lower():
                    applied = True
                    flipping_pages = False
                    
                continue_button.click()
                sleep(4 + random())
                    
            except:
                print("Couldn't find continue button")
                # need to check if it is submitted
                try:
                    driver.find_element(By.XPATH, "//div[@data-automation-id='auth_form_img_container']")
                    applied = True
                    flipping_pages = False
                except:
                    print("Couldn't find congratulations checkmark")
                flipping_pages = False
            flipping_page_counter += 1

    except Exception as e:
        print(e, "base apply")

    return applied


driver = webdriver.Chrome()
# driver.set_window_position(0, 0)
# found out width and clicking is unreliable
# driver.set_window_size(50, 1041)  # it is mandatory to be this width due to the weirdness of multiinput clicking
driver.get(sys.argv[1])
sleep(4 + random())
if apply(driver):
    print("WORKDAY: APPLIED")
    driver.close()
else:
    print("WORKDAY: ERROR APPLYING")
    driver.close()
    raise Exception("WORKDAY: ERROR APPLYING")
