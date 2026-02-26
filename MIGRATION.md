# Piano di Migrazione: Easyfish -> Orologic

Questo documento descrive i passaggi per integrare Easyfish come estensione all'interno del progetto Orologic.
**Principio Guida:** Non modificare i file core di Orologic se non strettamente necessario e autorizzato. Copiare i file invece di spostarli per mantenere un backup.

## Fase 1: Preparazione Struttura (Safe)
1.  Creare la directory di destinazione: `Mine/orologic/orologic_modules/easyfish/`.
2.  Creare un file `__init__.py` vuoto in questa directory per renderla un pacchetto Python.
3.  Copiare i seguenti file da `Mine/Easyfish/src/` a `Mine/orologic/orologic_modules/easyfish/`:
    -   `board.py`
    -   `constants.py`
    -   `interaction.py`
    -   `pgn_handler.py`
    -   `utils.py` (da valutare se ridondante con `board_utils.py`)
4.  Copiare `Mine/Easyfish/easyfish.py` in `Mine/orologic/orologic_modules/easyfish/main.py` (rinominandolo).

## Fase 2: Adattamento Codice (Refactoring in-place)
Lavorare SOLO sui file copiati in `orologic_modules/easyfish/`.

1.  **Engine**:
    -   Modificare `main.py` (ex easyfish.py) per importare `orologic_modules.engine`.
    -   Rimuovere l'uso di `src.engine_handler` locale.
    -   Usare `orologic_modules.engine.ENGINE` (globale) e `InitEngine()`.

2.  **Board Utils**:
    -   Confrontare `utils.py` (Easyfish) con `orologic_modules/board_utils.py`.
    -   Sostituire le chiamate a `MoveToString` con `board_utils.DescribeMove`.
    -   Se `utils.py` contiene funzioni uniche (es. `ExploreColumnsOrRows`), mantenerle o integrarle in `board_utils.py` (con cautela).

3.  **Localizzazione**:
    -   Importare la funzione di traduzione `_` da Orologic (`from orologic_modules.config import _` o simile).
    -   Avvolgere le stringhe hardcoded di Easyfish con `_()`.

4.  **Paths**:
    -   Aggiornare i percorsi dei file (PGN database, settings) per usare le cartelle di Orologic (`settings/`, `pgn/`).

## Fase 3: Integrazione (Richiede Autorizzazione)
Questi passaggi modificano i file esistenti di Orologic.

1.  **Menu Config**:
    -   File: `orologic_modules/config.py`
    -   Azione: Aggiungere alla chiave `MENU_CHOICES`:
        ```python
        "easyfish": _("Easyfish (Interfaccia Accessibile)")
        ```

2.  **Main Dispatch**:
    -   File: `orologic.py`
    -   Azione: Importare il modulo: `from orologic_modules.easyfish import main as easyfish_app`
    -   Azione: Aggiungere il blocco `elif` nel loop principale:
        ```python
        elif scelta == "easyfish":
            easyfish_app.run() # O funzione equivalente
        ```

## Fase 4: Pulizia e Testing
1.  Verificare che Easyfish si avvii dal menu di Orologic.
2.  Verificare che usi lo stesso motore configurato in Orologic.
3.  Verificare che le traduzioni funzionino.
4.  (Opzionale) Rimuovere i file originali in `Mine/Easyfish` una volta confermato il funzionamento completo.
