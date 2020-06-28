import os
import datetime
from fastapi import FastAPI, APIRouter, Request
from fastapi.templating import Jinja2Templates

from justengel_srv import utils

__all__ = ['app', 'router']


app = FastAPI()
router = APIRouter()
theme = utils.get_theme()
theme.install_app(app, serve_static=True,
                  site_name='JustEngel', show_sidenav=True,
                  primary_color='teal', secondary_color='purple')


@router.route('/', methods=['GET', 'POST'])
async def time_calculator(request: Request):
    DATETIME_FORMAT = '%b %d, %Y %I:%M %p'
    ctx = {'request': request, 'base_url': request.base_url,
           'title': 'Time Calculator',
           'pay': 10.00, 'today': datetime.date.today().strftime('%b %d, %Y'),
           'num_inputs': 0
           }

    if request.method == 'GET':
        return theme.TemplateResponse('time_calculator.html', ctx)

    # Method is POST
    form = await request.form()
    pay = float(form.get('pay', 10.00))

    input_times = []
    time_totals = []
    for i in range(1000):
        try:
            fsd = form['start_date'+str(i)]
            fst = form['start_time'+str(i)]
            fed = form['end_date'+str(i)]
            fet = form['end_time'+str(i)]
            start = datetime.datetime.strptime(fsd + ' ' + fst, DATETIME_FORMAT)
            end = datetime.datetime.strptime(fed + ' ' + fet, DATETIME_FORMAT)
            tm = (end - start).total_seconds() / 3600
            input_times.append(((fsd, fst),
                                (fed, fet)))
            time_totals.append(tm)
        except:
            break

    hours_worked = sum(time_totals)

    ctx['pay'] = pay
    ctx['paycheck'] = pay * hours_worked
    ctx['hours_worked'] = hours_worked
    ctx['time_totals'] = time_totals
    ctx['input_times'] = input_times
    ctx['num_inputs'] = len(input_times)
    return theme.TemplateResponse('time_calculator.html', ctx)


app.include_router(router)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)
