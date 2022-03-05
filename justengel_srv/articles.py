import os
from collections import OrderedDict
from fastapi import FastAPI, APIRouter, Request
from fastapi.templating import Jinja2Templates

from justengel_srv.utils import get_theme, template


__all__ = ['router']


router = APIRouter()
ARTICLE_PATH = os.path.join(os.path.dirname(__file__), 'templates/articles')


def get_articles(path=None, path_prefix='articles'):
    global ARTICLE_PATH
    if path is None:
        path = ARTICLE_PATH

    for filename in sorted(os.listdir(path)):
        name, ext = os.path.splitext(filename)
        name = name.replace('_', ' ')
        if ext == '.html' and name != 'index':
            yield name, os.path.join(path_prefix, filename)


def get_articles_url(path=None):
    return OrderedDict([(name, name)
                        for name, path in get_articles(path)])


def get_articles_path(path=None):
    return OrderedDict(get_articles(path))


@router.get('/')
async def articles(request: Request):
    global ARTICLE_PATH
    ctx = {'request': request, 'base_url': request.base_url,
           'title': 'Articles',
           'articles': get_articles_url(),
           }

    return template('articles.html', ctx)


@router.get('/{name}/')
def article_name(request: Request, name: str):
    ctx = {'request': request, 'base_url': request.base_url,
           'title': name,
           }

    articles = get_articles_path()
    path = articles[name]
    return template(path, ctx)


# Create the app
app = FastAPI()
app.include_router(router)
get_theme().install_app(app, serve_static=True,
                        site_name='JustEngel', show_sidenav=True,
                        primary_color='teal', secondary_color='purple')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)
