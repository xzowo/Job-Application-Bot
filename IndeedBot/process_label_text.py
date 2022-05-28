# so that when split is performed it is easier to identify keywords
def process_label_text(label_text):
    some_text = ''.join(label_text)
    some_text = some_text.replace("\n", " ")
    some_text = some_text.replace("?", " ")
    some_text = some_text.replace(",", " ")
    some_text = some_text.replace(".", " ")
    some_text = some_text.replace(":", " ")
    some_text = some_text.replace(";", " ")
    some_text = some_text.replace("*", " ")
    return some_text
