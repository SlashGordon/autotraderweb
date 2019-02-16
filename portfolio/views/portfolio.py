import json

from bootstrap_modal_forms.generic import BSModalDeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import ExpressionWrapper, FloatField, F, Max, Sum
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy

from portfolio.models import Portfolio, Orders, Dividend
from stocks.models import Stock, Series, Filter


@login_required(login_url='accounts:log_in')
def portfolio_list(request):
    user = get_object_or_404(User, pk=request.user.id)
    portfolios = Portfolio.objects.filter(user=user)
    data = {
        'portfolios': portfolios
    }

    return render(request, 'portfolio_list.html', data)


def __get_divs(portfolio):
    if portfolio:
        categories = set()
        stocks = set()
        dividends = []
        for my_div in portfolio.dividend_set.order_by('date').all():
            category = my_div.date.strftime('%b %Y')
            dividends.append({
                'id': my_div.id,
                'stock_name': my_div.stock.name,
                'stock_symbol': my_div.stock.symbol,
                'stock_id': my_div.stock.id,
                'sum': my_div.sum,
                'date': my_div.date,
                'category': category
            })
            categories.add(my_div.date.strftime('%b %Y'))
            stocks.add(my_div.stock.name)
        div_cols = []
        for stock_name in stocks:
            data = {'name': stock_name, 'data': []}
            for category in categories:
                my_sum = 0.0
                for value in dividends:
                    if value['category'] == category and stock_name == value['stock_name']:
                        my_sum += value['sum']
                data['data'].append(my_sum)
            div_cols.append(data)

        return list(categories), div_cols, dividends
    return None, None, None


@login_required(login_url='accounts:log_in')
def portfolio_viewer(request, id):
    user = get_object_or_404(User, pk=request.user.id)
    portfolio = get_object_or_404(Portfolio, user=request.user.id)
    div_categories, div_cols, divs = __get_divs(portfolio)
    portfolio_items = ___create_portfolio_items(user)
    orders = portfolio.orders_set.select_related().all()
    stock_data, region_data, industry_data, filter_values = __create_diversification(portfolio_items)
    portfolio_value_inti = sum(value['price_complete']*-1 for key, value in portfolio_items.items())
    portfolio_value = sum(value['price_complete']*-1 + value['earnings'] for key, value in portfolio_items.items())
    portfolio_value_pct = (portfolio_value / portfolio_value_inti - 1) * 100
    portfolio_value_div = sum(value['price_complete']*-1 + value['earnings_div'] for key, value in portfolio_items.items())
    portfolio_value_div_pct = (portfolio_value_div / portfolio_value_inti - 1) * 100
    return render(request, 'portfolio.html', {'value_div': portfolio_value_div, 'pct_div': portfolio_value_div_pct,
                                              'value': portfolio_value, 'pct': portfolio_value_pct, 'id': id,
                                              'name': portfolio.name, 'portfolio': portfolio_items,
                                              'stock_data': stock_data, 'region_data': region_data, 'orders': orders,
                                              'industry_data': industry_data, 'filter_values': filter_values,
                                              'div_categories': json.dumps(div_categories),
                                              'div_cols': json.dumps(div_cols),
                                              'dividends': divs})


def ___create_portfolio_items(user):
    ew = ExpressionWrapper(F('price') * F('size') * -1 + F('commission'), output_field=FloatField())
    my_orders = list(
        Orders.objects.filter(portfolio__user=user).values('stock__symbol', 'stock__id', 'stock__name', 'price', 'date',
                                                           'size').annotate(price_complete=ew))
    my_div = list(Dividend.objects.filter(portfolio__user=user).values('stock__id').annotate(sumall=Sum('sum')))
    items = {}
    for order in my_orders:
        if order['stock__id'] not in items:
            items[order['stock__id']] = order
            items[order['stock__id']]['div'] = 0.0
            for div in my_div:
                if div['stock__id'] == order['stock__id']:
                    items[order['stock__id']]['div'] = div['sumall']
                    break
        else:
            items[order['stock__id']]['size'] += order['size']
            items[order['stock__id']]['price_complete'] += order['price_complete']
    stock_ids = [items[orders]['stock__id'] for orders in items]
    prices_ids = Series.objects.values('stock__id').filter(stock__id__in=stock_ids).annotate(
        max_id=Max('id')).values_list('max_id', flat=True)
    filter_lev_ids = Filter.objects.values('stock__id').filter(name='LevermannScore').filter(
        stock__id__in=stock_ids).annotate(max_id=Max('id')).values_list('max_id', flat=True)
    filter_pio_ids = Filter.objects.values('stock__id').filter(name='PiotroskiScore').filter(
        stock__id__in=stock_ids).annotate(max_id=Max('id')).values_list('max_id', flat=True)
    prices = list(Series.objects.values('stock__id', 'priceclose').filter(id__in=prices_ids).all())
    lev = list(Filter.objects.values('stock__id', 'value', 'status').filter(id__in=filter_lev_ids).all())
    pio = list(Filter.objects.values('stock__id', 'value', 'status').filter(id__in=filter_pio_ids).all())
    # calculate performance SUM(size)*price_now + SUM(price_total)
    del_items = []
    for order in items:
        if items[order]['size'] > 0:
            last_price = 0.0
            for price in prices:
                if price['stock__id'] == items[order]['stock__id']:
                    last_price = price['priceclose']
                    break
            for it in lev:
                if it['stock__id'] == items[order]['stock__id']:
                    items[order]['piotroski'] = it['value']
                    items[order]['piotroski_status'] = it['status']
                    break
            for it in pio:
                if it['stock__id'] == items[order]['stock__id']:
                    items[order]['levermann'] = it['value']
                    items[order]['levermann_status'] = it['status']
                    break
            items[order]['earnings'] = items[order]['size'] * last_price + \
                                                   items[order]['price_complete']
            items[order]['earnings_div'] = items[order]['size'] * last_price + \
                                                   items[order]['price_complete'] + items[order]['div']
            items[order]['earnings_prc'] = (1 - items[order]['earnings']) / \
                                                       items[order]['price_complete']
            items[order]['earnings_div_prc'] = (1 - items[order]['earnings_div']) / \
                                                       items[order]['price_complete']
        else:
            del_items.append(order)

    for order in del_items:
        del items[order]

    return items


def __create_diversification(items):
    total_value = 0
    total_value_tags = 0
    stock_data_sum = {}
    region_data_sum = {}
    industry_data_sum = {}
    filter_values = []
    for key, item in items.items():
        filter_levermann = Filter.objects.values('value', 'status') \
            .filter(name__contains='LevermannScore') \
            .filter(stock__id=item['stock__id']).order_by('-date').first()
        filter_piotros = Filter.objects.values('value', 'status') \
            .filter(name__contains='PiotroskiScore') \
            .filter(stock__id=item['stock__id']).order_by('-date').first()
        if filter_levermann and filter_piotros:
            filter_values.append({'symbol': item['stock__id'],
                                  'levermann': filter_levermann['value'],
                                  'piotroski': filter_piotros['value'],
                                  'levermann_status': filter_levermann['status'],
                                  'piotroski_status': filter_piotros['status']})
        else:
            filter_values.append({'symbol': item['stock__id'],
                                  'levermann': 'unknown',
                                  'piotroski': 'unknown',
                                  'levermann_status': 'unknown',
                                  'piotroski_status': 'unknown'})
        stock = Stock.objects.select_related().filter(id=item['stock__id']).first()
        stock_data_sum[stock.symbol] = stock_data_sum.get(stock.symbol, 0.0) + \
                                       item['price_complete']
        if stock and stock.region and stock.region.region:
            region_data_sum[stock.region.region] = region_data_sum.get(stock.region.region, 0.0) + \
                                            item['price_complete']

        for tag in stock.tags.all():
            total_value_tags += item['price_complete']
            industry_data_sum[tag.tag] = industry_data_sum.get(tag.tag, 0.0) + item['price_complete']
        total_value += item['price_complete']

    return [{'name': key, 'y': val*100/total_value} for key, val in stock_data_sum.items()], \
           [{'name': key, 'y': val*100/total_value} for key, val in region_data_sum.items()], \
           [{'name': key, 'y': val*100/total_value_tags} for key, val in industry_data_sum.items()], filter_values


class PortfolioDeleteView(BSModalDeleteView):
    model = Portfolio
    fields = '__all__'
    success_message = 'Success: Order was deleted.'
    template_name = 'delete.html'

    def get_success_url(self):
        return reverse_lazy('portfolio:portfolio_list')
