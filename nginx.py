import os

from shutil import copytree

import docker as d
import logging

import shutil

import subprocess
from docker.errors import APIError, ContainerError

docker = d.from_env()


class NginxManager(object):
    def __init__(self, nginx_container='nginx', configuration_folder='/var/conf/nginx'):
        self.container = nginx_container
        self.folder = configuration_folder
        self.has_certbot = shutil.which('certbot-auto') is None
        if not self.has_certbot:
            logging.getLogger('manager').critical(
                'No HTTPS support on that system because we have not cerbot installed')
        self._check_and_setup()

    def _check_and_setup(self):
        """
        Setup Nginx if necessary
        :rtype: bool Return True if setup has been done.
        """
        if os.path.isdir(self.folder) and os.path.exists(os.path.join(self.folder, 'nginx.conf')):
            return False

        # Copy default configuration files
        if not os.path.isdir(self.folder):
            copytree(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'nginx'), self.folder)

        # Setup the nginx container
        try:
            docker.containers.run(
                'nginx',
                name=self.container,
                stdout=True,
                stderr=True,
                detach=True,
                networks=['web'],
                ports={'80/tcp': 80, '443/tcp': 443},
                restart_policy={'Name': 'always'},
                volumes={
                    '/var/www': {'bind': '/var/www', 'mode': 'ro'},
                    '/etc/letsencrypt/live/': {'bind': '/etc/letsencrypt/live/', 'mode': 'ro'},
                    self.folder: {'bind': '/etc/nginx', 'mode': 'ro'},
                }
            )
        except (ContainerError, APIError):
            logging.getLogger('manager').error('Can not setup Docker container')
            raise

    def register_host(self, domain, docker_container_name, docker_port, app_name, use_ssl=True):

        # Handle no certbot issue
        if not self.has_certbot:
            logging.getLogger('manager').error('Will deploy {} without SSL because we don\'t have certbot')
            use_ssl = False

        # Remove old configuration if it exists
        if self._has_conf(app_name):
            self._clear_conf(app_name)

        # Select the most appropriate model
        if use_ssl:
            model = '443-preauthorization-host'
        else:
            model = '80-host'

        # Write configuration for the host
        self._write_site_config(app_name, docker_container_name, docker_port, domain, model)

        # Reload Nginx
        self._reload()

        # If needed, configure SSL
        if use_ssl:
            # Issue the certificate
            self._cerbot(domain)
            # Write host configuration to use the new SSL certificate
            self._write_site_config(app_name, docker_container_name, docker_port, domain, '443-host')
            # Reload to apply edits
            self._reload()

    def _clear_conf(self, app_name):
        os.remove(os.path.join(self.folder, 'managed-hosts/{}.conf'.format(app_name)))

    def _cerbot(self, domain):
        command = "certbot-auto certonly -a webroot --webroot-path=/var/www/letsencrypt -d {}"
        command.format(domain)
        command = command.split(' ')
        with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE) as c:
            c.wait()
            logging.getLogger('manager').debug(c.stdout.read())
            logging.getLogger('manager').info(c.stderr.read())

    def _write_site_config(self, app_name, docker_container_name, docker_port, domain, model):
        self._write_conf(
            app_name, model,
            domain=domain, docker_container_name=docker_container_name, app_name=app_name, docker_port=docker_port
        )

    def _reload(self):
        docker.containers.get(self.container).exec_run('nginx -s reload')

    def _write_conf(self, name, source, **args):
        path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'nginx_templates/{}.conf'.format(source)
        )
        with open(path, 'r') as model:
            data = model.read().replace('\n', '')
            for key, value in args:
                data = data.replace('%{}%'.format(key), value)
        destination = os.path.join(
            self.folder,
            'managed-hosts/{}.conf'.format(name)
        )
        with open(destination, 'w') as configuration:
            configuration.write(data)

    def _has_conf(self, name):
        return os.path.exists(os.path.join(
            self.folder,
            'managed-hosts/{}.conf'.format(name)
        ))
