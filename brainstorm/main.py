import boto
import logging
import sys

from boto.s3.connection import S3Connection, OrdinaryCallingFormat
from cliff.app import App
from cliff.commandmanager import CommandManager


class BrainstormApp(App):

    log = logging.getLogger(__name__)

    def __init__(self):
        super(BrainstormApp, self).__init__(
                description='DHO command line tool',
                version='0.1',
                command_manager=CommandManager('cliff.demo'),
                )

    def initialize_app(self, argv):
        self.log.debug('initializing app')
        try:
            self.log.debug('attempting to create connection')
            self.conn = S3Connection(
                    host='objects.dreamhost.com',
                    is_secure=False,
                    calling_format=OrdinaryCallingFormat())
            self.log.debug('connection successfully created')
        except boto.exception.NoAuthHandlerFound:
            self.log.error('could not find boto credentials')

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    myapp = BrainstormApp()
    return myapp.run(argv)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
