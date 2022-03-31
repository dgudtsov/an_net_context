'''

@author: Denis Gudtsov
'''

net_context = {
"zebra1": {
    "loopback":                
        {
        "name":"lab-loop-2",
        "ip":"10.10.10.2",
        "gtp":"yes"       
        },                 
    "ip-intf":{
        # if empty - get it from context name 
        "name_prefix":"Gi_ipv4",
        "vlan": [3001,3002,4001,4002],        
        "port": ["3-1","3-2","4-1","4-2"],
        "ipaddr": ["10.10.31.1","10.10.32.1","10.10.41.1","10.10.42.1"],
        "mask":"24"
        },
    "bgp" : {
        "local_as":"64600",
        "router_id":"", #equal to loopback.ip
        "ipv4_ucast_af":{
            "neighbor":[]
            },
        "neighbor": {
            # if empty - get it from context name 
            "name_prefix":"Gi_ipv4",            
            "remote_as":"64601",
            "port": [], # port list will be copied from ip-intf
            "addr": ["10.10.31.10","10.10.32.10","10.10.41.10","10.10.42.10"]
            }
        },
    "bfd" : {
        "interface": {
            "name_prefix":"Gi_ipv4",            
            "addr": [], # from bgp neighbor
            "src":[], #src addr from ip-intf.ipaddr
            "port": [], # port list will be copied from ip-intf
            }
        }
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
