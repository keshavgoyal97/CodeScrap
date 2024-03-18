# This is a sample Python script.
import json
import ast

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import requests
from bs4 import BeautifulSoup
from collections import deque

url = 'https://www.geeksforgeeks.org/find-length-of-a-linked-list-iterative-and-recursive/'
parent_url = 'https://www.geeksforgeeks.org'
url_archives = {parent_url: 1}
url_queue = deque()
extract_pages = {}
# check status code for response received
# success code - 200
# print(r)
# nonBreakSpace = u'\xa0'

# Parsing the HTML
dlq = []
# soup = soup.replace(nonBreakSpace, ' ')



# print(soup.title)
#
# # Getting the name of the tag
# # print(soup)
#
# # Getting the name of parent tag
# print(soup.title.parent.name)


def valid_tag(element):
    return False if element.name is None else True


def extract_code_from_code_container(html_element):
    code = ""

    for child in html_element:
        if valid_tag(child):
            code = code + child.get_text().replace('\xa0', ' ') + "\n"

    return code


def extract_code_container_from_web_page(element):
    s = element.findAll('div', class_='code-block')
    if len(s) == 0:
        return None

    python_code_versions = []
    for s1 in s:
        i_ele = s1.find(lang="python3")
        if i_ele is not None:
            # print(s1)

            # print(s1.contents[3])
            code_block = s1.find("div", class_="container")
            # if code_block.contents[3] == " ":
            # print(len(code_block.contents[5].text))
            python_code_versions.append(extract_code_from_code_container(code_block).replace('"', "'"))

    return python_code_versions

def retrieve_all_valid_links_from_page(soup):
    a_tags = soup.findAll('a')
    for a_tag in a_tags:
        if a_tag.has_attr('href'):
            link = a_tag["href"]
            link = link.removesuffix('/')
            if link.startswith(parent_url) and link not in url_archives:
                url_queue.append(link)
                url_archives[link] = 1


# print(content)
# Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     url_queue.append(parent_url)
#     while len(url_queue) > 0:
#         url = url_queue.popleft()
#         print(f"stats queue size {len(url_queue)}  dlq size {len(dlq)}  url archives {len(url_archives)}  extracted codes {len(extract_pages)}")
#         r = requests.get(url)
#         soup = BeautifulSoup(r.content, 'html.parser')
#         soup.encode(formatter='html')
#         code_blocks = extract_code_container_from_web_page(soup)
#         if code_blocks is None:
#             dlq.append(url)
#             print("URL does not have any code blocks" + url)
#         else:
#             extract_pages[soup.title.string] = code_blocks
#
#         if len(extract_pages.keys()) >= 100:
#             with open("url_archive.json", "w+") as fp:
#                 json.dump(url_archives, fp)
#
#             with open("dlq.json", "w") as fp:
#                 json.dump(dlq, fp)
#
#             with open("extracted_code.json", "w") as fp:
#                 json.dump(extract_pages, fp)
#
#             with open("queued_url.json", "w") as fp:
#                 json.dump({"queue": [*url_queue]}, fp)
#
#             break
#
#         retrieve_all_valid_links_from_page(soup)
