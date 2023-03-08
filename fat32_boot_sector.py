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
        print(f'Fat type: {self.fat_type}')
        print(f'Bytes per sector: {self.bytes_per_sector}')
        print(f'Sectors per cluster: {self.sectors_per_cluster}')
        print(f'Reserved sectors: {self.reserved_sectors}')
        print(f'Number of FATs: {self.num_fats}')
        print(f'FAT size (in sectors): {self.fat_size_sectors}')
        print(f'Volumes size: {self.volumes_size}')
        print(f'Total sectors: {self.total_sectors}')
        with open(self.__disk, 'rb') as f:
            # Read the first sector, which is the boot sector
            boot_sector = f.read(self.rdet_first_sector + 32 * 20)
    

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


        
