import os

import aiohttp
import asyncio


class Target:
    def __init__(self, identifier, destination):
        self.identifier = identifier
        self.destination = destination


class ConcurrencyLock:
    def __init__(self, maxsize):
        self._queue = asyncio.Queue(maxsize=maxsize)

    async def acquire(self):
        await self._queue.put(True)

    async def release(self):
        await self._queue.get()
        self._queue.task_done()

    async def wait(self):
        await self._queue.join()


def get_file_storage(
    session: aiohttp.ClientSession,
    destination: str,
    chunk_size: int = 1024
):
    async def _runner(url: str):
        filename = os.path.basename(url)
        async with session.get(url) as resp:
            with open(os.path.join(destination, filename), 'wb') as fd:
                while chunk := await resp.content.read(chunk_size):
                    fd.write(chunk)
    return _runner


async def save_file(session, url, destination):
    filename = os.path.basename(url)
    async with session.get(url) as resp:
        print(os.path.join(destination, filename))
        with open(os.path.join(destination, filename), 'wb') as fd:
            while chunk := await resp.content.read(1024):
                fd.write(chunk)


def invoke(engine):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(
        engine.start()
    )
