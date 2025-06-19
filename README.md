# Solitario Console - Versione Refactorizzata
**AVVISO IMPORTANTE**: Se vedi le colonne delle carte del gioco nel terminale in modo distorto devi semplicemente allargare la finestra del terminale!

Un gioco del Solitario (Klondike) da terminale, scritto in Python con **sistema di rimescolamento migliorato** e **gestione avanzata degli scarti**. Permette di giocare con carte colorate e comandi da tastiera, seguendo le regole classiche del solitario con funzionalità aggiuntive per un'esperienza più realistica.

## 🆕 Novità della Versione Refactorizzata

### ✨ **Funzionalità Migliorate**
- **Sistema di scarti realistico**: Le carte non utilizzate vengono gestite correttamente
- **Rimescolamento automatico intelligente**: Quando il mazzo finisce, gli scarti vengono automaticamente rimescolati
- **Rimescolamento manuale**: Controllo completo del rimescolamento con comando dedicato
- **Informazioni dettagliate**: Visualizzazione del conteggio di mazzo, riserva e scarti
- **Debug scarti**: Visualizzazione delle carte negli scarti per controllo (quando sono poche)
- **Feedback migliorato**: Messaggi più informativi per ogni azione

### 🎮 **Nuovi Comandi**
- **`[sc]`** - Scarta la carta attualmente in riserva (la sposta negli scarti)
- **`[r]`** - Rimescola manualmente gli scarti nel mazzo (solo quando il mazzo è vuoto)

## Caratteristiche
- Visualizzazione delle carte in colonne e pile finali
- Colori per i semi (rosso per ♥ e ♦, bianco per ♠ e ♣)
- Comandi semplici da tastiera
- Gestione completa di pesca, spostamenti e fondazioni
- **Sistema di scarti avanzato con rimescolamento realistico**
- **Informazioni dettagliate sullo stato del gioco**
- **Controlli di debug per sviluppatori**

## Requisiti
- Python 3.7+
- [colorama](https://pypi.org/project/colorama/)

## Installazione
1. Clona o scarica questo repository
2. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```
   oppure
   ```bash
   pip install colorama
   ```

## Avvio del gioco
Esegui il file principale:
```bash
python src/solitario.py
```

## 🎯 Comandi di gioco

### Comandi Base
- **`[p]`** Pesca una carta dal mazzo
- **`[s]`** Sposta carte tra colonne
- **`[f]`** Sposta la carta in cima a una colonna verso le pile finali
- **`[m]`** Sposta la carta pescata dal mazzo a una colonna (scegli tu la colonna)
- **`[mf]`** Sposta la carta pescata dal mazzo alle pile finali
- **`[q]`** Esci dal gioco

### 🆕 Comandi Avanzati
- **`[sc]`** **Scarta carta riserva** - Sposta la carta attualmente in riserva negli scarti
- **`[r]`** **Rimescola scarti** - Rimescola manualmente gli scarti nel mazzo (solo se mazzo vuoto)

## 📊 Informazioni Visualizzate

Durante il gioco vedrai:
```
Carte disponibili: Mazzo(15) + Riserva(1) + Scarti(8) = 24
Carta in riserva: [7♠]
Scarti: 8 carte (troppe per essere mostrate)
```

- **Conteggio carte**: Numero esatto di carte in mazzo, riserva e scarti
- **Carta in riserva**: La carta attualmente utilizzabile dalla riserva
- **Debug scarti**: Visualizzazione degli scarti (se pochi) o conteggio se troppi

## 🔄 Sistema di Rimescolamento

### Rimescolamento Automatico
Quando il mazzo è vuoto e provi a pescare:
- Se ci sono carte negli scarti → **rimescolamento automatico**
- Se c'è solo una carta in riserva → suggerimento di scartarla prima

### Rimescolamento Manuale
- Usa `[r]` per rimescolare gli scarti quando il mazzo è vuoto
- Controllo completo del timing di rimescolamento

## Note sui colori
- I semi ♥ e ♦ sono visualizzati in rosso, ♠ e ♣ in bianco (per leggibilità su sfondo scuro)
- L'allineamento delle carte è gestito per mantenere la tabella ordinata anche con i colori

## Esempio di output
```
--- TAVOLO ---
[2♥]            [#]             [#]             [#]             [#]             [#]             [#]
                [7♣]            [#]             [#]             [#]             [#]             [#]
                                [5♦]            [#]             [#]             [#]             [#]
                                                [A♠]            [#]             [#]             [#]
                                                                [K♣]            [#]             [#]
                                                                                [J♥]            [#]
                                                                                                [Q♦]
[#] = Carta Coperta

--- PILE FINALI ---
♠: [  ]    ♥: [  ]    ♦: [  ]    ♣: [  ]
```

## 🎮 Strategia di Gioco

### Consigli per Principianti
1. **Scopri sempre le carte coperte** quando possibile
2. **Muovi gli Assi alle pile finali** appena disponibili
3. **Libera le colonne vuote** per posizionare i Re
4. **Usa gli scarti strategicamente** - non scartare carte utili troppo presto

### Gestione Avanzata
- **Pianifica i rimescolamenti**: Scarta carte non utili prima che il mazzo finisca
- **Monitora il conteggio**: Usa le informazioni dettagliate per pianificare le mosse
- **Debug mode**: Usa la visualizzazione degli scarti per tracciare le carte

## 🔧 Caratteristiche Tecniche

### Miglioramenti del Codice
- **Documentazione completa** con header dettagliato
- **Gestione errori robusta** per tutti i casi edge  
- **Separazione delle responsabilità** tra classi
- **Metodi di utilità** per conteggio e debug
- **Codice modulare e manutenibile**

### Sistema di Scarti Realistico
```python
def rimescola(self, scarti):
    """
    Aggiunge le carte scartate al mazzo esistente e rimescola tutto insieme.
    Più realistico: nel solitario reale non si butta via il mazzo residuo.
    """
```

## File del Progetto
- `solitario_test_refactoring.py` - **Versione principale refactorizzata** (consigliata)
- `solitario.py` - Versione originale base
- `requirements.txt` - Dipendenze del progetto

## Autore
- Progetto sviluppato da **Jechiu Mircea**
- Versione refactorizzata con sistema di scarti avanzato e miglioramenti UX
