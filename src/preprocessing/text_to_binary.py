def text_to_binary(text):

    binary = ''.join(format(ord(c), '08b') for c in text)

    return binary