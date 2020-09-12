import os
import time
import argparse
import browser_cookie3
import requests
import urllib.request
import shutil
import git
import zipfile
import stat
import logging
from datetime import datetime
from urllib.error import HTTPError
from configparser import ConfigParser


logger = logging.getLogger('overleaf_git')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(ch)

clean_up = True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CLI tool to automate the process of saving Overleaf projects to a Git repository.')
    args = parser.parse_args()

    # parse configuration variables
    logger.info('Parsing configuration variables...')
    config = ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
    if not os.path.isfile(config_path):
        logger.exception('Configuration error: configuration file could not be parsed.')
    config.read(config_path)

    OVERLEAF_PROJECT_URI = config['overleaf']['overleaf_project_url'] 
    GIT_REPOSITORY_URI = config['git']['git_repository_url'] 

    # download overleaf .zip file to a temporary directory (session cookie from browser required for authentication)
    logger.info('Downloading overleaf .zip file to a temporary directory...')
    try:
        temp_dir_name = 'data'
        if not os.path.exists(temp_dir_name):
            os.makedirs(temp_dir_name)
        current_datetime = datetime.now().strftime("%d-%m-%Y_%H-%M")
        zip_file_name = f'overleaf_{current_datetime}.zip'
        zip_file_path = os.path.join(temp_dir_name, zip_file_name)

        cookie_jar = browser_cookie3.chrome(domain_name='overleaf.com')
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
        urllib.request.install_opener(opener)
        url = OVERLEAF_PROJECT_URI + '/download/zip'

        with urllib.request.urlopen(url) as response, open(zip_file_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
            out_file.close()
            logger.info('Download complete.')
    except HTTPError:
        logger.exception('Authentication error: please login to overleaf in your browser first.')

    # clone the existing remote Git repository
    logger.info('Cloning the existing remote Git repository...')
    local_repo_path = os.path.splitext(zip_file_path)[0]
    if not os.path.exists(local_repo_path):
        os.makedirs(local_repo_path)
    else: 
        shutil.rmtree(local_repo_path)
    repo = git.Repo.clone_from(GIT_REPOSITORY_URI, local_repo_path)


    # unzip file contents and add them to the local Git repository
    logger.info('Unzipping contents of .zip file...')
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(local_repo_path)
    logger.info('Unzipping complete.')

    # check for changes
    logger.info('Checking for changes...')
    diff = repo.git.diff('HEAD', name_only=True)
    if diff:
        # add change to new Git commit and push commit to remote Git repostiory
        logger.info(f'Found changes in files: {diff}')
        repo.git.add('--all')
        commit_message = 'Automated project synchronization from Overleaf-Git'
        repo.index.commit(commit_message)
        
        # push new commit to remote Git repostiory
        logger.info('Pushing new commit to remote Git repository...')
        origin = repo.remote(name='origin')
        origin.push()
    else:
        logger.warning('No changes detected.')


    # clean-up all temporary files
    if clean_up:
        logger.info('Cleaning up all temporary files...')
        time.sleep(1) # wait for git process to terminate

        # make read-only files in .git directory removable
        for root, dirs, files in os.walk(temp_dir_name):  
            for dir in dirs:
                os.chmod(os.path.join(root, dir), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            for file in files:
                os.chmod(os.path.join(root, file), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        
        os.remove(zip_file_path)

        shutil.rmtree(local_repo_path)
        shutil.rmtree(temp_dir_name)

    logger.info('Done!')