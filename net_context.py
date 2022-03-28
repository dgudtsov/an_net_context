'''

@author: Denis Gudtsov
'''

'''
TODO:
add bgp in/out filtering
add ue ip pools

'''


from conf_context_lab import *

from template_context import *

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

class Interface(Unistruct):
    # create string from template + dict
    def stringify(self,template):
        interface_definition=""
        for idx,int_port in enumerate(self.port):

            kvp = dict ( name=self.name_prefix+"_"+int_port,
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

            kvp = dict ( name=self.name_prefix+"_"+port,
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

            kvp = dict ( name=self.name_prefix+"_"+port,
                         addr = self.addr[idx],
                         src = self.src[idx],
                         name_prefix = self.name_prefix
#                         context = getattr(self,"name","")
                    )

            intf = Unistruct (kvp)
            interfaces_definition+=template.format(interface = intf)

        return interfaces_definition


if __name__ == '__main__':

    bgp_conf, context_conf, bfd_conf = "","",""

    for context in net_context:

        c=dict({"name":context})

        net_cont = Context(c)

        if "ip-intf" in net_context[context].keys():

            loopback = Loopback(net_context[context]["loopback"])

            interface = Interface(net_context[context]["ip-intf"])

            if interface.name_prefix=="":
                interface.name_prefix = context

            if "bgp" in net_context[context].keys():
            # if bgp key is defined in current context
                bgp = BGP(net_context[context]["bgp"])

                bgp.name = context
                if bgp.router_id =="":
                    bgp.router_id = loopback.ip

                bgp.neighbor = BGP(net_context[context]["bgp"]["neighbor"])

                if bgp.neighbor.name_prefix=="":
                    bgp.neighbor.name_prefix = context

                bgp.neighbor.port = interface.port

    #        print bgp.neighbor.neighbors(bgp_neighbor_template)
    #        print bgp.neighbor.neighbors(bgp_ipv4_neighbor_template)

                ipv4_neighbor=bgp.neighbor.neighbors(bgp_ipv4_neighbor_template)

#                print prefix_list_template.format(context = net_cont)
                bgp_conf += bgp_template.format(bgp=bgp,
                                                ipv4_neighbor=bgp.neighbor.neighbors(bgp_ipv4_neighbor_template),
                                                neighbor_list = bgp.neighbor.neighbors(bgp_neighbor_template),
                                                prefix_list = prefix_list_template.format(context = net_cont)
                                                )

            #print bgp_template.format(bgp=bgp,ipv4_neighbor="",neighbor_list="")
                if "bfd"  in net_context[context].keys():
                    bfd = BFD(net_context[context]["bfd"])
    #                bfd = BFD(dict())
                    bfd.name = context
                    bfd.interfaces = BFD(net_context[context]["bfd"]["interface"])

                    if bfd.interfaces.name_prefix=="":
                        bfd.interfaces.name_prefix = context

                    bfd.interfaces.port = interface.port
                    bfd.interfaces.src = interface.ipaddr
                    bfd.interfaces.addr = bgp.neighbor.addr

                    interfaces = bfd.interfaces.interfaces(bfd_interfaces_template)

                    bfd_conf += bfd_template.format(bfd=bfd, bfd_interface = bfd.interfaces.interfaces(bfd_interfaces_template)
                                                )
#            print
            context_conf += net_context_template.format(context=net_cont,loopback=loopback,ip_interface=interface.stringify(ip_interface_template))

    print context_conf
    print bgp_conf
    print bfd_conf

    pass
