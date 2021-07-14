import os.path

import aiohttp
import asyncio


class DuiTangAlbum:
    session = aiohttp.ClientSession()
    queue_source = asyncio.Queue(maxsize=15)
    queue_image = asyncio.Queue(maxsize=25)
    has_more_source = True
    pre_page = 24

    def __init__(self, album_id, save_path):
        self.save_path = save_path
        self.URL = f'https://www.duitang.com/napi/album/detail/?album_id={album_id}'
        self.URL_SOURCE = f'https://www.duitang.com/napi/blog/list/by_album/?album_id={album_id}'
        self.URL_BLOG = f'https://www.duitang.com/napi/blog/detail/?blog_id='

    async def start(self):
        """
        开始下载任务
        以每页 24 条创建图片列表下载任务，下载的最大数量由 queue_source 控制
        等待任务 queue 取空并关闭 session
        :return:
        """
        start = 0
        while self.has_more_source:
            start = start + 1
            await self.queue_source.put(1)
            asyncio.create_task(self.task_source(start * self.pre_page))
        await self.queue_source.join()
        await self.queue_image.join()
        await self.session.close()

    async def task_source(self, start: int):
        """
        下载图片列表，并根据列表项创建图片下载任务
        图片下载的最大数量由 queue_image 控制
        :param start: 从第几个图片开始
        :return:
        """
        url = self.URL_SOURCE + f'&limit={str(self.pre_page)}&start={start}'
        data = await self.get_json(url)
        for obj in data['object_list']:
            await self.queue_image.put(1)
            asyncio.create_task(self.task_image(obj['id']))
        # 后续没有图片的情况
        if len(data['object_list']) == 0:
            self.has_more_source = False
        await self.queue_source.get()
        self.queue_source.task_done()

    async def task_image(self, blog_id):
        """
        图片下载任务，根据 blog_id 获取图片地址并保存图片
        :param blog_id: 图片页面的标识符
        :return:
        """
        data = await self.get_json(self.URL_BLOG + str(blog_id))
        if data is not None:
            await self.save_image(data['photo']['path'])
        await self.queue_image.get()
        self.queue_image.task_done()

    async def save_image(self, url: str):
        chunk_size = 1024
        filename = os.path.basename(url)
        async with self.session.get(url) as resp:
            with open(os.path.join(self.save_path, filename), 'wb') as fd:
                print(filename)
                while chunk := await resp.content.read(chunk_size):
                    fd.write(chunk)

    async def get_json(self, url):
        async with self.session.get(url) as response:
            json = await response.json(encoding='utf-8')
            if response.status == 200 and json['status'] == 1:
                return json['data']
            return None
