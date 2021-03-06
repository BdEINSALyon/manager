"""Manager

Usage:
  manage setup <server_domain>
  manage deploy <image> <app_name> <domain>
  manage redeploy <app_name> -f

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
import logging
import os
import sys

from docopt import docopt

import nginx

import postgres

logger = logging.getLogger('manager')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s::%(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class Manager(object):

    def __init__(self):
        if not os.path.isdir("/var/conf/manager"):
            logger.error("Not on a managed server, please setup before !")
            exit(2)

    def deploy(self, image, app_name, domain):
        logger.info("Start deployment of {}".format(app_name))

    def redeploy(self, app_name, force=False):
        logger.log((logging.INFO if force else logging.DEBUG), "Redeployment of {}".format(app_name))

    @staticmethod
    def setup(domain):
        logger.info("Setup a new managed server {}".format(domain))
        nginx_manager = nginx.NginxManager()
        postgres_manager = postgres.PostgresManager()
        os.mkdir('/var/conf/manager')
        if not os.path.exists('/var/www/html/index.html'):
            os.makedirs('/var/www/html/')
            with open('/var/www/html/index.html', 'w') as index:
                index.write("<html><head></head><body><h1>It works!</h1></body></html>")


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Manager 1.0')
    force = arguments['-f']

    if arguments['setup']:
        domain = arguments['<server_domain>']
        Manager.setup(domain)
    else:
        manager = Manager()
        app_name = arguments['<app_name>']
        if arguments['deploy']:
            image = arguments['<image>']
            domain = arguments['<domain>']
            manager.deploy(image, app_name, domain)
        elif arguments['redeploy']:
            manager.redeploy(app_name, force)
