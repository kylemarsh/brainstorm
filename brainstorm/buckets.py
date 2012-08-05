import logging

from cliff.lister import Lister


class Ls(Lister):
    """List either buckets or objects, depending on arguments
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Ls, self).get_parser(prog_name)
        parser.add_argument('buckets', nargs='*',
            help='list of buckets to show contents of')
        parser.add_argument('--prefix', dest='prefix', nargs='?',
            help='filter results to only show objects starting with <prefix>')
        parser.add_argument('--delimiter', dest='delimiter', nargs='?',
            help='string to delimit object heirarchies')
        return parser

    def take_action(self, parsed_args):
        if parsed_args.buckets:
            #List contents of specified buckets
            self.log.debug('listing contents of ' +
                    ' '.join(parsed_args.buckets))
            cols = ('Name', 'Size')
            data = []
            for bucketname in parsed_args.buckets:
                data.append((bucketname, '----'))
                bucket = self.app.conn.get_bucket(bucketname)
                for obj in bucket.list(
                        delimiter=parsed_args.delimiter,
                        prefix=parsed_args.prefix):
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
