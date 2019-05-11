Script to automatically add pitch accent information to an Anki deck.

### Usage
* get [kishimoto-tsuneyo/ja_pitch_accent](https://github.com/kishimoto-tsuneyo/ja_pitch_accent)
    * manually add contained images to your `collection.media.db2`
* get file `ACCDB_unicode.csv` from [javdejong/nhk-pronunciation](https://github.com/javdejong/nhk-pronunciation/blob/master/ACCDB_unicode.csv)
    * run `python3 strip_javdejong_nhk-pronunciation.py`
* copy your `collection.anki2` into the repo folder
    * use `anki_add_pitch.py` to add pitch accent info
    * use `remove_pitch.py` to remove pitch accent into

### Notes
* uses accent notation as given in [大辞林 アクセント解説](https://www.sanseido-publ.co.jp/publ/dicts/daijirin_ac.html).
* assumes your Anki cards' *third* field is contains a word's reading (e.g. expression, meaning, reading)
