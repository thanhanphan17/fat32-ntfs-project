from ntfs.mft.config import *
from ntfs.mft.property import *
from ntfs.helper import time_to_dt


class MFTAttrHeader(Property):
    """
        This class defines the header of an MFT attribute 
        and contains methods for reading and parsing the header data.
    """

    def __init__(self, data):
        Property.__init__(self, data)
        self.type = self.get_uint(0)
        self.length = self.get_uint(0x4)
        self.non_resident_flag = self.get_uchar(0x08)
        self.length_of_name = self.get_uchar(0x09)
        self.offset_to_name = self.get_ushort(0x0A)
        self.flags = self.get_ushort(0x0C)
        self.identifier = self.get_ushort(0x0E)

        if (self.non_resident_flag):
            self.lowest_vcn = self.get_ulonglong(0x10)
            self.highest_vcn = self.get_ulonglong(0x18)
            self.data_run_offset = self.get_ushort(0x20)
            self.comp_unit_size = self.get_ushort(0x22)
            self.alloc_size = self.get_ulonglong(0x28)
            self.real_size = self.get_ulonglong(0x30)
            self.data_size = self.get_ulonglong(0x38)
            if (self.length_of_name > 0):
                self.attr_name = self.get_chunk(
                    0x40, 2 * self.length_of_name).decode('utf-16')
        else:
            self.real_size = self.get_uint(0x10)
            self.attr_offset = self.get_ushort(0x14)
            self.indexed = self.get_uchar(0x16)
            if (self.length_of_name > 0):
                self.attr_name = self.get_chunk(
                    0x18, 2 * self.length_of_name).decode('utf-16')


class MFTAttr(Property):
    """
        This is the base class for all MFT attribute classes. It defines a factory 
        method for creating objects of the appropriate subclass based on the attribute type.
    """

    def __init__(self, data):
        Property.__init__(self, data)

        self.type_str = "$UNKNOWN"
        non_resident_flag = self.get_uchar(8)
        namength = self.get_uchar(9)
        header_size = 0

        if non_resident_flag:
            if namength == 0:
                header_size = 0x40
            else:
                header_size = 0x40 + 2 * namength
        else:
            if namength == 0:
                header_size = 0x18
            else:
                header_size = 0x18 + 2 * namength

        self.header = MFTAttrHeader(self.get_chunk(0, header_size))

    def factory(attr_type, data):
        constructors = {
            MFT_ATTR_STANDARD_INFORMATION: MFTAttrStandardInformation,
            MFT_ATTR_ATTRIBUTE_LIST: MFTAttrAttributeList,
            MFT_ATTR_FILENAME: MFTAttrFilename,
            MFT_ATTR_OBJECT_ID: MFTAttrObjectId,
            MFT_ATTR_SECURITY_DESCRIPTOR: MFTAttrSecurityDescriptor,
            MFT_ATTR_VOLUME_NAME: MFTAttrVolumeName,
            MFT_ATTR_VOLUME_INFO: MFTAttrVolumeInfo,
            MFT_ATTR_DATA: MFTAttrData,
            MFT_ATTR_INDEX_ROOT: MFTAttrIndexRoot,
            MFT_ATTR_INDEX_ALLOCATION: MFTAttrIndexAllocation,
            MFT_ATTR_BITMAP: MFTAttrBitmap,
            MFT_ATTR_REPARSE_POINT: MFTAttrReparsePoint,
            MFT_ATTR_LOGGED_TOOLSTREAM: MFTAttrLoggedToolstream,
        }

        if attr_type not in constructors:
            return None

        return constructors[attr_type](data)


class MFTAttrStandardInformation(MFTAttr):
    """
        This class represents the standard information attribute of 
        an MFT entry and contains methods for reading and parsing the attribute data.
    """

    def __init__(self, data):
        MFTAttr.__init__(self, data)
        self.type_str = "$STANDARD_INFORMATION"
        offset = self.header.size
        self.ctime = self.get_ulonglong(offset)
        self.atime = self.get_ulonglong(offset + 0x08)
        self.mtime = self.get_ulonglong(offset + 0x10)
        self.rtime = self.get_ulonglong(offset + 0x18)
        self.perm = self.get_uint(offset + 0x20)
        self.versions = self.get_uint(offset + 0x20)
        self.version = self.get_uint(offset + 0x28)
        self.class_id = self.get_uint(offset + 0x2C)
        if (self.size > 0x48):
            self.owner_id = self.get_uint(offset + 0x30)
            self.sec_id = self.get_uint(offset + 0x34)
            self.quata = self.get_ulonglong(offset + 0x38)
            self.usn = self.get_ulonglong(offset + 0x40)

    def ctime_dt(self):
        return time_to_dt(self.ctime)

    def atime_dt(self):
        return time_to_dt(self.atime)

    def mtime_dt(self):
        return time_to_dt(self.mtime)

    def rtime_dt(self):
        return time_to_dt(self.rtime)


class MFTAttrAttributeList(MFTAttr):
    """
        This class represents the attribute list attribute of an MFT entry
    """

    def __init__(self, data):
        MFTAttr.__init__(self, data)
        self.type_str = "$ATTRIBUTE_LIST"


class MFTAttrFilename(MFTAttr):
    """
        This class represents the filename attribute of an 
        MFT entry and contains methods for reading and parsing the attribute data.
    """

    def __init__(self, data):
        MFTAttr.__init__(self, data)
        self.type_str = "$FILE_NAME"

        offset = self.header.size
        self.parent_ref = struct.unpack("<hi", self.data[offset:offset + 6])[0]
        self.ctime = self.get_ulonglong(offset + 0x08)
        self.atime = self.get_ulonglong(offset + 0x10)
        self.mtime = self.get_ulonglong(offset + 0x18)
        self.rtime = self.get_ulonglong(offset + 0x20)
        self.alloc_size = self.get_ulonglong(offset + 0x28)
        self.real_size = self.get_ulonglong(offset + 0x30)
        self.flags = self.get_uint(offset + 0x38)

        self.reparse = self.get_uint(offset + 0x3C)
        self.fnamength = self.get_uchar(offset + 0x40)
        self.fnspace = self.get_uchar(offset + 0x41)
        self.fname = self.get_chunk(
            offset + 0x42, 2 * self.fnamength).decode('utf-16')

    def ctime_dt(self):
        return time_to_dt(self.ctime)

    def atime_dt(self):
        return time_to_dt(self.atime)

    def mtime_dt(self):
        return time_to_dt(self.mtime)

    def rtime_dt(self):
        return time_to_dt(self.rtime)


class MFTAttrObjectId(MFTAttr):
    def __init__(self, data):
        MFTAttr.__init__(self, data)
        self.type_str = "$OBJECT_ID"


class MFTAttrSecurityDescriptor(MFTAttr):
    def __init__(self, data):
        MFTAttr.__init__(self, data)
        self.type_str = "$SECURITY_DESCRIPTOR"


class MFTAttrVolumeName(MFTAttr):
    def __init__(self, data):
        MFTAttr.__init__(self, data)
        self.type_str = "$VOLUME_NAME"
        offset = self.header.size
        length = self.header.length - self.header.size
        self.vol_name = self.get_chunk(
            offset, 2 * length).decode('utf-16').partition(b'\0')[0]


class MFTAttrVolumeInfo(MFTAttr):
    def __init__(self, data):
        MFTAttr.__init__(self, data)
        offset = self.header.size()
        self.type_str = "$VOLUME_INFORMATION"
        self.major_ver = self.get_uchar(offset + 0x08)
        self.minor_ver = self.get_uchar(offset + 0x09)
        self.flags = self.get_ushort(offset + 0x0A)


class MFTAttrData(MFTAttr):
    def __init__(self, data):
        MFTAttr.__init__(self, data)
        self.type_str = "$DATA"
        offset = self.header.size


class MFTAttrIndexRoot(MFTAttr):
    def __init__(self, data):
        MFTAttr.__init__(self, data)
        self.type_str = "$INDEX_ROOT"


class MFTAttrIndexAllocation(MFTAttr):
    def __init__(self, data):
        MFTAttr.__init__(self, data)
        self.type_str = "$INDEX_ALLOCATION"


class MFTAttrBitmap(MFTAttr):
    def __init__(self, data):
        MFTAttr.__init__(self, data)
        self.type_str = "$BITMAP"


class MFTAttrReparsePoint(MFTAttr):
    def __init__(self, data):
        MFTAttr.__init__(self, data)
        self.type_str = "$REPARSE_POINT"


class MFTAttrLoggedToolstream(MFTAttr):
    def __init__(self, data):
        MFTAttr.__init__(self, data)
        self.type_str = "$LOGGED_UTILITY_STREAM"
