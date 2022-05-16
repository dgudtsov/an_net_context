'''

@author: Denis Gudtsov
'''

'''
v1.3
Changes:
- added cli argparse
- detailed errors output

TODO:
add bgp in/out filtering

'''
__all__ = []
__version__ = 0.1
__date__ = '2022-05-13'
__updated__ = '2022-05-13'

# BOTH format style are supported
#from conf_context_lab import *

from MTS_EPC_net_context_SAEGW_U_v011_Gi import *

#from conf_context_lab_old import *

from template_context import *

import ipaddress

import sys
import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

DEBUG = 0
TESTRUN = 0
PROFILE = 0

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
            range_end = net[-1] if net.version==4 else net[-1]+1
            # special trick to have :: at the end

            kvp = dict ( name=self.name+"_"+str(subpool)+"_"+str(range_start).replace(".", "_").replace(":", "_"),
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

    # return non-empty string only in case neighbors is ipv4
    def neighbors_v4(self,template):
        if self.version==4:
            return self.neighbors(template)
        else:
            return ""
    
    # return non-empty string only in case neighbors is ipv6
    def neighbors_v6(self,template):
        if self.version==6:
            return self.neighbors(template)
        else:
            return ""
    
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

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by user_name on %s.
  Copyright 2022 organization_name. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("--context", dest="print_context", action="append", type=str, required=False, help="print only selected network context. can be defined multiple times [default: %(default)s]")
        parser.add_argument("--intf", dest="print_intf", action="store_true", required=False, default=False, help="print network context ip-interface [default: %(default)s]")
        parser.add_argument("--bgp", dest="print_bgp", action="store_true", required=False, default=False, help="print BGP [default: %(default)s]")
        parser.add_argument("--bfd", dest="print_bfd", action="store_true", required=False, default=False, help="print BFD [default: %(default)s]")
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")

        # Process arguments
        args = parser.parse_args()

#        paths = args.paths
        verbose = args.verbose
        print_context = args.print_context
        print_intf = args.print_intf
        print_bgp = args.print_bgp
        print_bfd = args.print_bfd
        
        # enable all by default if none is selected
        if (not print_intf) & (not print_bgp) & (not print_bfd):
            print_intf = print_bgp = print_bfd = True

        if verbose > 0:
            print("Verbose mode on")

        bgp_conf, context_conf, bfd_conf = "","",""
    
        for context in net_context:
    
            c=dict({"name":context})
    
            net_cont = Context(c)
    
            if "ue-pool" in net_context[context].keys():
                ue_pool_subpool = uepool_cfg (net_context[context]["ue-pool"])
            else:
                ue_pool_subpool=""
    
            if "ip-intf" in net_context[context].keys():
    
                loopbacks=[]
                if "loopback" in net_context[context].keys():
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
                            size_of_bgp=len(net_context[context]["bgp"]["neighbor"])
                        else:
                            bgp.neighbor = BGP(net_context[context]["bgp"]["neighbor"])
                            size_of_bgp=1
    
                        # store bgp neighbor address version: ipv4 or ipv6 
                        bgp.neighbor.version = ipaddress.ip_network(unicode(bgp.neighbor.addr[0]), strict=False).version
                        
                        if size_of_bgp != len(net_context_interfaces):
                            print "error in context:",context,", size of bgp neighbor mismatch with number of context interfaces"
                            exit(1)
    
                        if bgp.neighbor.name_prefix=="":
    #                        bgp.neighbor.name_prefix = context
                            bgp.neighbor.name_prefix = interface.name_prefix
    
                        bgp.neighbor.port = interface.port
                        bgp.neighbor.vlan = interface.vlan
    
                        if len(bgp.neighbor.port) != len(bgp.neighbor.addr):
                            print "error in context:",context,", size of bgp neighbor addrs mismatch with context interfaces ipaddrs:"
                            print "interface ipaddr:",interface.ipaddr
                            print "bgp addr:",bgp.neighbor.addr
                            exit(1)
    
            #        print bgp.neighbor.neighbors(bgp_neighbor_template)
            #        print bgp.neighbor.neighbors(bgp_ipv4_neighbor_template)
#                        ipv4_neighbor=bgp.neighbor.neighbors(bgp_ipv4_neighbor_template)
#                        ipv6_neighbor=bgp.neighbor.neighbors(bgp_ipv6_neighbor_template)
    
        #                print prefix_list_template.format(context = net_cont)
                
                        bgp_conf += bgp_template.format(bgp=bgp,
                                                        ipv4_neighbor=bgp.neighbor.neighbors_v4(bgp_ipv4_neighbor_template),
                                                        ipv6_neighbor=bgp.neighbor.neighbors_v6(bgp_ipv6_neighbor_template),
                                                        neighbor_list = bgp.neighbor.neighbors(bgp_neighbor_template),
                                                        prefix_list = prefix_list_template.format(neighbor = bgp.neighbor) if bgp.neighbor.version==4 else prefix_list_v6_template.format(neighbor = bgp.neighbor)
                                                        )
    
                    #print bgp_template.format(bgp=bgp,ipv4_neighbor="",neighbor_list="")
                        if "bfd"  in net_context[context].keys():
    
                            bfd = BFD(net_context[context]["bfd"])
            #                bfd = BFD(dict())
                            bfd.name = context
    
    #                        bfd.interfaces = BFD(net_context[context]["bfd"]["interface"])
    
                            if isinstance(net_context[context]["bfd"]["interface"], list):
                                bfd.interfaces = BFD(net_context[context]["bfd"]["interface"][idx])
                                size_of_bfd = len(net_context[context]["bfd"]["interface"])
                            else:
                                bfd.interfaces = BFD(net_context[context]["bfd"]["interface"])
                                size_of_bfd=1
    
                            if size_of_bfd != len(net_context_interfaces):
                                print "error in context:",context,", size of bfd.neighbor mismatch with net_context_interfaces"
                                exit(1)
    
    
                            if bfd.interfaces.name_prefix=="":
    #                            bfd.interfaces.name_prefix = context
                                bfd.interfaces.name_prefix = interface.name_prefix
    
                            bfd.interfaces.port = interface.port
                            bfd.interfaces.vlan = interface.vlan
    
                            bfd.interfaces.src = interface.ipaddr
                            bfd.interfaces.addr = bgp.neighbor.addr
    
                            interfaces = bfd.interfaces.interfaces(bfd_interfaces_template)
    
                            bfd_conf += bfd_template.format(bfd=bfd, bfd_interface = bfd.interfaces.interfaces(bfd_interfaces_template)
                                                        )
        #            print
                    context_conf += net_context_template.format(context=net_cont,loopback=loopback_conf,ip_interface=interface.stringify(ip_interface_template), ue_pool=ue_pool_subpool)
    
        # if no context is selected, then print all contexts are defined
        # or print only those were selected 
        if (print_context == None or context in print_context) :
            if print_intf: print context_conf 
            if print_bgp:  print bgp_conf
            if print_bfd:  print bfd_conf

        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2


if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
        sys.argv.append("-v")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'net_context_2_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())
