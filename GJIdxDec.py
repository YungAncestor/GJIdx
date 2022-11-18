import lzma
import math
import sys


class IdxReader:
    f = None
    size = 0
    timestamp = 0
    compressedsize = 0
    chunklen = 0
    idxver = 0
    checksum = 0
    chunkoffset = []
    chunknum = 0
    datastart = 0

    def __init__(self, path):
        try:
            self.f = open(path, mode='rb')
        except IOError:
            print('Open file failed!')
            sys.exit()
        self.load_header()
        self.print_header()

    def __del__(self):
        self.f.close()

    def load_header(self):
        """
        Read header from idx file.
        dest.Size = reader.ReadInt64();
        dest.Date = reader.ReadInt64(); // (time_t 64 bits)
        dest.CompressedSize = reader.ReadInt64(); // compressed size
        dest.SeekChunkLength = reader.ReadInt32();
        dest.Compression = reader.ReadUInt16();
        ushort crc16 = reader.ReadUInt16();
        """
        self.size = int.from_bytes(self.f.read(8), byteorder='little')
        self.timestamp = int.from_bytes(self.f.read(8), byteorder='little')
        self.compressedsize = int.from_bytes(self.f.read(8), byteorder='little')
        self.chunklen = int.from_bytes(self.f.read(4), byteorder='little')

        # idxver 3 = lzma
        # 0 = no compression (UNTESTED!), 4 = oodle
        self.idxver = int.from_bytes(self.f.read(2), byteorder='little')

        self.checksum = int.from_bytes(self.f.read(2), byteorder='little')
        self.chunknum = math.ceil(self.size / self.chunklen)

        for i in range(0, self.chunknum):
            self.chunkoffset.append(int.from_bytes(self.f.read(4), byteorder='little'))

        self.datastart = self.f.tell()

    def print_header(self):
        print("[IdxHeader]Size:{}, Timestamp:{}, CompressedSize:{}, ChunkLen:{}, IdxVer:{}, Checksum:{}, ChunkNum:{}"
              .format(self.size, self.timestamp, self.compressedsize, self.chunklen, self.idxver, self.checksum,
                      self.chunknum))

    def read_chunk_raw(self, chunkid):
        """
        Read raw data from single chunk
        :param chunkid: chunk id starting from 0
        :return: chunk data
        """
        if chunkid >= self.chunknum:
            return None
        self.f.seek(self.datastart, 0)
        for i in range(0, chunkid):
            self.f.seek(self.chunkoffset[i], 1)
        print("[IdxReadChunkRaw]ChunkID: {}, Offset: {}, CompressedSize: {}".format(chunkid, self.f.tell(), self.chunkoffset[chunkid]))
        return self.f.read(self.chunkoffset[chunkid])

    def fix_lzma_header(self, rawdata):
        """
        Fix LZMA Header for compressed chunk data.
        :param rawdata: chunk data
        :return: decompressable lzma data
        """
        if not self.idxver == 3:
            print("Unsupported idx version {}!".format(self.idxver))
            return rawdata
        header = b'\x5D\x00\x00\x08\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'
        rawdata = rawdata[5:]
        return header + rawdata

    def decompress_all(self):
        """
        Decompress the idx using LZMA (idxver 3 only)
        :return: decompressed data if supported
        """
        if not self.idxver == 3:
            print("Unsupported idx version {}!".format(self.idxver))
            return None

        # read all chunk data, add headers and decompress
        # then join all decompressed data.
        tmp = b''
        for i in range(0, self.chunknum):
            tmp = tmp + lzma.decompress(self.fix_lzma_header(self.read_chunk_raw(i)))

        return tmp

    def output(self, path):
        try:
            outfile = open(path, mode='xb')
        except IOError:
            print('Open file for output failed!')
            return

        outfile.write(self.decompress_all())


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Bad parameters. Usage: GJIdxDec.py <path_to_idx> [output_file]')
    else:
        idx = IdxReader(sys.argv[1])
        if len(sys.argv) < 3:
            idx.output(sys.argv[1] + ".txt")
        else:
            idx.output(sys.argv[2])
