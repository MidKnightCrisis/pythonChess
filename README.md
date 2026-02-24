# PythonChess – Logikbasierte Schachengine

Ein von Grund auf in Python entwickeltes Schachspiel mit Fokus auf eine saubere Implementierung der Spiellogik und Validierung komplexer Spielzüge. 

Dieses Projekt dient als Test meiner Kenntnisse in der objektorientierten Programmierung, dem Zustandsmanagement und der GUI-Entwicklung mit `pygame`.

## Features

* **Vollständiges Regelwerk:** Implementierung aller Standard-Schachzüge.
* **Sonderregeln (Special Moves):** 
    * **En Passant:** Logik zur Erkennung und Ausführung des Schlagens im Vorbeigehen.
    * **Castling:** Prüfung von Bedrohungsfeldern und Verfügbarkeit (King/Queen-side).
    * **Promotion:** Automatische Umwandlung (aktuell in einer Dame) beim Erreichen des anderen Endes.
* **Move Validation:** Robuste `get_legal_moves` Logik, die Züge verhindert, welche den eigenen König ins Schach stellen würden.
* **Game States:** Automatische Erkennung von Schachmatt und Patt (Stalemate).
* **GUI:** Interaktives Spielfeld mit Highlight-Funktion für ausgewählte Figuren.

## 🛠️ Technische Details

* **Sprache:** Python 3.12
* **Bibliothek:** `pygame` für das Rendering und Event-Handling.
* **Architektur:** * Effiziente Zugverwaltung mittels `namedtuples`.
    * Modularer Aufbau für die Bewegungslogik (Slider vs. Stepper Pieces).
    * Simulationsbasierte Legalitätsprüfung (Move-Undo-Zyklus).

## 🏁 Installation & Start

1. Klone das Repository:
   ```bash
   git clone [https://github.com/MidKnightCrisis/pythonChess.git](https://github.com/MidKnightCrisis/pythonChess.git)
2. Installiere Abhängigkeiten:
   ```bash
   pip install -r requirements.txt
3. Starte das Spiel:
   ```bash
   python Main.py

* **Roadmap**
  * **Promotion-UI**: Auswahlmenü für die Promotion
  * **Implementierung einer Evaluation**: Auswertung des aktuellen Spielstandes
  * **primitive KI**: Anwendung der Evaluation als KI über Minimax-Algorithmus

* **Future Work**: Aktuell in Betracht gezogene, aber noch nicht fest geplante Implementierungen
  * **Stockfish-AI**: Anbindung an Stockfish für fortgeschrittenere KI
  * **Docker-Container**: Aneignung von Methoden für Hardware-unabhängigen Umgebung über Docker
  * **Web-Integration**: Aneignung von Methoden zur Einrichtung des Projekts im Netz
