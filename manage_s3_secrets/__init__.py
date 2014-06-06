'''
Created on May 29, 2014

@author: gene
'''

import argparse
import sys
import os
import boto.s3.key
import tempfile
import gnupg
import shutil
import logging

class Secrets():

    def __init__(self, args):
        self.conn_s3 = boto.connect_s3()
        self.args = args
        self.bytes_written = 0
        if not 'remotefile' in vars(self.args):
            setattr(self.args,
                    'remotefile',
                    os.path.basename(self.args.file.name))
        self.bucket = self.conn_s3.get_bucket(self.args.bucket)

    def run(self):
        if self.args.action == 'put':
            return self.put()
        elif self.args.action == 'get':
            return self.get()

    def encrypt(self, file_handle):
        try:
            gpg_home_dir = tempfile.mkdtemp()
            gpg = gnupg.GPG(gnupghome=gpg_home_dir)
            import_result = gpg.import_keys(self.args.gpgkey.read())
            content = gpg.encrypt_file(file_handle,
                                       import_result.fingerprints,
                                       always_trust=True)
            return content
        finally:
            shutil.rmtree(gpg_home_dir)

    def put(self):
        if self.args.gpgkey:
            self.args.remotefile += '.gpg'
            content = self.encrypt(self.args.file)
        else:
            content = self.args.file.read()
        k = boto.s3.key.Key(self.bucket)
        k.key = os.path.join(self.args.path, self.args.remotefile)
        self.bytes_written = k.set_contents_from_string(content)
        logging.info('Wrote %s bytes to file %s in bucket %s'
                      % (self.bytes_written, k.key, self.bucket.name))
        return True if self.bytes_written > 0 else False

    def delete(self):
        return self.bucket.delete_key(os.path.join(self.args.path,
                                                   self.args.remotefile))

    def get(self):
        if self.args.gpgkey and not self.args.remotefile.endswith('.gpg'):
            self.args.remotefile += '.gpg'
        k = self.bucket.get_key(os.path.join(self.args.path, self.args.remotefile))
        content = k.get_contents_as_string()
        if self.args.gpgkey:
            try:
                gpg_home_dir = tempfile.mkdtemp()
                gpg = gnupg.GPG(gnupghome=gpg_home_dir)
                import_result = gpg.import_keys(self.args.gpgkey.read())
                content = gpg.decrypt(content).data
            finally:
                shutil.rmtree(gpg_home_dir)
        return content


def type_filename(filename, mode='r'):
    if not os.path.exists(filename):
        msg = "The file %s does not exist" % filename
        raise argparse.ArgumentTypeError(msg)
    else:
        return open(filename, mode)

def type_loglevel(level):
    try:
        result = getattr(logging, level.upper())
    except AttributeError:
        raise argparse.ArgumentTypeError("'%s' is not a valid log level. "
                                         "Please use %s" % (level,
                                         [x for x in logging._levelNames.keys()
                                          if isinstance(x, str)]))
    return result

def collect_arguments(argv):
    defaults = {}
    defaults['bucket'] = "net.mozaws.ops.hiera-secrets"
    defaults['path'] = "type/"
    defaults['loglevel'] = "INFO"
    parser = argparse.ArgumentParser(description='Manage s3 stored secrets')
    parser.add_argument('-b', '--bucket',
                        default=defaults['bucket'],
                        help='S3 bucket to get secrets from or put secrets '
                        'in (default : %s)' % defaults['bucket'])
    parser.add_argument('-p', '--path',
                        default=defaults['path'],
                        help='S3 path to get secrets from or put secrets '
                        'in (default : %s)' % defaults['path'])
    parser.add_argument('-l', '--loglevel', type=type_loglevel,
                        default=defaults['loglevel'],
                        help='Log level verbosity (default : %s)'
                        % defaults['loglevel'])

    parsers = {}
    subparsers = parser.add_subparsers(dest='action',
                                       help='sub-command help')
    parsers['get'] = subparsers.add_parser('get', help='get help')
    parsers['get'].add_argument('remotefile',
                                help='Filename to fetch')
    parsers['get'].add_argument('-g', '--gpgkey', type=type_filename,
                                help='GPG private key to decrypt the file '
                                'with')

    parsers['put'] = subparsers.add_parser('put', help='put help')
    parsers['put'].add_argument('file', type=type_filename, metavar="FILE",
                                help='Filename to put')
    parsers['put'].add_argument('-g', '--gpgkey', type=type_filename,
                                help='GPG public key to encrypt the file '
                                'to')

    args = parser.parse_args(argv[1:])
    return args


def main():
    args = collect_arguments(sys.argv)
    logging.basicConfig(level=args.loglevel)
    secrets = Secrets(args)
    result = secrets.run()


if __name__ == '__main__':
    main()
