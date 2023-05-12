from database.database import Database
from utils.utils import read_app_config


config = read_app_config('config.json')
DB = Database(
    host=config['db_host'],
    port=config['db_port'],
    user=config['db_user'],
    password=config['db_password'],
    dbname=config['db_database'],
)
