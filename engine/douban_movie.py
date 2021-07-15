import aiohttp

from library import common


class DoubanMovie:
    """
    下载[豆瓣]电影信息
    """

    TYPE_STILLS = 'S'
    TYPE_POSTER = 'R'
    TYPE_WALLPAPER = 'W'

    TYPE_SORT_SCORE = 'S'
    TYPE_SORT_HOT = 'U'

    TAG_MOVIE = '电影'
    TAG_TV = '电视剧'
    TAG_VARIETY = '综艺'
    TAG_COMIC = '动漫'
    TAG_DOCU = '纪录片'
    TAG_SHORT = '短片'

    def __init__(self, ):
        self.session = aiohttp.ClientSession()
        self.file_storage = common.get_file_storage(self.session, target.destination)

        self.SEARCH_URL = 'https://movie.douban.com/j/new_search_subjects'

    @staticmethod
    def get_stills_url(movie_number, photo_type: str):
        """
        剧照链接
        :param photo_type: 查找类型
        :param movie_number:电影标识符
        :return: URL
        """
        return f'https://movie.douban.com/subject/{str(movie_number)}/photos?type={photo_type}'

