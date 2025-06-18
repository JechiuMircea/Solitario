"""
SOLITARIO - VERSIONE CON RIMESCOLAMENTO MIGLIORATO
==================================================
Questa è una versione refactorizzata di solitario.py con un sistema di rimescolamento più realistico.

NOVITÀ IMPLEMENTATE:
- Sistema di scarti: le carte non utilizzate vengono messe negli scarti
- Rimescolamento automatico: quando il mazzo finisce, gli scarti vengono automaticamente rimescolati
- Rimescolamento manuale: comando [r] per rimescolare gli scarti quando il mazzo è vuoto
- Comando scarta: comando [sc] per spostare la carta in riserva negli scarti
- Informazioni dettagliate: mostra il conteggio di mazzo, riserva e scarti
- Debug scarti: mostra le carte negli scarti (se poche) per controllo

COMANDI AGGIUNTIVI:
[sc] - Scarta la carta attualmente in riserva (la sposta negli scarti)
[r]  - Rimescola manualmente gli scarti nel mazzo (solo se mazzo vuoto)
"""

import random  # Importa il modulo random, usato per mescolare le carte e generare casualità nel gioco
from colorama import init, Fore, Style  # Importa le funzioni e costanti di colorama per colorare il testo nel terminale
import re  # Importa il modulo re, usato per le espressioni regolari (ad esempio per rimuovere i codici colore ANSI)

# --- Costanti ---
SEMI = ['♠', '♥', '♦', '♣']  # Lista dei semi delle carte
VALORI = ['A'] + [str(n) for n in range(2, 11)] + ['J', 'Q', 'K']  # Lista dei valori delle carte
COLORI = {'♠': 'N', '♣': 'N', '♥': 'R', '♦': 'R'}  # Dizionario che associa ogni seme al suo colore

# =============================================================================
# --- Classe Carta ---
# =============================================================================
class Carta:
    def __init__(self, valore, seme, coperta=True):  # Costruttore della carta
        self.valore = valore  # Valore della carta (A, 2-10, J, Q, K)
        self.seme = seme      # Seme della carta (♠, ♥, ♦, ♣)
        self.coperta = coperta  # True se la carta è coperta, False se scoperta

    def __str__(self):  # Rappresentazione testuale della carta
        if self.coperta:
            return "[#]"
        color = Fore.RED if self.seme in ['♥', '♦'] else Fore.WHITE
        return f"{color}[{self.valore}{self.seme}]{Style.RESET_ALL}"

    def colore(self):  # Restituisce il colore della carta
        return COLORI[self.seme]  # Usa il dizionario COLORI per determinare il colore

    def valore_num(self):  # Restituisce il valore numerico della carta
        if self.valore == 'A':  # Asso vale 1
            return 1
        if self.valore == 'J':  # Jack vale 11
            return 11
        if self.valore == 'Q':  # Regina vale 12
            return 12
        if self.valore == 'K':  # Re vale 13
            return 13
        return int(self.valore)  # Per i numeri da 2 a 10


# =============================================================================
# --- Classe Mazzo (riserva) ---
# =============================================================================
class Mazzo:
    def __init__(self):  # Costruttore del mazzo
        self.carte = [Carta(val, seme) for seme in SEMI for val in VALORI]  # Crea tutte le carte
        random.shuffle(self.carte)  # Mescola le carte

    def pesca(self):  # Pesca una carta dal mazzo
        return self.carte.pop() if self.carte else None  # Rimuove e restituisce l'ultima carta, None se vuoto

    def vuoto(self):  # Controlla se il mazzo è vuoto
        return len(self.carte) == 0  # True se non ci sono carte

    def rimescola(self, scarti):  # Rimescola le carte scartate nel mazzo
        """
        Aggiunge le carte scartate al mazzo esistente e rimescola tutto insieme.
        Questo è più realistico: nel solitario reale non si butta via il mazzo residuo,
        ma si aggiungono gli scarti e si rimescola tutto.
        """
        if scarti:  # Solo se ci sono carte negli scarti da rimescolare
            self.carte.extend(scarti[:])  # Aggiunge una copia degli scarti al mazzo esistente (invece di sostituire)
            random.shuffle(self.carte)  # Mescola di nuovo tutto il mazzo (carte esistenti + scarti)
            scarti.clear()  # Svuota la lista degli scarti dopo averla aggiunta al mazzo
            print(f"Rimescolate {len(scarti)} carte dagli scarti nel mazzo! Mazzo ora: {len(self.carte)} carte")  # Messaggio informativo dettagliato
        else:
            print("Nessuna carta negli scarti da rimescolare.")  # Messaggio se non ci sono scarti

    def aggiungi_scarto(self, carta, scarti):  # Aggiunge una carta agli scarti
        """
        Sposta una carta dalla riserva agli scarti.
        Questo simula il comportamento del solitario reale dove le carte
        non utilizzate vengono messe da parte.
        """
        scarti.append(carta)  # Aggiunge la carta alla lista degli scarti
        print(f"Carta {carta} aggiunta agli scarti.")  # Messaggio informativo

    def conta_carte_totali(self, riserva, scarti):  # Conta tutte le carte disponibili
        """
        Restituisce il numero totale di carte nel mazzo, riserva e scarti.
        Utile per debug e per sapere quante carte rimangono.
        """
        return len(self.carte) + len(riserva) + len(scarti)  # Somma tutte le carte


# =============================================================================
# --- Classe Tavolo (colonne di gioco) ---
# =============================================================================
class Tavolo:
    def __init__(self, mazzo):  # Costruttore del tavolo
        self.colonne = [[] for _ in range(7)]  # Crea 7 colonne vuote
        for i in range(7):  # Per ogni colonna (da 0 a 6)
            for j in range(i + 1):  # La colonna i riceve i+1 carte
                carta = mazzo.pesca()  # Pesca una carta dal mazzo
                carta.coperta = (j != i)  # Solo l'ultima carta è scoperta
                self.colonne[i].append(carta)  # Aggiunge la carta alla colonna

    def mostra(self):
        spazio = "                "  # Spazi tra le colonne
        max_len = max(len(col) for col in self.colonne)  # Trova la lunghezza massima tra tutte le colonne (serve per sapere quante righe stampare)
        for r in range(max_len):  # Cicla su ogni riga da stampare (fino alla colonna più lunga)
            riga = ""  # Inizializza la stringa della riga corrente
            for col in self.colonne:  # Cicla su ogni colonna del tavolo
                if r < len(col):  # Se la colonna ha una carta in questa riga
                    carta_str = str(col[r])  # Ottiene la stringa della carta (colorata o no)
                    visibile = strip_ansi(carta_str)  # Rimuove i codici ANSI per calcolare la lunghezza visibile della carta
                    spazi = 6 - len(visibile)  # Calcola quanti spazi servono per arrivare a 6 caratteri visibili
                    riga += carta_str + (" " * spazi) + spazio  # Aggiunge la carta, gli spazi necessari e lo spazio tra colonne
                else:
                    riga += " " * 6 + spazio  # Se la colonna è più corta, aggiunge solo spazi vuoti per mantenere l'allineamento
            print(riga)  # Stampa la riga completa con tutte le colonne

    def scopri_se_necessario(self, col_idx):
        # Scopre la carta in cima se è coperta
        if self.colonne[col_idx]:  # Se la colonna non è vuota
            if self.colonne[col_idx][-1].coperta:  # Se la carta in cima è coperta
                self.colonne[col_idx][-1].coperta = False  # Scoprila

    def sposta_carte(self, da_col, a_col, num_carte):
        # Sposta num_carte dalla colonna da_col alla colonna a_col
        if not (0 <= da_col < 7 and 0 <= a_col < 7):  # Indici validi?
            return False
        if len(self.colonne[da_col]) < num_carte:  # Abbastanza carte da spostare?
            return False
        carte_da_spostare = self.colonne[da_col][-num_carte:]  # Prendi le carte da spostare
        if not all(not carta.coperta for carta in carte_da_spostare):  # Tutte scoperte?
            return False
        if not self.colonne[a_col]:  # Se la colonna di destinazione è vuota
            if carte_da_spostare[0].valore != 'K':  # Solo un Re può andare su una colonna vuota
                return False
        else:
            carta_destinazione = self.colonne[a_col][-1]  # Carta in cima alla destinazione
            # Regole: colori alternati e valore decrescente
            if carta_destinazione.colore() == carte_da_spostare[0].colore() or carta_destinazione.valore_num() != carte_da_spostare[0].valore_num() + 1:
                return False
        self.colonne[a_col].extend(carte_da_spostare)  # Aggiungi le carte alla destinazione
        self.colonne[da_col] = self.colonne[da_col][:-num_carte]  # Rimuovi dalla partenza
        self.scopri_se_necessario(da_col)  # Scopri la nuova carta in cima se necessario
        return True  # Spostamento riuscito

    def aggiungi_da_mazzo(self, carta):
        # Aggiunge una carta dal mazzo a una colonna
        for col_idx in range(7):  # Prova tutte le colonne
            if not self.colonne[col_idx]:  # Se la colonna è vuota
                if carta.valore == 'K':  # Solo un Re può andare su una colonna vuota
                    self.colonne[col_idx].append(carta)
                    return True
            else:
                carta_destinazione = self.colonne[col_idx][-1]  # Carta in cima
                if carta_destinazione.colore() != carta.colore() and carta_destinazione.valore_num() == carta.valore_num() + 1:
                    self.colonne[col_idx].append(carta)
                    return True
        return False  # Nessuna colonna valida trovata

    def aggiungi_da_mazzo_a_colonna(self, carta, col_idx):
        # Aggiunge una carta dal mazzo a una colonna specifica
        if not (0 <= col_idx < 7):  # Indice valido?
            return False
        if not self.colonne[col_idx]:  # Se la colonna è vuota
            if carta.valore == 'K':  # Solo un Re può andare su una colonna vuota
                self.colonne[col_idx].append(carta)
                return True
        else:
            carta_destinazione = self.colonne[col_idx][-1]  # Carta in cima
            if carta_destinazione.colore() != carta.colore() and carta_destinazione.valore_num() == carta.valore_num() + 1:
                self.colonne[col_idx].append(carta)
                return True
        return False  # Mossa non valida


# =============================================================================
# --- Classe Pile Finali (fondazioni) ---
# =============================================================================
class Finali:
    def __init__(self):
        self.pile = {seme: [] for seme in SEMI}  # Crea un dizionario con una pila vuota per ogni seme (♠, ♥, ♦, ♣)

    def mostra(self):
        for seme in SEMI:  # Cicla su tutti i semi
            if self.pile[seme]:  # Se la pila per quel seme contiene almeno una carta
                carta = self.pile[seme][-1]  # Prende la carta in cima alla pila (l'ultima aggiunta)
                print(f"{seme}: [{carta.valore}{carta.seme}]", end="    ")  # Stampa il seme e la carta in cima
            else:
                print(f"{seme}: [  ]", end="    ")  # Se la pila è vuota, stampa solo il seme e uno spazio vuoto
        print()  # Va a capo dopo aver stampato tutte le pile

    def aggiungi(self, carta):
        pila = self.pile[carta.seme]  # Prende la pila corrispondente al seme della carta
        if not pila and carta.valore == 'A':  # Se la pila è vuota, solo un Asso può essere aggiunto
            pila.append(carta)
            return True
        elif pila and carta.valore_num() == pila[-1].valore_num() + 1:  # Se la pila ha carte, la carta deve essere la successiva
            pila.append(carta)
            return True
        return False  # Altrimenti la carta non può essere aggiunta

    def sposta_verso_finali(self, tavolo, col_idx):
        # Sposta la carta in cima alla colonna verso le fondazioni
        if not (0 <= col_idx < 7) or not tavolo.colonne[col_idx]:  # Indice valido e colonna non vuota?
            return False
        carta = tavolo.colonne[col_idx][-1]  # Prende la carta in cima alla colonna
        if not carta.coperta and self.aggiungi(carta):  # Se la carta è scoperta e può essere aggiunta alle finali
            tavolo.colonne[col_idx].pop()  # Rimuove la carta dalla colonna
            tavolo.scopri_se_necessario(col_idx)  # Scopre la nuova carta in cima se necessario
            return True
        return False  # Spostamento non possibile

    def vittoria(self):
        return all(len(self.pile[seme]) == 13 for seme in SEMI)


# =============================================================================
# --- Funzioni di controllo Game Over ---
# =============================================================================
def controlla_mosse_possibili(tavolo, finali, mazzo, riserva, scarti):
    """
    Controlla se ci sono ancora mosse possibili nel gioco.
    Restituisce True se ci sono mosse possibili, False se è Game Over.
    
    Args:
        tavolo: Istanza della classe Tavolo
        finali: Istanza della classe Finali  
        mazzo: Istanza della classe Mazzo
        riserva: Lista delle carte in riserva
        scarti: Lista delle carte scartate
    
    Returns:
        bool: True se ci sono mosse possibili, False se Game Over
    """
    
    # --- CONTROLLO 1: Carte disponibili da pescare o rimescolare ---
    if not mazzo.vuoto():  # Se il mazzo non è vuoto, possiamo sempre pescare
        return True
    
    if scarti:  # Se ci sono scarti, possiamo rimescolare
        return True
    
    if riserva:  # Se c'è una carta in riserva, possiamo scartarla o usarla
        carta_riserva = riserva[-1]  # Prende l'ultima carta in riserva
        
        # Controlla se la carta in riserva può essere spostata alle fondazioni
        if finali.aggiungi(carta_riserva):  # Prova ad aggiungere (senza modificare realmente)
            finali.pile[carta_riserva.seme].pop()  # Ripristina lo stato (rimuove la carta appena aggiunta)
            return True
        
        # Controlla se la carta in riserva può essere spostata su qualche colonna
        for col_idx in range(7):  # Prova tutte le colonne
            if tavolo.aggiungi_da_mazzo_a_colonna(carta_riserva, col_idx):  # Prova ad aggiungere (simulazione)
                tavolo.colonne[col_idx].pop()  # Ripristina lo stato (rimuove la carta appena aggiunta)
                return True
    
    # --- CONTROLLO 2: Mosse possibili tra colonne ---
    for i in range(7):  # Per ogni colonna sorgente
        colonna_sorgente = tavolo.colonne[i]
        if not colonna_sorgente or colonna_sorgente[-1].coperta:  # Salta colonne vuote o con carte coperte
            continue
            
        # Prova a spostare 1 carta dalla colonna i a tutte le altre colonne
        for j in range(7):  # Per ogni colonna destinazione
            if i != j:  # Non spostare sulla stessa colonna
                if tavolo.sposta_carte(i, j, 1):  # Prova a spostare 1 carta (simulazione)
                    # Ripristina lo stato (annulla la mossa)
                    carta_spostata = tavolo.colonne[j].pop()  # Rimuove la carta dalla destinazione
                    tavolo.colonne[i].append(carta_spostata)  # La rimette nella sorgente
                    return True
        
        # Prova a spostare sequenze più lunghe (2, 3, 4... carte)
        max_carte_spostabili = len([carta for carta in colonna_sorgente if not carta.coperta])  # Conta carte scoperte
        for num_carte in range(2, max_carte_spostabili + 1):  # Prova sequenze di 2+ carte
            for j in range(7):  # Per ogni colonna destinazione
                if i != j:  # Non spostare sulla stessa colonna
                    if tavolo.sposta_carte(i, j, num_carte):  # Prova a spostare num_carte (simulazione)
                        # Ripristina lo stato (annulla la mossa)
                        carte_spostate = tavolo.colonne[j][-num_carte:]  # Prende le carte spostate
                        tavolo.colonne[j] = tavolo.colonne[j][:-num_carte]  # Le rimuove dalla destinazione
                        tavolo.colonne[i].extend(carte_spostate)  # Le rimette nella sorgente
                        return True
    
    # --- CONTROLLO 3: Mosse possibili verso le fondazioni ---
    for i in range(7):  # Per ogni colonna
        colonna = tavolo.colonne[i]
        if colonna and not colonna[-1].coperta:  # Se la colonna ha carte e l'ultima è scoperta
            carta = colonna[-1]  # Prende la carta in cima
            if finali.aggiungi(carta):  # Prova ad aggiungere alle fondazioni (simulazione)
                finali.pile[carta.seme].pop()  # Ripristina lo stato (rimuove la carta appena aggiunta)
                return True
    
    # --- CONTROLLO 4: Scoprimento di nuove carte ---
    # Se tutte le carte scoperte non hanno mosse, ma ci sono carte coperte,
    # potremmo scoprirne di nuove spostando carte scoperte
    for i in range(7):  # Per ogni colonna
        colonna = tavolo.colonne[i]
        if len(colonna) >= 2:  # Se la colonna ha almeno 2 carte
            if not colonna[-1].coperta and colonna[-2].coperta:  # Ultima scoperta, penultima coperta
                # Se riusciamo a spostare l'ultima carta, scopriremmo la penultima
                # Questo è già coperto dai controlli precedenti, ma è importante notarlo
                pass
    
    # Se arriviamo qui, non ci sono mosse possibili
    return False

def messaggio_game_over(tavolo, finali, mazzo, riserva, scarti):
    """
    Genera un messaggio dettagliato per il Game Over.
    
    Args:
        tavolo, finali, mazzo, riserva, scarti: Stato del gioco
    
    Returns:
        str: Messaggio descrittivo del Game Over
    """
    carte_nelle_fondazioni = sum(len(finali.pile[seme]) for seme in SEMI)  # Conta carte nelle fondazioni
    carte_totali_distribuite = 52  # Numero totale di carte nel mazzo
    percentuale_completamento = (carte_nelle_fondazioni / carte_totali_distribuite) * 100  # Calcola percentuale
    
    messaggio = f"""
╔═══════════════════════════════════════╗
║               GAME OVER               ║
╠═══════════════════════════════════════╣
║ Non ci sono più mosse possibili!      ║
║                                       ║
║ Statistiche finali:                   ║
║ • Carte nelle fondazioni: {carte_nelle_fondazioni:2d}/52       ║
║ • Completamento: {percentuale_completamento:5.1f}%             ║
║ • Mazzo: {len(mazzo.carte):2d} carte                    ║
║ • Riserva: {len(riserva):2d} carte                  ║
║ • Scarti: {len(scarti):2d} carte                   ║
╚═══════════════════════════════════════╝
"""
    return messaggio


# =============================================================================
# --- Funzione principale ---
# =============================================================================
def main():
    init(autoreset=True)
    mazzo = Mazzo()  # Crea e mescola il mazzo
    tavolo = Tavolo(mazzo)  # Distribuisce le carte nelle colonne
    finali = Finali()  # Crea le pile finali vuote
    riserva = []  # Lista per le carte pescate dal mazzo
    scarti = []  # Lista per le carte scartate (non usata in questa versione)
    messaggio = ""  # Stringa per messaggi all'utente

    while True:  # Ciclo principale del gioco
        print("\n--- TAVOLO ---")
        tavolo.mostra()  # Visualizza le colonne del tavolo
        print("\n--- PILE FINALI ---")
        finali.mostra()  # Visualizza le pile finali
        if messaggio:  # Se c'è un messaggio da mostrare
            print(messaggio)
            messaggio = ""  # Pulisce il messaggio dopo averlo mostrato
        # --- CONTROLLO VITTORIA ---
        if finali.vittoria():
            print("Vittoria!")
            break
        
        # --- CONTROLLO GAME OVER ---
        if not controlla_mosse_possibili(tavolo, finali, mazzo, riserva, scarti):
            print(messaggio_game_over(tavolo, finali, mazzo, riserva, scarti))
            break
        
        # --- MOSTRA INFORMAZIONI AGGIUNTIVE ---
        carte_rimaste = mazzo.conta_carte_totali(riserva, scarti)  # Conta tutte le carte disponibili
        print(f"\nCarte disponibili: Mazzo({len(mazzo.carte)}) + Riserva({len(riserva)}) + Scarti({len(scarti)}) = {carte_rimaste}")
        
        # --- MOSTRA CARTA IN RISERVA SE PRESENTE ---
        if riserva:  # Se c'è almeno una carta in riserva
            print(f"Carta in riserva: {riserva[-1]}")  # Mostra l'ultima carta pescata (quella utilizzabile)
        
        # --- MOSTRA SCARTI SE PRESENTI (solo per debug) ---
        if scarti and len(scarti) <= 5:  # Mostra gli scarti solo se sono pochi (per non intasare l'output)
            print(f"Scarti: {[str(carta) for carta in scarti]}")  # Mostra tutte le carte negli scarti
        elif scarti:  # Se ci sono molti scarti, mostra solo il conteggio
            print(f"Scarti: {len(scarti)} carte (troppe per essere mostrate)")
        
        print("\nComandi: [p] Pesca  [s] Sposta  [f] Sposta verso finali  [m] da Mazzo a colonne  [mf] da Mazzo a finali")
        print("         [sc] Scarta carta riserva  [r] Rimescola scarti  [q] Esci")
        cmd = input("Comando: ").strip().lower()  # Chiede il comando all'utente

        if cmd == "q":
            print("Arrivederci!")
            break  # Esce dal ciclo e termina il gioco
        elif cmd == "p":
            if not mazzo.vuoto():  # Se il mazzo non è vuoto
                carta = mazzo.pesca()  # Pesca una carta dal mazzo
                carta.coperta = False  # La carta pescata è sempre scoperta
                riserva.append(carta)  # Aggiunge la carta alla riserva
                messaggio = f"Hai pescato: {carta}"  # Messaggio di conferma
            else:
                # --- GESTIONE MAZZO VUOTO ---
                if scarti:  # Se ci sono carte negli scarti, rimescola automaticamente
                    messaggio = "Mazzo finito! Rimescolo automaticamente gli scarti."
                    mazzo.rimescola(scarti)  # Rimescola gli scarti nel mazzo (scarti viene svuotato automaticamente)
                elif riserva:  # Se non ci sono scarti ma c'è una carta in riserva, spostala negli scarti
                    messaggio = "Mazzo finito! Sposta la carta in riserva negli scarti e usa comando [r] per rimescolare."
                else:
                    messaggio = "Mazzo, riserva e scarti vuoti! Nessuna carta disponibile."  # Nessuna carta disponibile
        elif cmd == "s":
            # Sposta carte tra colonne
            try:
                da_col = int(input("Da colonna (0-6): "))  # Chiede la colonna di partenza
                a_col = int(input("A colonna (0-6): "))    # Chiede la colonna di destinazione
                num_carte = int(input("Numero di carte da spostare: "))  # Quante carte spostare
                if tavolo.sposta_carte(da_col, a_col, num_carte):  # Tenta lo spostamento
                    print("Mossa valida!")  # Conferma se la mossa è valida
                else:
                    print("Mossa non valida!")  # Messaggio di errore se la mossa non è valida
            except ValueError:
                print("Input non valido!")  # Messaggio di errore se l'input non è un numero
        elif cmd == "f":
            # Sposta carta verso le fondazioni
            try:
                col_idx = int(input("Colonna (0-6): "))  # Chiede la colonna da cui spostare
                if finali.sposta_verso_finali(tavolo, col_idx):  # Tenta lo spostamento verso le fondazioni
                    print("Carta spostata verso le fondazioni!")  # Conferma se la mossa è valida
                else:
                    print("Mossa non valida!")  # Messaggio di errore se la mossa non è valida
            except ValueError:
                print("Input non valido!")  # Messaggio di errore se l'input non è un numero
        elif cmd == "m":
            # Sposta carta dal mazzo (riserva) alle colonne
            if not riserva:
                print("Riserva vuota! Pesca prima una carta.")  # Messaggio se la riserva è vuota
            else:
                carta = riserva[-1]  # Prende l'ultima carta pescata
                print(f"Carta da spostare: {carta}")  # Mostra la carta da spostare
                try:
                    col_idx = int(input("In quale colonna? (0-6): "))  # Chiede la colonna di destinazione
                    if tavolo.aggiungi_da_mazzo_a_colonna(carta, col_idx):  # Tenta di aggiungere la carta
                        riserva.pop()  # Rimuove la carta dalla riserva
                        print(f"Carta {carta} spostata dal mazzo alla colonna {col_idx}!")  # Conferma
                    else:
                        print("Mossa non valida! La carta non può essere messa in quella colonna.")  # Errore regole
                except ValueError:
                    print("Input non valido! Inserisci un numero da 0 a 6.")  # Errore input non numerico
        elif cmd == "mf":
            # Sposta carta dal mazzo (riserva) alle fondazioni
            if not riserva:
                print("Riserva vuota! Pesca prima una carta.")  # Messaggio se la riserva è vuota
            else:
                carta = riserva[-1]  # Prende l'ultima carta pescata
                if finali.aggiungi(carta):  # Tenta di aggiungere la carta alle fondazioni
                    riserva.pop()  # Rimuove la carta dalla riserva
                    print(f"Carta {carta} spostata dal mazzo alle fondazioni!")  # Conferma
                else:
                    print("Mossa non valida!")  # Messaggio di errore se la mossa non è valida
        elif cmd == "sc":
            # --- SCARTA CARTA DALLA RISERVA ---
            if not riserva:  # Se la riserva è vuota
                print("Riserva vuota! Non c'è niente da scartare.")  # Messaggio di errore
            else:
                carta_da_scartare = riserva.pop()  # Rimuove l'ultima carta dalla riserva
                mazzo.aggiungi_scarto(carta_da_scartare, scarti)  # La aggiunge agli scarti
                messaggio = f"Carta {carta_da_scartare} scartata."  # Messaggio di conferma
        elif cmd == "r":
            # --- RIMESCOLA SCARTI MANUALMENTE ---
            if not scarti:  # Se non ci sono scarti
                print("Nessuna carta negli scarti da rimescolare!")  # Messaggio di errore
            elif not mazzo.vuoto():  # Se il mazzo non è ancora vuoto
                print("Il mazzo non è vuoto! Puoi rimescolare solo quando il mazzo è finito.")  # Messaggio di errore
            else:
                mazzo.rimescola(scarti)  # Rimescola gli scarti nel mazzo
                messaggio = f"Rimescolate {len(mazzo.carte)} carte dagli scarti nel mazzo!"  # Messaggio di conferma
        else:
            print("Comando non riconosciuto.")  # Messaggio per comando non valido

def colora_seme(seme):
    # Restituisce il seme colorato: rosso per cuori e quadri, bianco per picche e fiori
    if seme in ['♥', '♦']:
        return Fore.RED + seme + Style.RESET_ALL  # Colora di rosso il seme e resetta lo stile dopo
    else:
        return Fore.WHITE + seme + Style.RESET_ALL  # Colora di bianco il seme e resetta lo stile dopo

def strip_ansi(text):
    # Rimuove i codici di escape ANSI (usati per i colori) da una stringa
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')  # Regex che trova i codici ANSI
    return ansi_escape.sub('', text)  # Restituisce la stringa senza codici ANSI

if __name__ == "__main__":
    # Punto di ingresso del programma: esegue main() solo se il file è eseguito direttamente
    main()