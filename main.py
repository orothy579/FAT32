#!/usr/bin/env python

from byte_buffer2 import *

class Superblock:
    def __init__(self, bb):
        bb.offset(0xb)
        self.sector_size = bb.get_uint2_le() #bytes per sector
        self.sector_per_cluster = bb.get_uint1_le() #sector per cluster
        self.reserved_sector_count = bb.get_uint2_le() # 예약된 sector 개수
        self.cluster_size = self.sector_per_cluster * self.sector_size #size of cluster
        self.fat_area_addr = self.sector_size * self.reserved_sector_count #FAT 시작 주소
        
        bb.m_offset = 0
        bb.offset(0x20+4)
        self.fat_sector_count = bb.get_uint4_le()
        self.fat_area_size = self.sector_size * self.fat_sector_count

        bb.m_offset = 0
        bb.offset(0x30-4)
        self.root_inode = bb.get_uint4_le()

        self.data_addr = self.fat_area_addr + (0x2*self.fat_area_size)

class FatArea:
    def __init__(self, bb):
      entry_count = bb.size()//4
      self.fat = []
      for i in range(0,entry_count):
        self.fat.append(bb.get_uint4_le())

class DirectoryEntry:
    def __init__(self, bb,fat):
        bb.offset(0xb)
        self.attr = bb.get_uint1_le()
        if self.attr == 0x20: self.is_file = True

        bb.m_offset =0
        bb.offset(0x14)
        self.cluster_hi = bb.get_uint2_le()
        bb.m_offset =0
        bb.offset(0x1a)
        self.cluster_low = bb.get_uint2_le()

        self.cluster_no = (self.cluster_hi <<16) | self.cluster_low
        self.clusters = []

        next = self.cluster_no
        while next != 0xfffffff:
          self.clusters.append(next)
          next = fat.fat[next]

    def export_to(self, source, path):
      with open(path, 'wb') as file:
        for cluster in self.clusters:
            physical_addr = sb.data_addr + (cluster-2)*sb.cluster_size
            source.seek(physical_addr)
            b = source.read(physical_addr)
            file.write(b)
  
if __name__ == "__main__":
    buffer = None
    with open('FAT32_simple.mdf', 'rb') as file:
        buffer = file.read(0x200)
        bb = ByteBuffer2(buffer)
        sb = Superblock(bb)

        addr = sb.fat_area_addr
        file.seek(addr)
        buffer2 = file.read(sb.fat_area_size)
        bb2 = ByteBuffer2(buffer2)
        fat_area = FatArea(bb2)

        leaf_addr = 0x404040
        file.seek(leaf_addr)
        buffer3 = file.read(0x20)
        bb3 = ByteBuffer2(buffer3)
        leaf = DirectoryEntry(bb3,fat_area)

        port_addr = 0x404060
        file.seek(port_addr)
        buffer4 = file.read(0x20)
        bb4 = ByteBuffer2(buffer4)
        port = DirectoryEntry(bb4,fat_area)


        print(hex(sb.sector_size))
        print(hex(sb.sector_per_cluster))
        print(hex(sb.cluster_size))
        print(hex(sb.root_inode))
        print(hex(sb.fat_area_addr))
        print(hex(sb.fat_sector_count))
        print(hex(sb.fat_area_size))
        print(hex(sb.data_addr))

        leaf.export_to(file ,'./leaf.jpg')
        port.export_to(file ,'./port.jpg')