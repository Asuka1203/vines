import sys

import asyncio

from src.duitang_album import DuiTangAlbum


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        DuiTangAlbum(sys.argv[1], r'D:/二次元表情').start()
    )
