"""Compare extracted PDF narrative text with the independently transformed source."""
import re


def normalize(text):
    # Line wrapping and discretionary hyphens are layout, not narrative content.
    return re.sub(r'\s+', '', text).replace('\u00ad', '')


def assert_narrative_parity(text, data, fonts):
    """Require every source paragraph, unchanged and in order, and font coverage."""
    actual = normalize(text)
    cursor = 0
    count = 0
    for chapter in data['chapters']:
        for paragraph in chapter['paragraphs']:
            expected = ''.join(run['text'] for run in paragraph['runs'])
            for char in set(expected):
                if char.isspace():
                    continue
                for name, cmap in fonts.items():
                    if ord(char) not in cmap:
                        raise AssertionError(f'{paragraph["id"]}: missing {char!r} in {name}')
            needle = normalize(expected)
            if not needle:
                continue
            found = actual.find(needle, cursor)
            if found < 0:
                raise AssertionError(f'{paragraph["id"]}: missing, reordered or changed PDF paragraph')
            cursor = found + len(needle)
            count += 1
    return count
