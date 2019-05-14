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
        network = OrderedDict()
        regex_name = r'object\snetwork\s(.*)'
        regex_value = r'(host|fqdn|range|subnet)\s(.*)'
        for line in self.running_config:
            if not any((i in line for i in ['object network', 'description', 'fqdn', 'host', 'range', 'subnet'])):
                flag_host_fqdn_range = False
            if line.startswith("object network"):
                flag_host_fqdn_range = True
                name = re.search(regex_name, line).group(1)
                value = []
            if flag_host_fqdn_range:
                if "host" in line:
                    value = [re.search(regex_value, line).group(2), 'host']
                if line.startswith('fqdn') :
                    value = [re.search(regex_value, line).group(2), 'fqdn']
                if "range" in line:
                    value = [re.search(regex_value, line).group(2), 'range']
                if "subnet" in line:
                    value = [re.search(regex_value, line).group(2), 'subnet']
                network[name] = value
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
        object_networks = self.parse_object_networks()
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
                if 'network-object object' in item:
                    obj = item.split()[2]
                    if len(object_networks[obj]) > 1:
                        expanded_value.append(object_networks[obj][0])
                expanded_group_object[key] = expanded_value
        return expanded_group_object

    def parse_object_group_service(self):
        """
        Method to parse object-group service
        :return: dictionary
         object-group service EXAM-PORTS tcp|udp|tcp-udp
          port-object eq 1301
          port-object eq 1302
          group-object HTTP-PORTS
        """
        object_service = OrderedDict()
        for line in self.running_config:
            if not any((i in line for i in ['service-object', 'group-object', 'description', 'port-object'])):
                flag_object_service = False
            if line.startswith("object-group service"):
                flag_object_service = True
                name = line.split()[2]
                value = []
            if flag_object_service:
                if 'port-object' in line:
                    print(line)
                    value.append(line.split()[2])
                if 'group-object' in line:
                    value.append(line.split()[1])
                if 'service-object' in line:
                    value.append(line.split()[3])
                object_service[name] = value
        return object_service
