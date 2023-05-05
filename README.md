## Zmeny voči jablkoj

<details>
<summary>Zmeny</summary>

- **Podpora priečinkov v zozname programov** (automatické načítanie všetkých riešení, validátorov a checkera z priečinku)
- Časovanie
  - Desatinný timelimit `-t 0.5`
  - **Jazykový timelimit** `-t "3,cpp=1,py=5"`
  - Detailnejšie vypisovanie trvania programov
    - **Milisekundová presnosť**
    - Zobrazovanie celkového času namiesto _User time_
    - Vypisovanie _Real/User/System time_
    - TLE čas sa neráta do `Max time`
  - Varovný timelimit pomocou `--wtime`
- Lepšie predvolené nastavenia
  - **Preskakovanie zvyšných vstupov** v sade po odmietnutí (vypnúť cez `-F`)
  - Štatistiky po vyhodnotení (vypnúť cez `--no-statistics`)
  - **Kompilovanie C++ s optimalizáciami a novším štandardom**
  - Zvýšené limity pre pamäť a zásobník
  - **Deduplikovanie programov na vstupe** (spolu s `-K` umožnuje rýchlejšie testovanie, vypnúť cez `--dupprog`)
  - **Paralelné generovanie vstupov** (pomocou prepínača `-j`)
- Podpora alternatívnych Python interpreterov (**PyPy**) pomocou `--pythoncmd cmd`
- **Rozšírená funkcionalita IDF o vlastné premenné**
- Možnosť nemať nainštalovaný `time`
- Kompilovanie Java riešení v dočasnom priečinku
- Informovanie o neúspešnom generovaní vstupov
- Sformátovaný a otypovaný kód
- Prepísané README
- Bugfixes

</details>

## Rýchlokurz

```bash
# napíšeme si riešenia, generátor, idf.txt a potom:
input-sample zadanie.md # nepovinné
input-generator idf.txt
input-tester .

# o pomoc požiadame `input-<program> -h`, napríklad:
input-generator -h
```

# `input-tool`

Nástroj, ktorý výrazne zjednodušuje vytváranie a testovanie vstupov pre súťažné programátorské príklady. Skladá sa z troch častí &ndash; **`input-sample`**, **`input-generator`** a **`input-tester`**.

## Inštalácia

Na **Linuxe** je to dosť jednoduché.

1. Prerekvizity:

   - Potrebujete `python3`
   - Odporúčame `time` (nestačí bashová funkcia)
   - Potrebujete kompilátory C/C++ (kompilujeme pomocou `make`), Pascalu (`fpc`), Javy, Rustu (`rustc`) &ndash; samozrejme iba pre jazyky ktoré plánujete spúštať

2. Nainštalujte cez `pip`:

   ```bash
   pip install git+https://github.com/fezjo/input-tool.git
   # alebo
   git clone git@github.com:fezjo/input-tool.git
   pip install -e .
   ```

   Aktualizuje sa pomocou:

   ```bash
   pip install -U git+https://github.com/fezjo/input-tool.git
   # alebo
   git pull
   ```

# `input-sample`

Tento skript dostane na vstupe (alebo ako argument) zadanie príkladu. Vyrobí (defaultne v priečinku `./test`) sample vstupy a sample výstupy pre tento príklad.

Defaultne pomenúva súbory `00.sample.in` resp. `00.sample.x.in`, ak je ich viac. Viete mu povedať, aby pomenúval vstupy inak, napr. `0.sample.in`, alebo `00.sample.a.in` aj keď je len jeden vstup. Dá sa nastaviť priečinok, kde sa vstupy a výstupy zjavia, a tiež prípony týchto súborov.

Príklady použitia:

```bash
input-sample -h
input-sample prikl1.md
input-sample -p 0.sample < cesta/k/zadaniam/prikl2.md
```

# `input-generator`

1. Najskôr treba nakódiť **generátor**, ktorý nazvite `gen` (teda napr. `gen.cpp` alebo `gen.py`).
2. Následne vytvoríte **IDF**, vysvetlené nižšie.
3. Spustíte `input-generator` pomocou `input-generator idf` a tešíte sa.

## Generátor

Názov generátoru sa začína `gen` (napríklad `gen.cpp`). Generátor je program, ktorý berie na vstupe jeden riadok (kde dáte čo chcete, napríklad dve čísla, maximálne $n$ a $m$.) Tento program vypíše, normálne na `stdout`, jeden vstup úlohy.

Dávajte si pozor, aby bol vypísaný vstup korektný, žiadne medzery na koncoch riadkov, dodržujte limity, čo sľubujete v zadaní (toto všetko vieme automatizovane zaručiť s pomocou validátora). Jedna z vecí, čo je dobré robiť, je generovať viacero typov vstupov. (Povedzme náhodné čísla, veľa clustrov rovnakých, samé párne lebo vtedy je bruteforce pomalý, atď.) To je dobré riešiť tak, že jedno z čísel, čo generátor dostane na vstupe je typ, podľa ktorého sa rozhodne, čo vygeneruje.

```bash
# Odporúčané je použiť základný tvar:
input-generator idf
```

## IDF

IDF (Input Description File) je súbor, ktorý popisuje, ako vyzerajú sady a vstupy. Jeden riadok IDF slúži na vyrobenie jedného vstupu (až na špeciálne riadky). Každý takýto riadok poslúži ako vstup pre generátor a to, čo generátor vypľuje sa uloží do správneho súboru, napr. `02.a.in`. Čiže do IDF chcete obvykle písať veci ako maximálne $n$ (alebo aj presné $n$), typ vstupu, počet hrán grafu, atď., ale to už je na generátori aby sa rozhodol, čo s tými číslami spraví.

Sady v IDF oddeľujeme práznymi riadkami. Sady sú číslované `1..9`, ak je ich napr. `20`, tak `01..20`. Vstupy v jednej sade sú postupne písmenkované `a-z` (ak je ich veľa, tak sa použije viac písmen).

Príklad IDF

```
# id pocet_vrcholov pocet_hran pocet_hracov
# 1. sada
{id} 10 1000 1
{id} 20 1000 2
{id} 30 1000 3

# 2.sada
$ hran=1000000
{id} 1000 {hran} 1
{id} 1000 {hran} 2
```

Vyrobí postupne vstupy `1.a.in`, `1.b.in`, `1.c.in`, `2.a.in`, `2.b.in`.

**Ak chcete niečim inicializovať `seed` vo svojom generátore, tak rozumný nápad je `{id}`**, pretože to je deterministické a zároveň unikátne pre každý vstup. Deterministické vstupy majú výhodu, že ak niekto iný pustí `input-generator` s rovnakými parametrami a rovnakým IDF, dostane rovnaké vstupy.

# `input-tester`

Cieľom tohto skriptu je otestovať všetky riešenia na vstupoch, overiť, či dávajú správne výstupy, zmerať čas behu a podobne.

**Pozor**, slúži to len na domáce testovanie, netestujte tým nejaké reálne kontesty, kde môžu užívatelia submitovať čo chcú. Nemá to totiž žiaden sandbox ani žiadnu ochranu pred neprajníkmi.

`input-tester` sa používa veľmi jednoducho. Iba spustíte `input-tester <zoznam riešení>` a ono to porobí všetko samé.

Odporúčame mať na konci `.bashrc` alebo pri spustení terminálu nastaviť kompilátory podobne ako sú na testovači, teda napríklad `export CXXFLAGS="-O2 -std=gnu++11 -Wno-unused-result -DDG=1"`.

Riešenia pomenúvame s prefixom '`sol`' štýlom `sol-<hodnotenie>-<autor>-<algoritmus>-<zlozitost>.<pripona>`. Teda názov má podmnožinu týchto častí v tomto poradí, teda napríklad `sol-75-fero-zametanie-n2.cpp` alebo `sol-100-dezo.py`. Validátor má prefix '`val`', prípadný hodnotič '`check`'.

### Generovanie výstupov

Ak ešte neexistuje vzorový výstup ku nejakému vstupu (teda napríklad ste práve vygenerovali vstupy), použije sa prvý program na jeho vygenerovanie. Ostatné programy porovnávajú svoje výstupy s týmto.

Dôležité je, aby program, ktorý generuje výstupy zbehol na všetkých vstupoch správne. Pokial by sa niekde zrúbal/vyTLEl, tak môžu byť výstupy pošahané.

## Užitočné prepínače

### `-t --time`

Neoptimálne riešenia by často bežali zbytočne dlho, ak vôbec aj dobehli. Tento argument nastaví časový limit v sekundách. Vie to byť desatinné číslo. Vie to byť rôzne pre jednotlivé jazyky. Napríklad `-t 1`, `t -0.5` alebo `-t "3,cpp=1,py=5"`.

### `-F --no-fskip`

Štandardne sa programy, ktoré na niektorom vstupe zlyhali nevyhodnocujú na zvyšných testov v danej sade. Takto to funguje na niektorých súťažiach a urýchľuje to testovanie napríklad bruteforcov. Často však takéto správanie necheme a preto ho môžeme týmto argumentom vypnúť.

### `-R --Reset`

Už existujú výstupy ale sú zlé? `-R` prepíše výstupy nanovo tým, čo vyrobí prvý program.

### `-K --keep-bin`

Ponecháva binárne súbory po kompilácii, čím sa značne urýchľuje celkový čas testovania. Je možné, že sa na začiatku vypíše veľa varovaní &ndash; malo by to byť vporiadku, ale treba ich zohľadniť a dávať si pozor.

### `-d --diff`

Niektoré úlohy potrebujú na určenie správnosti hodnotič. Ten vie byť automaticky určený ak ako argument uvedieme priečinok v ktorom sa nachádza a hodnotič má štandardné meno. Ak tieto podmienky nie sú splnené, vieme ho manuálne určiť pomocou tohoto argumentu, napríklad `-d checker.py`.

### `--pythoncmd`

Niekedy by sme boli radi, keby Python nebol taký pomalý. To sa dá väčšinou vyriešiť použitím _PyPy_ interpretera. Dokážeme to určiť pomocou tohoto argumentu, použitím `--pythoncmd pypy`.

### Príklady

```bash
# pomoc!
input-tester -h
# najzákladnejšie použitie, keď máme všetko v aktuálnom priečinku
input-tester .
# chceme si ušetriť kompiláciu pri dodatočnom spustení
input-tester -K .
# chceme spustiť iba vzorové riešenia
input-tester -K sol-100*
# chceme vidieť na ktorých všetkých vstupoch programy nefungujú, nielen na ktorých sadách
input-tester -KF .
# bežné použitie, ak si dáme všetky riešenia do priečinku `sols`
input-tester -K -t "3,cpp=0.5,py=5" sols .
```

# Pokročilé

Ak chcete vedieť, aké cool veci navyše dokážu `input-generator` a `IDF`, prečítajte si o nich v súbore [`GENERATOR.md`](GENERATOR.md).

Ak chcete vedieť, aké cool veci navyše dokáže `input-tester` a **ako písať validátor a hodnotič**, prečítajte si o tom v súbore [`TESTER.md`](TESTER.md).

# Feedback

Ak vám niečo nefunguje, alebo vám chýba nejaká funkcionalita, napíšte mi, prosím, mail alebo vyrobte issue.
