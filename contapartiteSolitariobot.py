"""
SOLITARIO SIMULATION BOT - Simulatore di Partite Multiple
=========================================================
Questo bot simula migliaia di partite complete di solitario per analizzare:
- Percentuali di vittoria vs stallo
- Durata media delle partite
- Mosse più comuni che portano alla vittoria
- Situazioni di stallo più frequenti
- Efficacia delle strategie di gioco

UTILIZZO:
- python solitario_simulation_bot.py        # 1000 partite
- python solitario_simulation_bot.py 500    # 500 partite
- python solitario_simulation_bot.py 100 debug  # 100 partite con debug
"""

import random
import time
import sys
from collections import defaultdict
from datetime import datetime
import os

# Importa le classi dal file del solitario
try:
    from gameOver_test_ import (
        Mazzo, Tavolo, Finali, Carta, SEMI, VALORI, 
        controlla_mosse_possibili, messaggio_game_over
    )
    print("✅ Importazione da gameOver_test_.py riuscita!")
    HAS_GAME_OVER = True
except ImportError:
    try:
        from solitario_test_refactoring import Mazzo, Tavolo, Finali, Carta, SEMI, VALORI
        print("✅ Importazione da solitario_test_refactoring.py riuscita!")
        HAS_GAME_OVER = False
        print("⚠️ Versione senza Game Over - userò logica di stallo semplificata")
    except ImportError:
        print("❌ Errore: Non riesco a importare da nessun file solitario")
        sys.exit(1)

class SolitarioSimulationBot:
    """Bot che simula un giocatore intelligente per migliaia di partite."""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.stats = {
            'partite_totali': 0, 'vittorie': 0, 'stalli': 0,
            'durata_totale': 0, 'mosse_totali': 0,
            'carte_nelle_fondazioni': [], 'mosse_per_partita': [],
            'durata_per_partita': [], 'cause_stallo': defaultdict(int),
            'strategie_vincenti': defaultdict(int)
        }
        # Anti-loop system
        self.ultime_mosse = []
        self.stati_visti = set()
    
    def setup_game(self):
        """Inizializza una nuova partita."""
        mazzo = Mazzo()
        tavolo = Tavolo(mazzo)
        finali = Finali()
        return mazzo, tavolo, finali, [], []
    
    def trova_mosse_fondazioni(self, tavolo, finali):
        """Trova carte spostabili alle fondazioni (MIGLIORATO con priorità)."""
        mosse = []
        for i in range(7):
            colonna = tavolo.colonne[i]
            if colonna and not colonna[-1].coperta:
                carta = colonna[-1]
                # Controllo veloce senza simulazione completa
                seme_pile = finali.pile[carta.seme]
                priorita = 0
                
                if not seme_pile and carta.valore == 'A':
                    priorita = 100  # Assi hanno priorità massima
                    # Bonus se libera carte coperte
                    if len(colonna) > 1 and colonna[-2].coperta:
                        priorita += 50
                    mosse.append((i, priorita))
                
                elif seme_pile and len(seme_pile) < 13:
                    ultimo_valore = seme_pile[-1].valore
                    if VALORI.index(carta.valore) == VALORI.index(ultimo_valore) + 1:
                        priorita = 90
                        # Bonus speciale per liberare Assi
                        if len(colonna) > 1:
                            carta_sotto = colonna[-2]
                            if not carta_sotto.coperta and carta_sotto.valore == 'A':
                                priorita += 80  # PRIORITÀ ALTISSIMA per liberare Assi
                            elif carta_sotto.coperta:
                                priorita += 40
                        mosse.append((i, priorita))
        
        # Ordina per priorità decrescente e restituisce solo gli indici
        mosse_ordinate = sorted(mosse, key=lambda x: x[1], reverse=True)
        return [mossa[0] for mossa in mosse_ordinate]
    
    def trova_mosse_colonne(self, tavolo):
        """Trova mosse intelligenti tra colonne (ottimizzato per velocità)."""
        mosse = []
        
        # Pre-calcola informazioni utili
        colonne_vuote = [i for i in range(7) if not tavolo.colonne[i]]
        
        for i in range(7):
            colonna = tavolo.colonne[i]
            if not colonna or colonna[-1].coperta:
                continue
            
            # Solo 1-3 carte per velocità (invece di tutte)
            max_carte = min(3, len([c for c in colonna if not c.coperta]))
            
            for num_carte in range(1, max_carte + 1):
                carta_da_spostare = colonna[-num_carte]
                
                for j in range(7):
                    if i == j:
                        continue
                    
                    dest_colonna = tavolo.colonne[j]
                    
                    # Controllo veloce compatibilità
                    if not dest_colonna:  # Colonna vuota
                        if carta_da_spostare.valore == 'K':  # Solo Re su colonne vuote
                            priorita = 25  # Priorità massima
                            # Bonus se scopre carte
                            if len(colonna) > num_carte and colonna[-(num_carte+1)].coperta:
                                priorita += 15
                            mosse.append((i, j, num_carte, priorita))
                    else:  # Colonna non vuota
                        ultima_carta = dest_colonna[-1]
                        if not ultima_carta.coperta:
                            # Controllo sequenza (valore decrescente, colore alternato)
                            if (VALORI.index(ultima_carta.valore) == VALORI.index(carta_da_spostare.valore) + 1 and
                                ((ultima_carta.seme in ['♠', '♣'] and carta_da_spostare.seme in ['♥', '♦']) or
                                 (ultima_carta.seme in ['♥', '♦'] and carta_da_spostare.seme in ['♠', '♣']))):
                                
                                priorita = 10
                                # Bonus se scopre carte
                                if len(colonna) > num_carte and colonna[-(num_carte+1)].coperta:
                                    priorita += 15
                                # Malus se colonna destinazione troppo piena
                                if len(dest_colonna) > 6:
                                    priorita -= 5
                                mosse.append((i, j, num_carte, priorita))
        
        # Ordina solo i primi 10 per velocità
        return sorted(mosse, key=lambda x: x[3], reverse=True)[:10]
    
    def genera_stato_gioco(self, tavolo, finali, mazzo, riserva, scarti):
        """Genera una rappresentazione dello stato del gioco per rilevare loop."""
        # Stato semplificato per rilevare loop
        stato_colonne = []
        for col in tavolo.colonne:
            if col:
                stato_colonne.append(f"{len(col)}-{col[-1].valore}{col[-1].seme}")
            else:
                stato_colonne.append("vuota")
        
        stato_fondazioni = []
        for seme in SEMI:
            stato_fondazioni.append(len(finali.pile[seme]))
        
        return f"{'|'.join(stato_colonne)}-{'|'.join(map(str, stato_fondazioni))}-{len(mazzo.carte)}-{len(riserva)}-{len(scarti)}"

    def rileva_loop(self, stato_attuale, azione):
        """Rileva se siamo in un loop infinito (MIGLIORATO)."""
        # Aggiungi l'azione alla storia
        self.ultime_mosse.append(azione)
        
        # Mantieni solo le ultime 30 mosse per performance
        if len(self.ultime_mosse) > 30:
            self.ultime_mosse.pop(0)
        
        # MIGLIORAMENTO 1: Rileva loop draw/discard specifico
        if len(self.ultime_mosse) >= 15:
            ultimi_15 = self.ultime_mosse[-15:]
            # Se più dell'80% sono pesca/scarta
            pesca_scarta = sum(1 for a in ultimi_15 if a in ["pesca", "scarta", "rimescola"])
            if pesca_scarta > 12:  # 12/15 = 80%
                return True
        
        # MIGLIORAMENTO 2: Controlla se abbiamo ripetuto la stessa azione troppe volte
        if len(self.ultime_mosse) >= 10:
            ultimi_10 = self.ultime_mosse[-10:]
            if len(set(ultimi_10)) <= 2:  # Solo 1-2 azioni diverse negli ultimi 10 tentativi
                return True
        
        # MIGLIORAMENTO 3: Controlla stati ripetuti con tolleranza
        if stato_attuale in self.stati_visti:
            # Conta quante volte abbiamo visto questo stato
            count = sum(1 for s in list(self.stati_visti)[-50:] if s == stato_attuale)
            if count > 3:  # Visto più di 3 volte recentemente
                return True
        
        self.stati_visti.add(stato_attuale)
        
        # Pulisci stati vecchi per evitare memory leak
        if len(self.stati_visti) > 2000:
            # Mantieni solo gli ultimi 1000
            self.stati_visti = set(list(self.stati_visti)[-1000:])
        
        return False

    def strategia_intelligente(self, mazzo, tavolo, finali, riserva, scarti):
        """Strategia intelligente con anti-loop."""
        
        # Genera stato attuale
        stato_attuale = self.genera_stato_gioco(tavolo, finali, mazzo, riserva, scarti)
        
        # PRIORITÀ 1: Fondazioni (sempre prioritario)
        mosse_fond = self.trova_mosse_fondazioni(tavolo, finali)
        if mosse_fond:
            azione = ("fondazioni", f"Col{mosse_fond[0]}→fond")
            if not self.rileva_loop(stato_attuale, azione[0]):
                if finali.sposta_verso_finali(tavolo, mosse_fond[0]):
                    return azione
        
        # PRIORITÀ 2: Riserva → fondazioni
        if riserva:
            carta = riserva[-1]
            if finali.aggiungi(carta):
                azione = ("riserva_fondazioni", "Ris→fond")
                if not self.rileva_loop(stato_attuale, azione[0]):
                    riserva.pop()
                    return azione
                else:
                    # Ripristina se è un loop
                    finali.pile[carta.seme].pop()
        
        # PRIORITÀ 3: Mosse tra colonne (con controllo anti-loop)
        mosse_col = self.trova_mosse_colonne(tavolo)
        for da_col, a_col, num_carte, priorita in mosse_col[:3]:  # Prova solo le prime 3 mosse migliori
            azione = ("colonne", f"{num_carte}c:{da_col}→{a_col}")
            if not self.rileva_loop(stato_attuale, azione[0]):
                if tavolo.sposta_carte(da_col, a_col, num_carte):
                    return azione
        
        # PRIORITÀ 4: Riserva → colonne (con anti-loop)
        if riserva:
            carta = riserva[-1]
            # Prima: colonne vuote con Re
            if carta.valore == 'K':
                for col_idx in range(7):
                    if not tavolo.colonne[col_idx]:
                        azione = ("riserva_re", f"Re→col{col_idx}")
                        if not self.rileva_loop(stato_attuale, azione[0]):
                            tavolo.colonne[col_idx].append(carta)
                            riserva.pop()
                            return azione
            
            # Poi: mosse strategiche che scoprono carte
            for col_idx in range(7):
                dest_col = tavolo.colonne[col_idx]
                if dest_col and not dest_col[-1].coperta:
                    ultima = dest_col[-1]
                    if (VALORI.index(ultima.valore) == VALORI.index(carta.valore) + 1 and
                        ((ultima.seme in ['♠', '♣'] and carta.seme in ['♥', '♦']) or
                         (ultima.seme in ['♥', '♦'] and carta.seme in ['♠', '♣']))):
                        azione = ("riserva_scopri", f"Ris→col{col_idx}")
                        if not self.rileva_loop(stato_attuale, azione[0]):
                            dest_col.append(carta)
                            riserva.pop()
                            return azione
        
        # PRIORITÀ 5: Gestione mazzo intelligente
        if not mazzo.vuoto():
            azione = ("pesca", "Pesca")
            if not self.rileva_loop(stato_attuale, azione[0]) or len(riserva) == 0:
                carta = mazzo.pesca()
                carta.coperta = False
                riserva.append(carta)
                return azione
        
        # PRIORITÀ 6: Rimescola
        if scarti and mazzo.vuoto():
            azione = ("rimescola", "Rimescola")
            if not self.rileva_loop(stato_attuale, azione[0]):
                mazzo.rimescola(scarti)
                return azione
        
        # PRIORITÀ 7: Scarto strategico (anti-loop)
        if riserva and len(riserva) >= 1:
            azione = ("scarta", "Scarta")
            if not self.rileva_loop(stato_attuale, azione[0]):
                carta = riserva.pop()
                mazzo.aggiungi_scarto(carta, scarti)
                return azione
        
        # PRIORITÀ 8: Strategia diversiva anti-loop MIGLIORATA
        if len(self.ultime_mosse) > 10:
            # Conta azioni recenti di pesca/scarta
            ultime_10 = self.ultime_mosse[-10:]
            pesca_scarta_count = sum(1 for azione in ultime_10 if azione in ["pesca", "scarta", "rimescola"])
            
            # Se più del 70% sono pesca/scarta, usa strategia diversiva
            if pesca_scarta_count >= 7:
                return self.strategia_diversiva(mazzo, tavolo, finali, riserva, scarti)
        
        # Controllo loop tradizionale
        if self.rileva_loop(stato_attuale, "diversiva_check"):
            return self.strategia_diversiva(mazzo, tavolo, finali, riserva, scarti)
        
        # PRIORITÀ 9: Pesca di emergenza
        if not mazzo.vuoto():
            carta = mazzo.pesca()
            carta.coperta = False
            riserva.append(carta)
            return ("pesca_emergenza", "PescaE")
        
        return ("nessuna", "Nessuna")
    
    def strategia_diversiva(self, mazzo, tavolo, finali, riserva, scarti):
        """Strategia alternativa AGGRESSIVA quando siamo in loop."""
        import random
        
        # OPZIONE 1: Forza fine partita se loop troppo lungo
        if len(self.ultime_mosse) > 50:
            return ("fine_forzata", "FineLoop")
        
        # OPZIONE 2: Prova mosse colonne casuali PRIMA
        colonne_con_carte = [i for i in range(7) if tavolo.colonne[i] and not tavolo.colonne[i][-1].coperta]
        colonne_vuote = [i for i in range(7) if not tavolo.colonne[i]]
        
        # Prova QUALSIASI mossa tra colonne
        if colonne_con_carte:
            for col_src in colonne_con_carte:
                carta_src = tavolo.colonne[col_src][-1]
                
                # Prova Re su colonne vuote
                if carta_src.valore == 'K' and colonne_vuote:
                    col_dest = random.choice(colonne_vuote)
                    if tavolo.sposta_carte(col_src, col_dest, 1):
                        return ("diversiva_re", f"Re{col_src}→{col_dest}")
                
                # Prova mosse valide casuali
                for col_dest in range(7):
                    if col_src != col_dest and tavolo.colonne[col_dest]:
                        ultima_dest = tavolo.colonne[col_dest][-1]
                        if (not ultima_dest.coperta and 
                            VALORI.index(ultima_dest.valore) == VALORI.index(carta_src.valore) + 1):
                            # Controlla colori alternati
                            if ((ultima_dest.seme in ['♠', '♣'] and carta_src.seme in ['♥', '♦']) or
                                (ultima_dest.seme in ['♥', '♦'] and carta_src.seme in ['♠', '♣'])):
                                if tavolo.sposta_carte(col_src, col_dest, 1):
                                    return ("diversiva_mossa", f"Diversiva{col_src}→{col_dest}")
        
        # OPZIONE 3: Gestione mazzo FORZATA
        if riserva:
            # Scarta SEMPRE se in loop
            carta = riserva.pop()
            mazzo.aggiungi_scarto(carta, scarti)
            return ("diversiva_scarta_force", "ScartaForce")
        
        elif not mazzo.vuoto():
            # Pesca SEMPRE se in loop
            carta = mazzo.pesca()
            carta.coperta = False
            riserva.append(carta)
            return ("diversiva_pesca_force", "PescaForce")
        
        elif scarti and mazzo.vuoto():
            # Rimescola e poi termina
            mazzo.rimescola(scarti)
            return ("diversiva_rimescola_force", "RimescolaForce")
        
        # ULTIMA OPZIONE: Termina partita
        return ("fine_forzata", "FineLoop")
    
    def rileva_stallo_semplice(self, mazzo, tavolo, finali, riserva, scarti):
        """Rileva stallo senza Game Over."""
        if mazzo.vuoto() and not riserva and not scarti:
            mosse_fond = self.trova_mosse_fondazioni(tavolo, finali)
            mosse_col = self.trova_mosse_colonne(tavolo)
            return len(mosse_fond) == 0 and len(mosse_col) == 0
        return False
    
    def gioca_partita_completa(self):
        """Gioca una partita completa."""
        start_time = time.time()
        mazzo, tavolo, finali, riserva, scarti = self.setup_game()
        
        # Reset anti-loop per ogni partita
        self.ultime_mosse = []
        self.stati_visti = set()
        
        mosse_count = 0
        max_mosse = 1000  # RIDOTTO per evitare loop infiniti - più realistico
        azioni = []
        
        while mosse_count < max_mosse:
            # Controlla vittoria
            if finali.vittoria():
                return {
                    'risultato': 'vittoria',
                    'mosse': mosse_count,
                    'durata': time.time() - start_time,
                    'carte_fondazioni': 52,
                    'azioni': azioni[-10:],
                    'causa_fine': 'vittoria_completa'
                }
            
            # Controlla stallo
            if HAS_GAME_OVER:
                if not controlla_mosse_possibili(tavolo, finali, mazzo, riserva, scarti):
                    return {
                        'risultato': 'stallo',
                        'mosse': mosse_count,
                        'durata': time.time() - start_time,
                        'carte_fondazioni': sum(len(finali.pile[s]) for s in SEMI),
                        'azioni': azioni[-10:],
                        'causa_fine': 'nessuna_mossa_possibile'
                    }
            else:
                if self.rileva_stallo_semplice(mazzo, tavolo, finali, riserva, scarti):
                    return {
                        'risultato': 'stallo',
                        'mosse': mosse_count,
                        'durata': time.time() - start_time,
                        'carte_fondazioni': sum(len(finali.pile[s]) for s in SEMI),
                        'azioni': azioni[-10:],
                        'causa_fine': 'stallo_semplice'
                    }
            
            # Esegue mossa
            azione, desc = self.strategia_intelligente(mazzo, tavolo, finali, riserva, scarti)
            azioni.append(azione)
            
            if azione == "nessuna" or azione == "fine_forzata":
                causa = 'nessuna_azione_possibile' if azione == "nessuna" else 'loop_infinito_forzato'
                return {
                    'risultato': 'stallo',
                    'mosse': mosse_count,
                    'durata': time.time() - start_time,
                    'carte_fondazioni': sum(len(finali.pile[s]) for s in SEMI),
                    'azioni': azioni[-10:],
                    'causa_fine': causa
                }
            
            mosse_count += 1
            
            if self.debug and mosse_count % 100 == 0:
                print(f"Mossa {mosse_count}: {desc}")
        
        # Timeout
        return {
            'risultato': 'timeout',
            'mosse': mosse_count,
            'durata': time.time() - start_time,
            'carte_fondazioni': sum(len(finali.pile[s]) for s in SEMI),
            'azioni': azioni[-10:],
            'causa_fine': 'limite_mosse_raggiunto'
        }
    
    def simula_partite_multiple(self, num_partite=1000):
        """Simula migliaia di partite CON CONTEGGIO MIGLIORATO."""
        print(f"🚀 Avvio simulazione MIGLIORATA di {num_partite} partite...")
        print(f"📊 Progresso in tempo reale con anti-loop avanzato:")
        print("🎮 Partite | 🏆 Vittorie | 🚫 Stalli | ⚡ Velocità | 🎯 Completamento | ⏱️ ETA")
        print("-" * 80)
        start_time = time.time()
        
        for i in range(num_partite):
            risultato = self.gioca_partita_completa()
            
            # Aggiorna statistiche
            self.stats['partite_totali'] += 1
            self.stats['mosse_totali'] += risultato['mosse']
            self.stats['durata_totale'] += risultato['durata']
            self.stats['carte_nelle_fondazioni'].append(risultato['carte_fondazioni'])
            self.stats['mosse_per_partita'].append(risultato['mosse'])
            self.stats['durata_per_partita'].append(risultato['durata'])
            self.stats['cause_stallo'][risultato['causa_fine']] += 1
            
            if risultato['risultato'] == 'vittoria':
                self.stats['vittorie'] += 1
                for azione in risultato['azioni']:
                    self.stats['strategie_vincenti'][azione] += 1
            else:
                self.stats['stalli'] += 1
            
            # CONTATORE IN TEMPO REALE
            partite_completate = i + 1
            
            # CONTEGGIO MIGLIORATO: Mostra progresso più frequentemente
            if (num_partite <= 50 and partite_completate % 2 == 0) or \
               (num_partite <= 100 and partite_completate % 5 == 0) or \
               (partite_completate % 10 == 0) or \
               (partite_completate == num_partite):
                
                # Calcola statistiche parziali
                perc_vittorie = (self.stats['vittorie'] / partite_completate) * 100
                perc_stalli = (self.stats['stalli'] / partite_completate) * 100
                tempo_trascorso = time.time() - start_time
                velocita = partite_completate / tempo_trascorso if tempo_trascorso > 0 else 0
                tempo_stimato = (num_partite - partite_completate) / velocita if velocita > 0 else 0
                
                # Calcola completamento medio
                if self.stats['carte_nelle_fondazioni']:
                    media_completamento = sum(self.stats['carte_nelle_fondazioni']) / len(self.stats['carte_nelle_fondazioni'])
                    perc_completamento = (media_completamento / 52) * 100
                else:
                    perc_completamento = 0
                
                # Barra di progresso
                progresso_perc = (partite_completate / num_partite) * 100
                barra_lunghezza = 20  # Più corta per fare spazio
                barra_completa = int((progresso_perc / 100) * barra_lunghezza)
                barra = "█" * barra_completa + "░" * (barra_lunghezza - barra_completa)
                
                # Stampa riga di progresso MIGLIORATA (sovrascrive la precedente)
                print(f"\r🎮 {partite_completate:3d}/{num_partite} [{barra}] {progresso_perc:5.1f}% | "
                      f"🏆 {self.stats['vittorie']:2d} ({perc_vittorie:4.1f}%) | "
                      f"🚫 {self.stats['stalli']:2d} ({perc_stalli:4.1f}%) | "
                      f"⚡ {velocita:4.1f} p/s | "
                      f"🎯 {perc_completamento:4.1f}% | "
                      f"⏱️ {tempo_stimato:3.0f}s", end="", flush=True)
        
        # Va a capo finale
        print()
        print("-" * 80)
        
        self.stats['tempo_simulazione'] = time.time() - start_time
        
        # Messaggio di completamento
        perc_vittorie_finale = (self.stats['vittorie'] / num_partite) * 100
        print(f"✅ Simulazione completata!")
        print(f"📊 Risultato finale: {self.stats['vittorie']} vittorie su {num_partite} partite ({perc_vittorie_finale:.1f}%)")
        print(f"⏱️ Tempo totale: {self.stats['tempo_simulazione']:.1f} secondi")
        print(f"⚡ Velocità media: {num_partite / self.stats['tempo_simulazione']:.1f} partite/secondo")
        print()
        
        return self.calcola_statistiche()
    
    def calcola_statistiche(self):
        """Calcola statistiche finali."""
        if self.stats['partite_totali'] == 0:
            return {}
        
        perc_vittorie = (self.stats['vittorie'] / self.stats['partite_totali']) * 100
        perc_stalli = (self.stats['stalli'] / self.stats['partite_totali']) * 100
        media_mosse = self.stats['mosse_totali'] / self.stats['partite_totali']
        media_durata = self.stats['durata_totale'] / self.stats['partite_totali']
        media_carte = sum(self.stats['carte_nelle_fondazioni']) / len(self.stats['carte_nelle_fondazioni'])
        
        return {
            'partite_totali': self.stats['partite_totali'],
            'vittorie': self.stats['vittorie'],
            'stalli': self.stats['stalli'],
            'percentuale_vittorie': perc_vittorie,
            'percentuale_stalli': perc_stalli,
            'media_mosse_per_partita': media_mosse,
            'media_durata_per_partita': media_durata,
            'media_carte_fondazioni': media_carte,
            'mosse_min': min(self.stats['mosse_per_partita']),
            'mosse_max': max(self.stats['mosse_per_partita']),
            'durata_min': min(self.stats['durata_per_partita']),
            'durata_max': max(self.stats['durata_per_partita']),
            'tempo_simulazione_totale': self.stats['tempo_simulazione'],
            'cause_stallo': dict(self.stats['cause_stallo']),
            'strategie_vincenti': dict(self.stats['strategie_vincenti']),
            'partite_per_secondo': self.stats['partite_totali'] / self.stats['tempo_simulazione']
        }
    
    def stampa_report(self, stats):
        """Stampa report finale."""
        print("\n" + "="*80)
        print("🎮 SOLITARIO SIMULATION BOT - REPORT FINALE")
        print("="*80)
        
        if HAS_GAME_OVER:
            print("📦 VERSIONE: gameOver_test_.py (con Game Over)")
        else:
            print("📦 VERSIONE: solitario_test_refactoring.py (base)")
        
        print(f"⏱️ TEMPO: {stats['tempo_simulazione_totale']:.1f} secondi")
        print(f"⚡ VELOCITÀ: {stats['partite_per_secondo']:.1f} partite/secondo")
        
        print(f"\n📊 RISULTATI:")
        print(f"   🎮 Partite: {stats['partite_totali']}")
        print(f"   🏆 Vittorie: {stats['vittorie']} ({stats['percentuale_vittorie']:.1f}%)")
        print(f"   🚫 Stalli: {stats['stalli']} ({stats['percentuale_stalli']:.1f}%)")
        
        print(f"\n📈 ANALISI:")
        print(f"   🎯 Mosse medie: {stats['media_mosse_per_partita']:.1f}")
        print(f"   ⏱️ Durata media: {stats['media_durata_per_partita']:.3f}s")
        print(f"   🃏 Carte medie fondazioni: {stats['media_carte_fondazioni']:.1f}/52")
        print(f"   📊 Completamento: {(stats['media_carte_fondazioni']/52)*100:.1f}%")
        
        print(f"\n🔍 ESTREMI:")
        print(f"   ⚡ Min mosse: {stats['mosse_min']}")
        print(f"   🐌 Max mosse: {stats['mosse_max']}")
        print(f"   ⏱️ Min durata: {stats['durata_min']:.3f}s")
        print(f"   ⏱️ Max durata: {stats['durata_max']:.3f}s")
        
        print(f"\n🚫 CAUSE STALLO:")
        for causa, count in stats['cause_stallo'].items():
            perc = (count / stats['partite_totali']) * 100
            print(f"   • {causa}: {count} ({perc:.1f}%)")
        
        if stats['strategie_vincenti']:
            print(f"\n🏆 STRATEGIE VINCENTI:")
            strategie = sorted(stats['strategie_vincenti'].items(), 
                             key=lambda x: x[1], reverse=True)
            for strategia, count in strategie[:5]:
                print(f"   • {strategia}: {count} volte")
        
        print(f"\n🎯 VALUTAZIONE:")
        if stats['percentuale_vittorie'] >= 15:
            print("   🏆 ECCELLENTE: Tasso vittoria molto alto!")
        elif stats['percentuale_vittorie'] >= 8:
            print("   ✅ BUONO: Tasso vittoria nella norma")
        elif stats['percentuale_vittorie'] >= 3:
            print("   ⚠️ ACCETTABILE: Tasso vittoria realistico")
        else:
            print("   ❌ CRITICO: Tasso vittoria molto basso")
        
        print("="*80)
    
    def salva_statistiche_su_file(self, stats, num_partite):
        """Salva le statistiche complete in un file di testo."""
        # Crea la struttura di cartelle
        cartella_stats = "statistiche_simulazioni"
        cartella_dettagliate = os.path.join(cartella_stats, "reports_dettagliati")
        
        # Crea le cartelle se non esistono
        os.makedirs(cartella_dettagliate, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_file = os.path.join(cartella_dettagliate, f"report_solitario_{timestamp}.txt")
        
        try:
            with open(nome_file, 'w', encoding='utf-8') as f:
                # Header del file
                f.write("="*80 + "\n")
                f.write("🎮 SOLITARIO SIMULATION BOT - STATISTICHE COMPLETE\n")
                f.write("="*80 + "\n")
                f.write(f"📅 Data/Ora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"📦 Versione: {'gameOver_test_.py (con Game Over)' if HAS_GAME_OVER else 'solitario_test_refactoring.py (base)'}\n")
                f.write(f"🎯 Partite simulate: {num_partite}\n")
                f.write("\n")
                
                # Statistiche principali
                f.write("📊 RISULTATI PRINCIPALI:\n")
                f.write("-" * 40 + "\n")
                f.write(f"🎮 Partite totali: {stats['partite_totali']}\n")
                f.write(f"🏆 Vittorie: {stats['vittorie']} ({stats['percentuale_vittorie']:.1f}%)\n")
                f.write(f"🚫 Stalli: {stats['stalli']} ({stats['percentuale_stalli']:.1f}%)\n")
                f.write(f"⏱️ Tempo simulazione: {stats['tempo_simulazione_totale']:.1f} secondi\n")
                f.write(f"⚡ Velocità: {stats['partite_per_secondo']:.1f} partite/secondo\n")
                f.write("\n")
                
                # Analisi dettagliata
                f.write("📈 ANALISI DETTAGLIATA:\n")
                f.write("-" * 40 + "\n")
                f.write(f"🎯 Mosse medie per partita: {stats['media_mosse_per_partita']:.1f}\n")
                f.write(f"⏱️ Durata media per partita: {stats['media_durata_per_partita']:.3f} secondi\n")
                f.write(f"🃏 Carte medie nelle fondazioni: {stats['media_carte_fondazioni']:.1f}/52\n")
                f.write(f"📊 Completamento medio: {(stats['media_carte_fondazioni']/52)*100:.1f}%\n")
                f.write("\n")
                
                # Estremi
                f.write("🔍 VALORI ESTREMI:\n")
                f.write("-" * 40 + "\n")
                f.write(f"⚡ Partita più veloce: {stats['mosse_min']} mosse\n")
                f.write(f"🐌 Partita più lunga: {stats['mosse_max']} mosse\n")
                f.write(f"⏱️ Durata minima: {stats['durata_min']:.3f} secondi\n")
                f.write(f"⏱️ Durata massima: {stats['durata_max']:.3f} secondi\n")
                f.write("\n")
                
                # Cause di stallo
                f.write("🚫 ANALISI CAUSE DI STALLO:\n")
                f.write("-" * 40 + "\n")
                for causa, count in stats['cause_stallo'].items():
                    perc = (count / stats['partite_totali']) * 100
                    f.write(f"• {causa}: {count} partite ({perc:.1f}%)\n")
                f.write("\n")
                
                # Strategie vincenti (se ci sono vittorie)
                if stats['strategie_vincenti']:
                    f.write("🏆 STRATEGIE VINCENTI (azioni finali più comuni):\n")
                    f.write("-" * 40 + "\n")
                    strategie = sorted(stats['strategie_vincenti'].items(), 
                                     key=lambda x: x[1], reverse=True)
                    for strategia, count in strategie:
                        f.write(f"• {strategia}: {count} volte\n")
                    f.write("\n")
                else:
                    f.write("🏆 STRATEGIE VINCENTI:\n")
                    f.write("-" * 40 + "\n")
                    f.write("Nessuna vittoria registrata in questa simulazione.\n")
                    f.write("\n")
                
                # Valutazione finale
                f.write("🎯 VALUTAZIONE FINALE:\n")
                f.write("-" * 40 + "\n")
                if stats['percentuale_vittorie'] >= 15:
                    valutazione = "🏆 ECCELLENTE: Tasso di vittoria molto alto!"
                elif stats['percentuale_vittorie'] >= 8:
                    valutazione = "✅ BUONO: Tasso di vittoria nella norma"
                elif stats['percentuale_vittorie'] >= 3:
                    valutazione = "⚠️ ACCETTABILE: Tasso di vittoria realistico"
                else:
                    valutazione = "❌ CRITICO: Tasso di vittoria molto basso"
                
                f.write(f"{valutazione}\n")
                f.write("\n")
                
                # Note tecniche
                f.write("🔧 NOTE TECNICHE:\n")
                f.write("-" * 40 + "\n")
                f.write(f"• Limite massimo mosse per partita: 10000 (velocità ottimizzata)\n")
                f.write(f"• Strategia utilizzata: Intelligente Veloce (ottimizzata performance)\n")
                f.write(f"• Priorità: 1)Fondazioni 2)Scopri carte 3)Re su vuote 4)Scarto veloce\n")
                f.write(f"• Rilevamento stallo: {'Avanzato (Game Over)' if HAS_GAME_OVER else 'Semplificato'}\n")
                f.write(f"• File sorgente: {'gameOver_test_.py' if HAS_GAME_OVER else 'solitario_test_refactoring.py'}\n")
                f.write("\n")
                
                # Footer
                f.write("="*80 + "\n")
                f.write("Fine del report statistiche\n")
                f.write("="*80 + "\n")
            
            print(f"💾 Statistiche salvate in: {nome_file}")
            return nome_file
            
        except Exception as e:
            print(f"❌ Errore nel salvataggio del file: {e}")
            return None
    
    def salva_log_cumulativo(self, stats, num_partite):
        """Salva un log cumulativo di tutte le simulazioni."""
        # Crea la cartella per le statistiche se non esiste
        cartella_stats = "statistiche_simulazioni"
        os.makedirs(cartella_stats, exist_ok=True)
        
        nome_log = os.path.join(cartella_stats, "log_cumulativo_simulazioni.txt")
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        try:
            # Controlla se il file esiste già
            file_exists = False
            try:
                with open(nome_log, 'r', encoding='utf-8'):
                    file_exists = True
            except FileNotFoundError:
                pass
            
            with open(nome_log, 'a', encoding='utf-8') as f:
                # Se è il primo record, aggiungi header
                if not file_exists:
                    f.write("="*100 + "\n")
                    f.write("🎮 SOLITARIO SIMULATION BOT - LOG CUMULATIVO SIMULAZIONI\n")
                    f.write("="*100 + "\n")
                    f.write("📅 Data/Ora | 🎯 Partite | 🏆 Vittorie (%) | 🚫 Stalli (%) | ⏱️ Tempo | ⚡ Vel | 📦 Versione\n")
                    f.write("-"*100 + "\n")
                
                # Aggiungi la nuova simulazione
                versione = "GameOver" if HAS_GAME_OVER else "Base"
                f.write(f"{timestamp} | {num_partite:6d} | {stats['vittorie']:4d} ({stats['percentuale_vittorie']:5.1f}%) | "
                       f"{stats['stalli']:4d} ({stats['percentuale_stalli']:5.1f}%) | {stats['tempo_simulazione_totale']:6.1f}s | "
                       f"{stats['partite_per_secondo']:5.1f} | {versione}\n")
            
            print(f"📝 Log cumulativo aggiornato: {nome_log}")
            return nome_log
            
        except Exception as e:
            print(f"❌ Errore nel salvataggio del log: {e}")
            return None
    
    def crea_readme_statistiche(self):
        """Crea un file README nella cartella delle statistiche."""
        cartella_stats = "statistiche_simulazioni"
        readme_path = os.path.join(cartella_stats, "README.md")
        
        # Crea il README solo se non esiste già
        if not os.path.exists(readme_path):
            try:
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write("# 📊 Statistiche Simulazioni Solitario\n\n")
                    f.write("Questa cartella contiene tutte le statistiche generate dal Solitario Simulation Bot.\n\n")
                    f.write("## 📁 Struttura delle Cartelle\n\n")
                    f.write("- **`reports_dettagliati/`**: Report completi di ogni singola simulazione\n")
                    f.write("- **`log_cumulativo_simulazioni.txt`**: Log storico di tutte le simulazioni\n\n")
                    f.write("## 📈 Tipi di File\n\n")
                    f.write("### Report Dettagliati\n")
                    f.write("- **Nome**: `report_solitario_YYYYMMDD_HHMMSS.txt`\n")
                    f.write("- **Contenuto**: Analisi completa di una singola simulazione\n")
                    f.write("- **Include**: Statistiche dettagliate, valori estremi, cause di stallo, valutazioni\n\n")
                    f.write("### Log Cumulativo\n")
                    f.write("- **Nome**: `log_cumulativo_simulazioni.txt`\n")
                    f.write("- **Contenuto**: Storico tabellare di tutte le simulazioni\n")
                    f.write("- **Include**: Data/ora, numero partite, percentuali vittorie/stalli, velocità\n\n")
                    f.write("## 🚀 Come Generare Statistiche\n\n")
                    f.write("```bash\n")
                    f.write("# Simulazione standard\n")
                    f.write("python bot_contagame_test.py 1000\n\n")
                    f.write("# Simulazione veloce\n")
                    f.write("python bot_contagame_test.py 50\n\n")
                    f.write("# Con debug\n")
                    f.write("python bot_contagame_test.py 100 debug\n")
                    f.write("```\n\n")
                    f.write("## 📊 Interpretazione Risultati\n\n")
                    f.write("- **🏆 Eccellente**: Tasso vittoria ≥ 15%\n")
                    f.write("- **✅ Buono**: Tasso vittoria ≥ 8%\n")
                    f.write("- **⚠️ Accettabile**: Tasso vittoria ≥ 3%\n")
                    f.write("- **❌ Critico**: Tasso vittoria < 3%\n\n")
                    f.write("---\n")
                    f.write(f"*Generato automaticamente il {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*\n")
                
                print(f"📖 README creato: {readme_path}")
                return readme_path
            except Exception as e:
                print(f"⚠️ Errore nella creazione del README: {e}")
                return None
        else:
            print(f"📖 README già esistente: {readme_path}")
        return readme_path

def main():
    """Funzione principale."""
    print("🤖 Avvio Solitario Simulation Bot...")
    
    num_partite = 1000
    debug_mode = False
    
    if len(sys.argv) > 1:
        try:
            num_partite = int(sys.argv[1])
            print(f"🎯 Partite: {num_partite}")
        except ValueError:
            print("❌ Numero non valido, uso 1000")
    
    if len(sys.argv) > 2 and sys.argv[2] == "debug":
        debug_mode = True
        print("🔍 Debug attivato")
    
    bot = SolitarioSimulationBot(debug=debug_mode)
    
    # Crea la struttura delle cartelle e il README
    bot.crea_readme_statistiche()
    
    statistiche = bot.simula_partite_multiple(num_partite)
    bot.stampa_report(statistiche)
    bot.salva_statistiche_su_file(statistiche, num_partite)
    bot.salva_log_cumulativo(statistiche, num_partite)

if __name__ == "__main__":
    main() 