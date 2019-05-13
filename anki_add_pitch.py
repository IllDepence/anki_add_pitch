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

def select_deck(c):
    decks = []
    for row in c.execute('SELECT decks FROM col'):
        deks = json.loads(row[0])
        for key in deks:
            d_id = deks[key]['id']
            d_name = deks[key]['name']
            decks.append((d_id, d_name))

    print('Which deck would you like to extend? (enter the number)\n')

    for i in range(len(decks)):
        print(' [{}] {}'.format(i, decks[i][1]))
    inp = int(input('\n'))
    return decks[inp]

def get_acc_patt(expr_field, dicts):
    expr_field = expr_field.replace('[\d]', '')
    expr_field = expr_field.replace('[^\d]', '')
    expr_field = expr_field.strip()
    for dic in dicts:
        patt = dic.get(expr_field, False)
        if patt:
            return patt
        guess = expr_field.split(' ')[0]
        patt = dic.get(guess, False)
        if patt:
            return patt
        guess = re.sub('[<&]', ' ', expr_field).split(' ')[0]
        patt = dic.get(guess, False)
        if patt:
            return patt
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
    return num_ktkn / len(s) > .5

if len(sys.argv) < 2:
    print('usage: python3 anki_add_pitch.py /path/to/collection.anki2 [deck_id]')
    sys.exit()

coll_path = sys.argv[1]

conn = sqlite3.connect(coll_path)
c = conn.cursor()

if len(sys.argv) == 3:
    deck_id = sys.argv[2]
else:
    deck_tpl = select_deck(c)
    deck_id = deck_tpl[0]

acc_dict = {}
with open('wadoku_pitchdb.tsv') as f:
    for line in f:
        orths_txt, hira, hz, accs_txt, patts_txt = line.strip().split('\u241e')
        orth_txts = orths_txt.split('\u241f')
        patts = patts_txt.split(',')
        patt_common = patts[0]  # TODO: extend to support variants?
        if is_katakana(orth_txts[0]):
            hira = hira_to_kata(hira)
        for orth in orth_txts:
            acc_dict[orth] = (hira, patt_common)
# with open('accdb.js', 'w') as f:
#     f.write(json.dumps(acc_dict))
# sys.exit()

note_ids = []
not_found_list = []
num_updated = 0
num_already_done = 0
num_svg_fail = 0

for row in c.execute('SELECT id FROM notes WHERE id IN (SELECT nid FROM'
                      ' cards WHERE did = ?) ORDER BY id', (deck_id,)):
    nid = row[0]
    note_ids.append(nid)

for nid in note_ids:
    row = c.execute('SELECT flds FROM notes WHERE id = ?', (nid,)).fetchone()
    flds_str = row[0]
    if '<!-- accent_start -->' in flds_str:
        # already has pitch accent image
        num_already_done += 1
        continue
    fields = flds_str.split('\x1f')
    expr_field = fields[0].strip()
    patt = get_acc_patt(expr_field, [acc_dict])
    if not patt:
        not_found_list.append([nid, expr_field])
        continue
    svg = pitch_svg(*patt)
    if not svg:
        num_svg_fail += 1
        continue
    fields[2] = ('{}<!-- accent_start --><br><hr><br>{}<!-- accent_end -->'
                ).format(fields[2], svg)  # add svg
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
