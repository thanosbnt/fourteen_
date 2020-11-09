import time
import random
from flask import request, jsonify
from flask_restful import Resource, reqparse, inputs
import requests
from pydub import AudioSegment
import pyOSC3
import io

import logging

logging.basicConfig(level='INFO')
logger = logging.getLogger(__name__)

class Test(Resource):
    """
    Test resource for experimenting.
    """
    # parser = reqparse.RequestParser()
    # parser.add_argument('email', type=str, store_missing=False)
    RADIO_LIST = ['http://tx.planetradio.co.uk/icecast.php?i=net1northyorkshire.mp3',
         'http://icecast.thisisdax.com/HeartBerkshireMP3',
         'http://tx.planetradio.co.uk/icecast.php?i=net1bournemouth.mp3',
         'http://radio.arqiva.tv/rnib-connect.mp3',
         'http://tx.planetradio.co.uk/icecast.php?i=magic1548.mp3',
         'http://icy-e-04.sharp-stream.com/totallyradio.mp3',
         'http://lincs.planetwideradio.com:8035/traxfm',
         'http://tx.planetradio.co.uk/icecast.php?i=viking.mp3',
         'http://icecast.thisisdax.com/CapitalEdinburghMP3',
         'http://tx.planetradio.co.uk/icecast.php?i=northsound2.mp3']

    # def fetch(self):
    #     radio_list = ['http://tx.planetradio.co.uk/icecast.php?i=net1northyorkshire.mp3',
    #          'http://icecast.thisisdax.com/HeartBerkshireMP3',
    #          'http://tx.planetradio.co.uk/icecast.php?i=net1bournemouth.mp3',
    #          'http://radio.arqiva.tv/rnib-connect.mp3',
    #          'http://tx.planetradio.co.uk/icecast.php?i=magic1548.mp3',
    #          'http://icy-e-04.sharp-stream.com/totallyradio.mp3',
    #          'http://lincs.planetwideradio.com:8035/traxfm',
    #          'http://tx.planetradio.co.uk/icecast.php?i=viking.mp3',
    #          'http://icecast.thisisdax.com/CapitalEdinburghMP3',
    #          'http://tx.planetradio.co.uk/icecast.php?i=northsound2.mp3']


    #     timeout_start = time.time()
    #     timeout = 1   # [seconds]
    #     radio = random.choice(radio_list)
    #     logger.info(radio)
    #     r = requests.get(radio, stream=True)
    #     ### get some chunks
    #     for chunk in r.iter_content(chunk_size=20000):
    #         print(type(chunk))
    #         if time.time() > timeout_start + timeout:
    #             return chunk
    #         else:
    #             continue

    def get(self):
        # args = self.parser.parse_args()
        # print(args)

        # chunk = self.fetch()
        # song = AudioSegment.from_file(io.BytesIO(chunk), format="mp3").export("/home/app/SuperCollider/file_1.wav", format="wav")
        radio = random.choice(self.RADIO_LIST)
        client = pyOSC3.OSCClient()
        client.connect( ( '10.5.0.11', 57120 ) )
        msg = pyOSC3.OSCMessage()
        msg.setAddress("/print")
        msg.append(radio)
        client.send(msg)


        return None
