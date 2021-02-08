from flask import Flask, g, render_template, jsonify, Response
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from extensions import db
from settings.config import BaseConfig
from api.errors import InvalidUsage
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from main.models import StreamingAuto, StreamingUser, NowPlaying
from apscheduler.schedulers.background import BackgroundScheduler

import time
from datetime import datetime
from datetime import timedelta
import atexit

import random
from flask import request, jsonify
from flask_restful import Resource, reqparse, inputs
import requests
from pydub import AudioSegment
import pyOSC3
import threading
import io
import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from shapely.geometry import Point


import logging
logger = logging.getLogger(__name__)


def create_before_request(app):
    def before_request():
        g.db = db
    return before_request


def create_app(**config_overrides):

    logger = logging.getLogger(__name__)
    logger.info('app starts...')

    app = Flask(__name__,
                template_folder="./")

    limiter = Limiter(key_func=get_remote_address)
    limiter.init_app(app)

    app.config.from_object(BaseConfig)

    if config_overrides:
        app.config.update(config_overrides)

    db.init_app(app)
    db.app = app

    migrate = Migrate(app, db)
    CORS(app)
    api = Api(app)
    from main import models

    db.create_all()
    app.before_request(create_before_request(app))

    def ckdnearest(gdA, gdB):
        nA = np.array(list(gdA.geometry.apply(lambda x: (x.x, x.y))))
        nB = np.array(list(gdB.geometry.apply(lambda x: (x.x, x.y))))
        btree = cKDTree(nB)
        dist, idx = btree.query(nA, k=1)
        gdA['dist'] = dist
        return gdA[gdA.dist == gdA.dist.min()]

    def x(row):
        try:
            x = row[0]
            return x
        except Exception:
            pass

    def y(row):
        try:
            x = row[1]
            return x
        except Exception:
            pass

    @app.errorhandler(InvalidUsage)
    def handle_invalid_usage(error):
        """
        Handles invalid api use 
        """
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    df = pd.read_csv('stations.csv')
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(
        df.place_geo_x, df.place_geo_y))

    @app.route('/')
    def home_page():
        example_embed = 'This string is from python'
        return render_template('index.html', embed=example_embed)

    @app.route('/api/audio_feed')
    def audio_play():
        def fetch():
            radio = 'http://10.5.0.11:8000/stream.mp3'
            r = requests.get(radio, stream=True)
            for chunk in r.iter_content(chunk_size=20000):
                yield chunk
        return Response(fetch(), mimetype="audio/mp3")

    @app.route('/api/queue', methods=["GET"])
    def populate_queue():
        """
        Random station playback
        """

        client = pyOSC3.OSCClient()
        client.connect(('10.5.0.11', 57120))

        msg = pyOSC3.OSCMessage()
        msg.setAddress("/stop")
        msg.append('stopping')
        client.send(msg)

        res = StreamingAuto.get_last()
        res_user = StreamingUser.get_last()

        if not res_user:
            radio = res.url
            name = res.name
            country = res.country
            place_name = res.place_name

        else:
            radio = res_user.url
            name = res_user.name
            country = res_user.country
            place_name = res_user.place_name

            StreamingUser.query.filter(StreamingUser.name == name).delete()

        msg = pyOSC3.OSCMessage()
        msg.setAddress("/start")
        msg.append(radio)
        msg.append(np.random.exponential())

        chunk = check_health(radio)
        song = AudioSegment.from_file(io.BytesIO(chunk), format="mp3")
        song.export("SuperCollider/out.wav", format="wav")

        f = open("SuperCollider/out.txt", "w")
        f.write(name)
        f.close()

        client.send(msg)

        if not res_user:
            jsonObj = {"msg": "{0} {1} {2}".format(
                res.country, res.place_name, res.name)}
        else:
            jsonObj = {"msg": "{0} {1} {2}".format(
                res_user.country, res_user.place_name, res_user.name)}

        # sleeping so backend and sc can 'sync'
        time.sleep(5)
        s = NowPlaying(country=str(country), place_name=str(place_name),
                       name=str(name), url=str(radio),
                       timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        db.session.add(s)
        db.session.flush()
        db.session.commit()
        return jsonObj

    @app.route('/api/get_names', methods=["GET"])
    def get_names():
        res = NowPlaying.get_last()
        radio = res.url
        name = res.name
        country = res.country
        place_name = res.place_name
        jsonObj = {"msg": "{0} {1} {2}".format(
            res.country, res.place_name, res.name)}
        return jsonObj

    @app.route('/api/stop', methods=["GET"])
    def stop_queue():
        switcher = 0
        client = pyOSC3.OSCClient()
        client.connect(('10.5.0.11', 57120))
        msg = pyOSC3.OSCMessage()
        msg.setAddress("/stop")
        msg.append('stopping')
        client.send(msg)
        jsonObject = {"msg": "stop"}
        return jsonObject

    @ app.route('/api/random', methods=["GET"])
    def send_random_station():

        gpd1 = gdf
        gpd2 = gpd.GeoDataFrame([['test', Point(float(request.args['x']), float(
            request.args['y']))]], columns=['Place', 'geometry'])

        radio_list = gpd1[gpd1.country == request.args['country']]
        logger.info(request.args['country'])
        logger.info(radio_list)
        if not radio_list:
            radio_list = random.choice(ckdnearest(gpd1, gpd2)[
                ['mp3', 'country', 'place_name', 'name']].values)

        logger.info(radio_list[0])

        client = pyOSC3.OSCClient()
        client.connect(('10.5.0.11', 57120))

        radio = radio_list[0]
        msg = pyOSC3.OSCMessage()
        msg.setAddress("/start")
        msg.append(radio)
        msg.append(np.random.exponential())

        client.send(msg)

        station_string = np.array2string(radio_list[1:]).replace(
            '[', '').replace(']', '').replace("'", '')

        s = StreamingAuto(country=radio_list[1], place_name=radio_list[2],
                          name=radio_list[3], url=radio,
                          timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        s.save()
        db.session.commit()

        jsonObject = {"msg": station_string}
        return jsonObject

    def check_health(station):
        """
        Gets some mp3 chunks to check if they are valid
        """
        radio = station
        r = requests.get(radio, stream=True)
        # get some chunks
        for chunk in r.iter_content(chunk_size=20000):
            return chunk

    # @ limiter.limit("1 per 20second")
    @ app.route('/api', methods=["GET"])
    def send_station():
        """
        Handles user requests
        """
        gpd1 = gdf
        gpd2 = gpd.GeoDataFrame([['test', Point(float(request.args['x']), float(
            request.args['y']))]], columns=['Place', 'geometry'])

        try:
            logger.info(gpd1[gpd1.country == request.args['country']])
            radio_list = (gpd1[gpd1.country == request.args['country']].sample(1)[
                ['mp3', 'country', 'place_name', 'name']].values)[0].tolist()

            logger.info(request.args['country'])
            logger.info(radio_list)
            if not radio_list:
                radio_list = random.choice(ckdnearest(gpd1, gpd2)[
                    ['mp3', 'country', 'place_name', 'name']].values)

            chunk = check_health(radio_list[0])
            song = AudioSegment.from_file(io.BytesIO(chunk), format="mp3")
            song.export("SuperCollider/out.wav", format="wav")

            f = open("SuperCollider/out.txt", "w")
            f.write(radio_list[3])
            f.close()

            res_user = StreamingUser(url=radio_list[0], country=radio_list[1], place_name=radio_list[2],
                                     name=radio_list[3], timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            res_user.save()
            db.session.commit()

            jsonObj = {"msg": "{0} {1} {2}".format(
                res_user.country, res_user.place_name, res_user.name)}

            logger.info(radio_list[0])
        except Exception as e:
            jsonObj = {"msg": "An error has occured. Please choose again"}
            logger.info(str(e))

        return jsonObj

    def add_random_station():
        # Need to try to catch corrupted mp3 before sending them to SC grrrr
        df = pd.read_csv('stations.csv')
        sample = df.sample()
        logger.info(sample)
        try:
            chunk = check_health(str(sample['mp3'].values[0]))
            song = AudioSegment.from_file(io.BytesIO(chunk), format="mp3")
            logger.info(str(sample['country'].values[0]))
            s = StreamingAuto(country=str(sample['country'].values[0]), place_name=str(sample['place_name'].values[0]),
                              name=str(sample['name'].values[0]), url=str(sample['mp3'].values[0]),
                              timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            db.session.add(s)
            db.session.flush()
            db.session.commit()
        except Exception as e:
            logger.info(str(e))
            db.session.rollback()
            pass

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=populate_queue, trigger="interval", seconds=30)
    scheduler.add_job(func=add_random_station, trigger="interval", seconds=90)

    scheduler.start()
    # Shutdown your cron thread if the web process is stopped
    atexit.register(lambda: scheduler.shutdown())

    return app
