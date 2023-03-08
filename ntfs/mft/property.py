from ntfs.mft.config import *

class Property(object):
    def __init__(self, data=None, offset=None, length=None, filename=None):
        if offset is None:
            offset = 0
        if data is not None:
            if length is None:
                self.data = data[offset:]
            else:
                self.data = data[offset:offset + length]
        elif filename is not None:
            with open(filename, 'rb') as f:
                f.seek(offset)
                if length is None:
                    self.data = f.read()
                else:
                    self.data = f.read(length)
                        
    @property
    def size(self):
        return len(self.data)
    
    def data(self):
        return self.data
   
    def get_chunk(self, offset, length):
        return self.data[offset:offset+length]
    
    def get_uchar(self, offset):
        return struct.unpack("B", self.data[offset:offset + 1])[0]
    
    def get_char(self, offset):
        return struct.unpack("b", self.data[offset:offset + 1])[0]
    
    def get_ushort(self, offset):
        return struct.unpack("<H", self.data[offset:offset + 2])[0]
    
    def get_uint(self, offset):
        return struct.unpack("<I", self.data[offset:offset + 4])[0]
    
    def get_ulonglong(self, offset):
        return struct.unpack("<Q", self.data[offset:offset + 8])[0]
    
    def get_ulonglong_b(self, offset):
        return struct.unpack(">Q", self.data[offset:offset + 8])[0]
    
    def get_string(self, offset, length):
        return struct.unpack(str(length) + "s", self.data[offset:offset + length])[0]
