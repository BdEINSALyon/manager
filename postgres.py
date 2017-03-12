import string
import random

import docker as d
import logging
from docker.errors import NotFound

docker = d.from_env()


class PostgresManager(object):

    def __init__(self, name='database'):
        try:
            self.container = docker.containers.get(name)
        except NotFound:
            logging.getLogger('manager').info('Unknown postgres container named "{}". Creating it ...')
            self.container = docker.containers.run('postgres', name=name, networks=("web",), detach=True)

    def create_database(self, database):
        self.container.exec_run('createdb {}'.format(database), user='postgres')

    def create_user(self, user):

        # Generate a password for the new user
        password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(30))

        # Create the user
        if not self._has_user(user):
            self._exec_command("CREATE USER {} WITH PASSWORD '{}'".format(user, password))
        else:
            raise Exception('User {} already exists!'.format(user))

        # Create his database
        self.create_database(user)

        # Grant all privileges on his database
        self._exec_command("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA {} TO {}".format(user, user))

        return "postgres://{}:{}@{}/{}".format(user, password, self.container.name, user), {
            'user': user,
            'password': password,
            'host': self.container.name,
            'database': user
        }

    def drop_user(self, user):
        self._exec_command("DROP USER {}".format(user))

    def _exec_command(self, command):
        logging.getLogger('manager').debug('Executing SQL on {}: {}'.format(self.container.name, command))
        command = command.replace('"', '\"')
        return self.container.exec_run('psql -c "{}"'.format(command), user='postgres')

    def _has_user(self, user):
        return user in self._exec_command('SELECT usename FROM pg_user').decode('utf-8')
