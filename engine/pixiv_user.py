import sys
from datetime import datetime

import aiohttp
import asyncio


if (sys.platform.startswith('win')
        and sys.version_info[0] == 3
        and sys.version_info[1] >= 8):
    policy = asyncio.WindowsSelectorEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)


cookies = 'first_visit_datetime_pc=2021-07-21+00%3A26%3A03; p_ab_id=5; p_ab_id_2=2; p_ab_d_id=853424; yuid_b=FBRIh3A; _gcl_au=1.1.179712625.1626794766; __utma=235335808.1817393791.1626794767.1626794767.1626794767.1; __utmz=235335808.1626794767.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utmc=235335808; OX_plg=pm; _im_vid=01FB28DDCK2TTVC9H24SKX9VGK; _im_uid.3929=b.488fce4e24f60c6b; __gads=ID=a8631375d99d7b64:T=1626794804:S=ALNI_MYQh2uwNI_gmdP7pgoWNJtXwxvgOw; privacy_policy_agreement=3; p_b_type=2; _ga=GA1.2.1817393791.1626794767; _gid=GA1.2.2144885215.1626794874; device_token=9661ac95bb613b265f5f28c06c137b3d; c_type=13; privacy_policy_notification=0; a_type=0; b_type=2; PHPSESSID=71003466_UNJfrnBR7eEdMOJH7zZTUltDTthxCG5I; login_ever=yes; __utmv=235335808.|2=login%20ever=yes=1^3=plan=normal=1^5=gender=female=1^6=user_id=71003466=1^9=p_ab_id=5=1^10=p_ab_id_2=2=1^11=lang=zh=1; ki_s=214908%3A0.0.0.0.2%3B214994%3A0.0.0.0.2%3B215190%3A0.0.0.0.2%3B217356%3A0.0.0.0.2; tags_sended=1; categorized_tags=6sZKldb07K~OT-C6ubi9i~ZxAyxs0UWi~pvU1D1orJa; _im_uid_ses.3929=1; __cf_bm=b76995fcb610df2527c93726ca22e2769c0681bb-1626798007-1800-Ae2SsMxL8S5jkBq3XInmBdmbgkUmot6XQp56wQ+essoHviuFJq79viDby6GBG4zoRC3NOcP7Io0Iq0z0xZe3n0HbFbVCHeKcnIR0ZfKwjVYTzxkxpg3cuv24qxH1JMSZFPPns2nynGbupW6AliTF0a/QXhfa/ibRJksXPpCpfH2GDj7qO4Inw7IyHTZHIvz2Qg==; tag_view_ranking=RTJMXD26Ak~uusOs0ipBx~Lt-oEicbBr~jhuUT0OJva~QjJSYNhDSl~jH0uD88V6F~Nbvc4l7O_x~ETjPkL0e6r~A1oTdhUlxh~PJlcDKH8I2~qW1DD3_EEC~WVRbK3kg3G~O0riLBoFTS~3zTBjGeK6o~WXbsuEKmd0~f-6mD28Iil~Za8yGdNz9N~2sgm5n-ALc~qCqegWCkc6~ay54Q_G6oX~1DreUdF52S~v3nOtgG77A~hhVYh4h14s~65aiw_5Y72~nnW_qUZnto~G4OQSTFumm~3-OZc4u8Oj~nSuMwg_8Tb~X8-oGgZ7-V~5m9I2ijATY~nm-96667yC~zMxnJ6p5R7~2NKc4vGSgQ~YRDwjaiLZn~t5wuY96p0s~UB9P3sELi3~7xyRz-BX8-~qtVr8SCFs5~ZxAyxs0UWi~FO5UFnietZ~TjzQohypbT~ClLaegOm3j~21paJKXch1~tlXeaI4KBb~Qfyjopqt3Z~5sqqiHTvD3~zx-g5-W1ik~1LN8nwTqf_~foBPiBr2cD~3K2g_lnLHZ~w6DOLSTOSN~xiDDtizeka~4KXgivPBMJ~v-OL0-Ncw6~b8QbNqtoeL~o7hvUrSGDN~5XeuL0klK_~_O3rPkfXWX~562khdE7He~uIaYQrjmIO~T0FIWOFoYX~wKl4cqK7Gl~gyoaRwlZx7; __utmt=1; ki_t=1626795047438%3B1626795047438%3B1626798217303%3B1%3B44; ki_r=aHR0cHM6Ly9saW5rLnpoaWh1LmNvbS8%2FdGFyZ2V0PWh0dHBzOi8vd3d3LnBpeGl2Lm5ldC9tZW1iZXIucGhwP2lkPTcxNDU3Nw%3D%3D; __utmb=235335808.89.10.1626794767'


class PixivUser:
    """
    下载 pixiv 画师图片
    """

    def __init__(self, user_id):
        self.session = aiohttp.ClientSession(headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Cookie': cookies,
            'Accept': 'application/json',
            'Referer': 'https://www.pixiv.net/'
        })
        self.user_id = user_id
        self.URL_ARTWORKS = f'https://www.pixiv.net/ajax/user/{str(user_id)}/profile/all?lang=zh'

    async def start(self):
        data = await self.get_json(self.URL_ARTWORKS)
        for art_id in data['illusts']:
            res = await self.get_json(f'https://www.pixiv.net/ajax/user/{self.user_id}/profile/illusts', {
                'ids[]': [art_id],
                'work_category': 'illustManga',
                'is_first_page': 1
            })
            dt = datetime.fromisoformat(res['works'][art_id]['createDate'])
            print(dt.tzinfo)
            break
            # print(f'https://i.pximg.net/img-original/img/{dt.strftime("%Y/%m/%d/%H/%M/%S")}/{art_id}_p0.png')
        await self.session.close()

    async def get_json(self, url, params=None):
        if params is None:
            params = {}
        # , proxy='http://127.0.0.1:62838'
        async with self.session.get(url, params=params) as response:
            json = await response.json(encoding='utf-8')
            if response.status == 200 and not json['error']:
                return json['body']
            return None

    async def get_raw(self, url, params=None):
        if params is None:
            params = {}
        async with self.session.get(url, params=params) as response:
            content = await response.text(encoding='utf-8')
            if response.status == 200:
                return content
            return None
