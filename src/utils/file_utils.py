import os
import shutil

def move_file(src: str, dst: str) -> None:
    """Move arquivo criando diretórios necessários"""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(src, dst)