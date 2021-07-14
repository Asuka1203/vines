import aiohttp
import asyncio

from lib import common


class DuiTangAlbum:
    """
    下载[堆糖]专辑
    """

    _has_more_page = True

    def __init__(self, target: common.Target):
        """
        为请求做准备
        :param target: common.Target 对象
        """
        self.session = aiohttp.ClientSession()
        self.file_storage = common.get_file_storage(self.session, target.destination)
        self.list_task_lock = common.ConcurrencyLock(15)
        self.image_task_lock = common.ConcurrencyLock(25)

        self.PRE_PAGE = 24  # 这个数量是固定的
        self.URL = f'https://www.duitang.com/napi/album/detail/?album_id={target.identifier}'
        self.URL_SOURCE = f'https://www.duitang.com/napi/blog/list/by_album/?album_id={target.identifier}'
        self.URL_BLOG = f'https://www.duitang.com/napi/blog/detail/?blog_id='

    async def start(self):
        """
        开始下载任务
        以每页 24 条创建图片列表下载任务，下载的最大数量由 queue_source 控制
        等待任务 queue 取空并关闭 session
        :return:
        """
        start = 0
        while self._has_more_page:
            await self.list_task_lock.acquire()
            start = start + 1
            asyncio.create_task(self.list_task(start * self.PRE_PAGE))

        await self.list_task_lock.wait()
        await self.image_task_lock.wait()
        await self.session.close()

    async def list_task(self, start: int):
        """
        下载图片列表，并根据列表项创建图片下载任务
        图片下载的最大数量由 queue_image 控制
        :param start: 从第几个图片开始
        :return:
        """
        url = self.URL_SOURCE + f'&limit={str(self.PRE_PAGE)}&start={start}'
        data = await self.get_json(url)
        for obj in data['object_list']:
            await self.image_task_lock.acquire()
            asyncio.create_task(self.image_task(obj['id']))
        # 后续没有图片的情况
        if len(data['object_list']) == 0:
            self._has_more_page = False
        await self.list_task_lock.release()

    async def image_task(self, blog_id):
        """
        图片下载任务，根据 blog_id 获取图片地址并保存图片
        :param blog_id: 图片页面的标识符
        :return:
        """
        data = await self.get_json(self.URL_BLOG + str(blog_id))
        if data is not None:
            await self.file_storage(data['photo']['path'])
        await self.image_task_lock.release()

    async def get_json(self, url):
        async with self.session.get(url) as response:
            json = await response.json(encoding='utf-8')
            if response.status == 200 and json['status'] == 1:
                return json['data']
            return None
