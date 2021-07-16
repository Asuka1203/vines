from engine.douban_movie import DoubanMovie
from library import common


if __name__ == '__main__':
    common.invoke(DoubanMovie(
        destination=r'E:\学习\douban',
        art_type=DoubanMovie.TAG_COMIC,
        country='日本',
        year_range='2021,2021'
    ))
