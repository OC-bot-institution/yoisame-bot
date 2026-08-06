from sudachipy import Dictionary

tokenizer = Dictionary().create()


def extract_phrase(text: str):
    tokens = list(tokenizer.tokenize(text))

    for i in range(1, len(tokens) - 1):

        # 「を」を探す
        if tokens[i].surface() != "を":
            continue

        start = i - 1
        end = i + 1

        found_verb = False

        while end < len(tokens):

            token = tokens[end]
            pos = token.part_of_speech()[0]
            surface = token.surface()

            # 動詞
            if pos == "動詞":
                found_verb = True
                end += 1
                continue

            # 「提出する」の提出
            if pos == "名詞" and not found_verb:
                end += 1
                continue

            # 「して」
            if surface in ("て", "で") and found_verb:
                end += 1
                break

            # 「た」「たい」「ない」「ます」など
            if pos == "助動詞" and found_verb:
                end += 1
                continue

            break

        if found_verb:
            return "".join(
                token.surface()
                for token in tokens[start:end]
            )

    return None