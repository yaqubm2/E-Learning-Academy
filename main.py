"""Flet entrypoint for local runs and packaging."""
from frontend.main import main
import flet as ft

if __name__ == '__main__':
    ft.run(main)
