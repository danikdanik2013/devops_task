import json
import logging
import os
import sys
import time
from datetime import datetime
from http import HTTPStatus
from urllib.request import urlopen

import docker
import git
import requests
from colorlog import ColoredFormatter

from setup import LOGS_PATH, APP_PORT

# NOTE Git will provide only 6 requests per some time. 403-will be normal for many requests.
wait_sec = 300
MIN_PYTHON = (3, 6)

LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"
logging.root.setLevel(LOG_LEVEL)
formatter = ColoredFormatter(LOG_FORMAT)
logging.basicConfig(filename=f'{LOGS_PATH}/{datetime.now()}.log')
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
log = logging.getLogger('pythonConfig')
log.setLevel(LOG_LEVEL)
log.addHandler(stream)


def send_telegram(text: str):
    """
    Func for sending messages about build to the Telegram channel.

    :param text: message text
    :return: None
    """
    token = "1187899533:AAHvwZbRqNXJOvT-8Vq-yHgoWOb8dQC2ua8"
    url = "https://api.telegram.org/bot"
    channel_id = '-1001383270620'
    url += token
    method = url + "/sendMessage"

    r = requests.post(method, data={
        "chat_id": channel_id,
        "text": text
    })

    if r.status_code != HTTPStatus.OK:
        raise Exception("post_text error")


class Github:
    def __init__(self, directory: str, path_to_dir: str):
        self.dir = directory
        self.path = path_to_dir

    @staticmethod
    def upload_directory(directory: str):
        """
        Func for uploading directory from git repo
        :directory: link with directory
        :return: None
        """
        try:
            git.Git(os.getcwd()).clone(directory)
        except Exception as e:
            send_telegram('Build failed')
            log.error("Something went wrong")
            log.error(e)
            sys.exit()

    def pull_directory(self):
        """
        Func for git pull repo
        :return: None
        """
        try:
            g = git.cmd.Git(self.dir)
            g.pull()
            log.info(f'Successfully pulled into {self.dir}')
        except Exception as e:
            log.error(e)
            sys.exit()

    def git_move(self):
        """
        Func for management git processes.
        :return:None
        """
        if not os.path.exists(self.dir) or os.listdir(os.getcwd() + '/' + self.dir) == []:
            self.upload_directory(sys.argv[1])
        else:
            log.warning(f"Directory with name {self.dir} has already created")
            while True:
                try:
                    cl_input = int(input("Enter 1 for pulling into this directory or 2 - for exit from program: "))
                    if cl_input == 1:
                        try:
                            self.pull_directory()
                        except Exception as e:
                            log.error("Something went wrong")
                            log.error(e)
                    elif cl_input == 2:
                        send_telegram('Build canceled')
                        sys.exit()
                    else:
                        raise ValueError
                    break
                except ValueError:
                    log.warning("That's not valid input")


class Docker:
    """
    Class to interact with docker
    """

    def __init__(self, client, image, name):
        self.client = client
        self.image = image
        self.name = name

    def start_contain(self):
        """
        Func for start docker containers.
        :return: container
        """
        try:
            tag_name = self.name['commit']['url'].split('/')[-1]
            similar = self.client.containers.get(tag_name)
            print(similar)
            if similar:
                while True:
                    try:
                        cont_inp = int(
                            input("Enter 1 for deleting container or 2 - for exit from program: "))
                        if cont_inp == 1:
                            try:
                                similar.stop()
                                self.cleanup_cont(cont=similar)
                            except Exception as e:
                                log.error("Something went wrong")
                                log.error(e)
                        elif cont_inp == 2:
                            send_telegram('Build canceled')
                            sys.exit()
                        else:
                            raise ValueError
                        break
                    except ValueError:
                        log.warning("That's not valid input")

            self.client.images.build(path=self.image, tag=tag_name)
            cont = self.client.containers.run(tag_name, detach=True, name=tag_name, ports={'8080/tcp': APP_PORT})
            status = cont.attrs['State']['Status']

            if cont and status == 'created':
                log.info("Successfully created container")
                log.info("Successfully started container")
                send_telegram(f'Successfully build for container with name: {tag_name}')
                return cont
        except Exception as e:
            log.error("Something went wrong at the start of the containers")
            log.error(e)
            send_telegram(f"Fail to build container {self.name['commit']['url'].split('/')[-1]}")
            sys.exit()

    def stop_cont(self, old_commit: dict):
        """
        Function for stopping docker container
        :param old_commit: old commit message
        :return: container instance
        """
        try:
            cont = self.client.containers.get(old_commit['commit']['url'].split('/')[-1])
            cont.stop()
            log.info("Stop previous container")
            return cont
        except Exception as e:
            log.error(e)

    @staticmethod
    def cleanup_cont(cont: issubclass):
        """
        Func for deleting docker container
        :param cont: container class
        :return: Success message or None
        """
        try:
            cont.remove()
            log.info(f'Deleted container {cont}')
            return "Success"
        except Exception as e:
            log.error(e)

    @staticmethod
    def cleanup_image(cont: issubclass, client: issubclass):
        """
        Func for deleting image
        :param cont: container class
        :param client: docker client
        :return: Success message or None
        """
        try:
            image = cont.attrs['Config']['Image']
            client.images.remove(image=image, force=True)
            log.info(f'Deleted image {image}')
            return "Success"
        except Exception as e:
            log.error(e)

    def docker_cleanup(self, old_commit: dict):
        """
        Func for managing docker cleanup
        :param old_commit: str
        :return: None
        """
        cont = self.stop_cont(old_commit)
        if cont and self.cleanup_cont(cont) and self.cleanup_image(cont, self.client):
            send_telegram("Successfully cleaned old container and image")
            log.info("Successfully cleaned old container and image")
        else:
            log.error("Something went wrong while cleaning")
            sys.exit()


def simple_test():
    """
    Func for testing app inside container
    :return: None
    """
    try:
        s = requests.Session()
        url = "http://0.0.0.0:3333"
        # Need some time to up app in container
        time.sleep(2)
        response = s.get(url)
        log.info("Check the response from app")
        log.info(response)
        send_telegram(f'Request tests: {response}')

    except Exception as e:
        log.error("Build fail on tests")
        log.error(e)
        send_telegram("Build fail on tests")


def root_check():
    """
    Func for checking root run
    :return: None
    """
    if not os.geteuid() == 0:
        sys.exit("\nOnly root can run this script\n")


def arg_parse():
    """
    Func for check args
    :return: None
    """
    if len(sys.argv) <= 1:
        sys.exit("\nPlease, enter the directory\n")


def python_check():
    """
    Func for check version of python. Python must be 3.6+
    :return: None
    """
    if not sys.version_info >= MIN_PYTHON:
        sys.exit()


def before_start():
    """
    Manage func for start processes
    :return:
    """
    python_check()
    root_check()
    arg_parse()


def main():
    before_start()
    commit = ''
    dir_name = sys.argv[1].split("/")[-1].split(".git")[0]
    path_to_dir = os.getcwd() + '/' + dir_name
    github = Github(directory=dir_name, path_to_dir=path_to_dir)
    github.git_move()
    client = docker.from_env()
    doc = Docker(client=client, image=path_to_dir, name=get_latest_commit(sys.argv[1].split("/")[-2], dir_name))
    doc.start_contain()
    simple_test()
    while True:
        old_commit = commit
        commit = get_latest_commit(sys.argv[1].split("/")[-2], dir_name)
        if old_commit != '' and commit != old_commit:
            doc.docker_cleanup(old_commit)
            log.info('NEW COMMIT')
            log.info(f"last commit: {commit['html_url']}")
            send_telegram(f"Looks like someone upload code to Git")
            github.pull_directory()
            doc.start_contain()
        time.sleep(wait_sec)


def get_latest_commit(owner: str, repo: str):
    """
    Func for getting last commit
    :param owner: owner for commit
    :param repo: repo
    :return: commit
    """
    try:
        url = 'https://api.github.com/repos/{owner}/{repo}/commits?per_page=1'.format(owner=owner, repo=repo)
        response = urlopen(url).read()
        data = json.loads(response.decode())
        return data[0]
    except Exception as e:
        log.error(e)
        sys.exit()


if __name__ == '__main__':
    main()
