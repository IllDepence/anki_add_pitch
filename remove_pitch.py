""" Removes pitch accent indicators from thrid field (assumend to be the reading
    field) of Anki cards.
"""

import json
import re
import sqlite3
import sys
import time

def select_deck():
    decks = []
    for row in c.execute('SELECT decks FROM col'):
        deks = json.loads(row[0])
        for key in deks:
            d_id = deks[key]['id']
            d_name = deks[key]['name']
            decks.append((d_id, d_name))

    print('Which deck would you like to extend?\n')

    for i in range(len(decks)):
        print(' [{}] {}'.format(i, decks[i][1]))
    inp = int(input('\n'))
    return decks[inp]

conn = sqlite3.connect('collection.anki2')
c = conn.cursor()

if len(sys.argv) == 2:
    deck_id = sys.argv[1]
else:
    deck_tpl = select_deck()
    deck_id = deck_tpl[0]

note_ids = []
not_found_list = []
num_updated = 0
num_already_done = 0

acc_patt = re.compile("<!-- accent_start -->.+<!-- accent_end -->", re.S)

for row in c.execute('SELECT id FROM notes WHERE id IN (SELECT nid FROM'
                      ' cards WHERE did = ?) ORDER BY id', (deck_id,)):
    nid = row[0]
    note_ids.append(nid)

for nid in note_ids:
    row = c.execute('SELECT flds FROM notes WHERE id = ?', (nid,)).fetchone()
    flds_str = row[0]
    if 'accent_start' not in flds_str:
        # has no pitch accent image
        num_already_done += 1
        continue
    fields = flds_str.split('\x1f')
    fields[2] = re.sub(acc_patt, '', fields[2])
    new_flds_str = '\x1f'.join(fields)
    c.execute('UPDATE notes SET flds = ? WHERE id = ?', (new_flds_str, nid))
    num_updated += 1
conn.commit()

print('skipped {} notes w/o accent image'.format(num_already_done))
print('updated {} notes'.format(num_updated))
