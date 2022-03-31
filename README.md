# an_net_context
Affirmed Networks MCC network config generator

Work with python **2.7**

# Usage
## Prepare configuration

### 1. Edit existing conf_context_lab.py
#### Any number of network contexts can be defined as the following:

        net_context = {
          "context-1": {
              "loopback":[],
              "ip-intf":[],
              "bgp" : {},
              "bfd" : {},
              "uepool": []
          },
          "context-2": {
              "loopback":[],
              "ip-intf":[],
              "bgp" : {},
              "bfd" : {},
              "uepool": []
          },
          "context-3": {},
          ...
          "context-N": {}
        }

#### Each context can store a number of loopbacks, ip interfaces, bgp and bfd entities:
          "context-1": {
              "loopback":[ {"name":"loopback-1","ip":"10.10.10.1",...},{"name":"loopback-2","ip":"10.10.10.2",...},...,{} ],
              "ip-intf":[ {"name_prefix":"ipv4",...},{"name_prefix":"ipv6",...},...,{} ],
              "bgp" : {...,"neighbor": [ {"name_prefix":"ipv4",...}, {"name_prefix":"ipv6",...},...,{} ] },
              "bfd" : {"interface": [ {"name_prefix":"ipv4",...}, {"name_prefix":"ipv6",...},...,{} ] },
              "uepool": [{ "name": "pool_1","ip_sub_pool_names": ["subpool_1","subpool_2",...], "ip_sub_pool_ranges": ["abcd / n","abcd / n",...] },..., {} ]
          }

#### UE Pools definition

UE pool is defined as array of dicts (hashes). Each dict has three keys: 
name - name of ue pool,
ip_sub_pool_names - array containing names of ue sub pools
ip_sub_pool_ranges - array in CIDR format corresponding to ip_sub_pool_names

    "ue-pool" : [
        { "name": "internet",
          "ip_sub_pool_names": ["subpool_1","subpool_2","subpool_3"],
          "ip_sub_pool_ranges": ["192.168.1.1/24","192.168.2.1/24","192.168.3.1/24"]
        },
        { "name": "internet6",
          "ip_sub_pool_names": ["subpool_4","subpool_5","subpool_6"],
          "ip_sub_pool_ranges": ["2a00:1fa0:4100::/44","2a00:1fa0:4110::/44","2a00:1fa0:4120::/44"]
        }                 
        ]


### 2. Verify existing configuration
Run: 

$ python conf_context_lab.py

Result of the configuration dump:

Configuration dump:

        {   'zebra1': {   'bfd': {   'interface': {   'addr': [],
                                                      'name_prefix': '',
                                                      'port': [],
                                                      'src': []}},
                          'bgp': {   'ipv4_ucast_af': {   'neighbor': []},
                                     'local_as': '64600',
                                     'neighbor': {   'addr': [   '10.10.31.10',
                                                                 '10.10.32.10',
                                                                 '10.10.41.10',
                                                                 '10.10.42.10'],
                                                     'name_prefix': '',
                                                     'port': [],
                                                     'remote_as': '64601'},
                                     'router_id': ''},
                          'ip-intf': {   'ipaddr': [   '10.10.31.1',
                                                       '10.10.32.1',
                                                       '10.10.41.1',
                                                       '10.10.42.1'],
                                         'mask': '24',
                                         'name_prefix': '',
                                         'port': ['3-1', '3-2', '4-1', '4-2'],
                                         'vlan': [3001, 3002, 4001, 4002]},
                          'loopback': {   'gtp': 'yes',
                                          'ip': '10.10.10.1',
                                          'name': 'lab-loop-1'}}}

### 3. Check reference of configuration in main module
check in net_context.py:

from **conf_context_lab** import *

replace conf_context_lab to actual name of configuration you have prepared.


### 4. Run configuration generator
Run:

$ python net_context.py

and you will get configuration commands on stdout. Copy & paste it into MCC cli:

        network-context zebra1 ; top; commit
         network-context zebra1 loopback-ip lab-loop-1 ip-address 10.10.10.1 gtp-u yes allow-subscriber-icmp-to-loopback false allow-network-icmp-to-loopback true 
         !

         ip-interface zebra1_3-1 port vth-3-1 vlan-tag 3001 ip-address 10.10.31.1 prefix-length 24 mtu 1500 admin-state enabled ; commit 
         !

         ip-interface zebra1_3-2 port vth-3-2 vlan-tag 3002 ip-address 10.10.32.1 prefix-length 24 mtu 1500 admin-state enabled ; commit 
         !

         ip-interface zebra1_4-1 port vth-4-1 vlan-tag 4001 ip-address 10.10.41.1 prefix-length 24 mtu 1500 admin-state enabled ; commit 
         !

         ip-interface zebra1_4-2 port vth-4-2 vlan-tag 4002 ip-address 10.10.42.1 prefix-length 24 mtu 1500 admin-state enabled ; commit 
         !

         !


        ip-protocols
        policy

        prefix-list pl_zebra1_bgp_in
         10 permit address 0.0.0.0 prefix-length 32
        !
        prefix-list pl_zebra1_bgp_out
         10 permit address 0.0.0.0 prefix-length 32
        !
        commit
...

You can check configuration example output in output.log file in this repo
