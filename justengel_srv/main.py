import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware

from justengel_material import MaterialTemplates, Link, Message
from justengel_srv.utils import MY_DIR, get_theme, set_theme, template, get_messages, add_message

from justengel_srv.local import settings


__all__ = ['app', 'theme']


app = FastAPI()

# Middleware
# app.add_middleware(HTTPSRedirectMiddleware)  # Nginx will do in most cases
app.add_middleware(CORSMiddleware, allow_origins=['https://justengel.com', 'https://www.justengel.com'])
app.add_middleware(TrustedHostMiddleware, allowed_hosts=['justengel.com', 'www.justengel.com', '127.0.0.1'])
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET, https_only=settings.HTTPS_ONLY)

# Static Files
static_dir = os.path.join(os.path.dirname(__file__), 'justengel_static')
app.mount("/justengel_static", StaticFiles(directory=str(static_dir)), name="justengel_static")


theme = MaterialTemplates(directory=os.path.join(MY_DIR, 'templates'), theme='justengel_material')
set_theme(theme)
theme.install_app(app, serve_static=True,
                  site_name='Justengel', show_sidenav=True,
                  primary_color='teal', secondary_color='purple lighten-1')

# Resume link first!
theme.add_sidenav_item(theme.DEFAULT_CONTEXT, name='Home', href='/')
theme.add_sidenav_item(theme.DEFAULT_CONTEXT, name='Resume', href='/resume/')

@app.get('/')
async def index(request: Request):
    ctx = {'request': request, 'base_url': request.base_url,
           'title': 'Home', 'FIXED_SIDENAV': True, 'MESSAGES': get_messages(request),
           }
    return template('index.html', ctx)


@app.get('/resume')
async def resume(request: Request):
    ctx = {'request': request, 'base_url': request.base_url,
           'title': 'Resume', 'FIXED_SIDENAV': True,
           }
    return theme.TemplateResponse('resume.html', ctx)


try:
    from justengel_srv import articles
    app.include_router(articles.router, prefix='/articles')
    theme.add_sidenav_item(theme.DEFAULT_CONTEXT, name='Articles', href='/articles/')
except (ImportError, Exception):
    print('Cannot run articles!')


try:
    from justengel_srv import time_calculator
    app.include_router(time_calculator.router, prefix='/time_calculator')
    theme.add_sidenav_item(theme.DEFAULT_CONTEXT, name='Time Calculator', href='/time_calculator/')
except (ImportError, Exception):
    print('Cannot run time_calculator!')


try:
    from justengel_srv import mortgage_calculator
    app.include_router(mortgage_calculator.router, prefix='/mortgage_calculator')
    theme.add_sidenav_item(theme.DEFAULT_CONTEXT, name='Mortgage Calculator', href='/mortgage_calculator/')
    theme.add_sidenav_item(theme.DEFAULT_CONTEXT, name='Raw Mortgage Calculator', href='/mortgage_calculator/raw/')
except (ImportError, Exception):
    print('Cannot run mortgage_calculator!')


if getattr(settings, 'RUN_OCR', False):
    try:
        from justengel_srv import ocr
        app.include_router(ocr.router, prefix='/ocr')
        theme.add_sidenav_item(theme.DEFAULT_CONTEXT, name='OCR', href='/ocr/')
    except (ImportError, Exception):
        print('Cannot run ocr! Missing dependencies!')


if getattr(settings, 'RUN_CRUD', False):
    try:
        from justengel_srv.crud import init, auth
        app.include_router(auth.router, prefix='')
        # theme.add_sidenav_item(theme.DEFAULT_CONTEXT, name='OCR', href='/ocr/')
        init(app)
    except (ImportError, Exception) as err:
        print('Cannot run database! Missing dependencies!')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)
