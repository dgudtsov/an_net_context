'''

@author: Denis Gudtsov
'''

'''
v1.2
Changes:
- list of loopbacks can be defined per each network context
- list of ip-intf, bgp, bfd
- added ue pools/subpools definition

TODO:
add bgp in/out filtering

'''

# BOTH format style are supported
from conf_context_lab import *

#from conf_context_lab_old import *

from template_context import *

import ipaddress

class Unistruct(object):
    def __init__(self,context):
        for k, v in context.iteritems():
            if not isinstance(v, dict):
                setattr(self, k, v)
        return

class Context(Unistruct):
    pass

class Loopback(Unistruct):
    pass

class UEPool(Unistruct):
    # create string from template + dict
    def stringify(self,template):
        subpool_definition=""
        for idx,subpool in enumerate(self.ip_sub_pool_names):
            
            net=ipaddress.ip_network(unicode(self.ip_sub_pool_ranges[idx]), strict=False)
            
            range_start = net[0]
            range_end = net[-1] 

            kvp = dict ( name=self.name+"_"+subpool+"_"+str(range_start).replace(".", "_").replace(":", "_"),
                         range_start =range_start,
                         range_end = range_end,
                         prefix = net.prefixlen,
                         uepool = self.name  
                    )

            subpool = Unistruct (kvp)
            subpool_definition+=template.format(subpool = subpool)

        return subpool_definition    
    pass

class Interface(Unistruct):
    # create string from template + dict
    def stringify(self,template):
        interface_definition=""
        for idx,int_port in enumerate(self.port):

            kvp = dict ( name=self.name_prefix+"_"+int_port+"_"+str(self.vlan[idx]),
                         port = int_port,
                         vlan = self.vlan[idx],
                         ip = self.ipaddr[idx],
                         mask = self.mask
                    )

            intf = Unistruct (kvp)
            interface_definition+=template.format(interface = intf)

        return interface_definition

class BGP(Unistruct):

    def neighbors(self,template):

        neighbors_definition=""

        for idx,port in enumerate(self.port):

            kvp = dict ( name=self.name_prefix+"_"+port+"_"+str(self.vlan[idx]),
                         addr = self.addr[idx],
                         remote_as= self.remote_as,
                         name_prefix = self.name_prefix
#                         context = getattr(self,"name","")
                    )

            neigh = Unistruct (kvp)
            neighbors_definition+=template.format(neighbor = neigh)


        return neighbors_definition

class BFD(Unistruct):

    def interfaces(self,template):

        interfaces_definition=""

        for idx,port in enumerate(self.port):

            kvp = dict ( name=self.name_prefix+"_"+port+"_"+str(self.vlan[idx]),
                         addr = self.addr[idx],
                         src = self.src[idx],
                         name_prefix = self.name_prefix
#                         context = getattr(self,"name","")
                    )

            intf = Unistruct (kvp)
            interfaces_definition+=template.format(interface = intf)

        return interfaces_definition

def uepool_cfg(cfg_obj):
    ue_sub_pool, ue_pool, ue_pool_subpool = "","",""
    
    for pool in cfg_obj:
        
        uepool = UEPool(pool)
    
        ue_sub_pool += uepool.stringify(uesubpool_template)
        
        ue_pool += uepool_template.format(uepool = uepool )
    
    return ue_pool + ue_sub_pool

if __name__ == '__main__':

    bgp_conf, context_conf, bfd_conf = "","",""

    for context in net_context:

        c=dict({"name":context})

        net_cont = Context(c)
        
        if "ue-pool" in net_context[context].keys():
            ue_pool_subpool = uepool_cfg (net_context[context]["ue-pool"])

        if "ip-intf" in net_context[context].keys():

            loopbacks=[]
            if isinstance(net_context[context]["loopback"], list):
                loopbacks = net_context[context]["loopback"]
            else:
                loopbacks.append(net_context[context]["loopback"])

#           loopback = Loopback(net_context[context]["loopback"])

            loopback_conf=""

            for loopback in loopbacks:
                loopback_conf += loopback_template.format(context=net_cont, loopback=Loopback(loopback))
            
            net_context_interfaces=[]
            if isinstance(net_context[context]["ip-intf"], list):
                net_context_interfaces = net_context[context]["ip-intf"]
            else: 
                net_context_interfaces.append(net_context[context]["ip-intf"])
            
            for idx, intf in enumerate(net_context_interfaces):
                interface = Interface(intf)
    
                if interface.name_prefix=="":
                    interface.name_prefix = context
    
                if "bgp" in net_context[context].keys():
                # if bgp key is defined in current context
                                  
                    bgp = BGP(net_context[context]["bgp"])
    
                    bgp.name = context
                    if bgp.router_id =="":
                        bgp.router_id = idx
    
                    if isinstance(net_context[context]["bgp"]["neighbor"], list):
                        bgp.neighbor = BGP(net_context[context]["bgp"]["neighbor"][idx])
                    else:
                        bgp.neighbor = BGP(net_context[context]["bgp"]["neighbor"])
    
                    if bgp.neighbor.name_prefix=="":
                        bgp.neighbor.name_prefix = context
    
                    bgp.neighbor.port = interface.port
                    bgp.neighbor.vlan = interface.vlan
    
        #        print bgp.neighbor.neighbors(bgp_neighbor_template)
        #        print bgp.neighbor.neighbors(bgp_ipv4_neighbor_template)
    
                    ipv4_neighbor=bgp.neighbor.neighbors(bgp_ipv4_neighbor_template)
    
    #                print prefix_list_template.format(context = net_cont)
                    bgp_conf += bgp_template.format(bgp=bgp,
                                                    ipv4_neighbor=bgp.neighbor.neighbors(bgp_ipv4_neighbor_template),
                                                    neighbor_list = bgp.neighbor.neighbors(bgp_neighbor_template),
                                                    prefix_list = prefix_list_template.format(neighbor = bgp.neighbor)
                                                    )
    
                #print bgp_template.format(bgp=bgp,ipv4_neighbor="",neighbor_list="")
                    if "bfd"  in net_context[context].keys():
                        
                       
                        bfd = BFD(net_context[context]["bfd"])
        #                bfd = BFD(dict())
                        bfd.name = context
                        
#                        bfd.interfaces = BFD(net_context[context]["bfd"]["interface"])
                        
                        if isinstance(net_context[context]["bfd"]["interface"], list):
                            bfd.interfaces = BFD(net_context[context]["bfd"]["interface"][idx])
                        else:
                            bfd.interfaces = BFD(net_context[context]["bfd"]["interface"])
    
                        if bfd.interfaces.name_prefix=="":
                            bfd.interfaces.name_prefix = context
    
                        bfd.interfaces.port = interface.port
                        bfd.interfaces.vlan = interface.vlan
                        
                        bfd.interfaces.src = interface.ipaddr
                        bfd.interfaces.addr = bgp.neighbor.addr
    
                        interfaces = bfd.interfaces.interfaces(bfd_interfaces_template)
    
                        bfd_conf += bfd_template.format(bfd=bfd, bfd_interface = bfd.interfaces.interfaces(bfd_interfaces_template)
                                                    )
    #            print
                context_conf += net_context_template.format(context=net_cont,loopback=loopback_conf,ip_interface=interface.stringify(ip_interface_template), ue_pool=ue_pool_subpool)

    print context_conf
    print bgp_conf
    print bfd_conf

    pass
