Script to automatically add pitch accent information to an Anki deck.

### Usage
* copy your `collection.anki2` into the repo folder
    * use `anki_add_pitch.py` to add pitch accent info
    * use `remove_pitch.py` to remove pitch accent into

### Notes
* generates accent notation as given in [大辞林 アクセント解説](https://www.sanseido-publ.co.jp/publ/dicts/daijirin_ac.html)
* assumes your Anki cards' *first* and *third* field to contain a word and its reading respectively (e.g. expression, meaning, reading)
* `accdb_minimal.tsv` was generated using `ACCDB_unicode.csv` from [javdejong/nhk-pronunciation](https://github.com/javdejong/nhk-pronunciation/blob/master/ACCDB_unicode.csv) (see `python3 strip_javdejong_nhk-pronunciation.py`)
