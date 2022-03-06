import os
import dataclasses
from collections import OrderedDict
from fastapi import FastAPI, APIRouter, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from justengel_srv.utils import template, get_messages, Route
from justengel_srv.load_app import theme, app


__all__ = ['router']


router = APIRouter(tags=["articles"])

# Static Files
static_dir = os.path.join(os.path.dirname(__file__), 'static_articles')
app.mount("/static_articles", StaticFiles(directory=str(static_dir)), name="static_articles")

TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), 'templates')
ARTICLE_PATH = os.path.join(TEMPLATES_PATH, 'articles')
theme.add_directory(TEMPLATES_PATH)
theme.add_sidenav_group(theme.DEFAULT_CONTEXT, name='Articles')

ARTICLES = []


@router.get('/')
async def list_articles(request: Request):
    global ARTICLE_PATH
    ctx = {'request': request, 'base_url': request.base_url, 'FIXED_SIDENAV': True, 'MESSAGES': get_messages(request),
           'title': 'Articles',
           'articles': ARTICLES,
           }

    return template('articles.html', ctx)

theme.add_sidenav_item(theme.DEFAULT_CONTEXT, name='Article List', href='/articles', group='Articles')


# Find all of the articles
for filename in sorted(os.listdir(ARTICLE_PATH)):
    name, ext = os.path.splitext(filename)
    name = name.replace('_', ' ')
    if ext == '.html' and name != 'index':
        art_route = Route(name=name, href='/articles/'+name, path=os.path.join('articles', filename))
        ARTICLES.append(art_route)
        art_route.add_sidenav_item(theme, group='Articles')
        # theme.add_sidenav_item(theme.DEFAULT_CONTEXT, art.name, art.href, group='Articles')


@router.get('/{name}/')
def article_name(request: Request, name: str):
    ctx = {'request': request, 'base_url': request.base_url, 'FIXED_SIDENAV': True, 'MESSAGES': get_messages(request),
           'title': name,
           }

    for article in ARTICLES:
        if article.name == name:
            return template(article.path, ctx)

    raise HTTPException(status_code=404, detail='Article "{}" not found'.format(name))


# Create the app to run just this file
app = FastAPI()
app.include_router(router)
theme.install_app(app, serve_static=True,
                  site_name='JustEngel', show_sidenav=True,
                  primary_color='teal', secondary_color='purple')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)
