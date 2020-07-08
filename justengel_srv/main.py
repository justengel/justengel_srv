import os
from fastapi import FastAPI, Request
from justengel_material import MaterialTemplates, Link, Message
from justengel_srv import utils


__all__ = ['app', 'theme']


app = FastAPI()
theme = MaterialTemplates(directory=os.path.join(utils.MY_DIR, 'templates'), theme='justengel_material')
utils.set_theme(theme)
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

try:
    from justengel_srv import ocr
    app.include_router(ocr.router, prefix='/ocr')
    theme.add_sidenav_item(theme.DEFAULT_CONTEXT, name='OCR', href='/ocr/')
except (ImportError, Exception):
    print('Cannot run ocr! Missing dependencies!')


@app.get('/')
async def index(request: Request):
    ctx = {'request': request, 'base_url': request.base_url,
           'title': 'Home',
           }
    ctx['MESSAGES'] = [Message(msg_type='Success', msg='Hello World!')]
    return theme.TemplateResponse('index.html', ctx)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)
