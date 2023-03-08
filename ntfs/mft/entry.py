from ntfs.mft.config import *
from ntfs.mft.property import *
from ntfs.mft.attribute import *


class MFTEntryHeader(Property):
    def __init__(self, data):
        Property.__init__(self, data)
        self.file_signature = self.get_string(0, 4)
        self.update_seq_offset = self.get_ushort(4)
        self.update_seq_size = self.get_ushort(6)
        self.LogFile_seq_number = self.get_ulonglong(8)
        self.seq_number = self.get_ushort(16)
        self.hardlink_count = self.get_ushort(18)
        self.first_attr_offset = self.get_ushort(20)
        self.flags = self.get_ushort(22)
        self.used_size = self.get_uint(24)
        self.allocated_size = self.get_uint(28)
        self.file_ref_to_baseFile = self.get_ulonglong(32)
        self.next_attr = self.get_ushort(40)
        self.ID = self.get_uint(44)


class MFTEntry(Property):
    def __init__(self, data=None, offset=None, length=None, filename=None, index=None):
        Property.__init__(self, data=data, filename=filename,
                          offset=offset, length=length)
        self.index = index
        self.attributes = []
        self.fname_str = ""
        self.check_data = 0
        self.property = ""
        self.real_size = None
        self.header = MFTEntryHeader(self.get_chunk(0, HEADER_SIZE))
        self.load_attributes()
        
        if self.check_data:
            self.property += "\nFile Size: " + str(self.real_size) + " (bytes)"
        self.property += "\n[Start Sector - End Sector]: " + str(
            int(offset/512)) + " - " + str(int(offset/512+self.header.allocated_size/512))

    def is_directory(self):
        return self.header.flags & 0x0002

    def is_file(self):
        return not self.is_directory

    def is_in_use(self):
        return self.header.flags & 0x0001

    def used_size(self):
        return self.header.used_size

    def getFileName(self):
        return self.fname_str

    def getID(self):
        return self.header.ID

    def getProperties(self):
        return self.property

    def get_attribute(self, offset):
        attr_type = self.get_uint(offset)
        if attr_type == 0xFFFFFFFF:
            return None
        length = self.get_uint(offset + 0x04)
        data = self.get_chunk(offset, length)
        return MFTAttr.factory(attr_type, data)

    def lookup_attribute(self, attr_type_id):
        for attr in self.attributes:
            if attr.header.type == attr_type_id:
                return attr
        return None

    def load_attributes(self):
        free_space = self.header.used_size - HEADER_SIZE
        offset = self.header.first_attr_offset
        while free_space > 0:
            attr = self.get_attribute(offset)
            if (attr is not None):
                if attr.header.type == MFT_ATTR_FILENAME:

                    self.fname_str = attr.fname
                    self.parent_ID = attr.parent_ref
                    self.property += "\nFile name: " + attr.fname
                    self.property += "\nAttribute: "

                    if (attr.flags == READ_ONLY):
                        self.property += "*READ ONLY*"
                    if (attr.flags == HIDDEN):
                        self.property += "*HIDDEN*"
                    if (attr.flags == SYSTEM):
                        self.property += "*SYSTEM*"
                    if (attr.flags == ARCHIVE):
                        self.property += "*ARCHIVE*"
                    if (attr.flags == COMPRESSED):
                        self.property += "*COMPRESSED*"
                    if (attr.flags == ENCRYPTED):
                        self.property += "*ENCRYPTED*"
                    if (attr.flags == DIRECTORY):
                        self.property += "*DIRECTORY*"

                    self.property += "\nCreation time: " + \
                        attr.ctime_dt().strftime('%d.%m.%Y %H:%M:%S')
                    self.property += "\nModification time: " + \
                        attr.mtime_dt().strftime('%d.%m.%Y %H:%M:%S')
                    self.property += "\nLast Accessed time: " + \
                        attr.atime_dt().strftime('%d.%m.%Y %H:%M:%S')

                if attr.header.type == MFT_ATTR_DATA:
                    if self.check_data == 0:
                        self.real_size = attr.header.real_size
                    self.check_data += 1
                self.attributes.append(attr)
                free_space = free_space - attr.header.length
                offset = offset + attr.header.length
            else:
                break
