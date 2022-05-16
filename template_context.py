'''

@author: Denis Gudtsov
'''

# Support of overlapping IP address in network context
net_context_template = """
network-context {context.name} ; top; commit
network-context {context.name} ip-shared-subnet enabled; commit
 {loopback}
 !
 {ip_interface}
 commit
 !
 {ue_pool}
 commit
 !
"""

uepool_template = """
 ue-pool {uepool.name} allocation-mode local-allocation ; exit
"""

uesubpool_template = """
 ip-sub-pool {subpool.name} ip-sub-pool-type UE-IP-Pool ue-pool {subpool.uepool} range-start {subpool.range_start} range-end {subpool.range_end} advertise yes suppressicmp false route-summary-prefix-length {subpool.prefix} ; exit
"""
#ipv6-prefix-length 64

loopback_template = """
 network-context {context.name} loopback-ip {loopback.name} ip-address {loopback.ip} gtp-u {loopback.gtp} allow-subscriber-icmp-to-loopback false allow-network-icmp-to-loopback true
"""

ip_interface_template = """
 ip-interface {interface.name} port vth-{interface.port} vlan-tag {interface.vlan} ip-address {interface.ip} prefix-length {interface.mask} mtu 1500 admin-state enabled ; exit
 !
"""
# disable

#loopback_template = """
# no loopback-ip {loopback.name}
#"""

#ip_interface_template = """
# ip-interface {interface.name} admin-state disabled ; commit
# no ip-interface {interface.name} ;
# !
#"""

bgp_template="""
ip-protocols
policy
{prefix_list}
!
ip-protocols bgp router {bgp.name} extended-asn-cap local-as  {bgp.local_as} router-id {bgp.router_id} ; top; commit
 !
ip-protocols bgp router {bgp.name} max-paths ebgp 4

 !
 {neighbor_list}
 commit

 !
 ipv4-ucast-af
  dampening admin-state disabled
  redistribute static
 !
  {ipv4_neighbor}
 !
 ipv6-ucast-af
  dampening admin-state disabled
 !
 commit
"""

bgp_ipv4_neighbor_template="""
   neighbor {neighbor.name}
    prefix-list out prefix-list-name pl_{neighbor.name_prefix}_bgp_out
    redistribute static

   !
"""
#     prefix-list in prefix-list-name pl_{neighbor.name_prefix}_bgp_in

#  neighbor {neighbor.name} neighbor-addr {neighbor.addr} remote-as {neighbor.remote_as} fall-over-bfd single-hop
# neighbor {neighbor.name} fall-over-bfd single-hop
bgp_neighbor_template="""
  neighbor {neighbor.name} neighbor-addr {neighbor.addr} remote-as {neighbor.remote_as} fall-over-bfd single-hop update-source phy-interface {neighbor.name}
 exit
 !
"""

# neighbor Gi_33-1_3020 neighbor-addr 172.16.31.158 remote-as 4292281322 fall-over-bfd single-hop update-source phy-interface Gi4_33-1_3020

bfd_template ="""
ip-protocols bfd bfd-timer-profile bfd_common_profile multiplier 3 tx-interval 500 rx-interval 500; commit
ip-protocols bfd instance {bfd.name}; commit
{bfd_interface}

"""
#bfd-session {interface.addr} src-ip-address {interface.src};
bfd_interfaces_template="""
bfd-interface {interface.name} bfd-timer-profile bfd_common_profile bfd-session {interface.addr} src-ip-address {interface.src}; exit; commit
"""

prefix_list_template="""
prefix-list pl_{neighbor.name_prefix}_bgp_in
 10 permit address 0.0.0.0 prefix-length 32
!
prefix-list pl_{neighbor.name_prefix}_bgp_out
 10 permit address 0.0.0.0 prefix-length 32
!
commit
"""
