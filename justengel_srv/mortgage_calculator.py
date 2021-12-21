from typing import Generator
from pydantic import BaseModel
import os
import datetime
from fastapi import FastAPI, APIRouter, Request
from fastapi.templating import Jinja2Templates
from justengel_srv.utils import get_theme, template


__all__ = ['Currency', 'Payment', 'calculate_payment', 'amortization',
           'app', 'router']


class Currency(float):
    def __new__(cls, value):
        if isinstance(value, str):
            value = value.replace(' ', '').replace(',', '').replace('$', '')
        return super().__new__(cls, value)

    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def validate(cls, v):
        return cls(v)

    def as_float(self):
        return f'{self:.2f}'

    def __str__(self):
        return f'${self:,.2f}'  # '${:,.2f}'.format(float(self))

    def __repr__(self):
        return f'${self:,.2f}'

    def __eq__(self, other):
        return round(self, 2) == round(other, 2)


class Payment(BaseModel):
    month: int
    balance: Currency
    payment: Currency
    principal: Currency
    interest: Currency
    extra: Currency = 0
    total_extra: Currency = 0
    total_interest: Currency = 0
    total_paid: Currency = 0


def calculate_payment(balance: Currency, rate: float, months_remaining: int) -> Currency:
    p = balance
    r = rate / 12 / 100
    n = months_remaining
    r1 = (1 + r)**n

    pmnt = p * ((r * r1)/(r1 - 1))
    return Currency(pmnt)


def amortization(balance: Currency, rate: float, years: float = 30, months: int = None, extra: float = 0) -> Generator[Payment, None, None]:
    if months is None:
        months = years * 12

    r = rate / 100 / 12
    total_extra = 0
    total_interest = 0
    total = 0
    month = 0

    monthly = calculate_payment(balance, rate, months)

    while balance > 0:
        interest = balance * r
        principal = monthly - interest
        balance -= (principal + extra)
        payment = monthly + extra

        if round(balance, 2) <= 0:
            balance = round(balance, 2)

            # Remove negative from extra first
            payment += balance  # Balance is negative
            extra += balance
            if extra < 0:
                principal += extra
                extra = 0

            balance = 0.0

        total_extra += extra
        total_interest += interest
        total += payment
        month += 1

        yield Payment(month=month, balance=Currency(balance),
                      payment=Currency(payment),
                      principal=Currency(principal),
                      interest=Currency(interest),
                      extra=Currency(extra),
                      total_extra=Currency(total_extra),
                      total_interest=Currency(total_interest),
                      total_paid=Currency(total))


# ===== Web App =====
router = APIRouter()


@router.get('/')
async def mortgage_calculator(request: Request, balance: Currency = 300_000, rate: float = 3.0, years: float = 30,
                              months: int = None, extra: Currency = 0):
    if months is not None:
        years = round(months / 12, 1)

    ctx = {'request': request, 'base_url': request.base_url,
           'title': 'Mortgage Calculator',
           'balance': balance, 'rate': rate, 'years': years, 'extra': extra}

    payments = list(amortization(balance, rate, years=years, months=months, extra=extra))
    ctx['payments'] = payments

    return template('mortgage_calculator.html', ctx)


@router.get('/raw')
async def raw(request: Request):
    ctx = {'request': request, 'base_url': request.base_url,
           'title': 'Raw Mortgage Calculator',
           }
    return template('raw_mortgage_calculator.html', ctx)


# Create the app
app = FastAPI()
app.include_router(router)
get_theme().install_app(app, serve_static=True,
                        site_name='JustEngel', show_sidenav=True,
                        primary_color='teal', secondary_color='purple')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)

    # print('{:^5} | {:^13} | {:^13} | {:^13} | {:^13} | {:^13}'.format(
    #         'Month', 'Payment', 'Principal', 'Interest', 'Extra', 'Balance'))
    # p = None
    #
    # for p in amortization(250_000, 2.0, years=15, extra=500):
    #     print('{:<5} | {:13.2f} | {:13.2f} | {:13.2f} | {:13.2f} | {:13.2f}'.format(
    #             p.month, p.payment, p.principal, p.interest, p.extra, p.balance
    #             ))
    #
    # print()
    # print('Years:', round(p.month/12, 1))
    # print('Total Extra:', p.total_extra)
    # print('Total Interest:', p.total_interest)
    # print('Total Paid:', p.total_paid)
