import os

from shutil import copytree

import docker as d
import logging
from docker.errors import APIError, ContainerError

docker = d.from_env()


class NginxManager(object):
    def __init__(self, nginx_container='nginx', configuration_folder='/var/conf/nginx'):
        self.container = nginx_container
        self.folder = configuration_folder
        self._check_and_setup()

    def _check_and_setup(self):
        """
        Setup Nginx if necessary
        :rtype: bool Return True if setup has been done.
        """
        if os.path.isdir(self.folder) and os.path.exists(os.path.join(self.folder, 'nginx.conf')):
            return False

        # Create configuration folder
        os.makedirs(self.folder)

        # Copy default configuration files
        copytree(os.path.join(os.path.dirname(os.path.realpath(__file__)), ['..', 'nginx']), self.folder)

        # Setup the nginx container
        try:
            docker.containers.run(
                self.container,
                stdout=True,
                stderr=True,
                detach=True,
                networks=['web'],
                ports={'80/tcp': 80, '443/tcp': 443},
                restart_policy={'Name': 'always'},
                volumes={
                    '/var/www': {'bind': '/var/www', 'mode': 'ro'},
                    self.folder: {'bind': '/etc/nginx', 'mode': 'ro'},
                }
            )
        except (ContainerError, APIError):
            logging.getLogger().error('Can not setup Docker container')
            raise

    def add_host(self):
        with open('data.txt', 'r') as myfile:
            data = myfile.read().replace('\n', '')
