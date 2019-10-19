import importlib
import logging
import os
import threading
import queue

import click
import requests

from webtoon_dl.providers import mapping, exceptions
from webtoon_dl.utils import parse_extension, sanitize_filename


_terminated = False
_total = 1

logger = logging.getLogger('logger')
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


def worker(q):
    tid = threading.get_ident()
    while True:
        job = q.get()
        if job is None or _terminated:
            logger.debug('[%d] Got termination signal; terminating...' % tid)
            q.task_done()
            break
        ep_name, dirname, headers, urls = job  # TODO:Queue structure
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        logger.debug('[%d] Downloading #%s to %s' % (tid, ep_name, dirname))
        counter = 1
        for url in urls:
            resp = requests.get(url, headers=headers)
            path = dirname + '/' + str(counter) + parse_extension(url)
            with open(path, 'wb') as image:
                for chunk in resp.iter_content(1024):
                    image.write(chunk)
            counter = counter + 1
        logger.info('%d/%d downloaded (%s)' % (_total - q.qsize() + 1, _total, ep_name))
        q.task_done()


def find_provider(url):
    for pattern, module in mapping:
        try:
            match = url.find(pattern) > -1
        except TypeError:
            match = pattern(url)
        if match:
            logger.info('Using provider %s' % module)
            return importlib.import_module('.' + module,
                                           package='webtoon_dl.providers')


@click.command()
@click.option('--count', '-c', default=0, help='Episodes to download. Unlimited if 0.')
@click.option('-j', default=8, help='Maximum count of threads.')
@click.option('--dest', '-d', type=click.Path(), default='.',
              help='Path to directory to download comic. Defaults to current directory.')
@click.option('--verbosity', default=1, type=click.IntRange(min=0, max=2, clamp=True),
              help='Verbosity, 0 to 2. Defaults to 1')
@click.argument('url')
def main(count, url, j, dest, verbosity):
    """
    A blazing fast webtoon downloader.
    """
    global _total, _terminated
    logger.setLevel(30 - verbosity * 10)

    provider = find_provider(url)

    # Start workers
    threads = []
    q = queue.Queue()
    for i in range(j):
        t = threading.Thread(target=worker, args=(q,))
        t.start()
        threads.append(t)

    episode_url = url
    current = 1
    html_src = requests.get(episode_url).text  # TODO: Custom header & cookie
    provider.initialize(url)

    dirname = os.path.join(dest, provider.get_dirname(html_src))

    req_header = provider.build_header(html_src, episode_url)
    ep_name = sanitize_filename(provider.get_episode_name(html_src))
    
    q.put((ep_name, dirname + ep_name, req_header, provider.get_image_list(html_src)))
    logger.debug("Dirname: " + dirname)
    logger.info("Downloading to: %s", os.path.normpath(dirname))
    
    while not current == count:
        try:
            logger.debug("Enqueued %s" % ep_name)
            episode_url = provider.get_next_episode_url(html_src)
            html_src = requests.get(episode_url).text
            req_header = provider.build_header(html_src, episode_url)
            ep_name = sanitize_filename(provider.get_episode_name(html_src))
            _total = _total + 1
            current = current + 1
            q.put((ep_name, dirname + ep_name, req_header, provider.get_image_list(html_src)))
        except exceptions.EndOfComic:
            logger.debug("End of comic")
            break
        except KeyboardInterrupt:
            click.echo("Aborted!")
            break

    logger.debug('Signalling termination')
    for i in threads:
        q.put(None)

    logger.debug('Waiting for queue to empty out')
    try:
        q.join()
    except KeyboardInterrupt:
        logger.debug("Panic")
        _terminated = True


if __name__ == "__main__":
    main()
