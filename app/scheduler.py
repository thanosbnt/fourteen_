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
from pydub import AudioSegment
import io
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


config = get_config()

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

df = pd.read_csv('stations.csv')


class Scheduler(object):
    def __init__(self):
        db_uri = BaseConfig.DB_URI
        self.engine = sqlalchemy.create_engine(db_uri)
        _session = scoped_session(sessionmaker(bind=self.engine))
        self.session = _session

    def crawl_datasource(self):
        while True:

            p = Process(target=self.add_random_station(df.sample()))
            p.start()
            p.join()
            # add random station every 60 sec
            sleep(int(90))

    def check_health(self, station):
        """
        Gets some mp3 chunks to check if they are valid
        """
        radio = station
        print(radio)
        r = requests.get(radio, stream=True)
        # get some chunks
        for chunk in r.iter_content(chunk_size=10000):
            return chunk

    def add_random_station(self, sample):
        # Need to try to catch corrupted mp3 before sending them to SC grrrr
        try:
            chunk = self.check_health(str(sample['mp3'].values[0]))
            song = AudioSegment.from_file(io.BytesIO(chunk), format="mp3")
            s = StreamingAuto(country=str(sample['country'].values[0]), place_name=str(sample['place_name'].values[0]),
                              name=str(sample['name'].values[0]), url=str(sample['mp3'].values[0]),
                              timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            self.session.add(s)
            self.session.flush()
            self.session.commit()
        except Exception as e:
            logger.info(str(e))
            pass

    def play_random_station(self):
        s_auto = self.session.execute(
            'SELECT * FROM streaming_auto ORDER BY timestamp DESC LIMIT 1')
        s_auto.fetchall()
        for i in s_auto:
            logger.info(i)


if __name__ == '__main__':
    s = Scheduler()
    s.crawl_datasource()

    # def get_station(self):
    #     s_auto = self.session.execute(
    #         'SELECT * FROM streaming_auto ORDER BY timestamp DESC LIMIT 1')
    #     s_auto.fetchall()

    #     logger.info(s_auto)

    #     client = pyOSC3.OSCClient()
    #     client.connect(('10.5.0.11', 57120))

    #     radio = radio_list[0]
    #     msg = pyOSC3.OSCMessage()
    #     msg.setAddress("/start")
    #     msg.append(radio)
    #     client.send(msg)
