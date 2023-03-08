# Fat table element's status
FREE = 0x0
BAD = 0x0FFFFFF7
EOF = 0x0FFFFFFF

#
FAT_ELEMENT_SIZE = 4

# get entry in sector
def getSectorData(disk, starting_sector, sector_count):
    with open(r"\\." + f"\{disk}:", 'rb') as f:
        f.seek(starting_sector * 512)
        data = f.read(sector_count * 512)
    return data


class BootSector:

    # Init to load boot sector with disk is name of disk fat32 type
    def __init__(self, disk):
        self.__disk = r"\\." + f"\{disk}:"
        self.fat_type = None
        self.bytes_per_sector = None
        self.sectors_per_cluster = None
        self.reserved_sectors = None
        self.num_fats = None
        self.total_sectors = None
        self.fat_size_sectors = None
        self.volumes_size = None
        self.rdet_first_sector = None
        self.boot_sector = self.__read()


    # Read boot sector
    def __read(self):
        with open(self.__disk, 'rb') as f:
            # Read the first sector, which is the boot sector
            boot_sector = f.read(512)

        # Read all the information from the boot sector
        self.fat_type = boot_sector[82:90].decode('utf-8')
        self.bytes_per_sector = int.from_bytes(boot_sector[11:13], byteorder='little')
        self.sectors_per_cluster = int.from_bytes(boot_sector[13:14], byteorder='little')
        self.reserved_sectors = int.from_bytes(boot_sector[14:16], byteorder='little')
        self.num_fats = int.from_bytes(boot_sector[16:17], byteorder='little')
        self.total_sectors = int.from_bytes(boot_sector[32:36], byteorder='little')
        self.fat_size_sectors = int.from_bytes(boot_sector[36:40], byteorder='little')
        self.volumes_size = int.from_bytes(boot_sector[32:36], byteorder='little')

        # Calculate starting sector of rdet
        self.rdet_first_sector = self.reserved_sectors + self.num_fats * self.fat_size_sectors

        return boot_sector


    # Show informations in boot sector
    def showInfo(self):
        with open(self.__disk, 'rb') as f:
            # Read the first sector, which is the boot sector
            boot_sector = f.read(512)

        info = ""
        info += f'\nJump code: ' + str(hex(int.from_bytes(boot_sector[0 : 3], byteorder='little')))
        info += f'\nOEM ID: ' + str(boot_sector[3 : 11].decode('utf-8'))
        info += f'\nBytes per sector: {self.bytes_per_sector}'
        info += f'\nSectors per cluster (Sc): {self.sectors_per_cluster}'
        info += f'\nReserved sectors: {self.reserved_sectors}'
        info += f'\nNumber of FATs (Nf): {self.num_fats}'
        info += f'\nRoot entry: ' + str(int.from_bytes(boot_sector[17 : 19], byteorder='little'))
        info += f'\nMedia type: ' + str(hex(int.from_bytes(boot_sector[21 : 22], byteorder='little')))
        info += f'\nSectors per track: ' + str(int.from_bytes(boot_sector[24 : 26], byteorder='little'))
        info += f'\nNumber of heads: ' + str(int.from_bytes(boot_sector[26 : 28], byteorder='little'))
        info += f'\nHidden sectors: ' + str(int.from_bytes(boot_sector[28 : 32], byteorder='little'))
        info += f'\nSize of volume (in sectors): {self.volumes_size}'
        info += f'\nTotal sectors: {self.total_sectors}'
        info += f'\nSectors per FAT (Sf): {self.fat_size_sectors}'
        info += f'\nPhysical disk number: ' + str(hex(int.from_bytes(boot_sector[64 : 65], byteorder='little')))
        info += f'\nReserve (for Windows NT): ' + str(int.from_bytes(boot_sector[65 : 66], byteorder='little'))
        info += f'\nBoot signature: ' + str(hex(int.from_bytes(boot_sector[66 : 67], byteorder='little')))
        info += f'\nVolume Serial Number: ' + str(hex(int.from_bytes(boot_sector[67 : 71], byteorder='little')))
        info += f'\nVolume Label: ' + str(boot_sector[71 : 82].decode('utf-8'))
        info += f'\nSystem ID: ' + str(self.fat_type)
        info += f'\nFlags describing the drive: ' + str(int.from_bytes(boot_sector[40 : 42], byteorder='little'))
        info += f'\n\t + FAT version: ' + str(int.from_bytes(boot_sector[42 : 44], byteorder='little'))
        info += f'\n\t + RDET starting cluster: ' + str(int.from_bytes(boot_sector[44 : 48], byteorder='little'))
        info += f'\n\t + File system information sector: ' + str(int.from_bytes(boot_sector[48 : 50], byteorder='little'))
        info += f'\n\t + Backup boot sector position: ' + str(int.from_bytes(boot_sector[50 : 52], byteorder='little'))
        info += f'\n\t + Reserved number: ' + str(int.from_bytes(boot_sector[52 : 64], byteorder='little'))

        return info

    # Calculate the starting byte of a specific sector
    def firstByteOfSector(self, sector):
        return (sector) * self.bytes_per_sector
    
    #
    def getSectorPerCluset(self):
        return self.sectors_per_cluster
    
    def getRdetFirstSector(self):
        return self.rdet_first_sector
    


    
    

class FatTable:
    def __init__(self, disk, boot_sector):
        self.data = None
        self.disk = disk
        self.boot_sector = boot_sector
        self.cluster_list = []
        self.sector_list = []
        self.__readData()
        
    
    def __readData(self):
        self.data = getSectorData(self.disk, self.boot_sector.reserved_sectors, self.boot_sector.fat_size_sectors)

    def getClusterCount(self, starting_cluster):
        with open(r"\\." + f"\{self.disk}:", 'rb') as f:
            # Go to file allocation table (FAT)
            f.seek(self.boot_sector.reserved_sectors * self.boot_sector.bytes_per_sector)
            
            # read the cluster status
            start_position = starting_cluster * FAT_ELEMENT_SIZE
            status = int.from_bytes(self.data[start_position : start_position + FAT_ELEMENT_SIZE], byteorder='little')

            # storing clusters
            cluster_count = 1

            while True:
                status = int.from_bytes(self.data[start_position + status * FAT_ELEMENT_SIZE : start_position + (status + 1) * FAT_ELEMENT_SIZE], byteorder='little')

                if status == BAD:
                    raise Exception("Tried to reach bad cluster - cluster: " + starting_cluster)
                
                if status != FREE and status != EOF and status != BAD:
                    cluster_count += 1

                if status == EOF or status == FREE:
                    return cluster_count
                
    
    # return cluster list 
    def getClustersList(self, starting_cluster):
        return self.cluster_list        
    
    def getFirstSector(self, starting_cluster):
        return self.boot_sector.rdet_first_sector + (starting_cluster - 2) * self.boot_sector.sectors_per_cluster
    
    def getEntrySectorCount(self, cluster_count):
        return cluster_count * self.boot_sector.sectors_per_cluster
    
    # return sector list 
    def getSectorList(self):
        return self.sector_list


        
