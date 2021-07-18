import asyncio

import bs4
import aiohttp

import os

queue = asyncio.Queue(10)
queue2 = asyncio.Queue(20)
session: aiohttp.ClientSession

PAGE_URL = 'https://wall.alphacoders.com/by_sub_category.php?id=333944&name=%E5%8E%9F%E7%A5%9E+%E5%A3%81%E7%BA%B8&lang=Chinese&quickload=3025'


async def get_image(href):
    async with session.get('https://wall.alphacoders.com/' + href) as resp:
        soup_big = bs4.BeautifulSoup(await resp.text(encoding='utf-8'), 'html.parser')
        src = soup_big.find('img', class_='main-content').get('src')
        filename = os.path.basename(src)
        async with session.get(src) as resp2:
            with open(os.path.join(r'D:\yuanshen', filename), 'wb') as fd:
                while chunk := await resp2.content.read(1024):
                    fd.write(chunk)
            print(href)
            await queue2.get()
            queue2.task_done()


async def get_images(url):
    print(url)
    async with session.get(url) as resp:
        if resp.status == 200:
            soup_out = bs4.BeautifulSoup(await resp.text(encoding='utf-8'), 'html.parser')
            boxgrs = soup_out.find(class_='page_container').find_all(class_='boxgrid')
            for boxgr in boxgrs:
                await queue2.put(1)
                href = boxgr.find('a').get('href')
                asyncio.create_task(get_image(href))
        await queue.get()
        queue.task_done()
        return resp.status == 200


async def main():
    global session
    session = aiohttp.ClientSession()
    page = 1
    first_page_url = 'https://wall.alphacoders.com/by_sub_category.php?id=333944&name=%E5%8E%9F%E7%A5%9E+%E5%A3%81%E7%BA%B8&lang=Chinese'
    await queue.put(1)
    asyncio.create_task(get_images(first_page_url))
    while True:
        await queue.put(1)
        page = page + 1
        page_url = f'{PAGE_URL}&page={page}'
        res = await get_images(page_url)
        if res is False:
            break
    await queue.join()
    await queue2.join()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
