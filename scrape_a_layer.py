# This program goes through every page in the current set of valid URLs and scan their pages for valid neighbor nodes
# This is a one-step BFS gathering of new nodes
# This is purely for data collection. No links are being established at this point

import requests
from bs4 import BeautifulSoup
from DataFiles import DataFiles
from confirm_page_structure import check_valid_page

base_url = "https://en.wikipedia.org/"

file_manager = DataFiles()

for url in file_manager.get_all_urls():
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

    for a in main_content.findAll("a", href=True):
        res = file_manager.test_valid_url(a["href"])
        if res == 0:
            # print(url)
            # url = "/wiki/John_McVie"
            href = str(a["href"])

            result = check_valid_page(href)
            if not result:
                file_manager.write_invalid_url(href)
            else:
                print(result)
                for genre in result[1:]:
                    file_manager.write_band(result[0], href, genre=genre)

    # break
