from fat32_boot_sector import *
import datetime

# some const values
ENTRY_SIZE = 32

# entry's status
EMPTY_ENTRY = 0x00
DELETED_ENTRY = 0xE5

# file's attribute
ARCHIVE = 0x20
DIRECTORY = 0x10
VOL_LABEL = 0x08
SYSTEM = 0x04
HIDDEN = 0x02
READ_ONLY = 0x01
SUB_ENTRY = 0x0F

# set formated time
def byteToBits(value, start_index, bit_cnt):
    return (value & (2 ** start_index - 1)) >> (start_index - bit_cnt)

def getDateTimeFromDosTime(dos_date, dos_time, dos_tenth_of_second):
    created_year = byteToBits(dos_date, 16, 7) + 1980
    created_month = byteToBits(dos_date, 9, 4)
    created_day = byteToBits(dos_date, 5, 5)
    created_hour = byteToBits(dos_time, 16, 5)
    created_minute = byteToBits(dos_time, 11, 6)
    created_second = int(byteToBits(dos_time, 5, 5) * 2 + dos_tenth_of_second / 100)
    creatied_milisecond = (dos_tenth_of_second % 100) * 10000
    return datetime.datetime(created_year, created_month, created_day, created_hour, created_minute, created_second, creatied_milisecond)


# build directory
class Entry:
    def __init__(self, parent_path, disk, starting_sector, index, fat):
        # detect position
        self.status = None
        self.disk = disk
        self.path = parent_path
        self.fat = fat

        # File's information
        self.name = None
        self.extensions_name = None
        self.attribute = None
        self.created_time = None
        self.last_accessed_date = None
        self.last_modified_time = None
        self.size = None
        self.starting_cluster = None
        self.cluster_count = None
        self.starting_sector = None
        self.sector_count = None
        self.content = None
        self.sub_entries = []
        self.children = []
        self.__readInfo(starting_sector, index)


    def __readInfo(self, starting_sector, index):
        # Read entry's data
        entry = getSectorData(self.disk, starting_sector, index)

        # find starting byte of entry
        starting_byte = index * ENTRY_SIZE

        # Read information from collected data
        self.status = int.from_bytes(entry[starting_byte : starting_byte + 1], byteorder='little')
        try:
            if self.status == DELETED_ENTRY:
                self.name = entry[starting_byte + 1 : starting_byte + 8].decode('utf-8')
            else:
                self.name = entry[starting_byte : starting_byte + 8].decode('utf-8')
        except:
            pass
    
        try:
            self.extensions_name = entry[starting_byte + 8 : starting_byte + 11].decode('utf-8')
        except:
            pass
        self.attribute = int.from_bytes(entry[starting_byte + 11 : starting_byte + 12], byteorder='little')
        self.size = int.from_bytes(entry[starting_byte + 28 : starting_byte + 32], byteorder='little')
        
        self.starting_cluster = int.from_bytes(entry[starting_byte + 20 : starting_byte + 22], byteorder='little')
        low_word_starting_cluster = int.from_bytes(entry[starting_byte + 26 : starting_byte + 28], byteorder='little')
        self.starting_cluster = self.starting_cluster << 16 | low_word_starting_cluster
        self.cluster_count = self.fat.getClusterCount(self.starting_cluster)
        self.starting_sector = self.fat.getFirstSector(self.starting_cluster)
        self.sector_count = self.fat.getEntrySectorCount(self.cluster_count)

        created_tenth_of_second = int.from_bytes(entry[starting_byte + 13 : starting_byte + 14], byteorder='little')
        created_time = int.from_bytes(entry[starting_byte + 14 : starting_byte + 16], byteorder='little')
        created_date = int.from_bytes(entry[starting_byte + 16 : starting_byte + 18], byteorder='little')
        last_accessed_date = int.from_bytes(entry[starting_byte + 18 : starting_byte + 20], byteorder='little')
        last_modified_time = int.from_bytes(entry[starting_byte + 22 : starting_byte + 24], byteorder='little')
        last_modified_date = int.from_bytes(entry[starting_byte + 24 : starting_byte + 26], byteorder='little')

        if self.extensions_name == 'txt' or self.extensions_name == 'TXT':
            self.content = self.getTextData()
                                
        try:
            self.created_time = getDateTimeFromDosTime(created_date, created_time, created_tenth_of_second)
            self.last_accessed_date = getDateTimeFromDosTime(last_accessed_date, 0, 0)
            self.last_modified_time = getDateTimeFromDosTime(last_modified_date, last_modified_time, 0)
        except:
            pass     
        

    # checking entry's status, empty or deleted or containing information
    def isDeleted(self):
        if self.status == DELETED_ENTRY:
            return True
        return False
    
    def isEmpty(self):
        if self.status == EMPTY_ENTRY:
            return True
        return False
    
    # get txt file data
    def getTextData(self):
        data = getSectorData(self.disk, self.starting_sector, self.sector_count)
        text = ''
        for index in range(0, int(self.sector_count * 512 / ENTRY_SIZE)):
            if int.from_bytes(data[index * ENTRY_SIZE : index * ENTRY_SIZE + 1], byteorder='little') != DELETED_ENTRY:
                text += data[index * ENTRY_SIZE : (index + 1) * ENTRY_SIZE].decode('utf-8').strip()
            if int.from_bytes(data[index * ENTRY_SIZE : index * ENTRY_SIZE + 1], byteorder='little') == EMPTY_ENTRY:
                return text
        return text


    # set file's full name from sub entries
    def setFullName(self):
        if len(self.sub_entries) == 0:
            self.name = self.name.strip() 
            if self.attribute == ARCHIVE:
                self.name += '.' + self.extensions_name
        else:
            self.name = ''
            for entry in reversed(self.sub_entries):
                self.name += entry.sub_name.strip(b'\xff\xff'.decode('utf-16'))
            self.name = self.name[0 : len(self.name) - 1]

    def setPath(self):
        self.path += f'\{self.name}'


    # get file's attribute
    def getAttribute(self):
        return self.attribute
    
    def getFileName(self):
        return self.name
    
    def getChildrenList(self):
        return self.children


    # get file's information
    def getInfo(self):
        if self.isDeleted() == True:
            return "This file is deleted"
    
        content = ""
        content += "\nPath: " + str(self.path)
        content += "\nName: " + str(self.name)
        content = "\nAttribute: "
        if (self.attribute == READ_ONLY):
            content += "READ ONLY"
        if (self.attribute == HIDDEN):
            content += "HIDDEN"
        if (self.attribute == SYSTEM):
            content += "SYSTEM"
        if (self.attribute == VOL_LABEL):
            content += "VOLUME ID"
        if (self.attribute == DIRECTORY):
            content += "DIRECTORY"
        if (self.attribute == ARCHIVE):
            content += "ARCHIVE"
        try:
            content += "\nCreation time: " + str(self.created_time.strftime('%d.%m.%Y %H:%M:%S:%f'))
            content += "\nLast Accessed time: " + str(self.last_accessed_date.strftime('%d.%m.%Y'))
            content += "\nModification time: " + str(self.last_modified_time.strftime('%d.%m.%Y %H:%M:%S'))
        except:
            pass
        content += "\nFirst cluster: " + str(self.starting_cluster)
        content += "\nNumber of clusters: " + str(self.cluster_count)
        content += "\nFilesize: " + str(self.size) + " (bytes)"
        content += "\nEntry count: " + str(len(self.sub_entries) + 1)
        content += "\n[Start Sector - End Sector]: " + str(self.starting_sector) + " - " + str(self.starting_sector + self.sector_count)
        # content += "\n-------------------"
        # if self.extensions_name == 'txt' or self.extensions_name == 'TXT':
        #     content += "\nContent:"
        #     content += self.content

        # if self.attribute == DIRECTORY:
        #     for child_entry in self.children:
        #         child_entry.showInfo()

        return content
    

    def showInfo(self):
        print(self.path)
        if self.isDeleted() == True:
            print("This file is deleted")
            return
        print("\nName: " + self.name)
        attribute = "\nAttribute: "
        if (self.attribute == READ_ONLY):
            attribute += "READ ONLY"
        if (self.attribute == HIDDEN):
            attribute += "HIDDEN"
        if (self.attribute == SYSTEM):
            attribute += "SYSTEM"
        if (self.attribute == VOL_LABEL):
            attribute += "VOLUME ID"
        if (self.attribute == DIRECTORY):
            attribute += "DIRECTORY"
        if (self.attribute == ARCHIVE):
            attribute += "ARCHIVE"
        print(attribute)
        try:
            print("\nCreation time: " + self.created_time.strftime('%d.%m.%Y %H:%M:%S:%f'))
            print("\nLast Accessed time: " + self.last_accessed_date.strftime('%d.%m.%Y'))
            print("\nModification time: " + self.last_modified_time.strftime('%d.%m.%Y %H:%M:%S'))
        except:
            pass
        print("\nFirst cluster: " + str(self.starting_cluster))
        print("\nNumber of clusters: " + str(self.cluster_count))
        print("\nFilesize: " + str(self.size) + " (bytes)")
        print("\nEntry count: " + str(len(self.sub_entries) + 1))
        print("\n[Start Sector - End Sector]: " + str(self.starting_sector) + " - " + str(self.starting_sector + self.sector_count))
        print("\n-------------------")
        if self.extensions_name == 'txt' or self.extensions_name == 'TXT':
            print("\nContent:")
            print(self.content)

        if self.attribute == DIRECTORY:
            for child_entry in self.children:
                child_entry.showInfo()

        print("###################################################")
        

    


class SubEntry():
    def __init__(self, disk, starting_sector, index):
        # sub entry info
        self.order = None
        self.sub_name = None
        self.attribute = None
        self.__readInfo(disk, starting_sector, index)

    def __readInfo(self, disk, starting_sector, index):
        # Read entry's data
        sub_entry = getSectorData(disk, starting_sector, 1)

        self.order = int.from_bytes(sub_entry[index * ENTRY_SIZE : index * ENTRY_SIZE + 1], byteorder="little")
        self.sub_name = sub_entry[index * ENTRY_SIZE + 1 : index * ENTRY_SIZE + 11].decode('utf-16')
        self.attribute = int.from_bytes(sub_entry[index * ENTRY_SIZE + 11 : index * ENTRY_SIZE + 12], byteorder="little")
        self.sub_name += sub_entry[index * ENTRY_SIZE + 14 : index * ENTRY_SIZE + 26].decode('utf-16')
        self.sub_name += sub_entry[index * ENTRY_SIZE + 28 : index * ENTRY_SIZE + 32].decode('utf-16')

    # get file's attribute
    def getAttribute(self):
        return SUB_ENTRY
    


class Root:
    def __init__(self, disk):
        self.path = f"{disk}:"
        self.disk = disk
        self.boot_sector = BootSector(disk)
        self.fat = FatTable(disk, self.boot_sector)
        self.tmp_sub_entries = []
        self.children = self.readInfo(self.path, self.boot_sector.rdet_first_sector)
        self.readDirectoryChildren(self.children)
        
    def readInfo(self, parent_path, starting_sector):
        index = 1
        directory_tree = []
        while True:
            entry = Entry(parent_path, self.disk, starting_sector, index, self.fat)
            sub_entry = SubEntry(self.disk, starting_sector, index)
            index += 1

            # Check if this entry is empty -> if empty, stop reading entry
            if entry.isEmpty():
                return directory_tree[1 : len(directory_tree)]
                
            # Check if this entry is deleted
            if entry.isDeleted():
                continue

            if entry.getAttribute() == SUB_ENTRY:
                self.tmp_sub_entries.append(sub_entry)
            else:
                entry.sub_entries = self.tmp_sub_entries.copy()
                entry.setFullName()
                entry.setPath()
                self.tmp_sub_entries.clear()
                directory_tree.append(entry)
        
    def readDirectoryChildren(self, root_entry_children):
        for entry in root_entry_children:
            if entry.getAttribute() == DIRECTORY:
                entry.children = self.readInfo(entry.path, entry.fat.getFirstSector(entry.starting_cluster))
                self.readDirectoryChildren(entry.children)
                

    # show details of file 
    def showInfo(self):
        for entry in self.children:
            entry.showInfo()

    def getPropertyFromPath(self, root_directory_children, path):
        property = None
        if path == self.path:
            return "HARD DRIVE"
        for entry in root_directory_children:
            if path == entry.path:
                return entry.getInfo()
            
            if entry.getAttribute() == DIRECTORY:
                property = self.getPropertyFromPath(entry.children, path)
        
        return property
        

    def getChildrenList(self):
        return self.children
    
    def getRoot(self):
        return self
