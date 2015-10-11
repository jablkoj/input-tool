# input-tool
Nástroj, ktorý výrazne zjednodušuje vytváranie a testovanie vstupov pre súťažné programátorské príklady. 
Skladá sa z troch častí -- **input-sample**, **input-generator** a **input-tester**

# Inštalácia
Na **Linuxe** je to dosť jednoduché. Inde to ani nefunguje :)

1. Stiahnite si zdrojáky -- `git clone git@github.com:jablkoj/input-tool.git`. Tento nástroj sa stále vyvíja, takže je fajn
raz za čas stiahnuť najnovšiu verziu. Stačí napísať `git pull` a všetko sa stiahne samé.
2. Spustite `./install.sh`. Tento príkaz vytvorí symlinky vo vnútri vášho  `/usr/local/bin`. 
Potrebuje na to rootovské práva, takže zadajte heslo, keď sa to spýta. Tento príkaz stačí spraviť raz,
**netreba** ho opakovať po update zdrojákov. To je čaro symlinkov. 

# input-sample
Ešte nie je prekódené.

# input-generator

1. Najskôr treba nakódiť **generátor**, ktorý nazvite `gen`, teda napr. `gen.cpp` alebo `gen.py`. 
(Ako generátor môžete teoreticky použiť hociaký príkaz, celkom užitočný je `cat`.)
2. Následne vytvoríte IDF, vysvetlené nižšie
3. Spustíte input-generátor a tešíte sa.

## Generátor
To je program, ktorý berie na vstupe jeden riadok (kde dáte čo chcete, napríklad dve čísla, maximálne $n$ a $m$.)
Tento program vypíše, normálne na stdout, jeden vstup úlohy. Dávajte si pozor, aby bol vypísaný vstup korektný,
žiadne medzery na koncoch riadkov, dodržujte limity, čo slubujete v zadaní. 
Jedna z vecí, čo je dobré robiť je generovať viacero typov vstupov.
(Povedzme náhodné čísla, veľa clustrov rovnakých, samé párne lebo vtedy je bruteforce pomalý, atď.) 
To je dobré riešiť tak, že jedno z čísel, čo generátor dostane na vstupe je typ, 
podľa ktorého sa rozhodne, čo vygeneruje.

O zvyšné veci by sa mal postarať input-generator.

## IDF
IDF -- input description file -- je súbor, ktorý popisuje, ako vyzerajú sady a vstupy. 
Jeden riadok IDF slúži na vyrobenie jedného vstupu (až na špeciálne riadky). 
Každý takýto riadok poslúži ako vstup pre generátor a to, čo generátor vypľuje sa uloží do správneho súboru,
napr. 02.a.in. Čiže do IDF chcete obvykle písať veci ako maximálne $n$ (alebo aj presné $n$), typ vstupu, 
počet hrán grafu, atď., ale to už je na generátori aby sa rozhodol, čo s tými číslami spraví.

Vstupy v jednej sade sú postupne písmenkované a-z (ak je ich veľa, tak sa použije viac písmen). 
Sady v IDF oddeľujeme práznymi riadkami. Sady sú číslované 1..9, ak je ich napr. 20, tak 01..20.

Príklad IDF
```
10 1000 1
20 1000 2
30 1000 3

1000 1000000 1
1000 1000000 2
```
Vyrobí postupne vstupy `1.a.in`, `1.b.in`, `1.c.in`, `2.a.in`, `2.b.in`.

IDF dokáže robiť veľa cool vecí navyše, ale tie ešte nie sú zdokumentované/otestované/naimplementované. 

## Súšťanie

```
$  input-generator idf
$  input-generator -i . -I input -g gen.cpp -qK < idf
#  You can use help to understand the previous line.
$  input-generator -h 
```

**Pozor** si treba dávať na to, že input-generátor, ak mu nepovieme ináč, 
zmaže všetky staré vstupy, okrem samplov.

# input-tester
