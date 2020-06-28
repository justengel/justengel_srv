import os
from typing import Union, Tuple
from fastapi import FastAPI, APIRouter, Request
from fastapi.templating import Jinja2Templates
from justengel_theme import ThemeTemplates
from justengel_material import MaterialTemplates

__all__ = ['MY_DIR', 'get_theme', 'set_theme']


MY_DIR = os.path.dirname(__file__)
theme: ThemeTemplates = None

def get_theme():
    global theme
    if theme is None:
        return MaterialTemplates(os.path.join(MY_DIR, 'templates'))
    return theme


def set_theme(tmp):
    global theme
    theme = tmp
    return theme
