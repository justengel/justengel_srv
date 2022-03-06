import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware

from justengel_material import MaterialTemplates
from justengel_srv.utils import MY_DIR, set_theme, template, get_messages

from justengel_srv.local import settings


__all__ = ['app', 'theme']  # use get_theme from utils


app = FastAPI()

# Middleware
# app.add_middleware(HTTPSRedirectMiddleware)  # Nginx will do in most cases
app.add_middleware(CORSMiddleware, allow_origins=['https://justengel.com', 'https://www.justengel.com'])
app.add_middleware(TrustedHostMiddleware, allowed_hosts=['justengel.com', 'www.justengel.com', '127.0.0.1'])
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET, https_only=settings.HTTPS_ONLY)

# Static Files
static_dir = os.path.join(os.path.dirname(__file__), 'static_justengel')
app.mount("/static_justengel", StaticFiles(directory=str(static_dir)), name="static_justengel")


theme = MaterialTemplates(directory=os.path.join(MY_DIR, 'templates'), theme='justengel_material')
set_theme(theme)
theme.install_app(app, serve_static=True,
                  site_name='Justengel', show_sidenav=True,
                  primary_color='teal', secondary_color='purple lighten-1')