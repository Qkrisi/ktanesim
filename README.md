# ktanesim

A Discord bot that simulates Keep Talking and Nobody Explodes bombs.

Visit the [wiki page](https://github.com/Qkrisi/ktanesim/wiki) to see how to add new modules.

## Setup

Requirements:

```
Python 3.8+
SQLite 3.24+
discord.py
cairosvg
Wand
```

 -Clone the [KTaNE Bot repository](https://github.com/qkrisi/ktanecord) and set it up according to its [README](https://github.com/Qkrisi/ktanecord/blob/master/README.md).
 
 -Create a copy of the `config.template` file and rename it to `config.py`
 
 -Open the `config.py` file and modify the values in it.
 
 These config fields should be the same in both:
 
 | Name in ktanesim | Name in the KTaNE Bot |
 | -- | -- |
 | PREFIX | token |
 | HOST | tpServerIP |
 | PORT | SimPort |

-Execute the `main.py` file

-Start the KTaNE bot (`node src/main.js` in the cloned KTaNE Bot repo)
