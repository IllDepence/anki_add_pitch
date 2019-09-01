""" Removes pitch accent indicators from Anki cards.
"""

import json
import re
import sqlite3
import sys
import time
from util import select_deck, select_note_fields, get_note_ids

if len(sys.argv) < 2:
    print('usage: python3 remove_pitch.py /path/to/collection.anki2')
    sys.exit()

# open Anki DB
coll_path = sys.argv[1]
conn = sqlite3.connect(coll_path)
c = conn.cursor()

# figure out collection structure
deck_id = select_deck(c, 'From which deck would you like to remove?')
note_ids = get_note_ids(c, deck_id)
expr_idx, reading_idx = select_note_fields(c, note_ids[0])

# remove pitch accent indicators
acc_patt = re.compile("<!-- accent_start -->.+<!-- accent_end -->", re.S)
not_found_list = []
num_updated = 0
num_already_done = 0
for nid in note_ids:
    row = c.execute('SELECT flds FROM notes WHERE id = ?', (nid,)).fetchone()
    flds_str = row[0]
    if 'accent_start' not in flds_str:
        # has no pitch accent image
        num_already_done += 1
        continue
    fields = flds_str.split('\x1f')
    fields[reading_idx] = re.sub(acc_patt, '', fields[reading_idx])
    new_flds_str = '\x1f'.join(fields)
    mod_time = int(time.time())
    c.execute('UPDATE notes SET usn = ?, mod = ?, flds = ? WHERE id = ?',
              (-1, mod_time, new_flds_str, nid))
    num_updated += 1
conn.commit()

print('skipped {} notes w/o accent image'.format(num_already_done))
print('updated {} notes'.format(num_updated))
