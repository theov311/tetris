from cx_Freeze import setup, Executable

setup(
    name = "Tetris à deux joueurs",
    version = "1.0",
    description = "Jeu Tetris humain vs IA",
    executables = [Executable("tetris_game.py", base="Win32GUI")]
)