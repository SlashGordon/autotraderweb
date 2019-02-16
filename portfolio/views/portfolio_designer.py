import json
from datetime import timedelta

from dateutil import parser
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Max
from django.views.decorators.http import require_POST

from portfolio.models import Portfolio, Orders
from stocks.models import Stock, Index, Region, Tag, Filter


@login_required(login_url='accounts:log_in')
def portfolio_designer(request):
    indices = Index.objects.select_related().all()
    regions = Region.objects.select_related().all()
    stocks = Stock.objects.select_related().all()
    latest_dates = Filter.objects.values('name', 'stock__symbol').filter(
        name__contains='LevermannScore').annotate(latest_created_at=Max("date"))
    filters = Filter.objects.select_related() \
        .filter(date__in=latest_dates.values('latest_created_at')) \
        .filter(name__contains='LevermannScore') \
        .order_by('-value')
    filter_data = {}
    for my_filter in filters:
        if my_filter.value in filter_data:
            filter_data[my_filter.value].append(my_filter.stock)
        else:
            filter_data[my_filter.value] = [my_filter.stock]
    tags = Tag.objects.select_related().filter(category='Industry').all()
    data = {
        'indices': indices,
        'regions': regions,
        'stocks': stocks,
        'tags': tags,
        'levermann': filter_data,
        'APPTITLE': 'Portfolio Designer'
    }
    return render(request, 'portfolio_designer.html', data)


@require_POST
@login_required(login_url='accounts:log_in')
def save_portfolio(request):
    user = get_object_or_404(User, pk=request.user.id)
    msg = ''
    if request.method == 'POST':
        name = request.POST.get('name')
        portfolio = request.POST.get('portfolio')
        if portfolio:
            portfolio = json.loads(portfolio)
        status, msg = __valid_portfolio(name, portfolio, user)
        if status:
            return __create_portfolio(name, portfolio, user)
    return HttpResponse(json.dumps({'message': "Couldn't create portfolio. {}".format(msg), 'status': 1}), status=200,
                        content_type='application/json')


def __create_portfolio(name, portfolio, user):
    portfolio_item = Portfolio(name=name, user=user, cash=0, initial_cash=0)
    order_items = []
    initial_cash = 0
    for items in portfolio:
        stock = Stock.objects.filter(id=items['id']).first()
        if not stock:
            return HttpResponse(json.dumps(
                {'message': "Stock {} doesnt exist.".format(items['id']), 'status': 1}),
                status=200,
                content_type='application/json')
        initial_cash += float(items['price']) * float(items['amount']) + float(items['commission'])
        myOrder = Orders(
            date=parser.parse(items['date'], ignoretz=True) + timedelta(days=1),
            size=int(items['amount']),
            price=float(items['price']),
            commission=float(items['commission']),
            stock_id=stock.id
        )
        order_items.append(myOrder)
    portfolio_item.initial_cash = initial_cash
    portfolio_item.save()
    for orderItem in order_items:
        orderItem.portfolio = portfolio_item
        orderItem.save()
    return HttpResponse(json.dumps({'message': "Created Portfolio {}".format(name), 'status': 0}),
                        content_type='application/json')


def __valid_portfolio(name, portfolio, user):
    if name:
        my_portfolio = Portfolio.objects.filter(name=name, user=user).first()
        if my_portfolio:
            return False, 'Portfolio already exists.'
    else:
        return False, 'Invalid portfolio name.'

    for item in portfolio:

        if not ('id' in item and 'price' in item and 'date' in item and 'amount' in item and 'commission' in item
                and item['amount'].isdigit() and is_number(item['price'])) \
                and item['id'].isdigit() and is_number(item['commission']):
            return False, 'Entry {} is wrong'.format(item)
    return True, ''


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False