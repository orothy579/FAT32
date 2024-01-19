from byte_buffer2 import *

class DirectoryEntry:
    def __init__(self, bb):
        bb.offset(0x400000+0x0b)
        self.attribute = bb.get_uint1_le() # attribute
        bb.offset(0x400000+0x10+4)
        self.s_cluster_high = bb.get_uint2_le() #Starting cluster high
        bb.m_offset += 4
        self.s_cluster_low = bb.get_uint2_le() #Starting cluster low
        self.filesize = bb.get_uint4_le()


        self.sector_count = bb.get_uint1_le() #sector per cluster
        self.cluster_size = self.sector_count * self.sector_size #size of cluster
        bb.m_offset = 0
        bb.offset(0x30-4)
        self.root_inode = bb.get_uint4_le()