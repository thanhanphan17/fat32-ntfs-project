import win32api

# ntfs boot sector (also called VBR): 512 bytes
class PartitionBootSector:
    def __init__(self, disk):
        self.__disk = r"\\." + f"\{disk}:"

    def __read(self):
        with open(self.__disk, "rb") as f:
            boot_sector = f.read(512)
            return boot_sector

    def showInfo(self):
        boot_sector = self.__read()

        # inside boot sector:
        # offset 0->3: jump instruction
        # offset 3->11: OEM ID (Original Equipment Manufacturer Identification?)
        # offset 11->36: BPB (BIOS parameter block)
        # offset 36->84: Extended BPB
        # offset 84->510: Bootstrap Code
        # offset 510->512: End of Sector Marker
        jump_instruction = boot_sector[0:3]
        oem_id = boot_sector[3:11]
        bpb = boot_sector[11:36]
        extended_bpb = boot_sector[36:84]
        bootstrap_code = boot_sector[84:510]
        end_of_sector_marker = boot_sector[510:512]

        print("OEM ID:  " + oem_id.decode("utf-8"))
        
        # inside BPB and Extended BPB (offset 11->84):
        bytes_per_sector = int.from_bytes(
            boot_sector[11:13], byteorder="little")

        sectors_per_cluster = int.from_bytes(
            boot_sector[13:14], byteorder="little")

        reserved_sectors = int.from_bytes(
            boot_sector[14:16], byteorder="little")

        media_descriptor = int.from_bytes(
            boot_sector[21:22], byteorder="little")

        sectors_per_track = int.from_bytes(
            boot_sector[24:26], byteorder="little")

        number_of_heads = int.from_bytes(
            boot_sector[26:28], byteorder="little")

        hidden_sectors = int.from_bytes(
            boot_sector[28:32], byteorder="little")

        total_sectors = int.from_bytes(
            boot_sector[40:48], byteorder="little")

        logical_cluster_number_for_the_file_MFT = int.from_bytes(
            boot_sector[48:56], byteorder="little")

        logical_cluster_number_for_the_file_MFTMirr = int.from_bytes(
            boot_sector[56:64], byteorder="little")

        clusters_per_file_record_segment = int.from_bytes(
            boot_sector[64:68], byteorder="little")

        clusters_per_index_buffer = int.from_bytes(
            boot_sector[68:69], byteorder="little")

        volume_serial_number = int.from_bytes(
            boot_sector[72:80], byteorder="big")     

        checksum = int.from_bytes(
            boot_sector[80:84], byteorder="little")
        
        print("Bytes Per Sector:  " + str(bytes_per_sector))
        print("Sectors Per Cluster:  " + str(sectors_per_cluster))
        print("Reserved Sectors:  " + str(reserved_sectors))
        print("Media Descriptor:  " + str(media_descriptor))
        print("Sectors Per Track:  " + str(sectors_per_track))
        print("Number Of Heads:  " + str(number_of_heads))
        print("Hidden Sectors:  " + str(hidden_sectors))
        print("Total Sectors:  " + str(total_sectors))
        print("Logical Cluster Number for the file $MFT:  " + str(logical_cluster_number_for_the_file_MFT))
        print("Logical Cluster Number for the file $MFTMirr:  " + str(logical_cluster_number_for_the_file_MFTMirr))
        print("Clusters Per File Record Segment:  " + str(clusters_per_file_record_segment))
        print("Clusters Per Index Buffer:  " + str(clusters_per_index_buffer))
        print("Volume Serial Number:  " + str(hex(volume_serial_number)))
        print("Checksum:  " + str(checksum))

drives = win32api.GetLogicalDriveStrings()
drives = drives.strip(":\\\x00")
print(drives)

selected_drive = input("Select: ")
PBS = PartitionBootSector(selected_drive)
PBS.showInfo()
