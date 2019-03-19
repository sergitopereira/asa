import re
import json
import logging


class ParseObjects(object):
    """
    This is a class in order to parse names and IPs of Cisco ASA running configuration Object-Groups
    """

    def __init__(self, running_config):
        self.running_config = running_config.split('\n')

    def parse_names(self):
        """
        This method parses name and IPS, returning a dictionary key=name, value=ip.
        Example:
        name 192.168.1.100 Office1
        name 8.8.8.8 dnsGoogle
        :return dictionary
        """
        regex = r'name\s((\d+\.?)+)\s(.*)'
        nameip = {}
        for line in self.running_config:
            result = re.search(regex, line)
            if result:
                nameip[result.group(3)] = result.group(1)
        return nameip

    def parse_object_networks(self):
        """
        This method parses object networks, returning a dictionary key=name, value=ip.
        Example:
        object network obj-192.168.100.10
         host 192.168.100.10
        object network www.sergio.com
         fqdn www.sergio.com
        object network OfficeNet
         subnet 192.168.0.0/24
        object network net1
         range 192.168.1.0 192.168.1.10
        :return dic
        """
        flag_host_fqdn_range = False
        network_host = {}
        network_fqdn = {}
        network_range = {}
        network = {}
        regex_name = r'object\snetwork\s(.*)'
        regex_value = r'(host|fqdn|range)\s(.*)'
        for line in self.running_config:
            if line.startswith("object "):
                flag_host_fqdn_range = True
                name = re.search(regex_name, line).group(1)
            if flag_host_fqdn_range:
                if "host" in line:
                    ip = re.search(regex_value, line).group(2)
                    network_host[name] = ip
                if "fqdn" in line:
                    fqdn = re.search(regex_value, line).group(2)
                    network_fqdn[name] = fqdn
            if "range" in line:
                range = re.search(regex_value, line).group(2)
                network_range[name] = range
        network['host'] = network_host
        network['fqdn'] = network_fqdn
        network['range'] = network_range
        return network


