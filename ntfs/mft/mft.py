from ntfs.mft.property import Property
from ntfs.helper import time_to_dt

from ntfs.mft.entry import *
from ntfs.mft.config import *


class MFT:
    def __init__(self, entry_size=1024, offset=None, filename=None):
        self.offset = offset
        self.entry_size = entry_size
        self.filename = filename
        self.entries = [filename]

    def get_entry(self, entry_id):
        entry_offset = entry_id * self.entry_size
        self.entry = MFTEntry(filename=self.filename, offset=self.offset +
                              entry_offset, length=self.entry_size, index=entry_id)

        if str(self.entry.header.file_signature)[2:6] != "FILE":
            return False

        self.entries.append(self.entry)
        return True

    def load_entries(self):
        n = 0
        while (self.get_entry(n)):
            n += 1
