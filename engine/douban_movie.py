import asyncio
import math
import os
import re

import aiohttp
import bs4

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

    @staticmethod
    def get_stills_url(movie_number, photo_type: str):
        """
        剧照链接
        :param photo_type: 查找类型
        :param movie_number:电影标识符
        :return: URL
        """
        return f'https://movie.douban.com/subject/{str(movie_number)}/photos?type={photo_type}'

    def __init__(
            self,
            destination: str,
            country: str,
            year_range: str,
            art_type: str = TAG_MOVIE,
            sort_type: str = TYPE_SORT_HOT
    ):
        self.session = aiohttp.ClientSession(headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://accounts.douban.com/'
        }, cookies={
            'push_doumail_num': '0',
            'push_noty_num': 0,
            '_pk_ses.100001.4cf6': '*',
            '_pk_ref.100001.4cf6': '%5B%22%22%2C%22%22%2C1626367316%2C%22https%3A%2F%2Faccounts.douban.com%2F%22%5D',
            '__utmc': '30149280',
            '__utmz': '30149280.1626367316.1.1.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/',
            'dbcl2': '"115982146:qjSslmchsY0"',
            'bid': 'zTUtcsgl7nA'
        })
        self.file_storage = common.get_file_storage(self.session, destination)
        self.subject_page_lock = common.ConcurrencyLock(6)
        self.images_page_lock = common.ConcurrencyLock(10)
        self.image_lock = common.ConcurrencyLock(30)

        self.SEARCH_URL = 'https://movie.douban.com/j/new_search_subjects'
        self.destination = destination
        self.art_type = art_type
        self.country = country
        self.year_range = year_range
        self.sort_type = sort_type

    def get_page_params(self, start):
        params = {
            'sort': self.sort_type,
            'range': '0,10',
            'tags': self.art_type,
            'start': start,
            'countries': self.country,
            'year_range': self.year_range
        }
        return params

    @staticmethod
    def get_photos_params(start, image_type):
        return {
            'type': image_type,
            'start': start,
            'size': 'a',
            'subtype': 'a'
        }

    async def start(self):
        start = 0
        while True:
            data = await self.get_json(f'{self.SEARCH_URL}?', self.get_page_params(start))
            if data is None or len(data) == 0:
                break
            start = start + 20
            for movie in data:
                # print(movie['url'])
                title = re.sub(r'[/:\\~*$%@&.`·?]', '_', movie['title'])
                dirname = os.path.join(self.destination, title)
                os.makedirs(dirname, exist_ok=True)
                await self.subject_page_lock.acquire()
                asyncio.create_task(self.subject_page_task(movie['url']))
                asyncio.create_task(self.images_scheduler(
                    movie['id'], self.TYPE_STILLS, os.path.join(dirname, '剧照'))
                )

        await self.image_lock.wait()
        await self.subject_page_lock.wait()
        await self.images_page_lock.wait()
        await self.session.close()

    async def images_scheduler(self, movie_id, image_type, dirname):
        params = self.get_photos_params(0, image_type)
        html_doc = await self.get_raw(f'https://movie.douban.com/subject/{movie_id}/photos', params)
        soup = bs4.BeautifulSoup(html_doc, 'html.parser')
        page_number = 1
        if paginator := soup.find(class_='paginator'):
            total_str = paginator.find(class_='count').string
            page_number = math.ceil(int(re.sub(r'[^\d]', '', total_str)) / 30)
        # print(page_number)
        for page in range(page_number):
            await self.images_page_lock.acquire()
            asyncio.create_task(self.images_page_task(movie_id, page * 30, image_type, dirname))

    async def images_page_task(self, movie_id, start, image_type, dirname):
        params = self.get_photos_params(start, image_type)
        html_doc = await self.get_raw(f'https://movie.douban.com/subject/{movie_id}/photos', params)
        soup = bs4.BeautifulSoup(html_doc, 'html.parser')
        li_list = soup.find(class_='article').find('ul').find_all('li')
        for li in li_list:
            await self.image_lock.acquire()
            href = li.find(class_='cover').find('a').get('href')
            asyncio.create_task(self.image_task(href, dirname))
        await self.images_page_lock.release()

    async def image_task(self, href, dirname):
        html_doc = await self.get_raw(href)
        soup = bs4.BeautifulSoup(html_doc, 'html.parser')
        src = soup.find(class_='article').find(class_='mainphoto').find('img').get('src')
        print(f'{src} -> {dirname}')
        await self.image_lock.release()

    async def subject_page_task(self, url):
        html_doc = await self.get_raw(url)
        soup = bs4.BeautifulSoup(html_doc, 'html.parser')
        title = soup.find(id='content').find('span').string
        link_report = soup.find(id='link-report')
        detail = ''
        if link_report:
            detail = link_report.find(property='v:summary').get_text()
        # print(title)
        title = re.sub(r'[/:\\~*$%@&.`·?]', '_', title)
        dirname = os.path.join(self.destination, title)
        os.makedirs(dirname, exist_ok=True)
        with open(os.path.join(dirname, '电影简介.txt'), 'w', encoding='utf-8') as f:
            f.writelines([title, '\n', detail.strip()])

        await self.subject_page_lock.release()

    async def get_json(self, url, params=None):
        if params is None:
            params = {}
        async with self.session.get(url, params=params) as response:
            json = await response.json(encoding='utf-8')
            if response.status == 200:
                try:
                    return json['data']
                except KeyError as err:
                    print('异常')
                    print(json)
                    raise err
            return None

    async def get_raw(self, url, params=None):
        if params is None:
            params = {}
        async with self.session.get(url, params=params) as response:
            content = await response.text(encoding='utf-8')
            if response.status == 200:
                return content
            return None
