# Tester

### Užitočné prepínače

```
input-tester:
  -h, --help
    show this help message and exit
  -t TIMELIMIT, --time TIMELIMIT
    set timelimit (default=3,cpp=1,py=5),
    can be set to unlimited using 0 and optionally in per language format (example "2,py=0,cxx=0.5")
  -F, --no-fskip
    dont skip the rest of input files in the same batch after first fail
  -R, --Reset
    recompute outputs
  -K, --keep-bin
    dont remove binary files after finishing
  -d, --diff
    program which checks correctness of output (default=diff),
    arguments given to program depends of prefix: diff $our $theirs, check $inp $our $theirs
  --pythoncmd
    what command is used to execute python, e.g. `python3` or `pypy3`
  -q, --quiet
    dont let subprograms print stuff
  -j THREADS, --threads THREADS
    how many threads to use (default=1)
```

### Inteligencia

Nástroj sa snaží byť inteligentný. Na zoznam riešení mu vieme dať priečinok a nástroj sa v ňom pokúsi nájsť relevantné programy (`sol*`, `val*`, `check*`, ...). Ďalej sa pokúsi (magicky) utriediť riešenia od najlepšieho po najhoršie. Poradie má zmysel napríklad, keď sa generujú nové výstupy. Nakoniec sa nástroj pokúsi zistiť, ako ste tieto programy chceli spustiť.

Aby inteligencia správne fungovala, chceme dodržiavať nasledujúci štýl názvov súborov:

- `sol*`

  - vo všeobecnosti chceme použiť formát `sol-<hodnotenie>-<autor>-<algoritmus>-<zlozitost>.<pripona>`
  - teda napríklad `sol-75-fero-zametanie-n2.cpp` alebo `sol-100-dezo.py`

- `val*` - validátor
- `check*`, `diff*`, `test*` - hodnotiče

Triedenie potom vyzerá napríklad takto: `sol-vzor` = `sol-vzorak` > `sol` > `sol-100` > `sol-40` > `sol-4` > `sol-wa`.

Ďalej sa automaticky pokúsi zistiť, aký program ste chceli spustiť a prípadne skompiluje, čo treba skompilovať. Ak napríklad zadáte `sol-bf` pokúsi sa nájsť, či tam nie je nejaké `sol-bf.py`, `sol-bf.cpp` ... a pokúsi sa doplniť príponu. Tiež sa pokúsi určiť, ako ste program chceli spustiť, či `./sol.py` alebo `python3 sol.py`. Samozrejme, hádanie nie je dokonalé ale zatiaľ skústenosti ukazujú, že funguje dosť dobre.

Inteligencia sa dá vypnúť pomocou `--no-sort` (triedenie), `--no-compile` (kompilácia), `--execute` (celé automatické rozoznávanie).

### Validátor

Riešenie, ktoré sa začína `val` je považované za validátor. Validátor je program, ktorý na `stdin` dostane vstup a zrúbe sa (`exit 1`), ak vstup nebol správny. Na `stderr` môžete vypísať nejakú krátku správu, že čo bolo zle, na `stdout` radšej nič nepíšte. Pokiaľ nerobíte zveriny, tak sa `stdout` v podstate zahodí.

Validátor navyše dostane ako argumenty názov vstupného súboru rozsekaný podľa bodky. Príklad: `./validator 00 sample a in < 00.sample.a.in`. Tieto argumenty môžete odignorovať, alebo využiť, a napríklad kontrolovať, že ak je číslo sady `01`, tak vstup má byť do 100, ak je číslo sady `02`, vstup má byť do 1000.

### Hodnotič / Checker

Správnosť výstupu sa nehodnotí tak, že ho len porovnáme so vzorovým? Treba checker? Nie je problém.

Hodnotič vie byť automaticky určený ak ako argument uvedieme priečinok v ktorom sa nachádza a hodnotič má štandardné meno, alebo ho vieme manuálne určiť pomocou `-d <program>`.

Podporujeme viacero typov hodnotičov, ktoré ako argumenty berú názvy súborov a budú spúštané vo formáte:

- `diff out_vzor out_test`
- `check inp out_vzor out_test`
- `ch_ito inp out_test out_vzor`
- `test dir name inp out_vzor out_test`

### Zobrazovanie

- Na konci sa zobrazí pekná tabuľka so zhrnutím (vypnete pomocou `--no-statistics`).
- Bežne sa výsledky zobrazujú farebne, dá sa to aj vypnúť (`--boring`).
- Tiež pokiaľ vás otravujú veci, čo vypisujú kompilátory a programy na stderr a podobne, dá sa to schovať pomocou `--quiet`.
- Ak máme na počítači nainštalovaný `time`, beh programov sa meria aj jednotlivo pre _Real/User/System_ čas a tento údaj sa zobrazuje pre každý beh (vieme to vypnúť pomocou `--no-rustime`)
