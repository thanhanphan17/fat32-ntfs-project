"""
    Partion Boot Sector 

    PartitionBootSector class , which is used to extract 
    information from the partition boot sector of a given disk.
    The class takes the disk name as an input parameter and 
    reads the first 512 bytes of the disk. It then extracts various pieces of
    information from the boot sector and stores them as instance variables.
"""


class PartitionBootSector:
    def __init__(self, disk):
        self.__disk = r"\\." + f"\{disk}:"
        self.boot_sector = self.__read()
        self.__calcInfo()

    def __read(self):
        with open(self.__disk, "rb") as f:
            boot_sector = f.read(512)
            return boot_sector

    def __calcInfo(self):
        """
            __calcInfo() method uses byte offsets to extract
            specific information from the boot sector
        """


        """
            inside boot sector:
            offset 0->3: jump instruction
            offset 3->11: OEM ID (Original Equipment Manufacturer Identification?)
            offset 11->36: BPB (BIOS parameter block)
            offset 36->84: Extended BPB
            offset 84->510: Bootstrap Code
            offset 510->512: End of Sector Marker
        """

        jump_instruction = self.boot_sector[0:3]
        bpb = self.boot_sector[11:36]
        extended_bpb = self.boot_sector[36:84]
        bootstrap_code = self.boot_sector[84:510]
        end_of_sector_marker = self.boot_sector[510:512]

        self.oem_id = self.boot_sector[3:11]

        # inside BPB and Extended BPB (offset 11->84):
        self.bytes_per_sector = int.from_bytes(
            self.boot_sector[11:13], byteorder="little")

        self.sectors_per_cluster = int.from_bytes(
            self.boot_sector[13:14], byteorder="little")

        self.reserved_sectors = int.from_bytes(
            self.boot_sector[14:16], byteorder="little")

        self.media_descriptor = int.from_bytes(
            self.boot_sector[21:22], byteorder="little")

        self.sectors_per_track = int.from_bytes(
            self.boot_sector[24:26], byteorder="little")

        self.number_of_heads = int.from_bytes(
            self.boot_sector[26:28], byteorder="little")

        self.hidden_sectors = int.from_bytes(
            self.boot_sector[28:32], byteorder="little")

        self.total_sectors = int.from_bytes(
            self.boot_sector[40:48], byteorder="little")

        self.logical_cluster_number_for_the_file_MFT = int.from_bytes(
            self.boot_sector[48:56], byteorder="little")

        self.logical_cluster_number_for_the_file_MFTMirr = int.from_bytes(
            self.boot_sector[56:64], byteorder="little")

        self.clusters_per_file_record_segment = int.from_bytes(
            self.boot_sector[64:68], byteorder="little")

        self.clusters_per_index_buffer = int.from_bytes(
            self.boot_sector[68:69], byteorder="little")

        self.volume_serial_number = int.from_bytes(
            self.boot_sector[72:80], byteorder="big")

        self.checksum = int.from_bytes(
            self.boot_sector[80:84], byteorder="little")

    def getPBSInfo(self):
        """
            getPBSInfo() returns a formatted string containing the extracted information
        """

        infoStr = ""

        infoStr += "OEM ID:  " + self.oem_id.decode("utf-8")
        infoStr += "\nBytes Per Sector:  " + str(self.bytes_per_sector)
        infoStr += "\nSectors Per Cluster:  " + str(self.sectors_per_cluster)
        infoStr += "\nReserved Sectors:  " + str(self.reserved_sectors)
        infoStr += "\nMedia Descriptor:  " + str(self.media_descriptor)
        infoStr += "\nSectors Per Track:  " + str(self.sectors_per_track)
        infoStr += "\nNumber Of Heads:  " + str(self.number_of_heads)
        infoStr += "\nHidden Sectors:  " + str(self.hidden_sectors)
        infoStr += "\nTotal Sectors:  " + str(self.total_sectors)
        infoStr += "\nLogical Cluster Number for the file $MFT:  " + \
            str(self.logical_cluster_number_for_the_file_MFT)
        infoStr += "\nLogical Cluster Number for the file $MFTMirr:  " + \
            str(self.logical_cluster_number_for_the_file_MFTMirr)
        infoStr += "\nClusters Per File Record Segment:  " + \
            str(self.clusters_per_file_record_segment)
        infoStr += "\nClusters Per Index Buffer:  " + \
            str(self.clusters_per_index_buffer)
        infoStr += "\nVolume Serial Number:  " + \
            str(hex(self.volume_serial_number))
        infoStr += "\nChecksum:  " + str(self.checksum)

        return infoStr

    def get_mft_offset(self):
        """
            get_mft_offset() calculates the offset of the Master File Table on the disk
        """
        return self.bytes_per_sector * (self.sectors_per_cluster *
                                        self.logical_cluster_number_for_the_file_MFT + 78)
