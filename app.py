import os
import argparse
import browser_cookie3
import requests
import urllib.request
import shutil
from datetime import datetime
import zipfile
import logging
from urllib.error import HTTPError
from configparser import ConfigParser


logger = logging.getLogger('overleaf_git')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(ch)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CLI tool to automate the process of saving Overleaf projects to a Git repository.')
    args = parser.parse_args()

    # parse configuration variables
    logger.info('Parsing configuration variables')
    config = ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
    if not os.path.isfile(config_path):
        logger.exception('Configuration error: configuration file not found.')
    config.read(config_path)

    OVERLEAF_PROJECT_URI = config['overleaf']['overleaf_project_url'] 
    GIT_REPOSITORY_URI = config['git']['git_repository_url'] 

    # download overleaf .zip file to a temporary directory (session cookie from browser required for authentication)
    logger.info('Download overleaf .zip file to a temporary directory')
    try:
        dir_name = 'data'
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        current_datetime = datetime.now().strftime("%d-%m-%Y_%H-%M")
        file_name = f'overleaf_{current_datetime}.zip'
        path = os.path.join(dir_name, file_name)

        cookie_jar = browser_cookie3.chrome(domain_name='overleaf.com')
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
        urllib.request.install_opener(opener)
        url = OVERLEAF_PROJECT_URI + '/download/zip'

        with urllib.request.urlopen(url) as response, open(path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
    except HTTPError:
        logger.exception('Authentication error: please login to overleaf in your browser first.')

    # unzip file contents

    # add contents zo new git commit

    # push git commit to repository
