from __future__ import print_function
from bisect import bisect_left
import random
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import itertools
import operator
import pickle
from datetime import datetime
import unicodedata

PUNCTUATION_TRANSLATE_TABLE = {i:None for i in range(sys.maxunicode)
    if unicodedata.category(unichr(i)).startswith('P') and i != 46}


def normalize_text(text):
    text = text.lower().translate(PUNCTUATION_TRANSLATE_TABLE)
    return text

#u'{1}:{0} '.format(*score)
# encode('utf8')
# word.title()


def concat_words(array):
    return ";".join(array)


class Statistics(object):
    def __init__(self):
        self.map = dict()
        self.sorted_map = dict()
        self.precomp = dict()

    def init(self, dirs, depth):
        for directory in dirs:
            for doc in os.listdir(directory):
                content = open(directory + doc, 'r').read().decode('utf8')
                terms = normalize_text(content).replace('.', ' . ').split()

                for i in range(len(terms) - depth):
                    key = concat_words(itertools.islice(terms, i, i + depth))
                    if key not in self.map:
                        self.map[key] = dict()
                        self.map[key][terms[i + depth]] = 0
                    self.map[key][terms[i + depth]] = self.map[key].get(terms[i + depth], 0) + 1

    def normalize(self):
        for first in self.map:
            total = sum(self.map[first].values())
            prev = 0
            for second in self.map[first]:
                new_part = 1.0 * self.map[first][second] / total
                self.map[first][second] = new_part + prev
                prev += new_part
            self.sorted_map[first] = sorted(self.map[first].items(), key = operator.itemgetter(1))
            self.precomp[first] = [r[1] for r in self.sorted_map[first]]
        self.map = {}

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)

    def get_random_next_word(self, prev):
        rand = random.random()
        return self.sorted_map[prev][bisect_left(self.precomp[prev], rand)][0]

    def get_random_word(self):
        return random.choice(self.sorted_map.keys())


def calc_stats_and_save(dirs, filename_one_word, filename_two_words):
    random.seed(datetime.now())
    one_word = Statistics()
    one_word.init(dirs, 1)
    one_word.normalize()
    one_word.save(filename_one_word)

    two_word = Statistics()
    two_word.init(dirs, 2)
    two_word.normalize()
    two_word.save(filename_two_words)


def load_stat_and_generate(filename_one_word, filename_two_words, count):
    result = ""
    one_word2 = Statistics.load(filename_one_word)
    two_words2 = Statistics.load(filename_two_words)

    first_word = one_word2.get_random_word()
    second_word = one_word2.get_random_next_word(first_word)

    result += first_word.title()
    if second_word != '.':
        result += ' '
    result += second_word

    i = 0
    while i < count:
        first_word = two_words2.get_random_next_word(concat_words([first_word, second_word]))
        first_word, second_word = second_word, first_word

        if second_word != '.':
            result += ' '

        result += second_word.title() if first_word == '.' else second_word
        i += 1
    if second_word != '.':
        result += '.'
    return result


if __name__ == '__main__':
    dirs = ('./corps/asimov/', './corps/dickens/', './corps/pratchett/')
    filename_one_word = "sorted_map1.pickle"
    filename_two_words = "sorted_map2.pickle"
    calc_stats_and_save(dirs, filename_one_word, filename_two_words)

    count = 10000
    print(load_stat_and_generate(filename_one_word, filename_two_words, count))