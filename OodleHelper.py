import ctypes


def decompress_chunk(data, decodesize):
    lib = ctypes.CDLL('oo2core_6_win64.dll')

    buffer = ctypes.create_string_buffer(decodesize)
    realsize = lib.OodleLZ_Decompress(data, len(data), buffer, decodesize,
                                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    if realsize == 0:
        print("[OodleHelper]ERROR: Decompress failed.")
        return None

    if not realsize == decodesize:
        print("[OodleHelper]Warning: Decompressed size mismatch. {} expected, got {}.".format(decodesize, realsize))

    return buffer[:realsize]


def compress_chunk(data):
    lib = ctypes.CDLL('oo2core_6_win64.dll')
    buffer_size = lib.OodleLZ_GetCompressedBufferSizeNeeded(len(data))
    buffer = ctypes.create_string_buffer(buffer_size)
    realsize = lib.OodleLZ_Compress(8, data, len(data), buffer, 1, None, None, None, None, 0)
    if realsize == 0:
        print("[OodleHelper]ERROR: Compress failed.")
        return None

    return buffer[:realsize]


if __name__ == '__main__':
    print("Oodle helper!")
