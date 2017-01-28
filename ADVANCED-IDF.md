# Používaj IDF ako mág 

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
Ako ste si domysleli, `{batch}` je označenie sady (čo môže byť aj '001'), `{name}` je označenie vstupu v sade a `{id}`
je poradie vstupu od začiatku IDF. Existuje aj `{rand}`, čo vráti pseudonáhodné číslo z [0, 2**31).

Ak chcete niečim inicializovať `seed` vo svojom generátore, tak rozumný nápad je `{id}`, 
pretože to je deterministické a zároveň unikátne pre každý vstup.
Deterministické vstupy majú výhodu, že ak niekto iný pustí `input-generator` s rovnakými parametrami a rovnakým IDF, 
dostane rovnaké vstupy.

### Efekty znakov '#', '@', '$', '!', '~' na začiatku riadku.

- Riadky začínajúce '#' sú ignorované. (t.j. komentáre)
- Riadky začínajúce znakom '~' majú tento znak odstránený so začiatku
  a ďalej sú immúnne voči špeciálnym efektom, s výjnimkou '\' na konci riadku.
- Znaky '@', '$', '!' majú rovnakú funkciu, hoci iný rozsah platnosti a precedenciu. 
  Vo všetkých troch prípadoch, nie je tento riadok chápaný ako popis vstupu, ale konfigurácia pre nasledujúce vstupy.
  Môžeme napríklad nastaviť `@ name=xyz batch=abc` a všetky nasledujúce vstupy sa budú volať `abc.xyz.in`.
  Toto ľahko spôsobí, že si niektoré vstupy premažeme, preto treba používať tieto konfigurátory s rozumom.
  - Rozsahy platnosti sú '@'-všetko, '$'-jedna sada, '!'-jeden vstup, formálnejšie.
    - '!' len pre nasledujúci vstup.
    - '$' platí po najbližší riadok začínajúci '$' alebo po prázdny riadok (oddeľovač sady), podľa toho, čo príde skôr.
      Aplikuje sa, iba ak nie je platný '!' konfigurátor.
    - '@' po najbližší riadok začínajúci '@' a aplikuje sa iba ak neplatí žiaden '$' ano '!' modifikátor
  - Konfigurovať vieme názov sady (batch), názov vstupu v sade (name) a prefix pre názov vstupu (class). 
    Príklady použitia tejto fičúre:
    - Mám Bujov generátor a Janov generátor, každý má svoj IDF. Na začiatku Bujovho IDF dáme `@class=b` a na začiatku
      Janovho `@class=j`. Pustím `input-generator -g gen-buj idf-buj && input-generator -g gen-jano idf-jano -k` 
      a vygeneruje mi to vstupy s disjunktnými názvami (napr. `1.ba.in` a `1.ja.in`). 
      Všimnite si `-k` v druhom spustení, aby sa nezmazali bujove vstupy.
    - Chcem vygenerovať aj sample. Ako?
      Na koniec IDF pridám `$batch=00.sample` a za to parametre sample vstupov. Pozor, sample dávame na koniec, inak 
      by sa nám pokazilo číslovanie ostatných vstupov. 
      
Príklad
```
10
20
$class=prvocislo-
37
47
!name=odpoved
42

$class=viac-nez-sto-
110
120

$batch=0.sample
1
2

!name=este-som-zabudol-jeden
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
           2.viac-nez-sto-a.in  <  110
           2.viac-nez-sto-b.in  <  120
                               .
  4.este-som-zabudol-jeden.in  <  8
```
Všimnite si, že posledný vstup má číslo sady 4 a nie 3. Totiž treta sada je tá sample, ktorá sa len inak volá.
Preto je dôležité dávať sample a custom sady na koniec.
  
### Zalamovanie riadkov
Ak riadok končí znakom '\', je to ako keby pokračoval nasledujúcim riadkom (pričom prípadné efekty znakov
'#', '@', '$', '!', '~', na začiatku ďalšieho riadku sa nevykonávajú).

Príklad
```
# komentár
platí to len # na začiatku riadku
a neplatí to po \
# zalomenom riadku
~# ak chcem zacat mriezkou, pouzijem ~
platia efekty {{name}} {name}
~neplatia efekty {{name}} {name}
!name=z
konfigurator sa vztahuje aj na premene: {name}
```
Sa interpretuje takto
```
platí to len # na začiatku riadku
a neplatí to po # zalomenom riadku
# ak chcem zacat mriezkou, pouzijem ~
platia efekty {name} d
neplatia efekty {{name}} {name}
konfigurator sa vztahuje aj na premene: z
```
