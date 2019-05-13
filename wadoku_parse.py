""" Script for generating wadoku_pitchdb.tsv from a wadoku.de XML dump:
    https://www.wadoku.de/wiki/display/WAD/Downloads+und+Links

    N O T E S

    (1) Pitch pattern is given as either the position after which pitch drops:

        1:         start high, then instadrop
        0,2,3,...: start low, instarise, then drop after x (0 never drops)

    or a list of numbers concatenated by em dashes, in which case the field
    "hatsuon" will contain [Akz] tokens. The pitch pattern is then given by
    splitting the word at the [Akz] tokens and applying each of the numbers
    to its corresponding word segment. Example 真行草:

        hatsuon:    しん[Akz]ぎょう[Akz]そう
        accent:     1—1—1

           １００　１１００　１００     (1 indicating high, 0 low)
        -> しん　　ぎょう　　そう

           １０１１０１００
        -> しんぎょうそう

    Note that "hatsuon" can contain more than just [Akz] tokens. Example:

        [Gr]ものみ･の･とう　[Akz]せい'しょ[Akz]<さっ'し>･きょう'かい

    (2) The number indicating the pitch pattern is the position in terms of
        morae and not hiragana. Example 写象主義者:

            しゃしょうしゅぎしゃ, 5

            １２３４５６７８９10  <- hiragana position
            ０１１１１０００００  <- incorrect
            しゃしょうしゅぎしゃ

            １１２２３４４５６６  <- mora position
            ００１１１１１１００  <- correct
            しゃしょうしゅぎしゃ
"""

import re
import sys
import xml.etree.ElementTree as ET

def mora_len(hira):
    return len([c for c in hira if c not in ['ゃ', 'ゅ', 'ょ']])

def hira_to_mora_pos(hira, pos):
    hira_mora_map = []
    m_pos = 0
    for h_pos, h in enumerate(hira):
        if h_pos > 0 and h not in ['ゃ', 'ゅ', 'ょ']:
            m_pos += 1
        hira_mora_map.append(m_pos)
    return hira_mora_map[pos]

def mora_to_hira_pos(hira, pos):
    # add one character for position in pattern succeeding word
    hira_ex = hira + 'ゑ'
    mora_hira_map = [[] for i in range(mora_len(hira_ex))]
    m_pos = 0
    for h_pos, h in enumerate(hira_ex):
        if h_pos > 0 and h not in ['ゃ', 'ゅ', 'ょ']:
            m_pos += 1
        mora_hira_map[m_pos].append(h_pos)
    return mora_hira_map[pos]

def zero_one_patt(hira, accent):
    first_mora_positions = mora_to_hira_pos(hira, 0)
    if accent == 1:
        # start high and instadrop
        patt = [0]*(len(hira)+1)
        for fmp in first_mora_positions:
            patt[fmp] = 1
    else:
        # start low and instarise
        patt = [1]*(len(hira)+1)
        for fmp in first_mora_positions:
            patt[fmp] = 0
        # then drop after accent pos (unless accent is 0)
        if accent != 0:
            # position after accent b/c hira is 0 based ↓
            for i in range(min(mora_to_hira_pos(hira, accent)), len(hira)+1):
                patt[i] = 0
    # convert to string
    return ''.join([str(zo) for zo in patt])

def zero_one_patt_complicated(hira, hatsuon, accent_txt):
    # split accent
    accents = [int(i) for i in accent_txt.split('—')]
    # split hira
    hatsu_filter = re.compile(r'(\[Akz\]|[ぁ-ゔー])')
    m = hatsu_filter.findall(hatsuon)
    hatsu_clean = ''.join(m)
    hira_parts = hatsu_clean.split('[Akz]')
    if ''.join(hira_parts) != hira or len(accents) != len(hira_parts):
        print('Akz token annotation does not check out.')
        print('hira: {}\nhatsuon: {}\naccent: {}'.format(
            hira, hatsuon, accent_txt
            ))
        raise IndexError
    zo_patts = []
    # get patterns of segments
    for hira_part, accent in zip(hira_parts, accents):
        zo_patts.append(zero_one_patt(hira_part, accent))
    # merge segments
    not_last = [patt[:-1] for patt in zo_patts[0:-1]]  # cut last element
    last = zo_patts[-1:]  #  use a is
    # convert to string
    return ''.join([str(zo) for zo in not_last+last])

if len(sys.argv) != 2:
    print('usage: python3 wadoku_parse.py /path/to/wadoku.xml')
    sys.exit()

tree = ET.parse(sys.argv[1])
entries_node = tree.getroot()
entries = entries_node.getchildren()
accent_number_patt = re.compile(r'\d+(—\d+)*')
with open('wadoku_pitchdb.tsv', 'w') as f:
    for entry in entries:
        # get nodes with the data we want
        form = entry.find('{http://www.wadoku.de/xml/entry}form')
        if form is None:
            continue
        orths = form.findall('{http://www.wadoku.de/xml/entry}orth')
        reading = form.find('{http://www.wadoku.de/xml/entry}reading')
        if orths is None or reading is None:
            continue
        hira = reading.find('{http://www.wadoku.de/xml/entry}hira')
        hatsuon = reading.find('{http://www.wadoku.de/xml/entry}hatsuon')
        accents = reading.findall('{http://www.wadoku.de/xml/entry}accent')
        if hira is None or hatsuon is None or accents is None:
            continue
        # get data from nodes
        orth_txts = [node.text.strip() for node in orths if node.text is not None]
        if len(orth_txts) == 0:
            continue
        orths_txt = '\u241f'.join(orth_txts)
        accent_txts = [node.text.strip() for node in accents if node.text is not None]
        if len(accent_txts) == 0:
            continue
        accents_txt = ','.join(accent_txts)
        hira_txt = hira.text
        hatsuon_txt = hatsuon.text
        zo_patts = []
        acc_patts = []
        for acc_txt in accent_txts:
            if not accent_number_patt.fullmatch(acc_txt):
                # Example from CSV: 々|じおくり|じ･おくり|-
                continue
            try:
                if int(acc_txt) > len(hira_txt):
                    # Example from CSV: …米|まい|まい|5,0
                    continue
                zo_patt = zero_one_patt(hira_txt, int(acc_txt))
            except ValueError:
                try:
                    zo_patt = zero_one_patt_complicated(
                        hira_txt, hatsuon_txt, acc_txt
                        )
                except IndexError:
                    continue
            zo_patts.append(zo_patt)
            acc_patts.append(acc_txt)
        if len(zo_patts) == 0:
            continue
        zo_patts_txt = ','.join(zo_patts)
        acc_patts_txt = ','.join(acc_patts)
        # write to CSV
        line = '\u241e'.join(
            [orths_txt, hira_txt, hatsuon_txt, acc_patts_txt, zo_patts_txt]
            )
        f.write('{}\n'.format(line))
