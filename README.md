# Solitario Console

Un gioco del Solitario (Klondike) da terminale, scritto in Python. Permette di giocare con carte colorate e comandi da tastiera, seguendo le regole classiche del solitario.

## Caratteristiche
- Visualizzazione delle carte in colonne e pile finali
- Colori per i semi (rosso per ♥ e ♦, bianco per ♠ e ♣)
- Comandi semplici da tastiera
- Gestione completa di pesca, spostamenti e fondazioni

## Requisiti
- Python 3.7+
- [colorama](https://pypi.org/project/colorama/)

## Installazione
1. Clona o scarica questo repository
2. Installa le dipendenze:
   ```bash
   pip install colorama
   ```

## Avvio del gioco
Esegui il file principale:
```bash
python Solitario.py
```

## Comandi di gioco
- `[p]` Pesca una carta dal mazzo
- `[s]` Sposta carte tra colonne
- `[f]` Sposta la carta in cima a una colonna verso le pile finali
- `[m]` Sposta la carta pescata dal mazzo a una colonna (scegli tu la colonna)
- `[mf]` Sposta la carta pescata dal mazzo alle pile finali
- `[q]` Esci dal gioco

## Note sui colori
- I semi ♥ e ♦ sono visualizzati in rosso, ♠ e ♣ in bianco (per leggibilità su sfondo scuro)
- L'allineamento delle carte è gestito per mantenere la tabella ordinata anche con i colori

## Esempio di output
```
--- TAVOLO ---
[2♥]            [#]             [#]             [#]             [#]             [#]             [#]
                [7♣]            [#]             [#]             [#]             [#]             [#]
...

--- PILE FINALI ---
♠: [  ]    ♥: [  ]    ♦: [  ]    ♣: [  ]
```

## Autore
- Progetto sviluppato con l'aiuto di ChatGPT 