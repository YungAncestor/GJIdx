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


if __name__ == '__main__':
    print("Oodle helper!")
