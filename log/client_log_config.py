import logging
import os

logger=logging.getLogger('client')
formatter=logging.Formatter('%(asctime)s - %(levelname)-8s - %(module)-8s - %(message)s')

file_name=os.path.join('log','client.log')
try:
    file_handler=logging.FileHandler(file_name, encoding='utf-8')
except:
    file_name = 'client.log'
    file_handler = logging.FileHandler(file_name, encoding='utf-8', )

file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    console=logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    logger.addHandler(console)
    logger.debug('Run client_log.py')