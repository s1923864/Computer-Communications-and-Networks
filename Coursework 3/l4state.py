from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_4
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import in_proto
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp
from ryu.lib.packet.ether_types import ETH_TYPE_IP

class L4State14(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_4.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(L4State14, self).__init__(*args, **kwargs)
        self.ht = set()

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def features_handler(self, ev):
        dp = ev.msg.datapath
        ofp, psr = (dp.ofproto, dp.ofproto_parser)
        acts = [psr.OFPActionOutput(ofp.OFPP_CONTROLLER, ofp.OFPCML_NO_BUFFER)]
        self.add_flow(dp, 0, psr.OFPMatch(), acts)

    def add_flow(self, dp, prio, match, acts, buffer_id=None):
        ofp, psr = (dp.ofproto, dp.ofproto_parser)
        bid = buffer_id if buffer_id is not None else ofp.OFP_NO_BUFFER
        ins = [psr.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, acts)]
        mod = psr.OFPFlowMod(datapath=dp, buffer_id=bid, priority=prio,
                                match=match, instructions=ins)
        dp.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        in_port, pkt = (msg.match['in_port'], packet.Packet(msg.data))
        dp = msg.datapath
        ofp, psr, did = (dp.ofproto, dp.ofproto_parser, format(dp.id, '016d'))
        eth = pkt.get_protocols(ethernet.ethernet)[0]



        #
        # write your code here


        ip_header = pkt.get_protocols(ipv4.ipv4)

        tcp_header = pkt.get_protocols(tcp.tcp)
        
        length_validation = len(ip_header) > 0 and len(tcp_header) > 0
        
        if length_validation :

            ip_header = ip_header[0]

            if in_port != 1:

                if in_port == 2 :

                    if (ip_header.dst, ip_header.src, 1, in_port) in self.ht:

                        match = psr.OFPMatch(in_port=in_port, eth_src=eth.src, eth_dst=eth.dst, ipv4_src=ip_header.src, ipv4_dst=ip_header.dst, tcp_src=tcp_header[0].src_port, tcp_dst=tcp_header[0].dst_port)

                        acts = [psr.OFPActionOutput(1)]

                        self.add_flow(dp, 1, match, acts, msg.buffer_id)

                        if ofp.OFP_NO_BUFFER != msg.buffer_id:
                            return

                    else:

                        acts = [psr.OFPActionOutput(ofp.OFPPC_NO_FWD)]
            else :

                if (tcp_header[0].has_flags(tcp.TCP_RST) or tcp_header[0].has_flags(tcp.TCP_SYN) or tcp_header[0].has_flags(tcp.TCP_FIN) or tcp_header[0].has_flags(tcp.TCP_ACK) or tcp_header[0].has_flags(tcp.TCP_URG) or tcp_header[0].has_flags(tcp.TCP_ECE) or tcp_header[0].has_flags(tcp.TCP_PSH) or tcp_header[0].has_flags(tcp.TCP_CWR)) and not tcp_header[0].has_flags(tcp.TCP_RST, tcp.TCP_SYN) and not tcp_header[0].has_flags(tcp.TCP_FIN, tcp.TCP_SYN):

                    self.ht.add((ip_header.src, ip_header.dst, in_port, 2))

                    match = psr.OFPMatch(in_port=in_port, eth_src=eth.src, eth_dst=eth.dst, ipv4_src=ip_header.src, ipv4_dst=ip_header.dst, tcp_src=tcp_header[0].src_port, tcp_dst=tcp_header[0].dst_port)

                    acts = [psr.OFPActionOutput(2)]

                    self.add_flow(dp, 1, match, acts, msg.buffer_id)
                    
                    if ofp.OFP_NO_BUFFER != msg.buffer_id:
                        return

                else:

                    acts = [psr.OFPActionOutput(ofp.OFPPC_NO_FWD)]
                    
        else:

            out_port = 2 if in_port != 2 else 1

            acts = [psr.OFPActionOutput(out_port)]


        #



        data = msg.data if msg.buffer_id == ofp.OFP_NO_BUFFER else None
        out = psr.OFPPacketOut(datapath=dp, buffer_id=msg.buffer_id,
                               in_port=in_port, actions=acts, data=data)
        dp.send_msg(out)
