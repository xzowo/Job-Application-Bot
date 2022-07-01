import json
from time import sleep, time
from random import random
from IndeedJobPost import IndeedJobPost
from datetime import datetime
from driver_config import *
from keyword_config import total_href_dict, offsite_links_dict, \
    company_vocab_omission_dict, common_dict_omissions, OFFSITE_LINKS_FNAME, TOTAL_LINKS_FNAME
from indeed_apply import apply
from process_label_text import process_label_text
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


# returns boolean of if overlap searching for jobs was detected. Due to indeed posting the same
# job on multiple pages, ignore returning true and quit based on number of pages iterated
def crawl_pg_and_do_work():

    try:
        wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class,'slider_item')]")))
        sleep(4 + random())
        prof_eles = driver.find_elements(By.XPATH, "//div[contains(@class,'slider_item')]")
        print(prof_eles, "\n")

        for ele in prof_eles:

            sleep(1 + random())
            try:
                ainfo = ele.find_element(By.XPATH, ".//a[contains(@class,'jcs-JobTitle')]")
            except:
                print("ERROR: ainfo")
                continue
            try:
                href = ainfo.get_attribute('href')
            except:
                print("ERROR: href")
                href = "not found"
            try:
                job_title = ainfo.get_attribute('aria-label')
                job_title = job_title.replace("full details of ", "")
            except:
                print("ERROR: job_title")
            try:
                company_name = ele.find_element(By.XPATH, ".//span[@class='companyName']").text
            except:
                print("ERROR: company_name")
            try:
                company_loc = ele.find_element(By.XPATH, ".//div[@class='companyLocation']").text
            except:
                print("ERROR: company_loc")
            try:
                rating_num = float(ele.find_element(By.XPATH, ".//span[@class='ratingNumber']/span").text)
            except:
                print("rating not found")
                rating_num = 0.0

            print(job_title, "|", company_name, "|", company_loc, "|", rating_num, "|", href)
            job_post = IndeedJobPost(job_title, company_name, company_loc, rating_num, href, True, datetime.today())

            if href in total_href_dict:
                continue

            sleep(2 + random())

            invalidate_company = False
            # need to check company for blacklisted words
            for word in company_vocab_omission_dict:
                if word.lower() in company_name.lower():
                    invalidate_company = True

            try:
                ele.find_element(By.XPATH, ".//div[@class='applied-snippet']")
                invalidate_company = True
            except:
                print("not applied to")

            if job_post.rating_num >= RATING_LOWER_BOUND and not invalidate_company:
                driver2.get(href)
                omission_count = 0
                contract_job = False
                job_desc_list = []
                job_desc_orig = ""

                try:
                    job_desc_orig = driver2.find_element(By.XPATH, "//div[@id='jobDescriptionText']").text
                    job_desc_copy = job_desc_orig + " "
                    processed_text = process_label_text(job_desc_copy)
                    job_desc_list = processed_text.lower().split()
                except:
                    print("ERROR: job_desc")

                if USING_OMISSION_DICT:
                    for word in job_desc_list:
                        if word in common_dict_omissions:
                            common_dict_omissions[word] += 1

                    for key in common_dict_omissions:
                        if common_dict_omissions[key] > 0:
                            omission_count += 1

                if OMIT_CONTRACT_JOBS:
                    try:
                        meta_data = driver2.find_element(By.XPATH, "//div[@id='salaryInfoAndJobType']")
                        if "contract" in meta_data.text.lower():
                            contract_job = True
                    except:
                        print("ERROR: meta_data")

                    if "Job Types: Full-time, Contract" in job_desc_orig:
                        contract_job = True

                if omission_count <= ALLOWED_STRIKES and not contract_job and href not in total_href_dict:
                    if not apply(driver2, job_post) and not job_post.onsite:
                        offsite_links_dict[job_post.href] = time()

                total_href_dict[href] = time()
            # done applying
            with open(OFFSITE_LINKS_FNAME, 'w') as file:
                json.dump(offsite_links_dict, file)

            with open(TOTAL_LINKS_FNAME, 'w') as file:
                json.dump(total_href_dict, file)

            print(job_post.asdict())
            print("\n")

    except Exception as err:
        print(err, "base")
    return False


if not DEBUG_MODE:
    try:
        pg_counter = 0
        flipping_jobs_pgs = True
        while flipping_jobs_pgs:
            if pg_counter > AMOUNT_OF_PGS_TO_SCAN:
                break
            if crawl_pg_and_do_work():
                break
            sleep(4 + random())
            try:
                next_pg = driver.find_element(By.XPATH, "//a[contains(@aria-label,'Next')]")
                driver.execute_script("arguments[0].click();", next_pg)
                print("\n\n")
                sleep(10 + random())
            except Exception as err:
                print("ERROR: next_pg")
                flipping_jobs_pgs = False

            pg_counter += 1
    except Exception as e:
        print(e, "root")

    driver.close()
    driver2.close()
