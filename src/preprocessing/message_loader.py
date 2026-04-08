def load_text_dataset(path):

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    return text


def split_into_chunks(text, chunk_size=500):

    chunks = []

    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i+chunk_size])

    return chunks