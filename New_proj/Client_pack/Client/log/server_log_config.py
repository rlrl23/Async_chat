import logging
import os
import logging.handlers

logger=logging.getLogger('server')
formatter=logging.Formatter('%(asctime)s - %(levelname)-8s - %(module)-8s - %(message)s')

file_name=os.path.join('log', 'server.log')
try:
    file_handler = logging.handlers.TimedRotatingFileHandler(file_name, when='D', interval=1, backupCount=10, encoding='utf-8')
except:
    file_name = 'server.log'
    file_handler = logging.handlers.TimedRotatingFileHandler(file_name,  when='D', interval=1, backupCount=10, encoding='utf-8')

file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    console=logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    logger.addHandler(console)
    logger.debug('Run server_log.py')