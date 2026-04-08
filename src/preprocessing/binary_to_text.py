def binary_to_text(binary):

    chars = []

    for i in range(0, len(binary) - 7, 8):

        byte = binary[i:i+8]

        chars.append(chr(int(byte, 2)))

    return ''.join(chars)