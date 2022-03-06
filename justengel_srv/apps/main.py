import os
import dataclasses
from collections import OrderedDict
from fastapi import FastAPI, APIRouter, Request
from fastapi.templating import Jinja2Templates

from justengel_srv.utils import template, get_messages, Route
from justengel_srv.load_app import theme, app
from justengel_srv.local import settings


__all__ = ['init', 'router']


router = APIRouter(tags=["apps"])
ROUTES = []

TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), 'templates')
theme.add_directory(TEMPLATES_PATH)
theme.add_sidenav_group(theme.DEFAULT_CONTEXT, name='Apps')


@router.get('/')
async def apps(request: Request):
    ctx = {'request': request, 'base_url': request.base_url, 'FIXED_SIDENAV': True, 'MESSAGES': get_messages(request),
           'title': 'Articles',
           'routes': ROUTES
           }

    return template('apps.html', ctx)

theme.add_sidenav_item(theme.DEFAULT_CONTEXT, name='App List', href='/apps', group='Apps')


try:
    from justengel_srv.apps import time_calculator

    tcr = Route(name='Time Calculator', href='/apps/time_calculator')
    ROUTES.append(tcr)
    tcr.add_sidenav_item(theme, group='Apps')
    router.include_router(time_calculator.router, prefix='/time_calculator')
except (ImportError, Exception) as err:
    print('Cannot run time_calculator!')


try:
    from justengel_srv.apps import mortgage_calculator

    mcr = Route(name='Mortgage Calculator', href='/apps/mortgage_calculator')
    ROUTES.append(mcr)
    mcr.add_sidenav_item(theme, group='Apps')
    router.include_router(mortgage_calculator.router, prefix='/mortgage_calculator')

    rmcr = Route(name='JS Mortgage Calculator', href='/apps/mortgage_calculator/js/')
    ROUTES.append(rmcr)
    rmcr.add_sidenav_item(theme, group='Apps')
    # router.include_router(mortgage_calculator.router, prefix='/mortgage_calculator/raw')
except (ImportError, Exception) as err:
    print('Cannot run mortgage_calculator!')


if getattr(settings, 'RUN_OCR', False):
    try:
        from justengel_srv.apps import ocr

        oroute = Route(name='OCR', href='/apps/ocr')
        oroute.add_sidenav_item(theme, group='Apps')
        oroute.include_router(router, ocr.router)
        ROUTES.append(oroute)
    except (ImportError, Exception) as err:
        print('Cannot run ocr! Missing dependencies!')


# Create the app
app = FastAPI()
app.include_router(router)
theme.install_app(app, serve_static=True,
                  site_name='JustEngel', show_sidenav=True,
                  primary_color='teal', secondary_color='purple')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)
