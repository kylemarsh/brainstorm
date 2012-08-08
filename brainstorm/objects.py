import logging
import os

from boto.exception import S3ResponseError
from cliff.command import Command
from cliff.show import ShowOne

from brainstorm.main import parse_path
from brainstorm.main import parse_acl


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


class CopyObject(Command):
    """Copy an object between your local computer and DHO.
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CopyObject, self).get_parser(prog_name)
        parser.add_argument('source', help='name of source object or file')
        parser.add_argument('destination',
            help='name of destination object or file')
        return parser

    def take_action(self, parsed_args):
        #TODO:
        src_type = self._path_type(parsed_args.source)
        dest_type = self._path_type(parsed_args.destination)
        if src_type == 'file' and dest_type == 'object':
            self._upload(parsed_args.source, parsed_args.destination)
        elif src_type == 'object' and dest_type == 'object':
            self._copy(parsed_args.source, parsed_args.destination)
        elif src_type == 'object' and dest_type == 'file':
            self._download(parsed_args.source, parsed_args.destination)
        else:
            self.log.warn('looks like you provided two local files. \
                Just use cp!')

    def _path_type(self, path):
        """Determine if a path is the path to a local file or an object on DHO
        """
        if os.stat(path):
            return 'file'
        return 'object'

    def _upload(self, source, destination):
        """Copy a local file up to DHO

        :param source: name of file to upload
        :paramtype source: str
        :param destination: name of destination object
        :paramtype destination: str
        """
        raise NotImplementedError

    def _copy(self, source, destination):
        """Copy an object from one place to another on DHO

        :param source: name of source object
        :paramtype source: str
        :param destination: name of destination object
        :paramtype destination: str
        """
        raise NotImplementedError

    def _download(self, source, destination):
        """Copy an object from DHO down to a local file

        :param source: name of object to download
        :paramtype source: str
        :param destination: name of destination file
        :paramtype destination: str
        """
        raise NotImplementedError


class ShowObject(ShowOne):
    """Show information about an object
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ShowObject, self).get_parser(prog_name)
        parser.add_argument('object', type=parse_path,
            help='name of object to show like bucket:object')
        return parser

    def take_action(self, parsed_args):
        bucketname, keyname = parsed_args.object
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
