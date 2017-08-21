"""
Usage:
    play_warp.py [options]

Options:
    --debug
    --host=<h>     Host [default: 0.0.0.0]
    --port=<p>     Port [default: 1081]
    --verbose=<v>  Verbose [default: 0]
"""
from socket import TCP_NODELAY
from time import time
import asyncio
import logging
import random
import functools
import re

import aiohttp
import aiosocks
import asyncio_redis
from aiosocks.helpers import Socks5Addr
from docopt import docopt as docoptinit
# import qbtrade as qb
import concurrent.futures
import json
import requests

FIRST_COMPLETED = concurrent.futures.FIRST_COMPLETED
# socks5_addr = Socks5Addr('ubuntu.urwork.qbtrade.org', '1080')
socks5_addr = Socks5Addr('localhost', '1080')
socks5_auth = None

REGEX_HOST = re.compile(r'(.+?):([0-9]{1,5})')
REGEX_CONTENT_LENGTH = re.compile(r'\r\nContent-Length: ([0-9]+)\r\n', re.IGNORECASE)
REGEX_CONNECTION = re.compile(r'\r\nConnection: (.+)\r\n', re.IGNORECASE)

clients = {}
verbose = 0


def is_aboard(host):
    url = 'http://ip.cn/index.php?ip={}'
    html = requests.get(url.format(host)).text.lower()
    if 'china' in html:
        return False
    else:
        return True


class Config:
    timeout = 30


async def check_iscn(host):
    url = 'http://ip.cn/index.php?ip={}'
    async with aiohttp.ClientSession() as ss:
        r = await ss.get(url.format(host))
        html = await r.text()
        html = html.lower()
        if 'china' in html:
            return True
        else:
            return False


class ProxySelector:
    def __init__(self):
        self.redis = None
        self.proxy_host = {}
        self.inwall = None
        self.outwall = None
        # asyncio.ensure_future(self.init())
        self.cn = set()
        self.notcn = set()

    async def init(self):
        self.redis = await asyncio_redis.Pool.create('service.qbtrade.org', poolsize=5)
        self.inwall = json.loads(await self.redis.get('proxy:human-inwall'))
        self.outwall = json.loads(await self.redis.get('proxy:human-outwall'))
        t = await self.redis.smembers('proxy:ip.cn:cn')
        # print(t, type(t))
        for x in t:
            # print(x, type(x))
            self.cn.add(await x)
        for x in await self.redis.smembers('proxy:ip.cn:notcn'):
            self.notcn.add(await x)

        print(self.cn)
        print(self.notcn)

    async def update_proxy(self, host):
        if host in self.cn or host in self.notcn:
            return
        r = await check_iscn(host)
        if r:
            self.cn.add(host)
            await self.redis.sadd('proxy:ip.cn:cn', [host])
        else:
            self.notcn.add(host)
            await self.redis.sadd('proxy:ip.cn:notcn', [host])

    def get_use_proxy_or_not(self, host):
        for item in self.inwall:
            if host.endswith(item):
                return False, 'human-inwall'

        for i in self.outwall:
            if host.endswith(i):
                return True, 'human-outwall'
        if host in self.proxy_host:
            return True, 'cannot-direct-connect'

        if host in self.notcn:
            return True, 'not-cn'

        return False, 'default'

    def add_outwall(self, host):
        logging.info('add to outwall', host)
        self.proxy_host[host] = True

    def set_result(self, host, timeout, use_proxy):
        self.proxy_host[host] = {'proxy': use_proxy, 'timeout': timeout}


def accept_client(client_reader, client_writer, *, loop=None):
    ident = hex(id(client_reader))[-6:]
    task = asyncio.ensure_future(process_warp(client_reader, client_writer, loop=loop), loop=loop)
    clients[task] = (client_reader, client_writer)
    started_time = time()

    def client_done(task):
        del clients[task]
        client_writer.close()
        logging.debug('[%s] Connection closed (took %.5f seconds)' % (ident, time() - started_time))

    logging.info('[%s] Connection started' % ident)
    task.add_done_callback(client_done)


async def process_warp(client_reader, client_writer, *, loop=None):
    ident = str(hex(id(client_reader)))[-6:]
    header = ''
    payload = b''
    try:
        RECV_MAX_RETRY = 3
        recv_retry = 0
        while True:
            line = await client_reader.readline()
            if not line:
                if len(header) == 0 and recv_retry < RECV_MAX_RETRY:
                    # handle the case when the client make connection but sending data is delayed for some reasons
                    recv_retry += 1
                    await asyncio.sleep(0.2, loop=loop)
                    continue
                else:
                    break
            if line == b'\r\n':
                break
            if line != b'':
                header += line.decode()

        m = REGEX_CONTENT_LENGTH.search(header)
        if m:
            cl = int(m.group(1))
            while len(payload) < cl:
                payload += await client_reader.read(1024)
    except Exception as e:
        logging.warning(e)

    if len(header) == 0:
        logging.debug('[%s] !!! Task reject (empty request)' % ident)
        return
    req = header.split('\r\n')[:-1]
    if len(req) < 4:
        logging.debug('[%s] !!! Task reject (invalid request)' % ident)
        return
    head = req[0].split(' ')
    if head[0] == 'CONNECT':  # https proxy
        await wrap_https(client_reader, client_writer, head, ident, loop)
    else:
        logging.warning('this is not http proxy')


async def wrap_https(client_reader, client_writer, head, ident, loop):
    try:
        logging.debug('proxy https %sBYPASSING <%s %s> (SSL connection)' %
                      ('[%s] ' % ident if verbose >= 1 else '', head[0], head[1]))
        m = REGEX_HOST.search(head[1])
        host = m.group(1)
        port = int(m.group(2))
        await proxy_selector.redis.hincrby('proxy:stats', host, 1)
        asyncio.ensure_future(proxy_selector.update_proxy(host))
        t, reason = proxy_selector.get_use_proxy_or_not(host)
        if t:
            logging.info(f'[{ident}] proxy  to {host}, {port} {reason}')
            req_reader, req_writer = await aiosocks.open_connection(proxy=socks5_addr,
                                                                    proxy_auth=socks5_auth,
                                                                    dst=(host, port), remote_resolve=True,
                                                                    loop=loop)
        else:
            logging.info(f'[{ident}] direct to {host}, {port} {reason}')
            try:
                req_reader, req_writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port, ssl=False, loop=loop), timeout=Config.timeout)
                await proxy_selector.redis.hincrby('proxy:direct-not-timeout', host, 1)
            except asyncio.TimeoutError:
                logging.warning(f'timeout for {host} add it to proxy')
                proxy_selector.add_outwall(host)
                await proxy_selector.redis.hincrby('proxy:direct-timeout', host, 1)
                raise
        client_writer.write(b'HTTP/1.1 200 Connection established\r\n\r\n')

        async def relay_stream(reader, writer):
            try:
                while True:
                    line = await reader.read(1024)
                    if len(line) == 0:
                        break
                    writer.write(line)
                    await asyncio.sleep(0)
            except Exception as e:
                logging.warning(e)

        tasks = [
            asyncio.ensure_future(relay_stream(client_reader, req_writer), loop=loop),
            asyncio.ensure_future(relay_stream(req_reader, client_writer), loop=loop),
        ]
        await asyncio.wait(tasks, loop=loop, return_when=FIRST_COMPLETED)
    except:
        logging.exception('unexpected failed')
    finally:
        return


async def start_warp_server(host, port, *, loop=None):
    # x = await check_is_abroad('www.baidu.com')
    # print(x)
    # x = await check_is_abroad('www.bitmex.com')
    # print(x)
    # return
    await proxy_selector.init()
    try:
        accept = functools.partial(accept_client, loop=loop)
        server = await asyncio.start_server(accept, host=host, port=port, loop=loop)
    except OSError as ex:
        logging.error('!!! Failed to bind server at [%s:%d]: %s' % (host, port, ex.args[1]))
        raise
    else:
        logging.info('Server bound at [%s:%d].' % (host, port))
        return server


def main():
    """CLI frontend function.  It takes command line options e.g. host,
    port and provides `--help` message.
    """
    docopt = docoptinit(__doc__)
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] [%(levelname)s] [ %(filename)s:%(lineno)s - %(name)s ] %(message)s ')
    logging.info('basic config')
    # qb.set_logger(__file__, debug=docopt['--debug'])
    host = docopt['--host']
    port = int(docopt['--port'])
    if not (1 <= port <= 65535):
        raise Exception('port must be 1-65535')

    global verbose
    verbose = int(docopt['--verbose'])
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_warp_server(host, port))
        loop.run_forever()
    except OSError:
        pass
    except KeyboardInterrupt:
        print('bye')
    finally:
        loop.close()


if __name__ == '__main__':
    proxy_selector = ProxySelector()
    main()
