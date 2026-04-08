def encode_repetition(bits, n=3):

    encoded = ""

    for bit in bits:
        encoded += bit * n

    return encoded


def decode_repetition(bits, n=3):

    decoded = ""

    for i in range(0, len(bits), n):

        block = bits[i:i+n]

        valid_bits = [b for b in block if b != "X"]

        if not valid_bits:
            decoded += "0"
        elif valid_bits.count("1") > valid_bits.count("0"):
            decoded += "1"
        else:
            decoded += "0"

    return decoded