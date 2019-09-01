""" Utility functions used in both extend and remove script.
"""

import json

def select_deck(c, msg):
    decks = []
    for row in c.execute('SELECT decks FROM col'):
        deks = json.loads(row[0])
        for key in deks:
            d_id = deks[key]['id']
            d_name = deks[key]['name']
            decks.append((d_id, d_name))

    print('{} (enter the number)'.format(msg))

    for i in range(len(decks)):
        print(' [{}] {}'.format(i, decks[i][1]))
    inp = int(input(''))
    return decks[inp][0]

def get_note_ids(c, deck_id):
    note_ids = []
    for row in c.execute('SELECT id FROM notes WHERE id IN (SELECT nid FROM'
                          ' cards WHERE did = ?) ORDER BY id', (deck_id,)):
        nid = row[0]
        note_ids.append(nid)
    return note_ids

def select_note_fields(c, note_id):
    example_row = c.execute(
        'SELECT flds FROM notes WHERE id = ?', (note_id,)
        ).fetchone()
    example_flds = example_row[0].split('\x1f')
    for i in range(len(example_flds)):
        if len(example_flds[i]) > 0:
            print(' [{}] {}'.format(i, example_flds[i][:20]))
    print('Select the field containing the Japanese expression. (enter the number) ')
    expr_idx = int(input(''))
    print('Select the field containing the reading. (enter the number) ')
    reading_idx = int(input(''))
    return expr_idx, reading_idx
