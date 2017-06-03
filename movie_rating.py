#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import pudb
import ipdb
from bson.json_util import dumps
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
import sys
from os import listdir
from os.path import join, isdir

BLACKLISTED_STR = ["(TV Movie)", ":", "(Short)"]


def get_movies(folder_path):
    """
    Get a list of movies from the given folder
    """
    # mypath = os.path.dirname(os.path.realpath(__file__))
    files = []
    try:
        files = [f for f in listdir(folder_path) if isdir(join(folder_path, f))]
    except OSError as msg:
        print("No movies were found in: {}".format(folder_path))
    return files


def get_movie_name_and_year(name):
    """
    name: original folder name contains the movie
    return: movie name with year in dotted notation
    """
    movie_name = ""
    year = ""
    if "720p" in name:
        movie_name = name.split("720p")[0].strip(".").replace(".", " ")
        # print(movie_name)
    elif "1080p" in name:
        movie_name = name.split("1080p")[0].strip(".").replace(".", " ")
    else: 
        movie_name = name
    title = []
    for x in movie_name.split(" ")[:-1]:
        if not set(x) & set(["(", ")"]):
            title.append(x.title())
        else:
            title.append(x)
    # print(title)
    year = movie_name.split(" ")[-1]
    # print(year)
    
    return " ".join(title), year


def create_query(movie_title, year):
    """
    movie_name: dotted notation name
    return query with name in + fashion
    """
    query = []
    # -1 is used to exclude year
    for i in movie_title.split(" "):
        if not set(["(", ")"]) & set(i):
            query.append(i)
    # add year separately
    query.append(year)
    return " ".join(query)


def get_movie_url(movie_title, year):
    """
    """
    movie_url = "http://www.imdb.com"
    movie_href = ""
    query = create_query(movie_title, year)

    url = "http://www.imdb.com/find?ref_=nv_sr_fn&q={}&s=tt&ttype=ft&ref_=fn_ft".format(query)
    expected_title = "{}".format(movie_title.lower())
    expected_year = "({})".format(year)
    doc=pq(url, method="get", verify=True)
    soup = BeautifulSoup(doc.html(), "html.parser")
    if soup.find("div", {"class": "findNoResults"}):
        url = "http://www.imdb.com/find?ref_=nv_sr_fn&q={}&s=tt".format(query)
        doc=pq(url, method="get", verify=True)
        soup = BeautifulSoup(doc.html(), "html.parser")
    table = soup.find('table', {'class': 'findList'})
    rows = table.findAll('tr')
    found = False
    for tr in rows:
        cols = tr.findAll('td')
        # pudb.set_trace()
        for col in cols:
            col_text = str(col.text.encode('utf-8').decode('ascii', 'ignore').strip())
            if col_text:
                for s in BLACKLISTED_STR:
                    col_text = col_text.replace(s, "")
                col_text = col_text.strip().lower()
                # NB: identify movie in there
                if col_text.startswith(expected_title) and col_text.endswith(expected_year):
                    movie_href = cols[1].find('a').get("href")
                    found = True
                    break
        if found:
            break
    movie_url += movie_href
    return movie_url


def get_imdb_id_by_url(url):
    """
    http://www.imdb.com/title/tt6255746/?ref_=fn_ft_tt_1
    """
    imdb_id = url.split("/")[-2]
    if imdb_id.startswith("tt"):
        return imdb_id
    else:
        return None


def get_movie_details_by_id(imdb_id):
    """
    https://api.themoviedb.org/3/movie/{imdb_id}?api_key=c73d7f19c33a3c43d4f4f66a80cde8d7
    original_title: string
    title: string
    release_date: string
    vote_average: number
    production_countries: list of dictionary
    original_language: string
    """
    import requests
    url = "https://api.themoviedb.org/3/movie/{}?api_key=c73d7f19c33a3c43d4f4f66a80cde8d7&format=json".format(imdb_id)
    response = requests.get(url)
    # TODO: 1. create mongo query based on this information
    # TODO:      a. query {original_title: "", title: "", release_date: "", imdb_id:, id:""}
    # TODO: 2. Create Media DB with a collection called Movies
    # TODO: 3. Get poster: https://image.tmdb.org/t/p/w500/{poster_path}
    ipdb.set_trace()
    data = response.json()
    assert response.status_code == 200, "Expected response code: 200, but got {}".format(dumps(data, indent=4))
    refined_data = {
        "original_title": "",
        "title": "",
        "release_date": "",
        "vote_average": 0,
        "original_language": "",
        "revenue": 0,
        "imdb_id": "",
        "poster_path": ""
    }
    if data:
        production_countries = [country["name"] for country in data["production_countries"]]
        for key in refined_data.keys():
            refined_data[key] = data.get(key)
        refined_data["production_countries"] = production_countries
    return refined_data
    # print(dumps(refined_data, indent=4))


def get_movie_rating_by_url(url, verify=False):
    """
    Get movie title to confirm
    Get movie rating
    """
    doc=pq(url, method="get", verify=True)
    soup = BeautifulSoup(doc.html(), "html.parser")
    rating_div = soup.find('span', {"itemprop": 'ratingValue'})
    rating_str = str(rating_div)
    if verify:
        verify_searched_results(url, soup)
    # Get rating
    rating = rating_str.replace('</span>', "").split(">")[-1]
    return rating


def verify_searched_results(url, soup_html):
    """
    Verify movie title and year find on IMDB against themoviedb.org
    """
    print("Verifying... ...")
    imdb_id = get_imdb_id_by_url(url)
    verified_data = get_movie_details_by_id(imdb_id)
    title_div = soup_html.find("h1", {"itemprop":"name"}).get_text().encode('utf-8').decode('ascii', 'ignore')
    title_str = title_div.lower()
    # Verify movie title and year
    release_year = get_release_year_by_date(verified_data.get("release_date"))
    try:
        assert release_year in title_div, \
            "Expected to find [{}] in [{}].".format(release_year, str(title_div.encode('utf-8')))
        assert verified_data['title'].lower() in title_div.lower(), \
            "Expected to find [{}] in [{}].".format(verified_data['title'], str(title_div.encode('utf-8')))
    except AssertionError as msg:
        print("\tFailed: {}".format(msg))
    else:
        print("\tPASSED!!!")
    print(url)


def get_release_year_by_date(release_date):
    """
    release_date: 2016-05-14 accepted format
    """
    return release_date.split("-")[0]


def get_movie_poster_by_poster_path(poster_path):
    """
    """
    poster_url = "https://image.tmdb.org/t/p/w500/{}".format(poster_path)
    if sys.version_info[0] < 3:
        import urllib
        urllib.urlretrieve(poster_url, "local-filename2.jpg")
    else:
        import urllib.request
        urllib.request.urlretrieve(poster_url, "local-filename3.jpg")


def main():
    movies = []
    verify = False
    path = "/run/media/nathan/DATA/Movies/"
    # A movie name from command line
    if len(sys.argv) == 2:
        if sys.argv[1] == '--verify':
            verify = True
            movies = get_movies(path)
        else:
            movies = [sys.argv[-1]]
    elif len(sys.argv) == 3:
        if sys.argv[1] == "--verify":
            verify = True
        movies = [sys.argv[-1]]
    # A directory of movies
    else:
        movies = get_movies(path)
    # No movies were found/given, use these movies for testing
    if not movies:
        movies = [
            # "Arrival.(II).2016.1080p.WEB-DL.DD5.1.H264-FGT",
            # "The.Boss.Baby.2017.1080p.WEB-DL.DD5.1.H264-FGT",
            # "Logan.2017.1080p.WEB-DL.DD5.1.H264-FGT",
            # "Gifted.2017.1080p.HC.WEBRip.x264.AAC2.0-STUTTERSHIT",
            # "War.Machine.2017.1080p.NF.WEBRip.DD5.1.x264-SB",
            # "Colossal.2016.1080p.WEB-DL.AAC2.0.H264-FGT.mkv",
            # "Gold.2016.1080p.WEB-DL.DD5.1.H264-FGT",
            # "The.Wizard.of.Lies.2017.1080p.WEBRip.DD5.1.x264-monkee",
            # "Jackie.2016.1080p.WEB-DL.DD5.1.H264-FGT",
            # "Manchester.by.the.Sea.2016.1080p.WEB-DL.DD5.1.H264-FGT",
            "Inner.Workings.2016.1080p.BluRay.x264-HDEX[EtHD]",
            "Moonlight.2016.720p.BluRay.x264-SPARKS[rarbg]",
            "The.Lego.Batman.Movie.2017.1080p.WEB-DL.DD5.1.H264-FGT",
            "Assassin's.Creed.2016.1080p.WEB-DL.DD5.1.H264-FGT"
        ]
        print("Using testing movie list: \n")
        print(dumps(movies, indent=4))
    
    # Lookup movies
    for name in movies:
        print(name)
        movie_title, year = get_movie_name_and_year(name)
        movie_url = get_movie_url(movie_title, year)
        imdb_id = get_imdb_id_by_url(movie_url)
        if not imdb_id:
            sys.exit("No IMDB ID found.")
        if set(sys.argv) & set(["--poster"]):
            poster_path = get_movie_details_by_id(imdb_id).get("poster_path")
            get_movie_poster_by_poster_path(poster_path)
        rating = get_movie_rating_by_url(movie_url, verify)
        
        print("{} ({}): {} / 10.0\n\n".format(movie_title, year, rating))

if __name__ == '__main__':
    main()