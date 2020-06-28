import os
from fastapi import FastAPI, Request
from justengel_material import MaterialTemplates
from justengel_srv import utils, time_calculator, mortgage_calculator


__all__ = ['app', 'theme']


app = FastAPI()
theme = MaterialTemplates(directory=os.path.join(utils.MY_DIR, 'templates'), theme='justengel_material')
utils.set_theme(theme)
theme.install_app(app, serve_static=True,
                  site_name='JustEngel', show_sidenav=True,
                  primary_color='teal', secondary_color='purple lighten-1')

app.include_router(mortgage_calculator.router, prefix='/mortgage_calculator')
app.include_router(time_calculator.router, prefix='/time_calculator')


@app.get('/')
async def index(request: Request):
    ctx = {'request': request, 'base_url': request.base_url,
           'title': 'Home',
           }
    return theme.TemplateResponse('index.html', ctx)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)
