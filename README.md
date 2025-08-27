# Console Banking — Learning Project

**Short description**  
A simple console banking app written in Python. This project is a learning playground to practice core Python skills: working with functions, control flow, user input, and SQLite databases. It also experiments with CLI UX (colors, emojis, light humor), a short unique-ID recovery flow, and modular code that’s easy to extend.

---

## Features
- ✅ Create accounts with age validation (must be 18+).  
- ✅ Auto-generated unique 10-digit account number.  
- ✅ Short human-friendly unique ID (letter + 2 digits) shown once for account recovery.  
- ✅ Login with username + login PIN. Recover login PIN using name + unique ID.  
- ✅ Deposit and withdraw flows, with transfer PIN verification and balance checks.  
- ✅ CLI UX with color and emojis (uses `colorama`) and light humor in prompts.

---

## Why I built this
This project helps me:
- Practice Python fundamentals (functions, conditionals, error handling).  
- Learn to persist data with SQLite and read/write reliably.  
- Prototype CLI UX ideas (colors, humour, recovery flows).  
- Prepare the code for future improvements (PIN hashing, tests, modularization).

---

## Tech / Dependencies
- Python 3.8+  
- Standard library: `sqlite3`, `random`, `datetime`  
- Extras: `colorama` for colored terminal output  
Install the dependency with:
```bash
pip install colorama
