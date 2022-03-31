'''

@author: Denis Gudtsov
'''

net_context = {
"zebra1": {
    "loopback": [ {
        "name":"lab-loop-1",
        "ip":"10.10.10.1",
        "gtp":"yes"       
        },
                  
        {
        "name":"lab-loop-2",
        "ip":"10.10.10.2",
        "gtp":"yes"       
        }                 
         ],
           
    "ip-intf":[ {
        # if empty - get it from context name 
        "name_prefix":"Gi_ipv4",
        "vlan": [3001,3002,4001,4002],        
        "port": ["3-1","3-2","4-1","4-2"],
        "ipaddr": ["10.10.31.1","10.10.32.1","10.10.41.1","10.10.42.1"],
        "mask":"24"
        },
       {
        "name_prefix":"Gi_ipv6",
        "vlan": [3011,3012,4011,4012],        
        "port": ["3-1","3-2","4-1","4-2"],
        "ipaddr": ["::1","::2","::3","::4"],
        "mask":"64"
       }
         ],
    "bgp" : {
        "local_as":"64600",
        "router_id":"", #equal to loopback.ip
        "ipv4_ucast_af":{
            "neighbor":[]
            },
        "neighbor": [ {
            # if empty - get it from context name 
            "name_prefix":"Gi_ipv4",            
            "remote_as":"64601",
            "port": [], # port list will be copied from ip-intf
            "addr": ["10.10.31.10","10.10.32.10","10.10.41.10","10.10.42.10"]
            },
            {           
            "name_prefix":"Gi_ipv6",            
            "remote_as":"64601",
            "port": [], # port list will be copied from ip-intf
            "addr": ["::1","::2","::3","::4"]
            }
         ]
        },
    "bfd" : {
        "interface": [ {
            "name_prefix":"Gi_ipv4",            
            "addr": [], # from bgp neighbor
            "src":[], #src addr from ip-intf.ipaddr
            "port": [], # port list will be copied from ip-intf
            },
            {
            "name_prefix":"Gi_ipv6",            
            "addr": [], # from bgp neighbor
            "src":[], #src addr from ip-intf.ipaddr
            "port": [], # port list will be copied from ip-intf
            }
        ]
        },
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
    }
}


def config_dump(key=None):
    print ("Configuration dump:")
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(net_context)   
#    print ( net_context)
    if (key): print("Module config: ",net_context[key])

if __name__ == "__main__":
    import pprint

    config_dump()
