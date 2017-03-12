"""Manager

Usage:
  manage setup <server_domain>
  manage deploy <image> <app_name> <domain>
  manage redeploy <app_name> -f

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
import os
import logging
from logging import StreamHandler

import sys
from docopt import docopt

logger = logging.getLogger()
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
