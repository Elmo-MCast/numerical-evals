
// Global constants

#define LEAF_ID 10
#define ID_SIZE_in_BITS 12 // we need to accomodate for both unique leaf ids and header ids.
#define NUM_HOSTS 48


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




header_type bitmap_t {
    fields {
        id : ID_SIZE_in_BITS;
        bitmap : NUM_HOSTS;
        next : 1;
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
        UDP_PORT_VXLAN  : parse_vxlan;
        default: ingress;
    }
}

#define VXLAN_VNI_BASEERAT 0xFFFFFE

header vxlan_t vxlan_;

parser parse_vxlan {
    extract(vxlan_);
    return select(latest.vni) {
        VXLAN_VNI_BASEERAT : parse_bitmap_hdr0;
        default: parse_inner_ethernet;
}




metadata bitmap_t bitmap_leaf_hdr_;
header bitmap_t bitmap_hdr0_;

parser parse_bitmap_hdr0 {
    extract(bitmap_hdr0_);
    set_metadata(bitmap_leaf_hdr_.id, latest.id);
    set_metadata(bitmap_leaf_hdr_.bitmap, latest.bitmap);
    return select(latest.next, latest.id) {
        LEAF_ID mask 0x0FFF : parse_inner_ethernet;
        0x1000 mask 0x1000 : parse_bitmap_hdr1;
        default: parse_inner_ethernet;
    }
}

header bitmap_t bitmap_hdr1_;

parser parse_bitmap_hdr1 {
    extract(bitmap_hdr1_);
    set_metadata(bitmap_leaf_hdr_.id, latest.id);
    set_metadata(bitmap_leaf_hdr_.bitmap, latest.bitmap);
    return select(latest.next, latest.id) {
        LEAF_ID mask 0x0FFF : parse_inner_ethernet;
        0x1000 mask 0x1000 : parse_bitmap_hdr2;
        default: parse_inner_ethernet;
    }
}

header bitmap_t bitmap_hdr2_;

parser parse_bitmap_hdr2 {
    extract(bitmap_hdr2_);
    set_metadata(bitmap_leaf_hdr_.id, latest.id);
    set_metadata(bitmap_leaf_hdr_.bitmap, latest.bitmap);
    return select(latest.next, latest.id) {
        LEAF_ID mask 0x0FFF : parse_inner_ethernet;
        0x1000 mask 0x1000 : parse_bitmap_hdr3;
        default: parse_inner_ethernet;
    }
}

header bitmap_t bitmap_hdr3_;

parser parse_bitmap_hdr3 {
    extract(bitmap_hdr3_);
    set_metadata(bitmap_leaf_hdr_.id, latest.id);
    set_metadata(bitmap_leaf_hdr_.bitmap, latest.bitmap);
    return select(latest.next, latest.id) {
        LEAF_ID mask 0x0FFF : parse_inner_ethernet;
        0x1000 mask 0x1000 : parse_bitmap_default_hdr;
        default: parse_inner_ethernet;
    }
}

header bitmap_t bitmap_default_hdr_;

parser parse_bitmap_default_hdr {
    extract(bitmap_default_hdr_);
    return parse_inner_ethernet;
    }
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




extern action bitmap_output_select(bitmap);  // The extern action for bitmap-based port selection

action bitmap_leaf_hdr_action() {
    bitmap_output_select(bitmap_leaf_hdr_.bitmap);
}

action inner_ipv4_bitmap_action(bitmap) {
    bitmap_output_select(bitmap);
}

action bitmap_default_hdr_action() {
    bitmap_output_select(bitmap_default_hdr_.bitmap);
}

table bitmap_table {
    reads {
        bitmap_leaf_hdr_.id : exact;  // This will be a least priority rule in the table
        inner_ipv4_.dstAddr : exact;  // The group/topic identifier
//        bitmap_default_hdr_.id : exact;  // A default action is specified at runtime (which will be
                                           // bitmap_default_hdr_action()
    }
    actions {
        leaf_hdr_action;
        inner_ipv4_bitmap_action;
        bitmap_default_hdr_action;
    }
    size: 1000;
}

control ingress {
    apply(bitmap_table);
}

control egress {
}