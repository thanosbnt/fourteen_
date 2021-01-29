import logging
import importlib
import multiprocessing
from settings.config import get_config
from settings.config import BaseConfig
from sqlalchemy.orm import sessionmaker, scoped_session
import sqlalchemy
from time import sleep
from multiprocessing import Process
from main.models import StreamingAuto, StreamingUser
import pandas as pd
import pyOSC3
from datetime import datetime
import requests
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


config = get_config()

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


class Streamer(object):
    def __init__(self):
        db_uri = BaseConfig.DB_URI
        self.engine = sqlalchemy.create_engine(db_uri)
        _session = scoped_session(sessionmaker(bind=self.engine))
        self.session = _session
        self.switcher = 0

    def crawl_datasource(self):
        while True:

            p = Process(target=self.play_random_station())
            p.start()
            p.join()

            sleep(int(30))

    def play_random_station(self):

        client = pyOSC3.OSCClient()
        client.connect(('10.5.0.11', 57120))

        if self.switcher == 0:
            pass
        else:
            msg = pyOSC3.OSCMessage()
            msg.setAddress("/stop")
            msg.append('stopping')
            client.send(msg)

        s_auto = self.session.execute(
            'SELECT * FROM streaming_auto ORDER BY timestamp DESC LIMIT 1')
        res = s_auto.fetchone()

        s_user = self.session.execute(
            'SELECT * FROM streaming_user ORDER BY timestamp DESC LIMIT 1')
        res_user = s_user.fetchone()

        if not res_user:
            radio = res.url
            name = res.name
        else:
            if res_user.timestamp > res.timestamp:
                radio = res_user.url
                name = res_user.name
            else:
                radio = res.url
                name = res.name

        msg = pyOSC3.OSCMessage()
        msg.setAddress("/start")
        msg.append(radio)
        client.send(msg)

        logger.info(radio)
        logger.info(name)
        self.switcher = self.switcher+1


if __name__ == '__main__':
    s = Streamer()
    s.crawl_datasource()
