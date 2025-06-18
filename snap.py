import os  # Importa il modulo per interagire con il sistema operativo
from datetime import datetime  # Importa la classe datetime per gestire data e ora
import re  # Importa il modulo per le espressioni regolari

# Funzione per creare uno snapshot della struttura di una cartella
# percorso: directory da analizzare
# nome_file_snapshot: nome del file di output (non usato direttamente, vedi sotto)
def snapshot_cartella(percorso, nome_file_snapshot="snap.txt"):
    # Trova il numero massimo già usato nei file snapshot nella cartella corrente
    max_num = 0
    pattern = re.compile(r"snapshot_(\d{3})_\d{8}_\d{6}\.txt")  # Pattern per trovare i file snapshot esistenti
    for f in os.listdir('.'):
        match = pattern.match(f)  # Verifica se il file corrisponde al pattern
        if match:
            num = int(match.group(1))  # Estrae il numero progressivo
            if num > max_num:
                max_num = num  # Aggiorna il massimo trovato
    numero = max_num + 1  # Numero progressivo per il nuovo snapshot
    numero_str = str(numero).zfill(3)  # Formatta il numero a 3 cifre (es: 001)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Ottiene data e ora attuali formattate
    nome_snapshot = f"snapshot_{numero_str}_{timestamp}.txt"  # Costruisce il nome del file snapshot
    with open(nome_snapshot, "w", encoding="utf-8") as f:  # Apre il file in scrittura con codifica UTF-8
        for root, dirs, files in os.walk(percorso):  # Attraversa ricorsivamente la cartella
            livello = root.replace(percorso, '').count(os.sep)  # Calcola il livello di profondità
            indent = ' ' * 4 * livello  # Indentazione per la cartella
            f.write(f"{indent}{os.path.basename(root)}/\n")  # Scrive il nome della cartella
            subindent = ' ' * 4 * (livello + 1)  # Indentazione per i file
            for file in files:
                f.write(f"{subindent}{file}\n")  # Scrive il nome del file
    print(f"Snapshot salvato in {nome_snapshot}")  # Messaggio di conferma

# Esegui lo snap della cartella corrente se lo script è eseguito direttamente
if __name__ == "__main__":
    snapshot_cartella(".", "snapshot.txt")  # Chiama la funzione sulla cartella corrente 

def mostra_tavolo(tavolo):
    # Calcola la colonna più lunga
    max_len = max(len(colonna) for colonna in tavolo)
    # Per ogni riga (dall'alto verso il basso)
    for i in range(max_len):
        riga = ""
        for colonna in tavolo:
            if i < len(colonna):
                carta, coperta = colonna[i]
                if coperta:
                    riga += "[#]    "
                else:
                    riga += f"[{carta}] ".ljust(6)
            else:
                riga += "      "  # spazio vuoto per colonne più corte
        print(riga) 