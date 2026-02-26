# EasyFish Roadmap & Todo

## 1. Refactoring & Architecture (Completed)
- [x] **Modularization**: Split monolithic `Easyfish.py` into `src/` modules (board, engine, pgn, utils, interaction).
- [x] **State Management**: Removed global variables dependency.
- [x] **Cleanup**: Removed unused code and organized imports.
- [x] **Integration**: Merged into Orologic as `orologic_modules/easyfish`.

## 2. Localization (I18N) (Current Priority)
- [ ] **String Encapsulation**: Wrap all user-facing strings with `_()`.
- [ ] **Extraction**: Update `messages.pot` using pybabel.
- [ ] **Translation (IT)**: Translate strings to Italian in `.po` file.
- [ ] **Compilation**: Compile `.mo` files.

## 3. Core Gameplay & Variants
- [ ] **T. Variants Support**:
    - [ ] Implement `.v` command: Start a new variation branch from current position.
    - [ ] Implement `.vok` command: Close current variant and return to the main line/parent branch.
    - [ ] Update Prompt Logic: Display current variance level (e.g., `15. Qc6 Lvl1 c4 >`) to indicate depth.
    - [ ] Handle "No Variant" error: Handle `.vok` when not in a variant.
- [ ] **AI. Takeback/Undo**: Command to delete/undo the last move made.
- [ ] **R. Board Editor**: Verify and fix editing starting from a completely empty board.

## 4. PGN Database & File Management
- [ ] **Y. Multi-game Management**:
    - [ ] Load all games from a single PGN file (currently appends/loads, but needs navigation).
    - [ ] `list_games`: Show a list of games in the DB.
    - [ ] `filter_games`: Filter by Player, Result, etc.
    - [ ] Select a specific game to load from the list.
- [ ] **V. Paste Full PGN**: Ability to paste a full PGN text (headers + moves) to load a game directly.
- [ ] **W. Copy PGN**: Verify `CopyPGNToClipboard` functionality (Refactored, needs testing).
- [ ] **AA. Board to Clipboard**: Copy the ASCII board representation to clipboard.

## 5. Analysis & Explorer Mode
- [ ] **X. Explorer Mode Testing**: Verify navigation (`d`, `e`, `z`) works correctly after refactoring.
- [ ] **U. Auto-Analysis Comment**: Implement `_a` to insert engine analysis directly into the move's comment.
- [ ] **Analysis Features**:
    - [ ] Save analysis settings between sessions.

## 6. Accessibility & Board Info
- [ ] **AC. Group Listing**: Add command to list *all* White pieces or *all* Black pieces at once.
- [ ] **AD. Pinned Pieces**: Logic to identify pinned pieces.
- [ ] **AE. Show Pinned**: Include "pinned" status in piece info output.

## 7. External Integrations & Future
- [ ] **O. Lichess**: Potential integration with Lichess API.
- [ ] **Wiki**: Create a GitHub Wiki for documentation (as mentioned in README).
