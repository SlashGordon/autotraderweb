import json

from django.db.models import Max, Sum, FloatField, F, Case, When, ExpressionWrapper
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DeleteView

from stocks.models import Orders, Series, Stock, Filter, Strategy
from stocks.tools.json import json_serial


def strategy_list(request):
    annotations = {}
    open_positions = Case(
        When(status='completed', is_sell=0, orders_id__isnull=True, then=F('price_complete')),
        default=0,
        output_field=FloatField()
    )
    annotations['earnings'] = ((F('portfolio__cash') - Sum(open_positions)) / F('portfolio__initial_cash') - 1) * 100
    my_portfolio_back_test = Orders.objects.filter(child__isnull=False).values('portfolio__id', 'portfolio__name', 'portfolio__user', 'portfolio__cash', 'portfolio__initial_cash').filter(portfolio__name__istartswith='B').\
        annotate(**annotations).order_by('-earnings')
    my_portfolio_demo = Orders.objects.values('portfolio__id', 'portfolio__name', 'portfolio__user', 'portfolio__cash', 'portfolio__initial_cash').filter(portfolio__name__istartswith='D').\
        annotate(**annotations).order_by('-earnings')
    my_portfolio_live = Orders.objects.values('portfolio__id', 'portfolio__name', 'portfolio__user', 'portfolio__cash', 'portfolio__initial_cash').filter(portfolio__name__istartswith='L').\
        annotate(**annotations).order_by('-earnings')
    my_portfolio_static = Orders.objects.values('portfolio__id', 'portfolio__name', 'portfolio__user', 'portfolio__cash', 'portfolio__initial_cash').filter(portfolio__user='Demo').\
        annotate(**annotations).order_by('-earnings')
    my_portfolio_demo = list(my_portfolio_demo.all())
    my_portfolio_live = list(my_portfolio_live.all())
    my_portfolio_static = list(my_portfolio_static.all())
    my_portfolios = list(Strategy.objects.all())
    for item in my_portfolio_demo:
        if item['earnings'] is None:
            item['earnings'] = 0
        for port in my_portfolios:
            if port.id == item['portfolio__id']:
                item['delete_url'] = port.get_delete_url()
                break
    for item in my_portfolio_live:
        if item['earnings'] is None:
            item['earnings'] = 0
        for port in my_portfolios:
            if port.id == item['portfolio__id']:
                item['delete_url'] = port.get_delete_url()
                break
    for item in my_portfolio_static:
        if item['earnings'] is None:
            item['earnings'] = 0
        for port in my_portfolios:
            if port.id == item['portfolio__id']:
                item['delete_url'] = port.get_delete_url()
                break

    data = {
        'portfolios_data': [("Live", my_portfolio_live),
                            ("Demo", my_portfolio_demo),
                            ("Backtest", list(my_portfolio_back_test.all())),
                            ("Static", my_portfolio_static)]
    }

    return render(request, 'strategy_list.html', data)


def __create_diversification(items):
    total_value = 0
    total_value_tags = 0
    stock_data_sum = {}
    region_data_sum = {}
    industry_data_sum = {}
    filter_values = []
    for item in items:
        filter_levermann = Filter.objects.values('value', 'status') \
            .filter(name__contains='LevermannScore') \
            .filter(stock__symbol=item['stock__symbol']).order_by('-date').first()
        filter_piotros = Filter.objects.values('value', 'status') \
            .filter(name__contains='PiotroskiScore') \
            .filter(stock__symbol=item['stock__symbol']).order_by('-date').first()
        if filter_levermann and filter_piotros:
            filter_values.append({'symbol': item['stock__symbol'],
                                  'levermann': filter_levermann['value'],
                                  'piotroski': filter_piotros['value'],
                                  'levermann_status': filter_levermann['status'],
                                  'piotroski_status': filter_piotros['status']})
        else:
            filter_values.append({'symbol': item['stock__symbol'],
                                  'levermann': 'unknown',
                                  'piotroski': 'unknown',
                                  'levermann_status': 'unknown',
                                  'piotroski_status': 'unknown'})
        stock = Stock.objects.select_related().filter(symbol=item['stock__symbol']).first()
        stock_data_sum[stock.symbol] = stock_data_sum.get(stock.symbol, 0.0) + \
                                       item['price_complete']
        region_data_sum[stock.region.region] = region_data_sum.get(stock.region, 0.0) + \
                                        item['price_complete']
        for tag in stock.tags.all():
            total_value_tags += item['price_complete']
            industry_data_sum[tag.tag] = industry_data_sum.get(tag.tag, 0.0) + item['price_complete']
        total_value += item['price_complete']

    return [{'name': key, 'y': val*100/total_value} for key, val in stock_data_sum.items()], \
           [{'name': key, 'y': val*100/total_value} for key, val in region_data_sum.items()], \
           [{'name': key, 'y': val*100/total_value_tags} for key, val in industry_data_sum.items()], filter_values


def strategy_viewer(request, id):
    name = Strategy.objects.filter(id=id).first().name
    # completed deals
    sell_performance = Orders.objects.filter(child__isnull=False, status="completed"). \
        values('stock__name', 'stock__symbol',  'stock__id', 'portfolio__initial_cash', 'date', 'id'). \
        annotate(earnings=(Sum('price_complete') + Sum('child__price_complete'))). \
        filter(portfolio__id=id).order_by('-earnings')
    signal_stats = Orders.objects.filter(child__isnull=False, status="completed"). \
        values('signal__name'). \
        annotate(earnings=(Sum('price_complete') + Sum('child__price_complete'))). \
        filter(portfolio__id=id).order_by('-earnings')
    # open deals
    order_ids = Orders.objects.filter(child__isnull=False).filter(portfolio__id=id).values_list('id', flat=True)
    open_stocks = Orders.objects.values_list('stock__id', flat=True).\
        filter(portfolio__id=id, orders_id__isnull=True).\
        exclude(id__in=order_ids)
    price_ids = Series.objects.values('stock__id').filter(stock__id__in=open_stocks).\
        annotate(max_id=Max('id')).values_list('max_id', flat=True)
    ew = ExpressionWrapper(F('stock__series__priceopen') * F('size') - Sum('price_complete'), output_field=FloatField())
    open_performance = Orders.objects. \
        filter(portfolio__id=id, orders_id__isnull=True). \
        filter(stock__series__id__in=price_ids, status="completed"). \
        exclude(id__in=order_ids). \
        values('stock__symbol', 'stock__id', 'stock__name', 'price_complete', 'date', 'size', 'stock__series__priceopen'). \
        annotate(earnings=ew)
    # create graph data
    graph_raw = sorted(sell_performance, key=lambda k: k['date'])
    graph = []
    if sell_performance:
        initial_cash = sell_performance[0]['portfolio__initial_cash']
        for graph_item in graph_raw:
            initial_cash += graph_item['earnings']
            graph.append([graph_item['date'], initial_cash])
        graph = json.dumps(graph, default=json_serial)

    signal_performance_graph = []
    for signal in signal_stats.all():
        signal_performance_graph.append([signal['signal__name'], signal['earnings']])
    if signal_performance_graph:
        signal_performance_graph = json.dumps(signal_performance_graph)
    open_perf = list(open_performance.all())
    stock_data, region_data, industry_data, filter_values = __create_diversification(open_perf)
    for idx, value in enumerate(filter_values):
        open_perf[idx]['levermann'] = value['levermann']
        open_perf[idx]['piotroski'] = value['piotroski']
        open_perf[idx]['levermann_status'] = value['levermann_status']
        open_perf[idx]['piotroski_status'] = value['piotroski_status']
    data = {
        'portfolioname': name,
        'portfolio_graph': graph,
        'signal_stats': signal_performance_graph,
        'performance': [
            {
                "name": "Open",
                "data": open_perf
            },
            {
                "name": "Sell",
                "data": list(sell_performance.all())
            }
        ],
        'open_performance': open_perf,
        'titles': [
            {
                "name": "Buy",
                "data": list(Orders.objects.filter(portfolio__name=name, is_sell=0).all())
            },
            {
                "name": "Sell",
                "data": list(Orders.objects.filter(portfolio__name=name, is_sell=1).all())
            }
        ],
        'stocks_data': json.dumps(stock_data),
        'regions_data': json.dumps(region_data),
        'industry_data': json.dumps(industry_data)
    }
    return render(request, 'strategy.html', data)


class StrategyDeleteView(DeleteView):
    model = Strategy
    fields = '__all__'
    template_name = 'delete.html'

    def get_success_url(self):
        return reverse_lazy('portfolio_strategies')
