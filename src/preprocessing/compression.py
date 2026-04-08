import zlib

def compress_text(text):

    compressed = zlib.compress(text.encode())

    return compressed


def decompress_text(data):

    return zlib.decompress(data).decode()