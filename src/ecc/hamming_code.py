def encode_hamming(data_bits):

    encoded = []

    for i in range(0, len(data_bits), 4):

        block = data_bits[i:i+4]

        if len(block) < 4:
            block = block.ljust(4, '0')

        d1,d2,d3,d4 = [int(b) for b in block]

        p1 = d1 ^ d2 ^ d4
        p2 = d1 ^ d3 ^ d4
        p3 = d2 ^ d3 ^ d4

        encoded.extend([p1,p2,d1,p3,d2,d3,d4])

    return ''.join(map(str,encoded))


def decode_hamming(bits):

    decoded = []

    for i in range(0, len(bits), 7):

        block = bits[i:i+7]

        if len(block) < 7:
            continue

        b = list(map(int, block))

        p1,p2,d1,p3,d2,d3,d4 = b

        c1 = p1 ^ d1 ^ d2 ^ d4
        c2 = p2 ^ d1 ^ d3 ^ d4
        c3 = p3 ^ d2 ^ d3 ^ d4

        error_pos = c1 + c2*2 + c3*4

        if error_pos != 0:
            b[error_pos-1] ^= 1

        decoded.extend([b[2],b[4],b[5],b[6]])

    return ''.join(map(str,decoded))