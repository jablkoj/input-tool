# Generátor

Generátor je program, ktorý berie na vstupe jeden riadok (kde dáte čo chcete, napríklad dve čísla, maximálne $n$ a $m$.) Tento program vypíše, normálne na `stdout`, jeden vstup úlohy.

Dávajte si pozor, aby bol vypísaný vstup korektný, žiadne medzery na koncoch riadkov, dodržujte limity, čo sľubujete v zadaní (toto všetko vieme automatizovane zaručiť s pomocou validátora).

Jedna z vecí, čo je dobré robiť, je generovať viacero typov vstupov &ndash; povedzme náhodné čísla, veľa clustrov rovnakých, samé párne lebo vtedy je bruteforce pomalý, atď. To je dobré riešiť tak, že jedno z čísel, čo generátor dostane na vstupe je typ, podľa ktorého sa rozhodne, čo vygeneruje.

Generátor sa bežne volá `gen` (príponu si `input-tool` vie domyslieť, takže `gen.py`, `gen.cpp`, `gen.pas`, ... je všetko obsiahnté pod `gen`). Ak sa váš generátor volá inak, treba to povedať testeru pomocou prepínača `-g`.

Keď chcete commitnúť vstupy na git, commitujete zdrojový kód generátoru a `idf`, nie binárku a vygenerované vstupy.

O zvyšné veci by sa mal postarať `input-generator`.

### Spúšťanie

Pokiaľ robíte vstupy do KSP, odporúčané je púšťať `input-generator idf` bez prepínačov, aby ostatní vedúci vedeli vygenerovať rovnaké vstupy. Prepínače slúžia hlavne na to, ak robíte vstupy pre nejakú inú súťaž, kde sú iné prípony/ iná priečinková štruktúra. Iné prepínače zasa pomáhajú pri debugovaní.

Pokiaľ potrebujete robiť zveriny, napríklad použiť viac generátorov na jednu úlohu, toto sa dá špecifikovať v IDF.

```
# Odporúčané je použiť defaultný tvar:
$ input-generator idf

# Keď potrebujete, dá sa však spraviť mnoho iných vecí
$ input-generator -i . -I input -g gen-special.cpp -qK < idf

# Pre pochopenie predošlého riadku spustite
$ input-generator -h
```

**Pozor** si treba dávať na to, že `input-generator`, ak mu nepovieme prepínačom inak, zmaže všetky staré vstupy, okrem samplov.

# Používaj IDF ako mág

V tomto texte si prezradíme nejak pokročilé funkcie a fičúrie IDF. Niektoré z nich sa vám môžu hodiť.

## Základné použitie IDF

IDF (Input Description File) je súbor, ktorý popisuje, ako vyzerajú sady a vstupy. Jeden riadok IDF slúži na vyrobenie jedného vstupu (až na špeciálne prípady popísané nižšie). Každý takýto riadok poslúži ako vstup pre generátor a to, čo generátor vypľuje sa uloží do správneho súboru, napr. `02.a.in`. Čiže do IDF chcete obvykle písať veci ako maximálne $n$ (alebo aj presné $n$), typ vstupu, počet hrán grafu, atď., ale to už je na generátore, aby sa rozhodol, čo s tými číslami spraví.

Asi je fajn upozorniť, že zo začiatku a konca každého riadku v IDF sú odstránené biele znaky. Hlavný účel IDF totiž je, aby určoval, čo dostane na vstupe genrátor, nie ako presne vyzerá výsledný vstup. Keďže je možné použiť aj príkazy typu `cat` ako generátor, biele znaky vedia niekedy zavážiť.

Vstupy v jednej sade sú postupne písmenkované `a`..`z` (ak je ich veľa, tak sa použije viac písmen).

Sady v IDF oddeľujeme práznymi riadkami. Sady sú číslované `1`..`9`, ak je ich napr. 20, tak `01`..`20`.

### Príklad IDF

```
10 1000 ciara
20 1000 nahodne
30 1000 hviezda

1000 1000000 ciara
1000 1000000 nahodne
```

Vyrobí postupne vstupy `1.a.in`, `1.b.in`, `1.c.in`, `2.a.in`, `2.b.in`. V tomto návode (aj v tom, čo vypisuje `input-generator`) sa používa nasledovná notácia

```
1.a.in  <  10 1000 ciara
```

čo znamená, že generátoru dáme na vstup `"10 1000 ciara"` a to, čo generátor vypľuje, sa uloží do súboru `1.a.in`.

## Špeciálne premenné

- `{batch}` &ndash; označenie sady (môže byť napríklad aj '001')
- `{name}` &ndash; označenie vstupu v sade
- `{id}` &ndash; poradie vstupu od začiatku IDF
- `{rand}` &ndash; pseudonáhodné číslo z [0, 2\*\*31)
- **`{nazov_premennej}` &ndash; hodnota premennej (vieme si vytvárať vlastné premenné pomocou `$+ nazov_premennej=<hodnota>`)**
- `{{nazov_premennej}}` &ndash; text '`{nazov_premennej}`'

Ak chcete svojmu generátoru povedať, aký vstup vyrába, nie je problém. Nasledujúci IDF:

```
{batch} {name} {id}
{batch} {name} {id} 47

{batch} {name} {id}
{id} {name}
{{name}} {{id}}
```

Vyrobí vstupy podľa:

```
1.a.in  <  1 a 1
1.b.in  <  1 b 2 47
        .
2.a.in  <  2 a 3
2.b.in  <  4 b
2.c.in  <  {name} {id}
```

**Ak chcete niečim inicializovať `seed` vo svojom generátore, tak rozumný nápad je `{id}`**, pretože to je deterministické a zároveň unikátne pre každý vstup. Deterministické vstupy majú výhodu, že ak niekto iný pustí `input-generator` s rovnakými parametrami a rovnakým IDF, dostane rovnaké vstupy.

## Efekty znakov '`#`', '`$`', '`~`', `\`'

- Riadky začínajúce '`#`' sú ignorované (čiže sú to komentáre).
- Riadky začínajúce znakom '`~`' majú tento znak odstránený so začiatku a ďalej sú immúnne voči špeciálnym efektom, s výjnimkou '`\`' na konci riadku.
- Riadok začínajúci '`$`' nie je chápaný ako popis vstupu, ale ako konfigurácia pre nasledujúce vstupy. Môžeme napríklad nastaviť `$ name=xyz batch=abc` a všetky nasledujúce vstupy sa budú volať `abc.xyz.in`.
- Riadky **končiace** '`\`' majú nasledujúci riadok ako súčasť toho istého vstupu

### Konfigurácia pomocou '`$`'

Konfigurácia platí až po najbližší riadok začínajúci `$`.

Ak sa viacero vstupov volá rovnako, jednoducho sa premažú, preto treba používať tieto konfigurátory s rozumom.

Konfigurovať vieme:

- názov sady (`batch`)
- názov vstupu v sade (`name`)
- prefix pre názov vstupu (`class`)
- generátor (`gen`)
- ľubovoľnú vlastnú premennú

Keďže whitespace-y slúžia na oddeľovanie parametrov, nepoužívajte ich v hodnotách parametrov.

Táto fičúra sa môže hodiť na riešenie nasledovných problémov:

- Mám Bujov generátor a Janov generátor, každý má svoj IDF. Chcem aby neboli kolízie medzi názvami vstupov.  
   _Riešenie:_
  Na začiatku Bujovho IDF dáme `$class=b` a na začiatku Janovho `$class=j`. Pustím `input-generator -g gen-buj idf-buj && input-generator -g gen-jano idf-jano -k` a vygeneruje mi to vstupy s disjunktnými názvami (napr. `1.ba.in` a `1.ja.in`). Všimnite si `-k` v druhom spustení, ktoré spôsobí, aby sa nezmazali Bujove vstupy.
- Mám tri generátory, a chcem mať len jeden IDF.  
  _Riešenie:_ Použijem `$gen=nazovgeneratora`, na správnych miestach.
- Chcem vygenerovať aj sample.  
  _Riešenie:_ Na koniec IDF pridám `$batch=00.sample` a za to parametre sample vstupov. Pozor, sample dávame na koniec, aby sa nám nepokazilo číslovanie ostatných sád.

### Príklady správania konfigurátorov

- ### IDF príklad 1

  ```
  10
  20
  $class=prvocislo-
  37
  47
  $name=odpoved
  # všimnime si, že s predošlým riadkom prestalo platiť class=prvocislo-
  42

  $batch=0.sample
  1
  2

  $name=este-som-zabudol-jeden
  8
  ```

  Vyrobí vstupy takto:

  ```
                  0.sample.a.in  <  1
                  0.sample.b.in  <  2
                                .
                        1.a.in  <  10
                        1.b.in  <  20
                  1.odpoved.in  <  42
              1.prvocislo-c.in  <  37
              1.prvocislo-d.in  <  47
                                .
    3.este-som-zabudol-jeden.in  <  8
  ```

  Všimnite si, že posledný vstup má číslo sady 3 a nie 2. Totiž druhá sada je tá sample, ktorá sa len inak volá. Preto je dôležité dávať sample a custom sady na koniec.

- ### IDF príklad 2

  ```
  # komentár
  platí to len # na začiatku riadku
  a neplatí to pri \
  # viacriadkových vstupoch
  ~# ak chcem začat mriežkou, použijem ~
  platia efekty {{name}} {name}
  ~neplatia efekty {{name}} {name}
  $name=z
  konfigurátor sa vzťahuje aj na premenné: {name}
  ```

  Sa interpretuje takto:

  ```
  platí to len # na začiatku riadku
  a neplatí to pri \n# viacriadkových vstupoch
  # ak chcem začat mriežkou, použijem ~
  platia efekty {name} d
  neplatia efekty {{name}} {name}
  konfigurátor sa vzťahuje aj na premenné: z
  ```

## Viacriadkové vstupy

Ak chcete, dať svojmu generátoru viac riadkový vstup, použite '`\`'. Ak riadok končí znakom '`\`', nasledujúci riadok bude tiež súčasťou tohto vstupu. Prípadné efekty znakov '`#`', '`$`', '`~`', na začiatku ďalšieho riadku sa nevykonávajú.

Príklad:

```
$gen=cat batch=0.sample
4\
1 2 3 4
3\
    1 2 3
```

Vyrobí dva sample vstupy. Všimnite si, že v IDF sa ignorujú biele znaky na začiatkoch a koncoch riadkov.

```
4
1 2 3 4
```

```
3
1 2 3
```
