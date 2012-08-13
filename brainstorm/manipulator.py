import logging
import os

from boto.exception import S3ResponseError
from cliff.command import Command

from brainstorm.main import parse_path


###########
# BUCKETS #
###########
class CreateBucket(Command):
    """Create a new bucket
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CreateBucket, self).get_parser(prog_name)
        parser.add_argument('bucketname', help='name of bucket to create')
        parser.add_argument('--private', dest='policy', const='private',
            action='store_const', help='create as private bucket')
        parser.add_argument('--public-read', dest='policy',
            const='public-read', action='store_const',
            help='create publicly readable bucket')
        parser.add_argument('--public-read-write', dest='policy',
            const='public-read-write', action='store_const',
            help='create publicly writable bucket')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('creating bucket %s' % parsed_args.bucketname)
        self.app.conn.create_bucket(
            parsed_args.bucketname,
            policy=parsed_args.policy)


class RemoveBucket(Command):
    """Delete an existing bucket
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(RemoveBucket, self).get_parser(prog_name)
        parser.add_argument('bucketname', help='name of bucket to delete')
        parser.add_argument('-f', '--force', action='store_true',
            help='force bucket deletion by removing bucket contents first')

        return parser

    def take_action(self, parsed_args):
        bucketname = parsed_args.bucketname
        bucket = self.app.conn.lookup(bucketname)
        if bucket:
            try:
                self.log.debug('deleting bucket %s' % bucketname)
                if parsed_args.force:
                    for k in bucket.list():
                        k.delete()
                bucket.delete()
            except S3ResponseError:
                if not parsed_args.force:
                    self.log.warn('could not remove bucket %s; try --force'
                        % bucketname)
                else:
                    self.log.warn('could not remove bucket %s' % bucketname)
        else:
            self.log.warn('could not load bucket %s' % bucketname)


###########
# OBJECTS #
###########
class DeleteObjects(Command):
    """Delete an existing object
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(DeleteObjects, self).get_parser(prog_name)
        parser.add_argument('objects', nargs='+', type=parse_path,
            help='list of objects to delete')
        parser.add_argument('-b', '--bucket',
            help='bucket to delete objects from')
        return parser

    def take_action(self, parsed_args):
        for bucketname, keyname in parsed_args.objects:
            if bucketname and not keyname:
                # something like -b mybucket object1
                keyname = bucketname
                bucketname = parsed_args.bucket
            if not bucketname:
                # something like -b mybucket :object1
                bucketname = parsed_args.bucket
            bucket = self.app.conn.lookup(bucketname)
            if bucket:
                self.log.debug('looking up key %s in bucket %s'
                        % (keyname, bucketname))
                k = bucket.get_key(keyname)
                if k:
                    try:
                        self.log.debug('deleting key %s' % keyname)
                        k.delete()
                    except S3ResponseError:
                        self.log.warn('could not remove key %s' % keyname)
                else:
                    self.log.warn('could not load key %s' % keyname)
            else:
                self.log.warn('could not load bucket %s' % bucketname)


class UploadFile(Command):
    """Upload a file from your local computer to DHO
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(UploadFile, self).get_parser(prog_name)
        parser.add_argument('source', help='name of source file')
        parser.add_argument('destination', type=parse_path,
            help='name of destination object')
        parser.add_argument('-f', '--force', action='store_true',
            default=False, help='force overwrite of existing object')
        return parser

    def take_action(self, parsed_args):
        source = parsed_args.source
        bucketname, keyname = parsed_args.destination
        self.log.info('uploading local file %s to %s:%s'
            % (source, bucketname, keyname))

        bucket = self.app.conn.lookup(bucketname)
        if not bucket:
            self.log.error("couldn't get bucket %s" % bucketname)
            return

        key = bucket.new_key(keyname)
        key.set_contents_from_filename(source, replace=parsed_args.force)
        self.log.debug('uploaded successfully')


class DownloadObject(Command):
    """Download an object from DHO to a local file
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(DownloadObject, self).get_parser(prog_name)
        parser.add_argument('source', type=parse_path,
            help='name of source object')
        parser.add_argument('destination', help='name of destination file')
        parser.add_argument('-f', '--force', action='store_true',
            default=False, help='force overwrite of existing file')
        return parser

    def take_action(self, parsed_args):
        bucketname, keyname = parsed_args.source
        destination = parsed_args.destination

        self.log.info('downloading %s:%s to local file %s'
            % (bucketname, keyname, destination))

        if os.path.exists(destination) and not parsed_args.force:
            self.log.warn('destination exists. Use --force to overwrite')
            return

        bucket = self.app.conn.lookup(bucketname)
        if not bucket:
            self.log.error("couldn't get bucket %s" % bucketname)
            return

        key = bucket.get_key(keyname)
        if not key:
            self.log.error("couldn't get key %s" % keyname)
            return

        key.get_contents_to_filename(destination)
