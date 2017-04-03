import collections
import random

idx_to_char = {}
char_to_idx = {}
ALPHABET_SIZE = 26
INFERIOR_LIMIT = 0.060
SUPERIOR_LIMIT = 0.080


def init_corespondency():
    global ALPHABET_SIZE
    for i in range(26):
        idx_to_char[i] = chr(ord('A') + i)
        char_to_idx[chr(ord('A') + i)] = i

    # if you want to add space to crypto alphabet, uncomment next lines:
    # idx_to_char[26] = ' '
    # char_to_idx[' '] = 26

    ALPHABET_SIZE = len(idx_to_char)


FREQUENCY = {
    'A': 8.167,
    'B': 1.492,
    'C': 2.782,
    'D': 4.253,
    'E': 12.702,
    'F': 2.228,
    'G': 2.015,
    'H': 6.094,
    'I': 6.966,
    'J': 0.153,
    'K': 0.772,
    'L': 4.025,
    'M': 2.406,
    'N': 6.749,
    'O': 7.507,
    'P': 1.929,
    'Q': 0.095,
    'R': 5.987,
    'S': 6.327,
    'T': 9.056,
    'U': 2.758,
    'V': 0.978,
    'W': 2.360,
    'X': 0.150,
    'Y': 1.974,
    'Z': 0.074
}


def short_demo():
    text = 'ILOVEPROGRAMMING'
    key = 'THECODEBREAKER'

    encrypted_text = []
    for i, letter in enumerate(text):
        encrypted_text.append(
            (
                char_to_idx[letter] +
                char_to_idx[
                    key[
                        i % len(key)
                    ]
                ]
            ) % ALPHABET_SIZE)

    print 'Input text: ', text
    print 'Input key : ', key
    print 'Encrypted : ', ''.join(
        idx_to_char[i] for i in encrypted_text
    )
    print ''


def filter_file(text_file):
    plain_text = open(text_file).read().upper()

    filtered_text = open('text.flt', 'w')

    for letter in plain_text:
        if letter in char_to_idx.keys():
            filtered_text.write(letter)

    filtered_text.close()


def encrypt_file(text_file, key_file):
    global FREQUENCY
    key = open(key_file).read().upper()
    plain_text = open(text_file, 'r').read()
    encrypted_file = open(text_file + '.enc', 'w')

    # For detailed analysis
    # frequency = collections.Counter(plain_text)
    # for item in frequency:
    #     FREQUENCY[item] = float(frequency[item]) / len(plain_text)

    # IC = 0
    # for letter in frequency:
    #     IC += (frequency[letter] * 1.0 / len(plain_text))**2
    # print 'IC normal text    = ', IC

    for i, letter in enumerate(plain_text):
        encrypted_file.write(idx_to_char[
            (char_to_idx[letter] +
             char_to_idx[
                key[
                    i % len(key)
                ]
            ]) % ALPHABET_SIZE
        ])

    encrypted_file.close()


def compute_coincidence_index(encrypted_text, start, step):
    text_block = encrypted_text[start::step]
    coincidence_index = 0.0
    text_len = len(text_block)
    frequency = collections.Counter(text_block)

    for letter in frequency:
        coincidence_index += (float(frequency[letter]) / text_len) * \
            ((float(frequency[letter] - 1)) / (text_len - 1))

    return coincidence_index


def compute_key_length(encrypted_text):
    key_len = 0

    while True:
        key_len += 1
        coincidence_indexes = []
        for i in range(key_len):
            coincidence_indexes.append(
                round(compute_coincidence_index(
                    encrypted_text,
                    start=i,
                    step=key_len),
                    ndigits=3)
            )

        ok = True

        for val in coincidence_indexes:
            if val < INFERIOR_LIMIT or val > SUPERIOR_LIMIT:
                ok = False
                break

        if ok is True:
            print 'coincidence_indexes: ', coincidence_indexes
            return key_len


def compute_mutual_coincidence_index(text):
    freq = collections.Counter(text)

    mutual_cidx = 0.0
    for letter in FREQUENCY.keys():
        mutual_cidx += float(FREQUENCY[letter]) * \
            (float(freq[letter]) / len(text))

    if mutual_cidx >= 1:
        mutual_cidx /= 100

    return mutual_cidx


def shift(text, counter):
    text = [(char_to_idx[char] + counter) % ALPHABET_SIZE
            for char in text
            ]
    return ''.join([idx_to_char[i] for i in text])


def compute_key(text, key_len):
    global INFERIOR_LIMIT, SUPERIOR_LIMIT
    key = []
    for i in range(key_len):
        s = -1
        while True:
            s = s + 1
            mutual_cidx = compute_mutual_coincidence_index(
                text=shift(text[i::key_len], s)
            )

            if mutual_cidx >= INFERIOR_LIMIT and mutual_cidx <= SUPERIOR_LIMIT:
                break

        found_char = idx_to_char[(ALPHABET_SIZE - s) % ALPHABET_SIZE]
        print 'shift = %3d' % s,
        print '\tmcidx = %6f' % round(mutual_cidx, 6),
        print '\tletter =', found_char
        key.append(found_char)

    return ''.join(key)


def decrypt_file(text_file):
    encrypted_text = open(text_file).read()

    frequency = collections.Counter(encrypted_text)

    suma = 0
    for letter in frequency:
        suma += (frequency[letter] * 1.0 / len(encrypted_text))**2
    print 'Coincidence index for encrypted text :', suma

    key_len = compute_key_length(encrypted_text)
    print 'KEY LENGTH: ', key_len
    key = compute_key(encrypted_text, key_len)
    print 'KEY FOUND : ', key

    decrypted_file = open(text_file + '.dcr', 'w')
    for idx, char in enumerate(encrypted_text):
        char_idx = (ALPHABET_SIZE + char_to_idx[char] -
                    char_to_idx[key[idx % key_len]]) % ALPHABET_SIZE
        decrypted_file.write(idx_to_char[char_idx])

    decrypted_file.close()


def main():
    init_corespondency()
    short_demo()

    print '1. Filter file - reduce to [A-Z]*'
    filter_file('text')

    print '2. Encrypt file - permute chars'
    encrypt_file('text.flt', 'key')

    print '3. Decrypt file - using cryptanalysis'
    decrypt_file('text.flt.enc')


if __name__ == '__main__':
    main()
