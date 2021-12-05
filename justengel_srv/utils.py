import os
from typing import Union, Tuple, List
from fastapi import FastAPI, APIRouter, Request
from fastapi.templating import Jinja2Templates
from starlette.background import BackgroundTask

from justengel_theme import ThemeTemplates
from justengel_material import MaterialTemplates, Message

__all__ = ['MY_DIR', 'get_theme', 'set_theme', 'template', 'add_message', 'get_messages']


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


def template(name: str, context: dict, status_code: int = 200, headers: dict = None, media_type: str = None,
             background: BackgroundTask = None, **kwargs):
    global theme
    return theme.TemplateResponse(name, context, status_code=status_code, headers=headers,
                                  media_type=media_type, background=background, **kwargs)


def add_message(request: Request, msg_type: str, msg: str):
    """Add a message to a session."""
    session = getattr(request, 'session', None)
    if session:
        notify = f'{msg_type},{msg}'
        try:
            request.session['messages'] += ';' + notify
        except (AttributeError, KeyError, ValueError, TypeError, Exception):
            request.session['messages'] = notify


def get_messages(request: Request) -> List[Message]:
    """Return a list of messages from the session."""
    messages = []

    session = getattr(request, 'session', None)
    if session:
        try:
            for v in session['messages'].split(';'):
                try:
                    msg_type, msg = v.split(',')
                    messages.append(Message(msg_type=msg_type, msg=msg))
                except (AttributeError, KeyError, ValueError, TypeError, Exception):
                    pass

            session['messages'] = ''
        except (AttributeError, KeyError, ValueError, TypeError, Exception):
            pass

    return messages
