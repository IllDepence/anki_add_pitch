Script to automatically add pitch accent information to an Anki deck.

### Usage
* `$ python3 anki_add_pitch.py /path/to/collection.anki2` to add pitch accent info
* `$ python3 remove_pitch.py /path/to/collection.anki2` to remove pitch accent info

### Features
* creates pitch accent illustrations in SVG, no image files involved (also [available online](https://illdepence.github.io/SVG_pitch/))
* illustrations include pitch annotations as well as aligned kana
* each accent position corresponds to one mora, 拗音 (e.g. きゃ) are automatically merged
* when an expression has several possible readings (e.g. 汚れ) the script tries to determine which one is used by inspecting the reading field of the card
* if a word is mostly katakana, katakana instead of hiragana are used in the illustration

### Example
![](example.jpg)

### Notes
* accent notation similar to [大辞林 アクセント解説](https://www.sanseido-publ.co.jp/publ/dicts/daijirin_ac.html)
* `wadoku_pitchdb.csv` was generated from a [Wadoku XML dump](https://www.wadoku.de/wiki/display/WAD/Downloads+und+Links) (see file `wadoku_parse.py` for details)
