import sys

from engine.douban_movie import DoubanMovie
from library import common


if __name__ == '__main__':
    common.invoke(DoubanMovie(
        destination=r'D:/douban',
        art_type=DoubanMovie.TAG_COMIC,
        country='美国',
        year_range='2021,2021'
    ))
