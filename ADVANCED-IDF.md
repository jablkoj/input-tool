# Používaj IDF ako mág 

V tomto texte si prezradíme nejak pokročilé funkcie a fičúrie IDF. Niektoré z nich sa vám môžu hodiť.
Asi je fajn upozorniť, že zo začiatku a konca každého riadku v IDF sú odstránené biele znaky. 
Hlavný účel IDF totiž je, aby určoval, čo dostane na vstupe genrátor, nie ako presne vyzerá výsledn vstup. Keďže je možné použiť aj príkazy typu `cat` ako generátor, biele znaky vedia niekedy zavážiť. 
 
### Špeciálne premenné
Ak chcete svojmu generátoru povedať, aký vstup vyrába, nie je problém. Nasledujúci IDF
```
{batch} {name} {id}
{batch} {name} {id} 47

{batch} {name} {id}
{id} {name}
{{name}} {{id}}
```
Vyrobí vstupy podľa
```
1.a.in  <  1 a 1
1.b.in  <  1 b 2 47
        .
2.a.in  <  2 a 3
2.b.in  <  4 b
2.c.in  <  {name} {id}
```
Ako ste si asi domysleli, `{batch}` je označenie sady (čo môže byť aj '001'), `{name}` je označenie vstupu v sade a `{id}`
je poradie vstupu od začiatku IDF. Existuje aj `{rand}`, čo vráti pseudonáhodné číslo z [0, 2**31).

Ak chcete niečim inicializovať `seed` vo svojom generátore, tak rozumný nápad je `{id}`, 
pretože to je deterministické a zároveň unikátne pre každý vstup.
Deterministické vstupy majú výhodu, že ak niekto iný pustí `input-generator` s rovnakými parametrami a rovnakým IDF, 
dostane rovnaké vstupy.

### Efekty znakov '#', '$', '~' na začiatku riadku

- Riadky začínajúce '#' sú ignorované (čiže sú to komentáre).
- Riadky začínajúce znakom '~' majú tento znak odstránený so začiatku
  a ďalej sú immúnne voči špeciálnym efektom, s výjnimkou '\' na konci riadku.
- Riadok začínajúci '$' nie je chápaný ako popis vstupu, ale ako konfigurácia pre nasledujúce vstupy. 
  Môžeme napríklad nastaviť `$ name=xyz batch=abc` a všetky nasledujúce vstupy sa budú volať `abc.xyz.in`.
  Konfigurácia platí až po najbližší riadok začínajúci '$'.
  Ak sa viacero vstupov volá rovnako, jednoducho sa premažú, preto treba používať tieto konfigurátory s rozumom.
  
  - Konfigurovať vieme názov sady (batch), názov vstupu v sade (name), prefix pre názov vstupu (class), a generátor (gen).
    Keďže whitespace-y slúžia na oddeľovanie parametrov, nepoužívajte ich v hodnotách parametrov.
    Táto fičúra sa môže hodiť na riešenie nasledovných problémov:
    - Mám Bujov generátor a Janov generátor, každý má svoj IDF. Chcem aby neboli kolízie medzi názvami vstupov. 
      Riešenie -- na začiatku  Bujovho IDF dáme `$class=b` a na začiatku Janovho `$class=j`. Pustím 
      ```
      input-generator -g gen-buj idf-buj && input-generator -g gen-jano idf-jano -k
      ```
      a vygeneruje mi to vstupy s disjunktnými názvami (napr. `1.ba.in` a `1.ja.in`). 
      Všimnite si `-k` v druhom spustení, ktoré spôsobí, aby sa nezmazali Bujove vstupy.
    - Mám tri generátory, a chcem mať len jeden IDF. Riešenie použijem $gen=nazovgeneratora, na správnych miestach.
    - Chcem vygenerovať aj sample. Riešenie
      Na koniec IDF pridám `$batch=00.sample` a za to parametre sample vstupov. Pozor, sample dávame na koniec, aby 
      sa nám nepokazilo číslovanie ostatných sád. 
      
Príklad správania konfigurátorov
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
Všimnite si, že posledný vstup má číslo sady 3 a nie 2. Totiž druhá sada je tá sample, ktorá sa len inak volá.
Preto je dôležité dávať sample a custom sady na koniec.
  
### Viacriadkové vstupy
Ak chcete, dať svojmu generátoru viac riadkový vstup, použite '\'.
Ak riadok končí znakom '\', nasledujúci riadok bude tiež súčasťou tohto vstupu, pričom prípadné efekty znakov
'#', '$', '~', na začiatku ďalšieho riadku sa nevykonávajú.

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

Ďalšie príklady 
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
Sa interpretuje takto
```
platí to len # na začiatku riadku
a neplatí to pri \n# viacriadkových vstupoch
# ak chcem začat mriežkou, použijem ~
platia efekty {name} d
neplatia efekty {{name}} {name}
konfigurátor sa vzťahuje aj na premenné: z
```
