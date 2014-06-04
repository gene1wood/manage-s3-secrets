import unittest
import tempfile
import sys
import os.path
import manage_s3_secrets


class SecretsTests(unittest.TestCase):

    def setUp(self):
        def get_tempfile_name(content, suffix=''):
            file_handle = tempfile.NamedTemporaryFile(
                                    suffix=suffix,
                                    delete=False,
                                    prefix=sys.argv[0] + '-unittest-')
            file_handle.write(content)
            file_handle.close()
            return file_handle.name

        self.tempfiles = {}
        self.test_content = '''{
  "example_attribute_dict": {
    "example_attribute": "value"
  },
  "run_list": [ "recipe[example]" ]
}'''
        self.tempfiles['secrets'] = get_tempfile_name(self.test_content, '.json')
        self.test_private_key = '''-----BEGIN PGP PRIVATE KEY BLOCK-----
Version: GnuPG v1

lQOYBFOI5SUBCADWX1cN+yIyt2fgCqm4vSjrDk551Q/QKr3UArFXBMu8wlK4cBrW
LrOxgYhq3otDSqcHWR42ka1z+J/8HGb8kT/+MsSFo05DbMOUQjPopXTU080ypIq1
cp/8F5TutrFp66m85TD3q51Lejf418Ze73gYsXWtZbVHFdOz72Z5XGVryo5D27he
IEryU+VVbe0QbLULXX7ybCkw4z/73rojXW7dKrGTacLzd3VTW91DE23J/Vg6ALMi
NykOE/qDeoJSt4LqczwagXRl3r4l9ZfaamNzX00V0EaLkpMrOAx0pxs65IVc63Ur
k+iOlYjG1SmfAZHcn9cMAiu0qBf5JbfvLjSvABEBAAEAB/0ec04n17+HVGMGbC1T
PFdcGtz4fv8Z3YBiZabayqfFXmr79OdIUOZIdV2zJH0ZUrjVbooVS+3HVo55yW+y
5PpMjtnjIQvPFbDVq0O5V7X350VeB15b9iDAi876y5ZO3+FCn4xW70MkGK5rrqa9
udFQMfZFFPiXf4O3VZmzl8rLm9LR1mUg+vIo3oHGX94St/leo6aM/cJHLSPqydwP
TKIrwmFh3o7F9WpHTtSWC35MlMFzEuewL/CIyVMjhMi6Se01hE42XYWt3yYRK28G
eklZgOANUU4sVNVjS+pPRC1b8/r+GpQwGdf6/w80vrcVWOm/7xmekIGy1Us2SSxa
4z/lBADXIpN2bbxh8V1UfOil3HcZMlS497Q0E7lMnQuDDFpbwPW/GUkTOdBxwu2Q
7rDsHQ7+usieJkGkf2ZYiXA94UfAGTNVtYDrhZyaRMX+pOHBP8a7PZfGlxmMkmv9
vbQFDN1vobtT6bvEH80e1EgIzESg4BSig9HjMBW61ZXfWPpMEwQA/xetzlaFuyX8
rQuks+E06ljtDrnjdZS2VHJS7tNFKXmbwE5XLF4T2fzQSrzyJ+oIt2nS23TsJxH5
qGzV4MqEkbkA6iOUCHf+PFh+YnIcmwCcG0KhY4jnEbsO3YIKVGT7MVaygL7HjZnS
0SQj33o4kF2bvYIoeatAGNT0+ihe0HUEANTRjhEM/+FeCgWx/mFiCKdBDgr0koEX
S2scHCGcHLmIyoEAbJF4PyZ3ZU/RyVr30GjesRL7JIbiQ6HT0azL0ZrsGCq+vvz8
RWUA/SLTVkI2itgbyPaDzVxbk/JvfcLd8PRer9v0qJ1jKGiqhfJjn4OSmaFHtKA6
M8wylDyTgVB1ULO0HUF1dG9nZW5lcmF0ZWQgS2V5IDxnZW5lQHJ1dGg+iQE4BBMB
AgAiBQJTiOUlAhsvBgsJCAcDAgYVCAIJCgsEFgIDAQIeAQIXgAAKCRBVz8M08u6J
YoHrCACB8NbYm1V7p53gHNvvxzsB70pM/ySR1goyvfbu8xGr8oCqOiPMWw/OJ8nH
tiCe7Dvbi962RGvnAavX+xp9xbc8gEczn5hIJNS0vuhrQX3QmCsvR6p6wtqX6R8o
fN5ruZRSk4xOg9QtBtUw+LI8vwz6bHBwwG1L9n/pIuVU/XWkS1cJ3c9GU9S0fDjS
WfqiCvq6eVhP7crZKVfSGQIMaH/EoqcHq/XSgdHJsTPmeQz6OnrAzldvxVFBl7N+
u4AMBK6gAOS1lSabhTZnq+Tpi3etCEuyulcrFuijFZ9f5OUYPc70bpuN4kjdAbFh
y9s6y5bsQAQyqi7QnH65c81cEQ/F
=SUjI
-----END PGP PRIVATE KEY BLOCK-----'''
        self.tempfiles['private_key'] = get_tempfile_name(self.test_private_key, '.priv')
        self.test_public_key = '''-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v1

mQENBFOI5SUBCADWX1cN+yIyt2fgCqm4vSjrDk551Q/QKr3UArFXBMu8wlK4cBrW
LrOxgYhq3otDSqcHWR42ka1z+J/8HGb8kT/+MsSFo05DbMOUQjPopXTU080ypIq1
cp/8F5TutrFp66m85TD3q51Lejf418Ze73gYsXWtZbVHFdOz72Z5XGVryo5D27he
IEryU+VVbe0QbLULXX7ybCkw4z/73rojXW7dKrGTacLzd3VTW91DE23J/Vg6ALMi
NykOE/qDeoJSt4LqczwagXRl3r4l9ZfaamNzX00V0EaLkpMrOAx0pxs65IVc63Ur
k+iOlYjG1SmfAZHcn9cMAiu0qBf5JbfvLjSvABEBAAG0HUF1dG9nZW5lcmF0ZWQg
S2V5IDxnZW5lQHJ1dGg+iQE4BBMBAgAiBQJTiOUlAhsvBgsJCAcDAgYVCAIJCgsE
FgIDAQIeAQIXgAAKCRBVz8M08u6JYoHrCACB8NbYm1V7p53gHNvvxzsB70pM/ySR
1goyvfbu8xGr8oCqOiPMWw/OJ8nHtiCe7Dvbi962RGvnAavX+xp9xbc8gEczn5hI
JNS0vuhrQX3QmCsvR6p6wtqX6R8ofN5ruZRSk4xOg9QtBtUw+LI8vwz6bHBwwG1L
9n/pIuVU/XWkS1cJ3c9GU9S0fDjSWfqiCvq6eVhP7crZKVfSGQIMaH/EoqcHq/XS
gdHJsTPmeQz6OnrAzldvxVFBl7N+u4AMBK6gAOS1lSabhTZnq+Tpi3etCEuyulcr
FuijFZ9f5OUYPc70bpuN4kjdAbFhy9s6y5bsQAQyqi7QnH65c81cEQ/F
=WSzd
-----END PGP PUBLIC KEY BLOCK-----'''
        self.tempfiles['public_key'] = get_tempfile_name(self.test_private_key, '.pub')
        self.test_key_fingerprint = '2F88B0C008A204059B6D093755CFC334F2EE8962'

    def test_parse_command_line(self):
        argv = [sys.argv[0], 'put', self.tempfiles['secrets']]
        args = manage_s3_secrets.collect_arguments(argv)
        self.assertEqual('put', args.action)
        self.assertEqual(self.tempfiles['secrets'], args.file.name)
        args.file.close()

    def test_put_secrets(self):
        argv = [sys.argv[0], 'put', self.tempfiles['secrets']]
        args_put = manage_s3_secrets.collect_arguments(argv)
        secrets_put = manage_s3_secrets.Secrets(args_put)
        result = secrets_put.run()
        self.assertNotEqual(secrets_put.bytes_written, 0)
        self.assertEqual(secrets_put.bytes_written,
                         len(self.test_content),
                         '%s bytes written to s3 which differs from actual '
                         'length of the content' % secrets_put.bytes_written)
        args_put.file.seek(0)
        argv = [sys.argv[0],
                'get',
                os.path.basename(self.tempfiles['secrets'])]
        args_get = manage_s3_secrets.collect_arguments(argv)
        secrets_get = manage_s3_secrets.Secrets(args_get)
        content = secrets_get.run()
        self.assertEqual(args_put.file.read(),
                         content,
                         'content of file put does not match content of file '
                         'fetched')
        args_put.file.close()

    def test_put_gpg_secrets(self):
        argv = [sys.argv[0],
                'put',
                '--gpgkey', self.tempfiles['public_key'],
                self.tempfiles['secrets']]
        args_put = manage_s3_secrets.collect_arguments(argv)
        secrets_put = manage_s3_secrets.Secrets(args_put)
        result = secrets_put.run()
        self.assertNotEqual(secrets_put.bytes_written, 0)
        argv = [sys.argv[0],
                'get',
                '--gpgkey', self.tempfiles['private_key'],
                os.path.basename(self.tempfiles['secrets'])]
        args_get = manage_s3_secrets.collect_arguments(argv)
        secrets_get = manage_s3_secrets.Secrets(args_get)
        content = secrets_get.run()
        self.assertEqual(self.test_content,
                         content,
                         'content of file put "%s" does not match content of '
                         'file fetched "%s"' % (self.test_content, content))
        args_put.file.close()


    def tearDown(self):
        argv = [sys.argv[0], 'put', self.tempfiles['secrets']]
        args = manage_s3_secrets.collect_arguments(argv)
        secrets = manage_s3_secrets.Secrets(args)
        args.file.close()
        secrets.delete()
        for tempfile_type in self.tempfiles.keys():
            os.remove(self.tempfiles[tempfile_type])

if __name__ == '__main__':
    unittest.main()