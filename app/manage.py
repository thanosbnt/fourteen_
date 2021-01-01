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
# manager.add_command('db', MigrateCommand)
# manager.add_command('add_building_data', AddBuildingData)
# manager.add_command('add_room_geometries', AddRoomGeometries)
# manager.add_command('add_grid_table', AddGridTable)

# manager.add_command('add_historic_beringar', AddHistoricBeringar)
# manager.add_command('add_historic_spaceti', AddHistoricSpaceti)
# manager.add_command('add_historic_hoxton', AddHistoricHoxton)

# manager.add_command('add_datasource', AddDatasource)
# manager.add_command('drop_datasource', DropDatasource)
manager.add_command('runserver', Server(
    use_debugger=config['flask_server']['use_debugger'],
    use_reloader=config['flask_server']['use_reloader'],
    host=config['flask_server']['host'],
    port=config['flask_server']['port'],
    processes=3
))


if __name__ == '__main__':
    manager.run()
