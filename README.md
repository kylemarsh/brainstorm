brainstorm
==========

cliff-based CLI for syncing files to DHO.

```
usage: brainstorm [--version] [-v] [--log-file LOG_FILE] [-q] [-h] [--debug]

DHO command line tool

optional arguments:
  --version            show program's version number and exit
  -v, --verbose        Increase verbosity of output. Can be repeated.
  --log-file LOG_FILE  Specify a file to log output. Disabled by default.
  -q, --quiet          suppress output except warnings and errors
  -h, --help           show this help message and exit
  --debug              show tracebacks on errors

Commands:
  create bucket  Create a new bucket
  delete         Delete an existing object
  down           Download an object from DHO to a local file
  help           print detailed help for another command
  list           List either buckets or objects, depending on arguments
  remove bucket  Delete an existing bucket
  set acl        Change a bucket or object's ACL to the specified canned value
  show           Show information about a bucket or object
  up             Upload a file from your local computer to DHO
```
