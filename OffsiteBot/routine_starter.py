import json
import subprocess
from time import sleep

INDEED_OFFSITE_LINKS_PATH = "..\\IndeedBot\\offsite_links.json"
LINKS_FNAME_ASSOC_PATH = "links_fname_assoc.json"


def work_on_offsite_links(OFFSITE_LINKS_PATH, FNAME_ASSOC_PATH):
    # load json with offsite links
    with open(OFFSITE_LINKS_PATH, "r") as file:
        offsite_links_dict = json.load(file)

    # detect known offsite links, substr to routine.py
    with open(FNAME_ASSOC_PATH, "r") as file:
        links_fname_assoc_dict = json.load(file)

    valid_links_list = []
    for link in offsite_links_dict:
        for key in links_fname_assoc_dict:
            if key in link:
                valid_links_list.append(link)
    print(valid_links_list)

    for link in valid_links_list:
        # run the python file associated with the detection
        routine_fname = links_fname_assoc_dict[key]
        try:
            p1 = subprocess.run(["python", routine_fname, link], timeout=600)
            print(p1)

            if p1.returncode == 0:
                print("APPLIED:", link)
                offsite_links_dict.pop(link)
                with open(OFFSITE_LINKS_PATH, "w") as file:
                    json.dump(offsite_links_dict, file)
            elif p1.returncode == 1:
                print("DID NOT APPLY:", link)
        except Exception as e:
            print("subproc timeout:", e)
        sleep(4)


work_on_offsite_links(INDEED_OFFSITE_LINKS_PATH, LINKS_FNAME_ASSOC_PATH)
