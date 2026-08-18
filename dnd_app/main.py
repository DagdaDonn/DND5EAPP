#!/usr/bin/env python3
"""MIMIC (D&D 5e Character Creator) — entry point."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dnd_app.ui.main_window import main
if __name__ == "__main__":
    main()
