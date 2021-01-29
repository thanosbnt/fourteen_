from app import create_app
from flask_migrate import MigrateCommand
from flask_script import Manager, Server
import os
import sys
import unittest
from settings.config import get_config

config = get_config()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


application = create_app()

manager = Manager(app=application)
manager.add_command('runserver', Server(
    use_debugger=config['flask_server']['use_debugger'],
    use_reloader=False,
    host=config['flask_server']['host'],
    port=config['flask_server']['port'],
    processes=3
))


if __name__ == '__main__':
    manager.run()
