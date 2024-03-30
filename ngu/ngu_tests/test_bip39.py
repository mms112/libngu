import sys

try:
    # make the test data
    from mnemonic import Mnemonic

    eng = Mnemonic('english')

    with open('b39_data.py', 'wt') as fd:
        print('vectors = [', file=fd)
        for ln in [16, 20, 24, 28, 32]:
            for val in [b'\0', b'\xff', b'\xab\xcd', b'\xa5\xa5', b'\xAA', b'\x55']:
                vector = val * (ln // len(val))
                exp = eng.to_mnemonic(vector)
                print('(%r, %r),' % (vector, exp), file=fd)
        print(']', file=fd)

    sys.path.insert(0, '..')
    # continue to test below on desktop
    from binascii import a2b_hex

except ImportError:
    sys.path.insert(0, '')      # bugfix
    from ubinascii import unhexlify as a2b_hex
    eng = None

import bip39
from ngu_tests import b39_data
from ngu_tests import b39_vectors

def seed_compact_form(seed_words):
    return " ".join([w[:4] for w in seed_words.split(" ")])

def test_vectors():
    for raw, words, ms, _ in b39_vectors.english[0:10]:
        target = a2b_hex(raw)
        assert bip39.a2b_words(words) == target
        assert bip39.a2b_words(seed_compact_form(words)) == target
        got = bip39.master_secret(words.encode('utf'), a2b_hex('5452455a4f52'))
        assert got == a2b_hex(ms)
        

def test_b2a():
    for vector, expect in b39_data.vectors:
        ans = bip39.b2a_words(vector)
        assert ans == expect, "(got) %r != (expected) %r " % (ans, expect)

def test_a2b():
    for value, words in b39_data.vectors:
        got = bip39.a2b_words(words)
        got_compact = bip39.a2b_words(seed_compact_form(words))
        assert got == value
        assert got_compact == value

def test_guessing():
    for value, words in b39_data.vectors:
        words = words.split()
        maybe = bip39.a2b_words_guess(words[:-1])
        assert words[-1] in maybe, '%r not in %r' % (words[-1], maybe)

def test_prefix():

    assert bip39.next_char('act') == (True, 'ioru', None)
    assert bip39.next_char('dkfjh') == (False, '', None)
    assert bip39.next_char('a') == (False, 'bcdefghilmnprstuvwx', None)
    assert bip39.next_char('q') == (False, 'u', None)
    assert bip39.next_char('qu') == (False, 'aeio', None)
    assert bip39.next_char('present') == (True, '', 'present')
    assert bip39.next_char('zoo') == (True, '', 'zoo')
    assert bip39.next_char('zo') == (False, 'no', None)

    wl = bip39.wordlist_en
    for w in wl:
        exact, nexts, final = bip39.next_char(w[0:4])
        assert exact == True
        if len(w) < 4:
            assert final in {w, None}           # act vs. aim
        else:
            assert final == w
    
def test_lookup():
    from bip39 import get_word_index

    if not eng: return

    for n, w in enumerate(eng.wordlist):
        assert get_word_index(w) == n
        assert get_word_index(w[0:4]) == n

test_vectors()
test_b2a()
test_a2b()
test_prefix()
test_guessing()
test_lookup()

print('PASS - test_bip39')
