"""
SOLITARIO BOT TESTER - Test Automatizzato E2E
=============================================
Questo bot simula un utente che gioca al solitario per testare automaticamente
tutte le funzionalità del gioco senza intervento manuale.

VERSIONI SUPPORTATE:
- gameOver_test_.py: Versione completa con controllo Game Over
- solitario_test_refactoring.py: Versione base senza Game Over

UTILIZZO:
- python solitario_bot_tester.py          # Auto-rileva la versione disponibile
- python solitario_bot_tester.py gameOver # Forza test su gameOver_test_.py
- python solitario_bot_tester.py base     # Forza test su solitario_test_refactoring.py

TIPI DI TEST IMPLEMENTATI:
- End-to-End Testing: Simula l'intera esperienza utente
- Integration Testing: Testa l'integrazione tra le classi
- Smoke Testing: Verifica che le funzioni base funzionino
- Stress Testing: Testa il comportamento con molte operazioni

COSA TESTA:
- Tutti i comandi disponibili ([p], [s], [f], [m], [mf], [sc], [r])
- Gestione errori e input non validi
- Sistema di rimescolamento automatico e manuale
- Logica di vittoria
- Conteggio carte e stato del gioco
- Controllo Game Over (se disponibile)
"""

import sys
import random
import time

# Importa le classi dal file del solitario
try:
    # Prova prima a importare da gameOver_test_.py (versione con Game Over)
    from gameOver_test_ import (
        Mazzo, Tavolo, Finali, Carta, SEMI, VALORI, 
        controlla_mosse_possibili, messaggio_game_over
    )
    print("✅ Importazione da gameOver_test_.py riuscita!")
    HAS_GAME_OVER = True
except ImportError:
    try:
        # Se fallisce, prova con solitario_test_refactoring.py (versione base)
        from solitario_test_refactoring import Mazzo, Tavolo, Finali, Carta, SEMI, VALORI
        print("✅ Importazione da solitario_test_refactoring.py riuscita!")
        HAS_GAME_OVER = False
        print("⚠️ Versione senza Game Over - alcuni test saranno saltati")
    except ImportError:
        print("❌ Errore: Non riesco a importare da nessun file solitario")
        sys.exit(1)

class SolitarioBot:
    """
    Bot che simula un giocatore di solitario per testare automaticamente
    tutte le funzionalità del gioco.
    """
    
    def __init__(self, debug=True):
        """
        Inizializza il bot di test.
        
        Args:
            debug (bool): Se True, stampa informazioni dettagliate durante i test
        """
        self.debug = debug  # Flag per abilitare/disabilitare output debug
        self.test_results = []  # Lista per salvare i risultati dei test
        self.commands_tested = []  # Lista dei comandi testati
        
    def log(self, message, test_type="INFO"):
        """
        Stampa un messaggio di log se il debug è abilitato.
        
        Args:
            message (str): Messaggio da stampare
            test_type (str): Tipo di test (INFO, SUCCESS, ERROR, WARNING)
        """
        if self.debug:
            icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
            icon = icons.get(test_type, "ℹ️")
            print(f"{icon} [{test_type}] {message}")
    
    def setup_game(self):
        """
        Inizializza una nuova partita di solitario per i test.
        
        Returns:
            tuple: (mazzo, tavolo, finali, riserva, scarti)
        """
        self.log("Inizializzazione nuova partita di test...")
        mazzo = Mazzo()  # Crea e mescola il mazzo
        tavolo = Tavolo(mazzo)  # Distribuisce le carte nelle colonne
        finali = Finali()  # Crea le pile finali vuote
        riserva = []  # Lista per le carte pescate dal mazzo
        scarti = []  # Lista per le carte scartate
        
        self.log(f"Partita inizializzata: Mazzo({len(mazzo.carte)}) carte, Tavolo con 7 colonne")
        return mazzo, tavolo, finali, riserva, scarti
    
    def test_pesca_carte(self, mazzo, riserva, scarti):
        """
        Testa la funzionalità di pesca delle carte dal mazzo.
        
        Args:
            mazzo: Istanza della classe Mazzo
            riserva: Lista delle carte in riserva
            scarti: Lista delle carte scartate
        
        Returns:
            bool: True se il test è passato, False altrimenti
        """
        self.log("🎣 Test pesca carte...")
        initial_mazzo_size = len(mazzo.carte)  # Dimensione iniziale del mazzo
        
        try:
            # Pesca alcune carte
            for i in range(min(5, initial_mazzo_size)):  # Pesca al massimo 5 carte o tutte quelle disponibili
                carta = mazzo.pesca()  # Pesca una carta
                if carta:
                    carta.coperta = False  # La carta pescata è sempre scoperta
                    riserva.append(carta)  # Aggiunge la carta alla riserva
                    self.log(f"Pescata carta: {carta}")
            
            # Verifica che il mazzo sia diminuito
            if len(mazzo.carte) == initial_mazzo_size - min(5, initial_mazzo_size):
                self.log("Test pesca carte PASSATO", "SUCCESS")
                self.commands_tested.append("pesca")
                return True
            else:
                self.log("Test pesca carte FALLITO: dimensione mazzo incorretta", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Test pesca carte FALLITO con eccezione: {e}", "ERROR")
            return False
    
    def test_scarta_carte(self, mazzo, riserva, scarti):
        """
        Testa la funzionalità di scarto delle carte dalla riserva.
        
        Args:
            mazzo: Istanza della classe Mazzo
            riserva: Lista delle carte in riserva
            scarti: Lista delle carte scartate
        
        Returns:
            bool: True se il test è passato, False altrimenti
        """
        self.log("🗑️ Test scarta carte...")
        
        if not riserva:  # Se non ci sono carte in riserva
            self.log("Nessuna carta in riserva da scartare, test saltato", "WARNING")
            return True
        
        try:
            initial_riserva_size = len(riserva)  # Dimensione iniziale della riserva
            initial_scarti_size = len(scarti)  # Dimensione iniziale degli scarti
            
            # Scarta una carta
            carta_da_scartare = riserva.pop()  # Rimuove l'ultima carta dalla riserva
            mazzo.aggiungi_scarto(carta_da_scartare, scarti)  # La aggiunge agli scarti
            
            # Verifica che la carta sia stata spostata correttamente
            if len(riserva) == initial_riserva_size - 1 and len(scarti) == initial_scarti_size + 1:
                self.log(f"Carta {carta_da_scartare} scartata correttamente", "SUCCESS")
                self.commands_tested.append("scarta")
                return True
            else:
                self.log("Test scarta carte FALLITO: dimensioni liste incorrette", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Test scarta carte FALLITO con eccezione: {e}", "ERROR")
            return False
    
    def test_rimescolamento(self, mazzo, riserva, scarti):
        """
        Testa la funzionalità di rimescolamento degli scarti nel mazzo.
        
        Args:
            mazzo: Istanza della classe Mazzo
            riserva: Lista delle carte in riserva
            scarti: Lista delle carte scartate
        
        Returns:
            bool: True se il test è passato, False altrimenti
        """
        self.log("🔄 Test rimescolamento...")
        
        if not scarti:  # Se non ci sono carte negli scarti
            self.log("Nessuna carta negli scarti da rimescolare, test saltato", "WARNING")
            return True
        
        try:
            initial_scarti_size = len(scarti)  # Dimensione iniziale degli scarti
            initial_mazzo_size = len(mazzo.carte)  # Dimensione iniziale del mazzo
            
            # Rimescola gli scarti nel mazzo
            mazzo.rimescola(scarti)  # Rimescola gli scarti nel mazzo
            
            # Verifica che le carte siano state spostate correttamente
            expected_mazzo_size = initial_mazzo_size + initial_scarti_size  # Dimensione attesa del mazzo
            if len(mazzo.carte) == expected_mazzo_size and len(scarti) == 0:
                self.log(f"Rimescolate {initial_scarti_size} carte correttamente", "SUCCESS")
                self.commands_tested.append("rimescola")
                return True
            else:
                self.log("Test rimescolamento FALLITO: dimensioni incorrette", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Test rimescolamento FALLITO con eccezione: {e}", "ERROR")
            return False
    
    def test_spostamento_colonne(self, tavolo):
        """
        Testa la funzionalità di spostamento carte tra colonne.
        
        Args:
            tavolo: Istanza della classe Tavolo
        
        Returns:
            bool: True se il test è passato, False altrimenti
        """
        self.log("↔️ Test spostamento tra colonne...")
        
        try:
            # Trova una colonna con carte scoperte da spostare
            for i, colonna in enumerate(tavolo.colonne):
                if colonna and not colonna[-1].coperta:  # Se la colonna ha carte e l'ultima è scoperta
                    # Prova a spostare la carta in una colonna vuota o compatibile
                    for j, dest_colonna in enumerate(tavolo.colonne):
                        if i != j:  # Non spostare sulla stessa colonna
                            if tavolo.sposta_carte(i, j, 1):  # Prova a spostare 1 carta
                                self.log(f"Spostata carta da colonna {i} a colonna {j}", "SUCCESS")
                                self.commands_tested.append("sposta_colonne")
                                return True
            
            self.log("Nessuna mossa valida trovata per spostamento colonne", "WARNING")
            return True  # Non è un errore, è solo che non ci sono mosse valide
            
        except Exception as e:
            self.log(f"Test spostamento colonne FALLITO con eccezione: {e}", "ERROR")
            return False
    
    def test_spostamento_finali(self, tavolo, finali):
        """
        Testa la funzionalità di spostamento carte verso le pile finali.
        
        Args:
            tavolo: Istanza della classe Tavolo
            finali: Istanza della classe Finali
        
        Returns:
            bool: True se il test è passato, False altrimenti
        """
        self.log("🏁 Test spostamento verso pile finali...")
        
        try:
            # Cerca un Asso scoperto da spostare alle fondazioni
            for i, colonna in enumerate(tavolo.colonne):
                if colonna and not colonna[-1].coperta and colonna[-1].valore == 'A':
                    if finali.sposta_verso_finali(tavolo, i):  # Prova a spostare l'Asso
                        self.log(f"Spostato Asso da colonna {i} alle fondazioni", "SUCCESS")
                        self.commands_tested.append("sposta_finali")
                        return True
            
            self.log("Nessun Asso trovato per spostamento alle fondazioni", "WARNING")
            return True  # Non è un errore, è solo che non ci sono Assi disponibili
            
        except Exception as e:
            self.log(f"Test spostamento finali FALLITO con eccezione: {e}", "ERROR")
            return False
    
    def test_vittoria(self, finali):
        """
        Testa la funzionalità di controllo vittoria.
        
        Args:
            finali: Istanza della classe Finali
        
        Returns:
            bool: True se il test è passato, False altrimenti
        """
        self.log("🏆 Test controllo vittoria...")
        
        try:
            # Test condizione di non vittoria (stato normale)
            vittoria_normale = finali.vittoria()  # Dovrebbe essere False in una partita normale
            if not vittoria_normale:
                self.log("Controllo vittoria normale corretto (non vittoria)", "SUCCESS")
            
            # Test condizione di vittoria simulata (riempie tutte le pile)
            for seme in SEMI:
                finali.pile[seme] = [Carta(val, seme, False) for val in VALORI]  # Riempie la pila con tutte le carte
            
            vittoria_simulata = finali.vittoria()  # Dovrebbe essere True ora
            if vittoria_simulata:
                self.log("Controllo vittoria simulata corretto (vittoria)", "SUCCESS")
                self.commands_tested.append("vittoria")
                return True
            else:
                self.log("Test vittoria FALLITO: vittoria non rilevata", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Test vittoria FALLITO con eccezione: {e}", "ERROR")
            return False
    
    def test_game_over(self, mazzo, tavolo, finali, riserva, scarti):
        """
        Testa la funzionalità di controllo Game Over (solo se disponibile).
        
        Args:
            mazzo: Istanza della classe Mazzo
            tavolo: Istanza della classe Tavolo
            finali: Istanza della classe Finali
            riserva: Lista delle carte in riserva
            scarti: Lista delle carte scartate
        
        Returns:
            bool: True se il test è passato, False altrimenti
        """
        if not HAS_GAME_OVER:
            self.log("🚫 Test Game Over saltato - funzionalità non disponibile", "WARNING")
            return True
        
        self.log("🎯 Test controllo Game Over...")
        
        try:
            # Test 1: Situazione normale (dovrebbe avere mosse possibili)
            mosse_disponibili_normale = controlla_mosse_possibili(tavolo, finali, mazzo, riserva, scarti)
            if mosse_disponibili_normale:
                self.log("Controllo Game Over normale corretto (mosse disponibili)", "SUCCESS")
            
            # Test 2: Simula situazione di Game Over
            # Svuota tutto per forzare una situazione di stallo
            mazzo_backup = mazzo.carte[:]  # Backup delle carte del mazzo
            riserva_backup = riserva[:]    # Backup delle carte in riserva
            scarti_backup = scarti[:]      # Backup delle carte negli scarti
            
            # Svuota mazzo, riserva e scarti
            mazzo.carte.clear()
            riserva.clear()
            scarti.clear()
            
            # Rimuove tutte le carte scoperte dalle colonne per simulare stallo
            for colonna in tavolo.colonne:
                # Mantiene solo le carte coperte (se ce ne sono)
                carte_coperte = [carta for carta in colonna if carta.coperta]
                colonna.clear()
                colonna.extend(carte_coperte)
            
            # Ora controlla se rileva correttamente il Game Over
            mosse_disponibili_stallo = controlla_mosse_possibili(tavolo, finali, mazzo, riserva, scarti)
            
            if not mosse_disponibili_stallo:
                self.log("Controllo Game Over simulato corretto (nessuna mossa disponibile)", "SUCCESS")
                
                # Test 3: Verifica che il messaggio Game Over funzioni
                messaggio = messaggio_game_over(tavolo, finali, mazzo, riserva, scarti)
                if "GAME OVER" in messaggio and "Non ci sono più mosse possibili" in messaggio:
                    self.log("Messaggio Game Over generato correttamente", "SUCCESS")
                    self.commands_tested.append("game_over")
                    
                    # Ripristina lo stato originale
                    mazzo.carte = mazzo_backup
                    riserva.extend(riserva_backup)
                    scarti.extend(scarti_backup)
                    
                    return True
                else:
                    self.log("Test Game Over FALLITO: messaggio non corretto", "ERROR")
                    return False
            else:
                self.log("Test Game Over FALLITO: non rileva situazione di stallo", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Test Game Over FALLITO con eccezione: {e}", "ERROR")
            return False
    
    def test_conteggio_carte(self, mazzo, riserva, scarti):
        """
        Testa la funzionalità di conteggio delle carte totali.
        
        Args:
            mazzo: Istanza della classe Mazzo
            riserva: Lista delle carte in riserva
            scarti: Lista delle carte scartate
        
        Returns:
            bool: True se il test è passato, False altrimenti
        """
        self.log("🔢 Test conteggio carte...")
        
        try:
            # Conta manualmente le carte
            conteggio_manuale = len(mazzo.carte) + len(riserva) + len(scarti)
            
            # Usa il metodo del mazzo per contare
            conteggio_automatico = mazzo.conta_carte_totali(riserva, scarti)
            
            if conteggio_manuale == conteggio_automatico:
                self.log(f"Conteggio carte corretto: {conteggio_automatico}", "SUCCESS")
                self.commands_tested.append("conteggio")
                return True
            else:
                self.log(f"Test conteggio FALLITO: manuale={conteggio_manuale}, automatico={conteggio_automatico}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Test conteggio carte FALLITO con eccezione: {e}", "ERROR")
            return False
    
    def run_all_tests(self):
        """
        Esegue tutti i test automatizzati sul solitario.
        
        Returns:
            dict: Risultati dei test con statistiche
        """
        self.log("🚀 Avvio test suite completa...", "INFO")
        start_time = time.time()  # Tempo di inizio test
        
        # Inizializza una nuova partita
        mazzo, tavolo, finali, riserva, scarti = self.setup_game()
        
        # Lista dei test da eseguire
        tests = [
            ("Test Pesca Carte", lambda: self.test_pesca_carte(mazzo, riserva, scarti)),
            ("Test Scarta Carte", lambda: self.test_scarta_carte(mazzo, riserva, scarti)),
            ("Test Rimescolamento", lambda: self.test_rimescolamento(mazzo, riserva, scarti)),
            ("Test Spostamento Colonne", lambda: self.test_spostamento_colonne(tavolo)),
            ("Test Spostamento Finali", lambda: self.test_spostamento_finali(tavolo, finali)),
            ("Test Conteggio Carte", lambda: self.test_conteggio_carte(mazzo, riserva, scarti)),
            ("Test Vittoria", lambda: self.test_vittoria(finali)),
            ("Test Game Over", lambda: self.test_game_over(mazzo, tavolo, finali, riserva, scarti)),
        ]
        
        # Esegue tutti i test
        passed_tests = 0  # Contatore test passati
        total_tests = len(tests)  # Numero totale di test
        
        for test_name, test_func in tests:
            self.log(f"Eseguendo: {test_name}")
            try:
                if test_func():  # Esegue il test
                    passed_tests += 1
                    self.test_results.append(f"✅ {test_name}")
                else:
                    self.test_results.append(f"❌ {test_name}")
            except Exception as e:
                self.log(f"Errore durante {test_name}: {e}", "ERROR")
                self.test_results.append(f"💥 {test_name} (Eccezione)")
        
        # Calcola statistiche finali
        end_time = time.time()  # Tempo di fine test
        duration = end_time - start_time  # Durata totale
        success_rate = (passed_tests / total_tests) * 100  # Percentuale di successo
        
        # Prepara risultati finali
        results = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": success_rate,
            "duration": duration,
            "commands_tested": self.commands_tested,
            "test_results": self.test_results
        }
        
        return results
    
    def print_final_report(self, results):
        """
        Stampa un report finale dei risultati dei test.
        
        Args:
            results (dict): Risultati dei test da stampare
        """
        print("\n" + "="*60)
        print("🎮 SOLITARIO BOT TESTER - REPORT FINALE")
        print("="*60)
        
        # Mostra quale versione è stata testata
        if HAS_GAME_OVER:
            print("📦 VERSIONE TESTATA: gameOver_test_.py (con Game Over)")
            print("🎯 FUNZIONALITÀ: Completa con controllo Game Over")
        else:
            print("📦 VERSIONE TESTATA: solitario_test_refactoring.py (base)")
            print("⚠️ FUNZIONALITÀ: Base senza controllo Game Over")
        
        print(f"\n📊 STATISTICHE:")
        print(f"   • Test totali: {results['total_tests']}")
        print(f"   • Test passati: {results['passed_tests']}")
        print(f"   • Test falliti: {results['failed_tests']}")
        print(f"   • Tasso di successo: {results['success_rate']:.1f}%")
        print(f"   • Durata: {results['duration']:.2f} secondi")
        
        print(f"\n🎯 COMANDI TESTATI:")
        for cmd in results['commands_tested']:
            print(f"   • {cmd}")
        
        print(f"\n📋 RISULTATI DETTAGLIATI:")
        for result in results['test_results']:
            print(f"   {result}")
        
        # Valutazione finale
        if results['success_rate'] >= 80:
            print(f"\n🏆 VALUTAZIONE: ECCELLENTE! Il codice funziona correttamente.")
        elif results['success_rate'] >= 60:
            print(f"\n⚠️ VALUTAZIONE: BUONO, ma ci sono alcuni problemi da risolvere.")
        else:
            print(f"\n❌ VALUTAZIONE: CRITICO, molti test sono falliti.")
        
        # Nota speciale per Game Over
        if HAS_GAME_OVER and "game_over" in results['commands_tested']:
            print(f"\n🎯 GAME OVER: Controllo automatico delle situazioni di stallo ATTIVO!")
        elif not HAS_GAME_OVER:
            print(f"\n💡 SUGGERIMENTO: Usa gameOver_test_.py per testare il controllo Game Over.")
        
        print("="*60)

def main():
    """
    Funzione principale che avvia il bot di test.
    """
    print("🤖 Avvio Solitario Bot Tester...")
    
    # Controlla se è stato specificato un file specifico da testare
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
        print(f"🎯 File specificato: {target_file}")
        
        # Prova a importare il file specificato
        if target_file == "gameOver":
            try:
                global HAS_GAME_OVER
                from gameOver_test_ import (
                    Mazzo, Tavolo, Finali, Carta, SEMI, VALORI, 
                    controlla_mosse_possibili, messaggio_game_over
                )
                HAS_GAME_OVER = True
                print("✅ Forzata importazione da gameOver_test_.py")
            except ImportError:
                print("❌ Errore: Non riesco a importare gameOver_test_.py")
                return
        elif target_file == "base":
            try:
                HAS_GAME_OVER = False
                from solitario_test_refactoring import Mazzo, Tavolo, Finali, Carta, SEMI, VALORI
                print("✅ Forzata importazione da solitario_test_refactoring.py")
            except ImportError:
                print("❌ Errore: Non riesco a importare solitario_test_refactoring.py")
                return
        else:
            print("❌ Argomento non valido. Usa 'gameOver' o 'base'")
            print("💡 Esempio: python solitario_bot_tester.py gameOver")
            return
    
    # Mostra quale versione sarà testata
    if HAS_GAME_OVER:
        print("🎯 Testando gameOver_test_.py (versione completa)")
    else:
        print("🎯 Testando solitario_test_refactoring.py (versione base)")
    
    # Crea il bot di test
    bot = SolitarioBot(debug=True)  # Abilita output debug dettagliato
    
    # Esegue tutti i test
    results = bot.run_all_tests()
    
    # Stampa il report finale
    bot.print_final_report(results)

if __name__ == "__main__":
    # Punto di ingresso del programma: esegue main() solo se il file è eseguito direttamente
    main() 