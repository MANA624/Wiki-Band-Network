# This file goes through all genres

import requests
from bs4 import BeautifulSoup
from DataFiles import DataFiles

base_url = "https://en.wikipedia.org/"

file_manager = DataFiles()

for url in file_manager.get_all_urls():
    # url = "/wiki/Tears_for_Fears"
    r = requests.get(base_url + url)
    # r = requests.get("https://en.wikipedia.org/wiki/Christine_McVie")
    print(url)

    soup = BeautifulSoup(r.text, 'html.parser')
    main_content = soup.findAll("div", {"id": "content"})

    # If, for some bizarre reason, there's not exactly one id="content" div tag
    if len(main_content) != 1:
        main_content = soup
    else:
        main_content = main_content[0]

    # Ensure we only add one of each connection with a set
    add_urls = dict()

    for a in main_content.findAll("a", href=True):
        href = str(a["href"])
        res = file_manager.test_valid_url(href)
        if res == 1:
            # print(href)

            if href in add_urls:
                add_urls[href] += 1
            else:
                add_urls[href] = 1

    this_num = file_manager.get_node_num(url)

    for u in add_urls:
        file_manager.write_edge(this_num, file_manager.get_node_num(u), add_urls[u])

    # break
