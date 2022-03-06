import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware

from justengel_srv.utils import MY_DIR, set_theme, template, get_messages
from justengel_srv.load_app import app, theme
from justengel_srv.local import settings


__all__ = ['app']


# SideNav Links
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
    from justengel_srv import apps

    # main.init()  # Just in case of a double import
    app.include_router(apps.router, prefix='/apps')
except (ImportError, Exception) as err:
    print('Cannot run apps!', err)


try:
    from justengel_srv import articles

    app.include_router(articles.router, prefix='/articles')
except (ImportError, Exception) as err:
    print('Cannot run articles!', err)


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
