import json

TOTAL_LINKS_FNAME = 'total_links.json'
OFFSITE_LINKS_FNAME = 'offsite_links.json'
COMPANY_KEYWORD_OMISSIONS_FNAME = 'company_keyword_omissions.json'
COMMON_KEYWORD_OMISSIONS_FNAME = 'common_keyword_omissions.json'

with open(TOTAL_LINKS_FNAME, 'r') as file:
    total_href_dict = json.load(file)
with open(OFFSITE_LINKS_FNAME, 'r') as file:
    offsite_links_dict = json.load(file)
with open(COMPANY_KEYWORD_OMISSIONS_FNAME, 'r') as file:
    company_vocab_omission_dict = json.load(file)
with open(COMMON_KEYWORD_OMISSIONS_FNAME, 'r') as file:
    common_dict_omissions = json.load(file)

HIGHEST_PRIORITY_PHRASES_FNAME = 'highest_priority_phrases.json'
PROFILE_KEYWORD_PHRASES_FNAME = 'profile_keyword_phrases.json'
PROFILE_KEYWORD_WORDS_FNAME = 'profile_keyword_words.json'
COMMON_KEYWORD_PHRASES = 'common_keyword_phrases.json'


def expand_dict(some_dict):
    keys = list(some_dict.keys()).copy()
    for word in keys:
        some_dict[word.lower()] = some_dict[word]
    return some_dict


with open(HIGHEST_PRIORITY_PHRASES_FNAME, 'r') as file:
    highest_priority_dict = expand_dict(json.load(file))

with open(PROFILE_KEYWORD_PHRASES_FNAME, 'r') as file:
    phrases_keyword_dict = expand_dict(json.load(file))

with open(PROFILE_KEYWORD_WORDS_FNAME, 'r') as file:
    word_keyword_dict = expand_dict(json.load(file))

with open(COMMON_KEYWORD_PHRASES, 'r') as file:
    common_keyword_dict = expand_dict(json.load(file))


# iterate dictionary words and check if in text list
def get_response(some_text, some_text_list, INDEXING="TEXT"):
    if INDEXING == "TEXT":
        for word in highest_priority_dict:
            if word.lower() in some_text.lower():
                print("Found match:", word, highest_priority_dict[word])
                return highest_priority_dict[word]

        for word in word_keyword_dict:
            if word.lower() in some_text_list:
                print("Found match:", word, word_keyword_dict[word])
                return word_keyword_dict[word]

        for word in phrases_keyword_dict:
            if word.lower() in some_text.lower():
                print("Found match in full str:", word, phrases_keyword_dict[word])
                return phrases_keyword_dict[word]

        for word in common_keyword_dict:
            if word.lower() in some_text.lower():
                print("Found match in full str:", word, common_keyword_dict[word])
                return common_keyword_dict[word]

    elif INDEXING == "DICTIONARY":
        for word in some_text_list:
            if word in highest_priority_dict:
                print("Found match:", word, highest_priority_dict[word])
                return highest_priority_dict[word]
            if word in word_keyword_dict:
                print("Found match:", word, word_keyword_dict[word])
                return word_keyword_dict[word]
            if word in phrases_keyword_dict:
                print("Found match:", word, phrases_keyword_dict[word])
                return phrases_keyword_dict[word]
            if word in common_keyword_dict:
                print("Found match:", word, common_keyword_dict[word])
                return common_keyword_dict[word]

    print("No match found: defaulting response")
    return None
