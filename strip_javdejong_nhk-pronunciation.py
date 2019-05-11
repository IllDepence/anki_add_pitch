""" Strip file

        github.com/javdejong/nhk-pronunciation/blob/master/ACCDB_unicode.csv

    to only contain necessary information to display pitch accent pattern. Also
    add identifier for github.com/kishimoto-tsuneyo/ja_pitch_accent/ images.

    input CSV columns:      example values:             note:
         0 NID              56405
         1 ID               45175
         2 WAVname          J45175.wav
         3 K_FLD            1
         4 ACT              3114550010
         5 midashigo        タトエ                      w/ 濁点
         6 nhk              例え
         7 kanjiexpr        譬え
         8 NHKexpr          "例え{譬,喩}"
         9 numberchars      3
        10 nopronouncepos
        11 nasalsoundpos
        12 majiri           同じようなタトエガある
        13 kaisi            5
        14 KWAV             K45175.wav
        15 midashigo1       タトエ                      w/o 濁点
        16 akusentosuu      2
        17 bunshou          1
        18 ac               12                          accent pattern

    Accent pattern explanation:
        0 = low
        1 = high
        2 = high and following will be low

                20       02       01
        E.g: 箸 hl    橋 lhl   端 lhh

        Also, leading zeros are omitted. (例え 012→12, but 気 0→0)

    As identifier for a word, we will use:
        NHK + midashigo
"""

import csv

words_done = []
patt_to_img_id = {
    '0': '0-1',
    '01': '0-2',
    '011': '0-3',
    '0111': '0-4',
    '01111': '0-5',
    '011111': '0-6',
    '2': '1-1',
    '20': '1-2',
    '200': '1-3',
    '2000': '1-4',
    '20000': '1-5',
    '200000': '1-6',
    '02': '2-2',
    '020': '2-3',
    '0200': '2-4',
    '02000': '2-5',
    '020000': '2-6',
    '012': '3-3',
    '0120': '3-4',
    '01200': '3-5',
    '012000': '3-6',
    '0112': '4-4',
    '01120': '4-5',
    '011200': '4-6',
    '01112': '5-5',
    '011120': '5-6',
    '011112': '6-6',
    }

with open('ACCDB_unicode.csv') as f:
    csv_reader = csv.reader(f, delimiter=',', quotechar='"')
    for row in csv_reader:
        writing_nhk = row[6]
        writing_alt = row[7]
        writing_disp = row[8]
        katakana = row[5]
        num_kana = len(row[15])  # used in nhk-pronunciation code for length
        accent_pattern_csv = row[18]

        word_id = writing_nhk+katakana
        if word_id in words_done:
            # ACCDB_unicode.csv sometimes contains multiple pronunciation
            # patterns for one and the same word. Looking at a small sample it
            # seemed the variant listed earlier is in line with the patterns
            # given on wadoku.de
            continue
        words_done.append(word_id)

        # Pad accent pattern given in CSV with 0s from the left side. E.g.:
        #
        #                         ０１１１
        #     ガクセイ, 111   →   ガクセイ
        #
        # As in: https://github.com/javdejong/nhk-pronunciation/blob/master/
        #        nhk_pronunciation.py#L225
        acc_patt_csv_len = len(accent_pattern_csv)
        accent_pattern = '0'*(num_kana-acc_patt_csv_len) + accent_pattern_csv

        img_id = patt_to_img_id.get(accent_pattern, False)
        if img_id:
            img_file = 'ja_pitch_accent_{}.png'.format(img_id)
        else:
            img_file = ''

        new_vals = [
            writing_nhk,
            writing_alt,
            writing_disp,
            katakana,
            accent_pattern,
            img_file
            ]
        sep = '\u241f'
        line = sep.join(new_vals)
        with open('accdb_clean.tsv', 'a') as f:
            f.write('{}\n'.format(line))
