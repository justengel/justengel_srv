import os
from fastapi import FastAPI, Request

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
# app.add_middleware(HTTPSRedirectMiddleware)
# app.add_middleware(CORSMiddleware, allow_origins=['https://justengel.com', 'https://www.justengel.com'])
# app.add_middleware(TrustedHostMiddleware, allowed_hosts=['justengel.com', '*.justengel.com'])
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET, https_only=False)

theme = MaterialTemplates(directory=os.path.join(MY_DIR, 'templates'), theme='justengel_material')
set_theme(theme)
theme.install_app(app, serve_static=True,
                  site_name='JustEngel', show_sidenav=True,
                  primary_color='teal', secondary_color='purple lighten-1')


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


@app.get('/')
async def index(request: Request):
    ctx = {'request': request, 'base_url': request.base_url,
           'title': 'Home', 'MESSAGES': get_messages(request),
           }
    return template('index.html', ctx)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)
