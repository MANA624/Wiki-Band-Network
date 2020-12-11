import requests
from bs4 import BeautifulSoup
from DataFiles import DataFiles


# This file is responsible for the initial scraping of all the list of rock, country, and metal bands
# to populate the text files with all of the band names and their URLs


def initial_scrape(curr_genre):
    params = {
        "rock": {
            "url": "https://en.wikipedia.org/wiki/List_of_rock_music_performers",
            "inds": [1, 28]
        },
        "country": {
            "url": "https://en.wikipedia.org/wiki/List_of_country_music_performers",
            "inds": [1, 27]
        },
        "metal": {
            "url": "https://en.wikipedia.org/wiki/List_of_heavy_metal_bands",
            "inds": []
        }
    }

    curr_page = params[curr_genre]
    r = requests.get(curr_page["url"])

    soup = BeautifulSoup(r.text, 'html.parser')

    if curr_genre in ["country", "rock"]:
        bands_list = soup.findAll("ul")[curr_page["inds"][0]:curr_page["inds"][1]]
        bands_list = "".join([str(band) for band in bands_list])

    elif curr_genre in ["metal"]:
        bands_list = soup.find("table", {"class": "wikitable"}).tbody.findAll("tr")
        bands_list = ''.join([str(row.findAll("td")[0]) for row in bands_list if len(row.findAll("td")) > 0])

    else:
        raise Exception("Invalid genre!")

    soup = BeautifulSoup(bands_list, "html.parser")
    hrefs = soup.findAll('a', href=True, title=True)

    urls = [a['href'] for a in hrefs]
    titles = [a['title'] for a in hrefs]

    if len(urls) != len(titles):
        raise Exception("Oops! There was a parsing error!")

    file_handler = DataFiles()
    file_handler.set_genre(curr_genre)
    file_handler.write_header()
    for i in range(len(urls)):
        file_handler.write_band(titles[i], urls[i])


if __name__ in "__main__":
    initial_scrape("rock")
    initial_scrape("country")
    initial_scrape("metal")
