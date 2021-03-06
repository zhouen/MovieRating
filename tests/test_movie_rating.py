#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import pytest

from ..movie_rating.movie_rating import get_imdb_id_by_url
from ..movie_rating.movie_rating import get_movie_details_by_id
from ..movie_rating.movie_rating import get_movie_name_and_year
from ..movie_rating.movie_rating import create_query
from ..movie_rating.movie_rating import get_release_year_by_date
from ..movie_rating.movie_rating import get_movie_rating_by_url


def test_create_query():
    """
    """
    test_cases = [
        {
            "title": "The Lego Batman Movie",
            "series": None,
            "year": "2017",
            "expected_query": "The Lego Batman Movie y:2017"
        },
        {
            "title": "Assassin's Creed",
            "series": None,
            "year": "2016",
            "expected_query": "Assassin's Creed y:2016"
        },
        {
            "title": "Moonlight",
            "series": None,
            "year": "2016",
            "expected_query": "Moonlight y:2016"
        },
        {
            "title": "Daddys Home",
            "series": "2",
            "year": "2017",
            "expected_query": "Daddys Home 2 y:2017"
        }
    ]
    for test in test_cases:
        actual_query = create_query(test["title"], test["series"], test["year"])
        assert actual_query == test["expected_query"], \
            "Expected query: [{}], but got: [{}]".format(
                test["expected_query"], 
                actual_query
            )


def test_get_imdb_id_by_url():
    """
    Test
    """
    movie_url = "http://www.imdb.com/title/tt6255746/?ref_=fn_ft_tt_1"
    expected_id = "tt6255746"
    actual_id = get_imdb_id_by_url(movie_url)
    assert expected_id == actual_id, \
        "Expected movie id: [{}], but got: [{}]".format(expected_id, actual_id)


@pytest.mark.skip(reason='skip for now')
def test_get_movie_rating_by_url():
    """
    """
    movie_url = "http://www.imdb.com/title/tt6255746/?ref_=fn_ft_tt_1"
    actual_rating = get_movie_rating_by_url(movie_url)
    expected_rating = "6.4"
    assert actual_rating, \
        "Expected movie rating is a digit, but got: [{}]".format(actual_rating)
    assert expected_rating == actual_rating, \
        "Expected rating: [{}], but got: [{}]".format(
            expected_rating,
            actual_rating
        )


def test_get_movie_details_by_id():
    """
    Test get_movie_details_by_id()
    tt4116284
    """
    movie_id = "tt4116284"
    expected_movie_details = {
        "original_title": "The Lego Batman Movie",
        "title": "The Lego Batman Movie",
        "release_date": "2017-02-08",
        "vote_average": 7.2,
        "original_language": "en",
        "imdb_id": "tt4116284",
        "production_countries": [
            {
            "iso_3166_1": "DK",
            "name": "Denmark"
            },
            {
                "iso_3166_1": "US",
                "name": "United States of America"
            }
        ]
    }
    actual_details = get_movie_details_by_id(movie_id)
    for key, expected_value in expected_movie_details.items():
        assert expected_value == actual_details.get(key), \
            "Expected movie details: [{}] is [{}], but got: [{}]".format(
                key,
                expected_value,
                actual_details.get(key)
            )

@pytest.mark.skip(reason='get_movie_name_and_year is depricated')
def test_get_movie_name_and_year():
    """
    """
    filenames = [
        "Inner.Workings.2016.1080p.BluRay.x264-HDEX[EtHD]",
        "Moonlight.2016.720p.BluRay.x264-SPARKS[rarbg]",
        "The.Lego.Batman.Movie.2017.1080p.WEB-DL.DD5.1.H264-FGT",
        "Assassin's.Creed.2016.1080p.WEB-DL.DD5.1.H264-FGT",
        "Prometheus.2012.普罗米修斯.国英双语.HR-HDTV.AC3.1024X576-人人影视制作"
    ]
    expected_results = [
        {
            "name": "Inner Workings",
            "year": "2016"
        },
        {
            "name": "Moonlight",
            "year": "2016"
        },
        {
            "name": "The Lego Batman Movie",
            "year": "2017"
        },
        {
            "name": "Assassin's Creed",
            "year": "2016"
        },
        {
            "name": "Prometheus",
            "year": "2012"
        }
    ]
    for ind, name in enumerate(filenames):
        expected_name = expected_results[ind]["name"]
        expected_year = expected_results[ind]["year"]
        actual_name, actual_year = get_movie_name_and_year(name)
        assert expected_name == actual_name, \
            "Expected name: [{}], but got: [{}]".format(
                expected_name,
                actual_name
            )
        assert expected_year == actual_year, \
            "Expected year: [{}], but got: [{}]".format(
                expected_name,
                actual_year
            )
    # The same name should be returned
    irregular_name = "Some.Name.Without.Resolution.2014.WEB-DL.DD5.1.H264-FGT"
    actual_name, actual_year = get_movie_name_and_year(irregular_name)
    expected_name = "Some Name Without Resolution"
    expected_year = "2014"
    assert expected_name == actual_name, \
        "Expected name: [{}], but got: [{}]".format(expected_name, actual_name)
    assert expected_year == actual_year, \
            "Expected year was [{}], but got: [{}]".format(
                expected_year,
                actual_year
            )

def test_get_release_year_by_date():
    """
    :return:
    """
    test_dates = [
        "2016-01-25",
        "2015-12-12",
        "0000-00-00"
    ]
    for date in test_dates:
        actual_year = get_release_year_by_date(date)
        expected_year = date.split("-")[0]
        assert expected_year == actual_year, \
                "Expected year: [{}], but got: [{}]".format(
                    expected_year,
                    actual_year
                )
