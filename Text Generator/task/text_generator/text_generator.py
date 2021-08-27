import progressbar
import random
import re
from collections import Counter

from nltk import trigrams
from nltk.tokenize import WhitespaceTokenizer

LINES = 100

ENDING = re.compile(r'[.!?]$')
_trigrams = []


def gen_model(start_token):
    """
    Generates the frequency list of tails from a starting token
    :param start_token: starting token
    :return: list containing tails and their counts [tail, count]
    """
    # Gets tails of the head
    tails = [token[1] for token in _trigrams if token[0] == start_token]
    # Forms a list of tail and its count (tail, count)
    output = [(tail, count) for tail, count in Counter(tails).items() if not re.match(ENDING, tail)]

    return output


def gen_sentence(start_gen):
    """
    Generates a sentence based on a starting token
    :param start_gen: generator that yields starting words
    :return: a string representing the generated sentence
    """
    start = start_gen.__next__()
    output = start.split()
    i = 1
    while True:
        start = output[i]
        if len(output) >= 5 and re.search(ENDING, start):
            break
        if re.match(ENDING, start):
            word = start_gen.__next__()
        else:
            word = gen_next(' '.join([output[i - 1], start]))
        output.append(word)
        i += 1
    return ' '.join(output)


def gen_next(token):
    """
    Generates the next token based on a starting token
    :param token: starting token
    :return: a string representing the generated token
    """
    model = gen_model(token)
    tails, weights = map(list, zip(*model))
    return random.choices(tails, weights=weights)[0]


def gen_start():
    """
    Generates a random starting token for a sentence
    :return: a string representing the generated token
    """
    capitals = [token[0] for token in _trigrams if token[0][0].isupper()]
    while True:
        yield random.choice(capitals)


def generate_paragraph(lines=10):
    """
    Generates n number of lines based on a corpus
    :param lines: number of lines to print
    """
    global _trigrams
    while True:
        print('Enter corpus filename:')
        filename = input()
        try:
            file = open(filename, "r", encoding='utf-8')
        except FileNotFoundError:
            print('File does not exist!')
            continue
        tk = WhitespaceTokenizer()
        words = tk.tokenize(' '.join(file.readlines()).replace('"', ''))
        _trigrams = list(trigrams(words))
        _trigrams = [(' '.join((token[0], token[1])), token[2]) for token in _trigrams]

        start_gen = gen_start()
        output = ''
        for _ in progressbar.progressbar(range(lines)):
            # Needed because some head tokens will not generate any tails
            while True:
                try:
                    output += f'{gen_sentence(start_gen)}\n'
                except ValueError:
                    continue
                break
        return output


print(generate_paragraph(LINES))
