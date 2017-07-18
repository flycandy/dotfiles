#!/usr/bin/env python3
"""
Usage:
    onchange.py
    onchange.py exec <folder> <cmd>
    onchange.py <watch>...

execute .onchange script when the parent folder changes
if a/.onchange exist, then if folder a changes, .onchange will be executed
it will be executed at most 1 time per 5 second

"""
import os
import threading
import time
import arrow
import logging
from docopt import docopt as docoptinit

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer


class Runner:
    def __init__(self, folder):
        logging.info('watch folder {}'.format(folder))
        self.folder = folder
        self.observer = Observer()
        self.last_modify = arrow.now()
        self.last_change = arrow.now().replace(days=-1)

    class MyHandler(FileSystemEventHandler):
        def __init__(self, parent):
            self.parent = parent

        def on_created(self, event: FileSystemEvent):
            for ignore in ['.onchange', '.git', '.idea']:
                if event.src_path.find(ignore) >= 0:
                    # logging.info('ignore {}'.format(event))
                    return
            path = os.path.join(os.getcwd(), event.src_path)
            logging.info('do {} {}'.format(self.parent.folder, path))
            cmd = 'cd {} && chmod +x .onchange &&  ./.onchange {}'.format(self.parent.folder, path)
            os.system(cmd)
            logging.info('done {} {}'.format(self.parent.folder, path))

        def on_modified(self, event):
            for ignore in ['.onchange', '.git', '.idea']:
                if event.src_path.find(ignore) >= 0:
                    # logging.info('ignore {}'.format(event))
                    return
            # logging.info('Got it! {} {}'.format(event, arrow.now()))
            self.parent.last_modify = arrow.now()

    def execute(self):
        while True:
            if self.last_modify > self.last_change:
                self.last_change = self.last_modify
                time.sleep(0.1)
                # logging.info('execute script {}/.onchange'.format(self.folder))
                os.system('cd {} && chmod +x .onchange &&  ./.onchange'.format(self.folder))
                logging.info('done {}'.format(self.folder))
                os.system("osascript -e 'display notification \"Sync Done\"'")
            time.sleep(5)

    def start(self):
        event_handler = self.MyHandler(self)
        self.observer.schedule(event_handler, self.folder, recursive=True)
        self.observer.start()
        threading.Thread(target=self.execute, daemon=True).start()


class WatchSingleFolder:
    def __init__(self, folder, cmd):
        logging.info('watch folder {}'.format(folder))
        self.cmd = cmd
        self.folder = folder
        self.observer = Observer()
        self.last_modify = arrow.now()
        self.last_change = arrow.now().replace(days=-1)

    class MyHandler(FileSystemEventHandler):
        def __init__(self, parent):
            self.parent = parent

        def on_created(self, event: FileSystemEvent):
            for ignore in ['.onchange', '.git', '.idea']:
                if event.src_path.find(ignore) >= 0:
                    return
            print('changed', event)

        def on_modified(self, event):
            for ignore in ['.onchange', '.git', '.idea']:
                if event.src_path.find(ignore) >= 0:
                    return
            self.parent.last_modify = arrow.now()
            print('modify', event)

    def execute(self):
        while True:
            if self.last_modify > self.last_change:
                self.last_change = self.last_modify
                time.sleep(0.1)
                # logging.info('execute script {}/.onchange'.format(self.folder))
                print('do', self.cmd)
                os.system(self.cmd)
                print('done')
            time.sleep(5)

    def start(self):
        event_handler = self.MyHandler(self)
        self.observer.schedule(event_handler, self.folder, recursive=True)
        self.observer.start()
        threading.Thread(target=self.execute).start()


def main():
    docopt = docoptinit(__doc__)
    logging.basicConfig(level=logging.INFO, format='%(asctime)-15s  %(message)s')
    lst = []
    # for folder, folders, files in os.walk(os.path.expanduser('~/Dropbox/qb')):
    if not docopt['<watch>']:
        docopt['<watch>'] = ['.']
    print(docopt)
    if docopt['exec']:
        r = WatchSingleFolder(docopt['<folder>'], docopt['<cmd>'])
        r.start()
    else:
        for f in docopt['<watch>']:
            for folder, folders, files in os.walk(f):
                if '.onchange' in files:
                    # print(folder)
                    r = Runner(folder)
                    r.start()
                    lst.append(r)
                    # print(x)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for r in lst:
            r.observer.stop()
    for r in lst:
        r.observer.join()


if __name__ == "__main__":
    main()
