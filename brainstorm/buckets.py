import logging

from cliff.lister import Lister


class Ls(Lister):
    """List either buckets or objects, depending on arguments"""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.debug("listing buckets")
        return (['Name'], ([bucket.name]
                for bucket in self.app.conn.get_all_buckets()))
