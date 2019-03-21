# Cisco ASA repository

Purpose of this repository is to parse running configuration of cisco ASA running-config

Usage:
```python
from parse_object_groups import ParseObjects
a=ParseObjects(running-config)
a.parse_names()
```
Result:
```python
{ 'Router': '10.23.23.25',
 'Fax': '172.21.17.100',
 'Secondary-Printer': '192.168.100.10'}
```

```python
a.parse_object_networks()
```
Result:
```python
{ OBJ-192.168.10.5': ['192.168.10.5', 'host'],
 'OBJ-IP-LOCAL-IPPOOL': ['192.168.236.1 192.168.236.254', 'range'],
 'PAT-IP': ['12.12.12.12', 'host'],
 'FW-INSIDE-PATs': ['8.8.8.8 8.8.8.9', 'range'],
 'www.google.com': ['www.google.com', 'fqdn'],
 }
```


```python
a.expand_object_group_network()
```
Result
```python
OrderedDict([('DMZ-JTEST-REAL-LOCAL', ['192.168.19.0/24']),
             ('DMZ-JTEST-MAPPED-LOCAL', ['10.10.19.0/24']),
             ('OFFICE_IPS',
              ['192.168.1.0/24']),
             )
             
```
The resuts is in CIDR notation and newwotk objects are replaced with the correct value