import sys


class IdxEditor:
    f = None
    hashlist = []
    pathlist = []
    sizelist = []

    def __init__(self, path):
        try:
            self.f = open(path, mode='rb')  # use binary mode to avoid mess with encodings
        except IOError:
            print('[IdxEditorInit]Open file failed!')
            sys.exit()
        self.load_lists()

    def __del__(self):
        self.f.close()

    def load_lists(self):
        self.f.seek(0)
        # version 3 decoded line: (hash)\x09(path)\x09(size)\x0a
        linepos = 0
        tmp = b''
        while True:
            nextchar = self.f.read(1)
            if nextchar == b'\x0a':  # next line
                if not linepos == 2:
                    print('[IdxLoadList]Malformed index at position {}!'.format(self.f.tell()))
                    sys.exit()
                linepos = 0
                self.sizelist.append(tmp)
                tmp = b''
            elif nextchar == b'\x09':  # same line
                if linepos == 0:
                    self.hashlist.append(tmp)
                    linepos = 1
                elif linepos == 1:
                    self.pathlist.append(tmp)
                    linepos = 2
                else:
                    print('[IdxLoadList]Malformed index at position {}!'.format(self.f.tell()))
                    sys.exit()
                tmp = b''
            else:
                tmp = tmp + nextchar

            if not nextchar:
                break

        if not tmp == b'':
            print('[IdxLoadList]Malformed index at EOF position{}!'.format(self.f.tell()))
            sys.exit()

        hashcount = len(self.hashlist)
        pathcount = len(self.pathlist)
        sizecount = len(self.sizelist)

        if not hashcount == pathcount == sizecount:
            print('[IdxLoadList]IDX decoded lines count mismatch! {}, {}, {}'.format(hashcount, pathcount, sizecount))
            sys.exit()

        print('[IdxLoadList]{} lines loaded.'.format(hashcount))

    def get_path_by_hash(self, sha1hash):
        for i in range(len(self.hashlist)):
            if self.hashlist[i] == sha1hash:
                print('[IdxGetPathByHash]Found path {} for hash {} at position {}.'
                      .format(self.pathlist[i], sha1hash, i))
                return self.pathlist[i]
        return None

    def get_size_by_hash(self, sha1hash):
        for i in range(len(self.hashlist)):
            if self.hashlist[i] == sha1hash:
                print('[IdxGetSizeByHash]Found size {} for hash {} at position {}.'
                      .format(self.sizelist[i], sha1hash, i))
                return self.sizelist[i]
        return None

    def get_hash_by_path(self, path):
        for i in range(len(self.pathlist)):
            if self.pathlist[i] == path:
                print('[IdxGetHashByPath]Found hash {} for path {} at position {}.'
                      .format(self.hashlist[i], path, i))
                return self.hashlist[i]
        return None

    def get_size_by_path(self, path):
        for i in range(len(self.pathlist)):
            if self.pathlist[i] == path:
                print('[IdxGetSizeByPath]Found size {} for path {} at position {}.'
                      .format(self.sizelist[i], path, i))
                return self.sizelist[i]
        return None

    def set_path_by_hash(self, sha1hash, path):
        for i in range(len(self.hashlist)):
            if self.hashlist[i] == sha1hash:
                print('[IdxSetPathByHash]Set path {} -> {} for hash {} at position {}.'
                      .format(self.pathlist[i], path, sha1hash, i))
                self.pathlist[i] = path
                return True
        return False

    def set_size_by_hash(self, sha1hash, size):
        for i in range(len(self.hashlist)):
            if self.hashlist[i] == sha1hash:
                print('[IdxSetSizeByHash]Set size {} -> {} for hash {} at position {}.'
                      .format(self.sizelist[i], size, sha1hash, i))
                self.sizelist[i] = size
                return True
        return False

    def set_hash_by_path(self, path, sha1hash):
        for i in range(len(self.pathlist)):
            if self.pathlist[i] == path:
                print('[IdxSetHashByPath]Set hash {} -> {} for path {} at position {}.'
                      .format(self.hashlist[i], sha1hash, path, i))
                self.hashlist[i] = sha1hash
                return True
        return False

    def set_size_by_path(self, path, size):
        for i in range(len(self.pathlist)):
            print(i)
            if self.pathlist[i] == path:
                print('[IdxSetSizeByPath]Set size {} -> {} for path {} at position {}.'
                      .format(self.sizelist[i], size, path, i))
                self.sizelist[i] = size
                return True
        return False

    def exchange_by_path(self, path1, path2):
        hash1 = self.get_hash_by_path(path1)
        hash2 = self.get_hash_by_path(path2)
        if hash1 is None or hash2 is None:
            print("[IdxExchangeByPath]Fail to find one or both of the files' hash: {}, {}"
                  .format(path1, path2))
            return False
        tmp1 = self.set_path_by_hash(hash1, path2)
        tmp2 = self.set_path_by_hash(hash2, path1)
        if tmp1 is True and tmp2 is True:
            print("[IdxExchangeByPath]Hash exchanged successfully. {} <--> {}"
                  .format(path1, path2))
            return True
        print("[IdxExchangeByPath]Set path failed!")
        return False

    def remove_by_path(self, path):
        for i in range(len(self.pathlist)):
            if self.pathlist[i] == path:
                print('[IdxRemoveByPath]{} -> position {}, removed.'
                      .format(path, i))
                self.hashlist.pop(i)
                self.pathlist.pop(i)
                self.sizelist.pop(i)
                return True
        return False

    def append(self, sha1hash, path, size):
        self.hashlist.append(sha1hash)
        self.pathlist.append(path)
        self.sizelist.append(size)
        print('[IdxAppend]Done.')

    def output(self, path):
        hashcount = len(self.hashlist)
        pathcount = len(self.pathlist)
        sizecount = len(self.sizelist)

        if not hashcount == pathcount == sizecount:
            print('[IdxEditorOutput]IDX decoded lines count mismatch! {}, {}, {}'
                  .format(hashcount, pathcount, sizecount))
            return False

        try:
            outfile = open(path, mode='wb')
        except IOError:
            print('[IdxEditorOutput]Open file for output failed!')
            return False

        for i in range(hashcount):
            outfile.write(self.hashlist[i])
            outfile.write(b'\x09')
            outfile.write(self.pathlist[i])
            outfile.write(b'\x09')
            outfile.write(self.sizelist[i])
            outfile.write(b'\x0a')

        print('[IdxEditorOutput]{} lines written.'.format(hashcount))
        return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Please specify decoded idx file to test with...')
    else:
        idx = IdxEditor(sys.argv[1])
        # do something evil
        tmp01 = idx.exchange_by_path(b'data/tables/locale/vi.tab', b'data/tables/locale/zh_MYSG.tab')
        tmp02 = idx.exchange_by_path(b'data/caches/locale_vi.new_cache', b'data/caches/locale_zh_MYSG.new_cache')
        tmp03 = idx.get_hash_by_path(b'asset/interface/Resource/font/Regular.ttf')
        tmp04 = idx.get_size_by_path(b'asset/interface/Resource/font/Regular.ttf')
        if tmp03 and tmp04:
            tmp05 = idx.set_hash_by_path(b'asset/interface/Resource/font/ZhunYuan.TTF', tmp03)
            tmp06 = idx.set_size_by_path(b'asset/interface/Resource/font/ZhunYuan.TTF', tmp04)
        if tmp01 is True and tmp02 is True and tmp05 is True and tmp06 is True:
            idx.output(sys.argv[1] + '.new')
