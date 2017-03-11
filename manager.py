"""Manager

Usage:
  manage setup <server domain>
  manage deploy <image> <app name> <domain>
  manage redeploy <app name> -f

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
from docopt import docopt


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Manager 1.0')
    print(arguments)