import asyncio
from aiohttp import web
import logging

address = '127.0.0.1'
port = 18080

async def index(request):
    return web.Response(body = b'<h1>This is index.</h1>', content_type = 'text/html')

async def init():
    app = web.Application()
    app.router.add_route('GET', '/', index)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, address, port)
    await site.start()
    logging.info('server started at http://%s:%d...' % (address, port))
    return site

loop = asyncio.get_event_loop()
loop.run_until_complete(init())
loop.run_forever()