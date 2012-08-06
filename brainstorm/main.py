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
                command_manager=CommandManager('brainstorm.commands'),
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


def parse_acl(acp):
    """Parse the AccessControlPolicy object returned from a get_acl() call
    to tell us who has what access in a nice list of tuples.

    :param acp: AccessControlPolicy object returned from get_acl()
    :paramtype acp: boto.s3.acl.Policy
    """
    aggregated_grants = {}
    parsed_grants = []
    for grant in acp.acl.grants:
        if grant.id:
            grant_list = aggregated_grants.setdefault(grant.id, [])
            grant_list.append(grant.permission)
        else:
            if grant.type == 'Group' and grant.uri.endswith('AllUsers'):
                grant_list = aggregated_grants.setdefault('Public', [])
                grant_list.append(grant.permission)
    for entity, permissions in aggregated_grants.items():
        parsed_grants.append(
            (entity, ', '.join((x.lower() for x in permissions))))

    return parsed_grants


def parse_path(path):
    """Parse paths like bucketname:objectname

    :param paths: list of paths to parse.
    :paramtype paths: [str]
    """
    (bucketname, prefix) = path.partition(':')[::2]
    return (bucketname, prefix)


def main(argv=sys.argv[1:]):
    myapp = BrainstormApp()
    return myapp.run(argv)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
