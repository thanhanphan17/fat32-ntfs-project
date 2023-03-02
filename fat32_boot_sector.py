class BootSector:
    # Init to load boot sector with disk is name of disk fat32 type
    def __init__(self, disk):
        self.__disk = r"\\." + f"\{disk}:"

    def __read(self):
        with open(self.__disk, 'rb') as f:
            # Read the first sector, which is the boot sector
            boot_sector = f.read(512)

        return boot_sector

    def showInfo(self):
        boot_sector = self.__read()

        fat_type = boot_sector[82:90].decode('utf-8')
        bytes_per_sector = int.from_bytes(
            boot_sector[11:13], byteorder='little')
        sectors_per_cluster = int.from_bytes(
            boot_sector[13:14], byteorder='little')
        reserved_sectors = int.from_bytes(
            boot_sector[14:16], byteorder='little')
        num_fats = int.from_bytes(boot_sector[16:17], byteorder='little')
        total_sectors = int.from_bytes(boot_sector[32:36], byteorder='little')
        fat_size_sectors = int.from_bytes(
            boot_sector[36:40], byteorder='little')

        volumes_size = int.from_bytes(boot_sector[32:36], byteorder='little')

        print(f'Fat type: {fat_type}')
        print(f'Bytes per sector: {bytes_per_sector}')
        print(f'Sectors per cluster: {sectors_per_cluster}')
        print(f'Reserved sectors: {reserved_sectors}')
        print(f'Number of FATs: {num_fats}')
        print(f'Total sectors: {total_sectors}')
        print(f'FAT size (in sectors): {fat_size_sectors}')
        print(f'Volumes size: {volumes_size}')


# Open the disk or file in binary mode
BSFat32 = BootSector('E')

BSFat32.showInfo()
