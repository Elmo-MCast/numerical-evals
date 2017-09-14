
// Global constants

#define LEAF_ID 10
#define ID_SIZE_in_BITS 13 // an extra least-significant bit is to indicate end of bitmap headers,
                           // also we need to accomodate for both unique leaf ids and header ids.
#define NUM_HOSTS 48
#define NUM_HEADERS 4


// Header types

header_type ethernet_t {
    fields {
        dstAddr : 48;
        srcAddr : 48;
        etherType : 16;
    }
}

header_type ipv4_t {
    fields {
        version : 4;
        ihl : 4;
        diffserv : 8;
        totalLen : 16;
        identification : 16;
        flags : 3;
        fragOffset : 13;
        ttl : 8;
        protocol : 8;
        hdrChecksum : 16;
        srcAddr : 32;
        dstAddr: 32;
    }
}

header_type udp_t {
    fields {
        srcPort : 16;
        dstPort : 16;
        length_ : 16;
        checksum : 16;
    }
}

header_type vxlan_t {
    fields {
        flags : 8;
        reserved : 24;
        vni : 24;
        reserved2 : 8;
    }
}




header_type baseerat_start_t {
    fields{
        type : 16
    }
}

header_type baseerat_bitmap_t {
    fields {
        id : ID_SIZE_in_BITS;
        bitmap : NUM_HOSTS;
    }
}


// Parser functions


parser start {
    return parse_ethernet;
}

#define ETHERTYPE_IPV4 0x0800

header ethernet_t ethernet_;

parser parse_ethernet {
    extract(ethernet_);
    return select(latest.etherType) {
        ETHERTYPE_IPV4 : parse_ipv4;
        default: ingress;
    }
}

#define IP_PROTOCOLS_UDP 17

header ipv4_t ipv4_;

field_list ipv4_checksum_list {
        ipv4_.version;
        ipv4_.ihl;
        ipv4_.diffserv;
        ipv4_.totalLen;
        ipv4_.identification;
        ipv4_.flags;
        ipv4_.fragOffset;
        ipv4_.ttl;
        ipv4_.protocol;
        ipv4_.srcAddr;
        ipv4_.dstAddr;
}

field_list_calculation ipv4_checksum {
    input {
        ipv4_checksum_list;
    }
    algorithm : csum16;
    output_width : 16;
}

calculated_field ipv4_.hdrChecksum  {
    verify ipv4_checksum;
    update ipv4_checksum;
}

parser parse_ipv4 {
    extract(ipv4_);
    return select(latest.protocol) {
        IP_PROTOCOLS_UDP  : parse_udp;
        default: ingress;
    }
}

#define UDP_PORT_VXLAN 4789
#define UDP_PORT_BASEERAT 0xFFFE

header udp_t udp_;

field_list udp_checksum_list {
        ipv4_.srcAddr;
        ipv4_.dstAddr;
        8'0;
        ipv4_.protocol;
        udp_.length_;
        udp_.srcPort;
        udp_.dstPort;
        udp_.length_;
        payload;
}

field_list_calculation udp_checksum {
    input {
        udp_checksum_list;
    }
    algorithm : csum16;
    output_width : 16;
}

calculated_field udp_.checksum {
    update udp_checksum;
}

parser parse_udp {
    extract(udp_);
    return select(latest.dstPort) {
        UDP_PORT_BASEERAT : parse_baseerat_start_hdr;
        UDP_PORT_VXLAN  : parse_vxlan;
        default: ingress;
    }
}




header baseerat_start_t baseerat_start_hdr_;

parser parse_baseerat_start_hdr {
    extract(baseerat_start_hdr_);
    return parse_bitmap_hdr0;
}

metadata baseerat_t leaf_hdr;
header baseerat_t bitmap_hdr[NUM_HEADERS];

parser parse_bitmap_hdr0 {
    extract(bitmap_hdr[0]);
    set_metadata(leaf_hdr.id, latest.id);
    set_metadata(leaf_hdr.bitmap, latest.bitmap);
    return select(latest.id) {
        LEAF_ID mask 0x7FF : parse_baseerat_end_hdr;
        0x100 mask 0x100 : parse_bitmap_hdr1;
        default: parse_baseerat_end_hdr;
    }
}

parser parse_bitmap_hdr1 {
    extract(bitmap_hdr[1]);
    set_metadata(leaf_hdr.id, latest.id);
    set_metadata(leaf_hdr.bitmap, latest.bitmap);
    return select(latest.id) {
        LEAF_ID mask 0x7FF : parse_baseerat_end_hdr;
        0x100 mask 0x100 : parse_bitmap_hdr2;
        default: parse_baseerat_end_hdr;
    }
}

parser parse_bitmap_hdr2 {
    extract(bitmap_hdr[2]);
    set_metadata(leaf_hdr.id, latest.id);
    set_metadata(leaf_hdr.bitmap, latest.bitmap);
    return select(latest.id) {
        LEAF_ID mask 0x7FF : parse_baseerat_end_hdr;
        0x100 mask 0x100 : parse_bitmap_hdr3;
        default: parse_baseerat_end_hdr;
    }
}

parser parse_bitmap_hdr3 {
    extract(bitmap_hdr[3]);
    set_metadata(leaf_hdr.id, latest.id);
    set_metadata(leaf_hdr.bitmap, latest.bitmap);
    return parse_baseerat_end_hdr;
    }
}

#define BASEERAT_VXLAN 4789

parser parse_baseerat_end_hdr {
    return select(baseerat_start_hdr_.type) {
        BASEERAT_VXLAN : parse_vxlan;
        default: ingress;
    }
}




header vxlan_t vxlan_;

parser parse_vxlan {
    extract(vxlan_);
    return parse_inner_ethernet;
}

header ethernet_t inner_ethernet_;

parser parse_inner_ethernet {
    extract(inner_ethernet_);
    return select(latest.etherType) {
        ETHERTYPE_IPV4 : parse_inner_ipv4;
        default: ingress;
    }
}

header ipv4_t inner_ipv4_;

field_list inner_ipv4_checksum_list {
        inner_ipv4_.version;
        inner_ipv4_.ihl;
        inner_ipv4_.diffserv;
        inner_ipv4_.totalLen;
        inner_ipv4_.identification;
        inner_ipv4_.flags;
        inner_ipv4_.fragOffset;
        inner_ipv4_.ttl;
        inner_ipv4_.protocol;
        inner_ipv4_.srcAddr;
        inner_ipv4_.dstAddr;
}

field_list_calculation inner_ipv4_checksum {
    input {
        inner_ipv4_checksum_list;
    }
    algorithm : csum16;
    output_width : 16;
}

calculated_field inner_ipv4_.hdrChecksum  {
    verify inner_ipv4_checksum;
    update inner_ipv4_checksum;
}

parser parse_inner_ipv4 {
    extract(inner_ipv4_);
    return select(latest.protocol) {
        IP_PROTOCOLS_UDP  : parse_inner_udp;
        default: ingress;
    }
}

header udp_t inner_udp_;

field_list inner_udp_checksum_list {
        inner_ipv4_.srcAddr;
        inner_ipv4_.dstAddr;
        8'0;
        inner_ipv4_.protocol;
        inner_udp_.length_;
        inner_udp_.srcPort;
        inner_udp_.dstPort;
        inner_udp_.length_;
        payload;
}

field_list_calculation inner_udp_checksum {
    input {
        inner_udp_checksum_list;
    }
    algorithm : csum16;
    output_width : 16;
}

calculated_field inner_udp_.checksum {
    update inner_udp_checksum;
}

parser parse_inner_udp {
    extract(inner_udp_);
    return ingress;
}

// @Shahbaz: update this part with match action code

action action0() {
}

table table0 {
    reads {
        ethernet_.etherType : exact;
    }
    actions {
        action0;
    }
    size: 1;
}

control ingress {
    apply(table0);
}

control egress {
}