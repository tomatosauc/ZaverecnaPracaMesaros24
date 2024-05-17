README.md

# Úvod

Môj prvý, dlhodobejší projekt, na ktorom som pracoval dlho. Je to jednuduchý softvér na vytváranie zasadacích poriadkov, napríklad pre testové obdobia. Je potrebné, aby celý tento priečinok bol uložený priamo v priečinku užívateľa. 

# Python a jeho knižnice

Odporúčam verziu Pythonu 3.12, alebo 3.11, kvôli match statementom. 

## Knižnice

Knižnica Pillow (PIL) je podstatnou knižnicou tohto projektu. Pre jej inštaláciu sa obráťte ku kapitole "Inštalácia knižnice pillow".

V prípade, že program sa odmietne skompilovať, kvoli knižnici s menom psycopg2 (čo by ale nemalo nastať), tak oprava je jednoduchá. Na riadku 70 stačí zmeniť 'import psycopg2 as db_connection' na 'db_connection=""'. Jedinná nefunkčnosť tejto opravy je tá, že užívateľ nemôže používať databázu na uskladnenie dát.

### Inštalácia knižnice pillow

Pre počítače s operačným systémom Windows:
- Otvorte príkazový riadok
- Zadajte nasledujúci príkaz
```
pip install pillow
```
- Počkajte na dokončenie inštalácie

Pre počítače s operačným systémom MacOS:
- Otvorte Terminal
- Zadajte nasledujúci príkaz
```
pip3 install pillow --break-system-packages
```
- Počkajte na dokončenie inštalácie
# Obsah súboru

Skrytý priečinok obsahuje iba súbory so zoznammi žiakov. Tieto súbory sú otvoriteľné v akomkoľvek textovom editore. Zahrnuté su triedy Owls a Zingers. Samotný program je možné bežať odkiaľkoľvek z počítača.

--Tomas Mesaros--