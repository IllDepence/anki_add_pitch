""" Add pitch accent indicators to thrid field (assumend to be the reading
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

def get_acc_img(expr_field, dicts):
    expr_field = expr_field.replace('[\d]', '')
    expr_field = expr_field.replace('[^\d]', '')
    expr_field = expr_field.strip()
    for dic in dicts:
        acc_img = dic.get(expr_field, False)
        if acc_img:
            return acc_img
        guess = expr_field.split(' ')[0]
        acc_img = dic.get(guess, False)
        if acc_img:
            return acc_img
        guess = re.sub('[<&]', ' ', expr_field).split(' ')[0]
        acc_img = dic.get(guess, False)
        if acc_img:
            return acc_img
    return False

conn = sqlite3.connect('collection.anki2')
c = conn.cursor()

acc_dict1 = {}
with open('accdb_clean.tsv') as f:
    for line in f:
        try:
            kan, kan_var, disp, ktkn, patt, img = line.strip().split('\u241f')
        except ValueError:
            print(line)
            sys.exit()
        if len(img) == 0:
            continue
        img = '<img src="{}">'.format(img)
        acc_dict1[kan] = img
        acc_dict1[kan_var] = img

acc_dict2 = {}
with open('ja_pitch_accents.tsv') as f:
    for line in f:
        try:
            wid, kan, hir, patt, img, mor, drp = line.strip().split('\t')
        except ValueError:
            continue
        if len(img) == 0:
            continue
        acc_dict2[kan] = img

if len(sys.argv) == 2:
    deck_id = sys.argv[1]
else:
    deck_tpl = select_deck()
    deck_id = deck_tpl[0]

note_ids = []
not_found_list = []
num_updated = 0
num_already_done = 0

for row in c.execute('SELECT id FROM notes WHERE id IN (SELECT nid FROM'
                      ' cards WHERE did = ?) ORDER BY id', (deck_id,)):
    nid = row[0]
    note_ids.append(nid)

for nid in note_ids:
    row = c.execute('SELECT flds FROM notes WHERE id = ?', (nid,)).fetchone()
    flds_str = row[0]
    if 'ja_pitch_accent' in flds_str:
        # already has pitch accent image
        num_already_done += 1
        continue
    fields = flds_str.split('\x1f')
    expr_field = fields[0].strip()
    acc_img = get_acc_img(expr_field, [acc_dict1, acc_dict2])
    if not acc_img:
        not_found_list.append([nid, expr_field])
        continue
    fields[2] = ('{}<br><br><!-- accent_start -->{}<!-- accent_end -->'
                ).format(fields[2], acc_img)  # add image
    new_flds_str = '\x1f'.join(fields)
    c.execute('UPDATE notes SET flds = ? WHERE id = ?', (new_flds_str, nid))
    num_updated += 1
conn.commit()

print('skipped {} already annotated notes'.format(num_already_done))
print('updated {} notes'.format(num_updated))
print('could not find {} expressions'.format(len(not_found_list)))
if len(not_found_list) > 0:
    with open('not_found_{}'.format(int(time.time())), 'w') as f:
        for nid, expr in not_found_list:
            f.write('{}: {}\n'.format(nid, expr))
