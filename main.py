import threading
from bs4 import BeautifulSoup
import requests
import pandas as pd


'''
This program gathers information of the top animes on the My Anime List website (https://myanimelist.net/topanime.php)
and exports the information crawled into an Excel and CSV file.

Specify the number of pages to crawl using PAGES_TO_CRAWL
Specify the name of the exported file using FILE_NAME
Specify the number of threads created using NUM_OF_THREADS (Note: there must be at least 1 thread)
'''


# Loops through the first n pages of the MAL webpage and calls the get_anime_links function on each page
def get_animes(n):
    print("Finding Animes")
    for i in range(n):
        get_anime_links(50 * i)
        print("Found " + str(len(animes)) + " animes")


# Sifts through the html of the given page and pulls out the links to the anime page
def get_anime_links(limit):
    source_code = requests.get(BASE_URL + str(limit))
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, "html.parser")
    links = soup.find_all("a", "hoverinfo_trigger fl-l ml12 mr8")
    # Adds all found links to animes
    for link in links:
        animes.append(link.get('href'))


# Finds data of the anime given its MAL link
def get_anime_data(link):
    source_code = requests.get(link)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, "html.parser")

    # Finds name of anime
    try:
        name = soup.find("h1", {"class": "title-name h1_bold_none"}).strong.contents
        name = name.pop()
    except:
        print("Missing Name: " + link)
        name = ""

    # Finds the number of episode of the anime
    try:
        episodes = soup.find("span", {"id": "curEps"}).contents
        # print(episodes)
        episodes = int(episodes.pop())
    except:
        print("Missing episodes: " + link)
        episodes = ""

    # Finds the Season of release of the anime
    try:
        release = soup.find("span", {"class": "information season"}).a.contents
        # print(release)
        release = release.pop()
    except:
        print("Missing release: " + link)
        release = ""

    # Finds the score of the anime
    try:
        score = soup.find("span", {"itemprop": "ratingValue"}).contents
        # print(score)
        score = float(score.pop())
    except:
        print("Missing score: " + link)
        score = ""

    # Finds the number of people who rated the anime
    try:
        rating_count = soup.find("span", {"itemprop": "ratingCount"}).contents
        rating_count = int(rating_count.pop())
        # print(rating_count)
    except:
        print("Missing rating count: " + link)
        rating_count = ""

    # Finds the number of members of the anime
    try:
        members = soup.find("span", {"class": "numbers members"}).strong.contents
        # print(members)
        members = int(members.pop().replace(",", ""))
    except:
        print("Missing member count: " + link)
        members = ""

    # Adds the crawled data to data
    data.append([name, episodes, release, score, rating_count, members])


# Create threads
def create_threads(number_of_threads):
    print("Gathering information on the animes found")
    for i in range(number_of_threads):
        t = threading.Thread(target=coder, args=(i,))
        threads.append(t)
        t.start()


# Ran by each thread once created
def coder(index):
    print("Thread " + str(index) + " created")
    while True:
        try:
            # Takes one element from animes and crawls it
            link = animes.pop(0)
            print("Thread " + str(index) + " now crawling " + link)
            get_anime_data(link)
        except IndexError:
            # Once there is nothing to crawl, end the loop
            print("Thread " + str(index) + " ended")
            break


# Constants
BASE_URL = "https://myanimelist.net/topanime.php?limit="

# User input
PAGES_TO_CRAWL = 5
NUM_OF_THREADS = 8
FILE_NAME = "MAL_data"

# Defining variables
animes = []
data = []
threads = []

# Gets animes and cralw them
get_animes(PAGES_TO_CRAWL)
# print(animes)
create_threads(NUM_OF_THREADS)

# Wait for all threads to terminate
for x in threads:
    x.join()

# Convert to Pandas Data Frame
print("Loading Data")
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
df = pd.DataFrame(data, columns=['Anime Name', 'Number of Episodes', 'Season of Release',
                                 'MAL Rating', 'Rating Count', 'Members'])
df.index = range(1, df.shape[0] + 1)
print(df)

# Exports as csv and Excel files
print("Exporting Data")
df.to_csv(FILE_NAME + ".csv")
df.to_excel(FILE_NAME + ".xlsx")
