""" Add pitch accent indicators to Anki cards.

    Below script makes use of data from Wadoku by Ulrich Apel.
    (See file wadoku_parse.py for more details.)
    Wadoku license information is available on the web:

    http://www.wadoku.de/wiki/display/WAD/Wörterbuch+Lizenz
    http://www.wadoku.de/wiki/display/WAD/%28Vorschlag%29+Neue+Wadoku-Daten+Lizenz
"""

import json
import re
import sqlite3
import sys
import time
from draw_pitch import pitch_svg
from util import select_deck, select_note_fields, get_note_ids

def get_accent_dict(path):
    acc_dict = {}
    with open(path) as f:
        for line in f:
            orths_txt, hira, hz, accs_txt, patts_txt = line.strip().split('\u241e')
            orth_txts = orths_txt.split('\u241f')
            if clean_orth(orth_txts[0]) != orth_txts[0]:
                orth_txts = [clean_orth(orth_txts[0])] + orth_txts
            patts = patts_txt.split(',')
            patt_common = patts[0]  # TODO: extend to support variants?
            if is_katakana(orth_txts[0]):
                hira = hira_to_kata(hira)
            for orth in orth_txts:
                if not orth in acc_dict:
                    acc_dict[orth] = []
                new = True
                for patt in acc_dict[orth]:
                    if patt[0] == hira and patt[1] == patt_common:
                        new = False
                        break
                if new:
                    acc_dict[orth].append((hira, patt_common))
    return acc_dict

def get_acc_patt(expr_field, reading_field, dicts):
    def select_best_patt(reading_field, patts):
        best_pos = 9001
        best = patts[0]  # default
        for patt in patts:
            hira, p = patt
            try:
                pos = reading_field.index(hira)
                if pos < best_pos:
                    best = patt
                    best_pos = pos
            except ValueError:
                continue
        return best
    expr_field = expr_field.replace('[\d]', '')
    expr_field = expr_field.replace('[^\d]', '')
    expr_field = expr_field.strip()
    for dic in dicts:
        patts = dic.get(expr_field, False)
        if patts:
            return select_best_patt(reading_field, patts)
        guess = expr_field.split(' ')[0]
        patts = dic.get(guess, False)
        if patts:
            return select_best_patt(reading_field, patts)
        guess = re.sub('[<&]', ' ', expr_field).split(' ')[0]
        patts = dic.get(guess, False)
        if patts:
            return select_best_patt(reading_field, patts)
    return False

def hira_to_kata(s):
    return ''.join(
        [chr(ord(ch) + 96) if ('ぁ' <= ch <= 'ゔ') else ch for ch in s]
        )

def is_katakana(s):
    num_ktkn = 0
    for ch in s:
        if ch == 'ー' or ('ァ' <= ch <= 'ヴ'):
            num_ktkn += 1
    return num_ktkn / max(1, len(s)) > .5

def clean_orth(orth):
    orth = re.sub('[()△×･〈〉{}]', '', orth)  # 
    orth = orth.replace('…', '〜')  # change depending on what you use
    return orth

if len(sys.argv) < 2:
    print('usage: python3 anki_add_pitch.py /path/to/collection.anki2')
    sys.exit()

# load pitch data
print('loading pitch data')
acc_dict = get_accent_dict('wadoku_pitchdb.csv')
# with open('accdb.js', 'w') as f:
#     f.write(json.dumps(acc_dict))
# sys.exit()

# open Anki DB
coll_path = sys.argv[1]
conn = sqlite3.connect(coll_path)
c = conn.cursor()

# figure out collection structure
deck_id = select_deck(c, 'Which deck would you like to extend?')
note_ids = get_note_ids(c, deck_id)
expr_idx, reading_idx = select_note_fields(c, note_ids[0])

# extend notes
not_found_list = []
num_updated = 0
num_already_done = 0
num_svg_fail = 0
for nid in note_ids:
    row = c.execute('SELECT flds FROM notes WHERE id = ?', (nid,)).fetchone()
    flds_str = row[0]
    if '<!-- accent_start -->' in flds_str:
        # already has pitch accent image
        num_already_done += 1
        continue
    fields = flds_str.split('\x1f')
    expr_field = fields[expr_idx].strip()
    reading_field = fields[reading_idx].strip()
    patt = get_acc_patt(expr_field, reading_field, [acc_dict])
    if not patt:
        not_found_list.append([nid, expr_field])
        continue
    hira, LlHh_patt = patt
    LH_patt = re.sub(r'[lh]', '', LlHh_patt)
    svg = pitch_svg(hira, LH_patt)
    if not svg:
        num_svg_fail += 1
        continue
    fields[reading_idx] = (
        '{}<!-- accent_start --><br><hr><br>{}<!-- accent_end -->'
        ).format(fields[reading_idx], svg)  # add svg
    new_flds_str = '\x1f'.join(fields)
    mod_time = int(time.time())
    c.execute('UPDATE notes SET usn = ?, mod = ?, flds = ? WHERE id = ?',
              (-1, mod_time, new_flds_str, nid))
    num_updated += 1
conn.commit()

print('\n- - - done - - -')
print('skipped {} already annotated notes'.format(num_already_done))
print('updated {} notes'.format(num_updated))
print('failed to generate {} annotations'.format(num_svg_fail))
print('could not find {} expressions'.format(len(not_found_list)))
if len(not_found_list) > 0:
    with open('not_found_{}'.format(int(time.time())), 'w') as f:
        for nid, expr in not_found_list:
            f.write('{}: {}\n'.format(nid, expr))
