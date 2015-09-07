from common_config import *

DEBUG = False
PORT = 80
MYSQL_DB_NAME = 'newscollect'
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_USERNAME = 'root'
MYSQL_PASSWORD = ''

DATABASE_URI = 'mysql://{username}:{password}@{host}:{port}/{db_name}'.format(username=MYSQL_USERNAME,
                                                                              password=MYSQL_PASSWORD,
                                                                              host=MYSQL_HOST,
                                                                              db_name=MYSQL_DB_NAME,
                                                                              port=MYSQL_PORT
                                                                              )
