import json
import time

with open("offsite_links.json", "r") as file:
    offsite_links_dict = json.load(file)

DEL_JOBS_OLDER_THAN_DAYS = 7

def seconds_to_days(seconds):
    mins = seconds / 60
    hours = mins / 60
    days = hours / 24
    return days

del_entry_list = []
for key in offsite_links_dict:
    if seconds_to_days(time.time()) - seconds_to_days(offsite_links_dict[key]) > DEL_JOBS_OLDER_THAN_DAYS:
        del_entry_list.append(key)

for key in del_entry_list:
    offsite_links_dict.pop(key)


with open("offsite_links.json", "w") as file:
    json.dump(offsite_links_dict, file)