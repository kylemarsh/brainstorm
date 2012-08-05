import logging

from boto.exception import S3ResponseError
from cliff.command import Command
from cliff.lister import Lister

from brainstorm.main import parse_path


class Ls(Lister):
    """List either buckets or objects, depending on arguments
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Ls, self).get_parser(prog_name)
        parser.add_argument('buckets', nargs='*', type=parse_path,
            help='list of buckets to show contents of')
        parser.add_argument('--prefix', dest='prefix', nargs='?',
            help='filter results to only show objects starting with <prefix>')
        parser.add_argument('--delimiter', dest='delimiter', nargs='?',
            default='/', help='string to delimit object heirarchies')
        return parser

    def take_action(self, parsed_args):
        buckets = parsed_args.buckets
        if buckets:
            #List contents of specified buckets
            self.log.debug('listing contents of ' +
                ' '.join((x[0] for x in buckets)))

            cols = ('Name', 'Size')
            data = []
            for (bucketname, prefix) in buckets:
                delimiter = parsed_args.delimiter
                if not prefix:
                    # prefix found on bucket overrides --prefix
                    prefix = parsed_args.prefix
                else:
                    # in order to mimic ls as closely as possible, we should
                    # append a delimiter to the end of the prefix
                    # automatically unless they "wildcard" it.
                    if prefix[-1] != delimiter and prefix[-1] != '*':
                        prefix += delimiter
                    prefix = prefix.rstrip('*')

                data.append((bucketname, '----'))
                bucket = self.app.conn.get_bucket(bucketname)
                self.log.debug('listing %s:%s' % (bucketname, prefix))
                for obj in bucket.list(delimiter=delimiter, prefix=prefix):
                    # Warning: buckets can be *huge*. This brings every
                    # matching key in a bucket into memory!
                    try:
                        data.append((obj.name, obj.size))
                    except AttributeError:
                        data.append((obj.name, '0'))
            return (cols, data)
        else:
            #No bucket specified; list buckets
            self.log.debug("listing buckets")
            return (['Name'], ([bucket.name]
                    for bucket in self.app.conn.get_all_buckets()))


class NewBucket(Command):
    """Create a new bucket
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(NewBucket, self).get_parser(prog_name)
        parser.add_argument('bucketname',
            help='name of bucket to create')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('creating bucket %s' % parsed_args.bucketname)
        self.app.conn.create_bucket(parsed_args.bucketname)


class RemoveBucket(Command):
    """Delete an existing bucket
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(RemoveBucket, self).get_parser(prog_name)
        parser.add_argument('bucketname', help='name of bucket to delete')
        parser.add_argument('-r', '--recursive', action='store_true',
            help='force bucket deletion by removing bucket contents first')

        return parser

    def take_action(self, parsed_args):
        bucketname = parsed_args.bucketname
        bucket = self.app.conn.lookup(bucketname)
        if bucket:
            try:
                self.log.debug('deleting bucket %s' % bucketname)
                if parsed_args.recursive:
                    for k in bucket.list():
                        k.delete()
                bucket.delete()
            except S3ResponseError:
                if not parsed_args.recursive:
                    self.log.warn('could not remove bucket %s; try --recursive'
                        % bucketname)
                else:
                    self.log.warn('could not remove bucket %s' % bucketname)
        else:
            self.log.warn('could not load bucket %s' % bucketname)
