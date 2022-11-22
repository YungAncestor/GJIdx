import lzma
import math
import sys
import time
import hashlib


class IdxBuilder:
    f = None
    size = 0
    timestamp = 0
    compressedsize = 0
    chunklen = 524288
    idxver = 3
    checksum = 0
    chunkoffset = []
    chunknum = 0
    datastart = 0
    bodysize = 0
    idxbody = b''
    idxheader = b''

    def __init__(self, path):
        try:
            self.f = open(path, mode='rb')
        except IOError:
            print('Open file failed!')
            sys.exit()
        # get file size
        self.size = len(self.f.read())
        # set file pointer to beginning
        self.f.seek(0)
        self.timestamp = int(time.time())
        self.chunknum = math.ceil(self.size / self.chunklen)
        self.build_body()
        self.build_header()
        self.print_header()


    def __del__(self):
        self.f.close()

    def build_body(self):
        pseudoheader = b'\x5d\x00\x00\x08\x00'
        for i in range(0, self.chunknum):
            # lzma compress (idxver 3)
            tmp = lzma.compress(self.f.read(self.chunklen), format=lzma.FORMAT_ALONE, preset=1)
            # remove lzma header & add pseudo header
            tmp = tmp[13:]
            tmp = pseudoheader + tmp
            # get chunk compressed size
            self.chunkoffset.append(len(tmp))
            print("[IdxBuildChunk]ChunkID: {}, CompressedSize: {}"
                  .format(i, len(tmp)))
            # append to idx body
            self.idxbody = self.idxbody + tmp

        # calculate compressed length
        self.bodysize = len(self.idxbody)
        print("[IdxBuildBody]IdxBodyLength: {}".format(self.bodysize))

    def build_header(self):
        # chunk offsets
        chunkindex = b''
        for i in range(0, self.chunknum):
            chunkindex = chunkindex + int.to_bytes(self.chunkoffset[i], byteorder='little', length=4)

        self.compressedsize = len(self.idxbody) + len(chunkindex) + 32
        # build header
        self.idxheader = int.to_bytes(self.size, byteorder='little', length=8)
        self.idxheader = self.idxheader + int.to_bytes(self.timestamp, byteorder='little', length=8)
        self.idxheader = self.idxheader + int.to_bytes(self.compressedsize, byteorder='little', length=8)
        self.idxheader = self.idxheader + int.to_bytes(self.chunklen, byteorder='little', length=4)
        self.idxheader = self.idxheader + int.to_bytes(self.idxver, byteorder='little', length=2)

        # calculate the crc16 checksum
        self.checksum = crc16_ccitt(self.idxheader)
        self.idxheader = self.idxheader + int.to_bytes(self.checksum, byteorder='big', length=2)

        self.idxheader = self.idxheader + chunkindex
        self.datastart = len(self.idxheader)
        print("[IdxBuildHeader]IdxHeaderLength: {}".format(self.datastart))

    def print_header(self):
        print("[IdxHeader]Size:{}, Timestamp:{}, CompressedSize:{}, ChunkLen:{}, IdxVer:{}, Checksum:{}, ChunkNum:{}"
              .format(self.size, self.timestamp, self.compressedsize, self.chunklen, self.idxver, self.checksum,
                      self.chunknum))

    def get_sha1_hash(self):
        return hashlib.sha1(self.idxheader + self.idxbody).hexdigest()

    def output(self, path):
        try:
            outfile = open(path, mode='wb')
        except IOError:
            print('Open file for output failed!')
            return False

        outfile.write(self.idxheader + self.idxbody)
        return True


def crc16_ccitt(bytestr):
    data = bytearray(bytestr)
    crc = 0x0000
    for pos in data:
        crc ^= pos
        for i in range(8):
            if (crc & 1) != 0:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return ((crc & 0xff) << 8) + (crc >> 8)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Bad parameters. Usage: GJIdxEnc.py <input_file> [output_file]')
    else:
        idx = IdxBuilder(sys.argv[1])
        if len(sys.argv) < 3:
            idx.output(idx.get_sha1_hash())
        else:
            idx.output(sys.argv[2])
