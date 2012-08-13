import logging

from boto.exception import S3ResponseError
from cliff.lister import Lister
from cliff.show import ShowOne

from brainstorm.main import parse_path
from brainstorm.main import parse_acl


class List(Lister):
    """List either buckets or objects, depending on arguments
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)
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


class Show(ShowOne):
    """Show information about a bucket or object
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Show, self).get_parser(prog_name)
        parser.add_argument('target', type=parse_path,
            help='name of object to show like bucket:object')
        return parser

    def take_action(self, parsed_args):
        bucketname, keyname = parsed_args.target
        if keyname:
            self.log.info('showing details of %s:%s' % (bucketname, keyname))
            return self._show_key(bucketname, keyname)
        else:
            self.log.info('showing details for bucket %s' % bucketname)
            return self._show_bucket(bucketname)

    def _show_bucket(self, bucketname):
        bucket = self.app.conn.lookup(bucketname)
        rows = ['Name', 'ACLs']
        data = [bucketname, '']
        if bucket:
            try:
                self.log.debug('looking up acl for %s' % bucketname)
                acp = bucket.get_acl()
                for (entity, permissions) in parse_acl(acp):
                    rows.append('  %s' % entity)
                    data.append(permissions)
                return (rows, data)
            except S3ResponseError:
                self.log.warn('could not get acl for %s' % bucketname)
        else:
            self.log.warn('could not load bucket %s' % bucketname)

    def _show_key(self, bucketname, keyname):
        bucket = self.app.conn.lookup(bucketname)
        if bucket:
            self.log.debug('looking up key %s in bucket %s'
                    % (keyname, bucketname))
            k = bucket.get_key(keyname)
            if k:
                rows = ['Name', 'Size', 'Last Modified', 'Content Type',
                        'etag', 'ACLs']
                data = [k.name, k.size, k.last_modified, k.content_type,
                        k.etag, '']
                acp = k.get_acl()
                for (entity, permissions) in parse_acl(acp):
                    rows.append('  %s' % entity)
                    data.append(permissions)
                if k.metadata:
                    rows.append('Metadata')
                    data.append('')
                    for x, v in k.metadata.iteritems():
                        rows.append('  %s' % x)
                        data.append(v)

                return (rows, data)
            else:
                self.log.warn('could not load key %s in bucket %s'
                        % (keyname, bucketname))
        else:
            self.log.warn('could not load bucket %s' % bucketname)
