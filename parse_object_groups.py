import re
import json
import logging

class ParseObjects(object):
    """
    This is a class in order to parse names and IPs of Cisco ASA running configuration Object-Groups
    """

    def __init__(self, running_config):
        self.running_config = running_config.split('\n')

    def parsenames(self):

        """
        Tis is method to parse name ans IPS.
        Example:
        name 192.168.1.100 Office1
        name 8.8.8.8 dnsGoogle
        :return dictionary
        """
        regex = r'name\s((\d+\.?)+)\s(.*)'
        nameip = {}
        for line in self.running_config:
            result = re.search(regex,line)
            if result:
                nameip[result.group(3)]=result.group(1)
        return nameip
