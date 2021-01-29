from extensions import db
from geoalchemy2 import Geometry, WKTElement
from geoalchemy2.shape import to_shape
from sqlalchemy import func, text
import json
from datetime import datetime
from typing import NoReturn
from sqlalchemy.exc import IntegrityError
import datetime
from settings.config import get_config
import logging

config = get_config()
logging.basicConfig(level='INFO')
logger = logging.getLogger(__name__)


class StreamingAuto(db.Model):
    __tablename__ = "streaming_auto"
    __table_args__ = {"extend_existing": True}

    stream_id = db.Column(db.Integer, primary_key=True,
                          unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    place_name = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False)

    def __init__(self, name, place_name, country, url, timestamp):
        self.name = name
        self.place_name = place_name
        self.country = country
        self.url = url
        self.timestamp = timestamp

    def json(self):
        """Creates a JSON of the LatestReadings data"""
        return {
            'name': self.name,
            'place_name': self.place_name,
            'country': self.country,
            'url': self.url
        }

    def save(self):
        """put object in queue to be committed to database"""
        try:
            db.session.add(self)
            db.session.flush()
        except IntegrityError as e:
            db.session.rollback()

    @staticmethod
    def commit():
        """apply changes to the database"""
        db.session.commit()

    @classmethod
    def get_last(cls):
        """Fetch all"""
        return cls.query.order_by(text('timestamp desc')).first()

    @classmethod
    def get_all(cls):
        """Fetch all"""
        return cls.query.order_by(text('timestamp desc')).limit(5).all()


class StreamingUser(db.Model):
    __tablename__ = "streaming_user"
    __table_args__ = {"extend_existing": True}

    stream_id = db.Column(db.Integer, primary_key=True,
                          unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    place_name = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False)

    def __init__(self, name, place_name, country, url, timestamp):
        self.name = name
        self.place_name = place_name
        self.country = country
        self.url = url
        self.timestamp = timestamp

    def json(self):
        """Creates a JSON of the LatestReadings data"""
        return {
            'name': self.name,
            'place_name': self.place_name,
            'country': self.country,
            'url': self.url
        }

    def save(self):
        """put object in queue to be committed to database"""
        try:
            db.session.add(self)
            db.session.flush()
        except IntegrityError as e:
            db.session.rollback()

    @staticmethod
    def commit():
        """apply changes to the database"""
        db.session.commit()

    @classmethod
    def get_last(cls):
        """Fetch all"""
        return cls.query.order_by(text('timestamp desc')).limit(10).first()

    @classmethod
    def get_all(cls):
        """Fetch all"""
        return cls.query.order_by(text('timestamp desc')).limit(5).all()


class NowPlaying(db.Model):
    __tablename__ = "now_playing"
    __table_args__ = {"extend_existing": True}

    stream_id = db.Column(db.Integer, primary_key=True,
                          unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    place_name = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False)

    def __init__(self, name, place_name, country, url, timestamp):
        self.name = name
        self.place_name = place_name
        self.country = country
        self.url = url
        self.timestamp = timestamp

    def json(self):
        """Creates a JSON of the LatestReadings data"""
        return {
            'name': self.name,
            'place_name': self.place_name,
            'country': self.country,
            'url': self.url
        }

    def save(self):
        """put object in queue to be committed to database"""
        try:
            db.session.add(self)
            db.session.flush()
        except IntegrityError as e:
            db.session.rollback()

    @staticmethod
    def commit():
        """apply changes to the database"""
        db.session.commit()

    @classmethod
    def get_last(cls):
        """Fetch all"""
        return cls.query.order_by(text('timestamp desc')).limit(10).first()

    @classmethod
    def get_all(cls):
        """Fetch all"""
        return cls.query.order_by(text('timestamp desc')).limit(5).all()
