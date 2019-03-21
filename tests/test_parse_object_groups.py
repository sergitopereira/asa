import unittest
from parse_object_groups import ParseObjects

# to run unitests
# python -m unittest -v tests.test_parse_object_groups.TestParseObjects
running_config_name = '''
omitted output
!
name 192.168.1.100 Chicago
name 172.16.0.100 DFW
name 192.168.2.200 Main-office
name 8.8.7.7 TestServer
!
omitted output
!
object network obj-192.168.100.10
 host 192.168.100.10
object network www.sergio.com
 fqdn www.sergio.com
object network OfficeNet
 subnet 192.168.0.0 255.255.255.0
object network net1
 range 192.168.1.0 192.168.1.10
'''


class TestParseObjects(unittest.TestCase):
    def test_parse_names(self):
        expected_dict_names = {'Chicago': '192.168.1.100',
                               'DFW': '172.16.0.100',
                               'Main-office': '192.168.2.200',
                               'TestServer': '8.8.7.7'}
        a = ParseObjects(running_config_name)
        self.assertEqual(expected_dict_names, a.parse_names())

    def test_parse_object_networks(self):
        expected_dict_object_net = {'obj-192.168.100.10': ['192.168.100.10', 'host'],
                                    'www.sergio.com': ['www.sergio.com', 'fqdn'],
                                    'OfficeNet': ['192.168.0.0 255.255.255.0', 'subnet'],
                                    'net1': ['192.168.1.0 192.168.1.10', 'range']}
        a = ParseObjects(running_config_name)
        print(a.parse_object_networks())
        self.assertEqual(expected_dict_object_net, a.parse_object_networks())
