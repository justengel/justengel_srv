import io
import easyocr
from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from justengel_srv import utils

__all__ = ['app', 'router']


app = FastAPI()
router = APIRouter()
theme = utils.get_theme()
theme.install_app(app, serve_static=True,
                  site_name='JustEngel', show_sidenav=True,
                  primary_color='teal', secondary_color='purple')


ocr = easyocr.Reader(['en'])


@router.route('/', methods=['GET', 'POST'])
async def get_ocr(request: Request):
    ctx = {'request': request,
           'base_url': request.base_url,
           }

    form = await request.form()
    file = form.get('file', None)
    if file is not None:
        res = ocr.readtext(await file.read())
        probable_text = '\n'.join((item[1] for item in res))
        return StreamingResponse(io.BytesIO(probable_text.encode()), media_type="text/plain")
    return theme.TemplateResponse('ocr.html', ctx)


app.include_router(router)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)
