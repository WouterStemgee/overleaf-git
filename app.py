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

logger = logging.getLogger(__name__)

OVERLEAF_PROJECT_URI = ''
GIT_REPOSITORY_URI = ''


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CLI tool to automate the process of saving Overleaf projects to a Git repository.')
    args = parser.parse_args()

    # download overleaf .zip file to a temporary directory (session cookie from browser required for authentication)
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

        with urllib.request.urlopen(url) as response, open(path, 'w') as out_file:
            shutil.copyfileobj(response, out_file)
    except HTTPError:
        logger.exception('Authentication error: please login to overleaf in your browser first.')

    # unzip file contents

    # add contents zo new git commit

    # push git commit to repository
