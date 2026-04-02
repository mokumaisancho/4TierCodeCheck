
from collections import Counter

def word_freq(text):
    words = text.lower().split()
    return Counter(words)

def top_words(text, n=5):
    freq = word_freq(text)
    return freq.most_common(n)
