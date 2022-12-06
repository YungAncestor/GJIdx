import sys


class ZFS:
    f = None
    hashes = []
    sizes = []
    offsets = []
    flags = []

    def __init__(self, path):
        try:
            self.f = open(path, mode='rb')
        except IOError:
            print('Open file failed!')
            sys.exit()
        self.load_file()

    def __del__(self):
        self.f.close()

    def load_file(self):
        # Reads from dataXXX zfs file.
        self.f.seek(0)
        self.hashes = []
        self.sizes = []
        self.offsets = []
        self.flags = []
        zfs_header = self.f.read(4)
        if zfs_header != b'\x5a\x46\x53\x00':
            # "ZFS\x00"
            print("[ZFSLoadFile]Bad ZFS Header!")
            sys.exit()
        while True:
            zfile_header = self.f.read(4)
            if zfile_header != b'\x5b\x49\x58\x5d':
                # "[IX]"
                print("[ZFSLoadFile]Bad ZFS Chunk Header! Position: {}".format(self.f.tell()))
                sys.exit()
            next_chunk = int.from_bytes(self.f.read(4), byteorder='little')
            for i in range(0x1000):
                # 0x1000 is hardcoded count of files per chunk
                this_hash = self.f.read(20).hex()
                this_offset = int.from_bytes(self.f.read(4), byteorder='little')
                this_size = int.from_bytes(self.f.read(4), byteorder='little')
                this_checksum = int.from_bytes(self.f.read(2), byteorder='little')
                this_dummy = int.from_bytes(self.f.read(1), byteorder='little')
                this_flag = int.from_bytes(self.f.read(1), byteorder='little')
                if this_offset == 0:
                    continue
                if DEBUG:
                    print("[ZFSLoadFile][{}]Hash:{}, offset:{}, size:{}, checksum:{}, "
                          "unknown:{}, flag:{}. Next chunk:{}"
                          .format(self.f.tell(), this_hash, this_offset, this_size, this_checksum,
                                  this_dummy, this_flag, next_chunk))

                self.hashes.append(this_hash)
                self.offsets.append(this_offset)
                self.sizes.append(this_size)
                # loop end, go to next file in this trunk

            if next_chunk == 0:
                if DEBUG:
                    print("[ZFSLoadFile]{} valid files loaded.".format(len(self.hashes)))
                break
            self.f.seek(next_chunk)

    def check_hash(self, myhash):
        for i in range(len(self.hashes)):
            if self.hashes[i] == myhash:
                return True
        return False

    def get_pos_by_hash(self, myhash):
        for i in range(len(self.hashes)):
            # start from 0
            if self.hashes[i] == myhash:
                return i
        # return total count if not found because 0 is the first file
        return self.get_file_count()

    def get_size_by_hash(self, myhash):
        for i in range(len(self.hashes)):
            if self.hashes[i] == myhash:
                return self.sizes[i]
        return 0

    def get_file_count(self):
        return len(self.hashes)

    def get_file_content_by_hash(self, myhash):
        for i in range(len(self.hashes)):
            if self.hashes[i] == myhash:
                self.f.seek(self.offsets[i])
                return self.f.read(self.sizes[i])
        return None


DEBUG = False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Bad parameters. To test this script with a dataXXX zfs file, use: ZFSHelper.py <path_to_dataXXX> [hash]')
    else:
        DEBUG = True
        myzfs = ZFS(sys.argv[1])
        print(myzfs.get_file_count())
        if len(sys.argv) > 2:
            print(myzfs.check_hash(sys.argv[2]))
            print(myzfs.get_pos_by_hash(sys.argv[2]))
            print(myzfs.get_size_by_hash(sys.argv[2]))
            # print(myzfs.get_file_content_by_hash(sys.argv[2]))
