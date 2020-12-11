from DataFiles import DataFiles
import os
from bs4 import BeautifulSoup
import requests

# This file is for gathering what all things bands are called
# This is useful for identifying which Wikipedia pages refer to bands
# I.e. band, group, singer, duo, etc. all need to be accounted for
# Shouldn't need to run the file more than once. Ever
# It just confirms suspicions about the structure of web pages

# Confirm:
# Every page starts with the band name, bolded
# Then says a conjugated "be" ("is", "are", "was", "were")
# Then says what music group they are ("band", "duo")

# Corrected: Ambrosia, Damn Yankees, Iona, John Paul Jones, Scafell Pike, Q5, Lindisfarne, Trivium
# Removed from rock: The Notorious BIG, Sir Mix-a-lot, Sugarhill Gang, and Tupac

band_types = [
              # Rock band labels
              "band",
              "duo",
              "supergroup",
              "singer",
              "musician",
              "guitarist",
              "group",
              "rapper",
              "trio",
              # Country artist labels
              "duet",
              "ensemble",
              "vocalist",
              "music artist",
              "music</a> artist",
              "recording artist",
              "pop artist",
              "country</a> artist",
              "country artist",
              "folk artist",
              "folk</a> artist",
              "instrument artist",
              "red dirt</a> artist",
              "indie artist",
              "guitar</a> player",
              "guitar player",
              "blues</a> star",
              "blues star",
              "country</a> star",
              "country star",
              "music</a> entertainer",
              "music entertainer",
              "music</a> performer",
              "music performer",
              "songwriter and entertainer",
              "mandolinist",
              "fiddler",
              "fiddle</a> player",
              "fiddle player"
              "pianist",
              "saxophonist",
              "instrumentalist",
              "violinist",
              "banjo player",
              "banjo</a> player",
              "banjoist",
              # Metal labels
              "quartet",
              # Miscellaneous
              "quintet",
              ]

bes = ["is", "are", "were", "was"]

base_url = "https://en.wikipedia.org/"


# Pass in a paragraph, and see if it has a valid structure, according to the rules
def check_valid_p(t):
    # Ignore capitalization
    t = t.lower()
    # Only take the first 350 characters of the string to ignore later content in the paragraph
    t = t[:350]

    if "</b>" not in t:
        return False

    bold_pos = t.find("</b>")
    be_pos = len(t)
    for be in bes:
        pos = t.find(be, bold_pos)
        if pos != -1:
            be_pos = min(be_pos, pos)

    if be_pos == len(t):
        return False

    for band_type in band_types:
        if band_type in t[be_pos:]:
            return True


def check_valid_page(url):
    url = base_url + url
    r = requests.get(url)

    soup = BeautifulSoup(r.text, 'html.parser')
    contains_valid_p = False
    for p in soup.findAll("p"):
        p = str(p)
        if check_valid_p(p):
            contains_valid_p = True

    if not contains_valid_p:
        return False

    main_content = soup.findAll("h1", {"id": "firstHeading"})
    if len(main_content) != 1:
        raise Exception("Error!!!!! Heading format broken on page")
    title = main_content[0].get_text()

    for table in soup.findAll("table", {"class": "infobox"}):
        # print(table)
        for tr in table.findAll("tr"):
            if "genres" in str(tr).lower():
                genres = [title]
                for genre in ["rock", "country", "metal"]:
                    if genre in str(tr.get_text()).lower():
                        genres.append(genre)
                # If no genre matches, we aren't interested
                if len(genres) == 1:
                    return False
                # Otherwise, return what genres it matches on
                return genres

    # It didn't have a matching infobox table, so it isn't a valid table
    return False


def check_all():
    file_manager = DataFiles()
    urls = file_manager.get_all_urls()

    for url in urls:
        # url = "/wiki/Lindsey_Buckingham"
        is_a_band = check_valid_page(url)

        if not is_a_band:
            print(base_url + url)

        break


if __name__ in "__main__":
    check_all()
