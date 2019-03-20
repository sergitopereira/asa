import re
import json
import logging
from netaddr import IPAddress
from collections import OrderedDict


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
        This method parses object networks, returning a dictionary key=name, value=dictionary.
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
        network_subnet = {}
        network = {}
        regex_name = r'object\snetwork\s(.*)'
        regex_value = r'(host|fqdn|range|subnet)\s(.*)'
        for line in self.running_config:
            if not any((i in line for i in ['object network', 'description', 'fqdn', 'host', 'range', 'subnet'])):
                flag_host_fqdn_range = False
            if line.startswith("object network"):
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
                if "subnet" in line:
                    range = re.search(regex_value, line).group(2)
                    network_subnet[name] = range
        network['host'] = network_host
        network['fqdn'] = network_fqdn
        network['range'] = network_range
        network['subnet'] = network_subnet
        return network

    def parse_object_group_network(self):

        """
        This method parses object-groups, returning a dictionary
        example:
        object-group network ItNetwork
        description IT Network
         network-object 178.255.82.64 255.255.255.224
         network-object host
         group-object InternalNet
        :return: dictionary
        """
        group_objects = OrderedDict()
        flag_object_group = False
        for line in self.running_config:
            if not any((i in line for i in ['network-object', 'group-object', 'description'])):
                flag_object_group = False
            if line.startswith("object-group network"):
                flag_object_group = True
                name = line.split()[2]
                values = []
                group_objects[name] = values
            if flag_object_group and 'object-group' not in line:
                values.append(line)
                group_objects[name] = values
        return group_objects

    def expand_object_group_network(self):
        """
        This Method returns a dictionary as key the name the object-group and values group-objects, IPS in cidr,fqdns
        :return: dictionary
        """
        names = self.parse_names()
        expanded_group_object = OrderedDict()
        group_objects = self.parse_object_group_network()
        for key, value in group_objects.items():
            expanded_value = []
            for item in value:
                if 'host' in item:
                    host = item.split()[2]
                    if host in names.keys():
                        expanded_value.append(names[host])
                    else:
                        expanded_value.append(host)
                if 'group-object' in item:
                    expanded_value.append(item.split()[1])
                network = re.search(r'object\s(\d+.*)', item)
                if network:
                    network = item.split()[1]
                    mask = IPAddress(item.split()[2]).netmask_bits()
                    network_cidr = '{}/{}'.format(network, mask)
                    expanded_value.append(network_cidr)
                expanded_group_object[key] = expanded_value
        return expanded_group_object
