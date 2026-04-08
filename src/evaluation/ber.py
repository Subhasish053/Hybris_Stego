def calculate_ber(original_bits, extracted_bits):

    errors = 0

    for a, b in zip(original_bits, extracted_bits):
        if a != b:
            errors += 1

    return errors / len(original_bits)