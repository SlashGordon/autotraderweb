import base64
import json
import zlib

from json2html import *
from datetime import date, datetime, timedelta

from django.db.models import Avg, Count,Max
from django.shortcuts import render
from stocks.models import Filter, Jsondata, Orders, Parameter, \
    Plot, Series, Signal, Stock, Index, Region
from stocks.tools.json import json_serial


def create_filter_date_range():
    date_last = Filter.objects.latest('date').date
    date_range = (
        # The start_date with the minimum possible time
        datetime.combine(date_last, datetime.min.time()),
        # The start_date with the maximum possible time
        datetime.combine(date_last, datetime.max.time())
    )
    return date_range


def order_view(request, order_id):
    data = {
        "order": Orders.objects.filter(id=order_id).first()
    }
    return render(request, 'order.html', data)


def stock_signal(request):
    signals = list(Signal.objects.values('stock__symbol', 'stock__id', 'id',
                                         'name', 'profit_in_percent', 'status'))
    signal_pivot = {}
    for signal in signals:
        signal_pivot.setdefault(signal['stock__id'], {}).update(
            {'%s' % signal['name']: [signal['stock__id'], signal['profit_in_percent'],
                                     signal['status'], signal['stock__symbol'], signal['id']]})
    data = {
        'signals': signal_pivot,
        'titles': list(Signal.objects.values_list('name', flat=True).distinct()),
        'APPTITLE': 'Signal Performance'
    }
    return render(request, 'stock_signal.html', data)


def __create_overall_performance(signals):
    overall_performance = []
    for signal in signals:
        overall_performance.append([signal['name'], signal['total']])
    return json.dumps(overall_performance)


def __create_performance_over_indices(signals_index):
    json_container = []
    categories = []
    index_before = ""
    for signal in signals_index:
        if index_before == "" or index_before != signal['stock__index__symbol']:
            index_before = signal['stock__index__symbol']
            json_container.append({"name": index_before, "data": []})
        if index_before == signal['stock__index__symbol']:
            json_container[len(json_container) - 1]['name'] = signal['stock__index__symbol']
            json_container[len(json_container) - 1]['data'].append(signal['total'])
        if signal['name'] not in categories:
            categories.append(signal['name'])
    return json.dumps(categories), json.dumps(json_container)


def stock_signal_performance(request):
    signals_index = list(Signal.objects.values('name', 'stock__index__symbol').annotate(
        total=Avg('profit_in_percent')).order_by('stock__index__symbol', 'name'))
    signals = list(Signal.objects.values('name').annotate(total=Avg('profit_in_percent')).
                   order_by('name'))
    categories, json_container = __create_performance_over_indices(signals_index)
    data = {
        'categories': categories,
        'signals_index': json_container,
        'signals': __create_overall_performance(signals),
        'APPTITLE': 'Signal Performance'
    }
    return render(request, 'stock_signal_performance.html', data)


def stock_list_index(request):
    indices = Index.objects.select_related().all()
    data = {
        'indices': indices,
        'APPTITLE': 'Stock List'
    }
    return render(request, 'stock_list_index.html', data)


def stock_list_region(request):
    regions = Region.objects.select_related().all()
    stocks = Stock.objects.select_related().all()
    data = {
        'regions': regions,
        'stocks': stocks,
        'APPTITLE': 'Stock List over region'
    }
    return render(request, 'stock_list_region.html', data)


def stock_list_filter(request):
    latest_dates = Filter.objects.values('name', 'stock__symbol').annotate(latest_created_at=Max("date"))
    filters = Filter.objects.values('name', 'stock__symbol', 'stock__id', 'status', 'value')\
        .filter(date__in=latest_dates.values('latest_created_at')).order_by('stock__symbol', 'name')
    filter_names = list(Filter.objects.values('name').annotate(Count('name')).order_by('name'))
    data = {
        'header': [value['name'] for value in filter_names],
        'filters': list(filters.all()),
        'APPTITLE': 'Filter'
    }
    return render(request, 'filter.html', data)


def stock_list_filter_stock_is_hot(request):
    latest_dates = Filter.objects.values('name', 'stock__symbol').filter(name__contains='StockIsHot').annotate(latest_created_at=Max("date"))
    filters = Filter.objects.values('name', 'stock__symbol', 'stock__id','status', 'value') \
        .filter(date__in=latest_dates.values('latest_created_at')) \
        .filter(name__contains='StockIsHot') \
        .order_by('stock__symbol', 'name')
    data = {
        'header': ['StockIsHot2', 'StockIsHot3', 'StockIsHot6'],
        'filters': filters
    }
    return render(request, 'filter.html', data)


def stock_list_filter_piotroski(request):
    latest_dates = Filter.objects.values('name', 'stock__symbol').filter(name__contains='PiotroskiScore').annotate(latest_created_at=Max("date"))
    filters = Filter.objects.values('name', 'stock__symbol', 'stock__id','status', 'value') \
        .filter(date__in=latest_dates.values('latest_created_at')) \
        .filter(name__contains='PiotroskiScore') \
        .order_by('stock__symbol', 'name')
    data = {
        'header': ['Piotroski'],
        'filters': filters
    }

    return render(request, 'filter.html', data)


def stock_list_filter_levermann(request):
    latest_dates = Filter.objects.values('name', 'stock__symbol').filter(name__contains='LevermannScore').annotate(latest_created_at=Max("date"))
    filters = Filter.objects.values('name', 'stock__symbol', 'stock__id', 'status', 'value') \
        .filter(date__in=latest_dates.values('latest_created_at')) \
        .filter(name__contains='LevermannScore') \
        .order_by('stock__symbol', 'name')
    data = {
        'header': ['Levermann'],
        'filters': filters
    }

    return render(request, 'filter.html', data)


def prettify_json_data(json_data):
    item_list = []
    for data in json_data:
        item_list.append(
            {
                "name": data.name,
                "data": json2html.convert(json=json.loads(data.data), table_attributes="class=\"table\"")
            }
        )
    return item_list


def stock_data(request, stock_id):
    stock = Stock.objects.select_related().filter(id=stock_id)[0]
    plot_data = list(Series.objects.values_list('date', 'priceclose').filter(resolution='P1D').filter(stock__id=stock_id).order_by('date'))
    filter_data = Filter.objects.filter(stock__id=stock_id).order_by('date')
    json_data = Jsondata.objects.filter(stock__id=stock_id)
    signal_data = Signal.objects.select_related().filter(stock__id=stock_id).order_by('date')
    signal_plot_data = {}
    status = {
        -2: "strong sell",
        -1: "sell",
        0: "hold",
        1: "buy",
        2: "strong buy",
    }
    for my_signal in signal_data:
        if my_signal.name not in signal_plot_data:
            signal_plot_data[my_signal.name] = {
                'name': my_signal.name,
                'data': []
            }
        signal_plot_data[my_signal.name]['data'].append({
            "x": my_signal.date.date(),
            "y": my_signal.profit_in_percent,
            "status": status[my_signal.status],
            "parameter": ", ".join(str(param.value) for param in my_signal.parameter_set.all())
        })
    filter_plot_data = {}
    for my_filter in filter_data:
        if my_filter.name not in filter_plot_data:
            filter_plot_data[my_filter.name] = {
                'name': my_filter.name,
                'data': []
            }
        filter_plot_data[my_filter.name]['data'].append({
            "x": my_filter.date.date(),
            "y": my_filter.value,
            "status": "buy" if my_filter.status == 1 else "sell"
            })
    series_lines = []
    series_signal = []
    for plot_key in filter_plot_data:
        series_lines.append({
            'name': filter_plot_data[plot_key]['name'],
            'data': filter_plot_data[plot_key]['data']
        })
    for plot_key in signal_plot_data:
        series_signal.append({
            'name': signal_plot_data[plot_key]['name'],
            'data': signal_plot_data[plot_key]['data']
        })
    data = {
        'stock': stock,
        'data':  json.dumps(plot_data, default=json_serial),
        'filters_da': json.dumps(series_lines, default=json_serial),
        'signals_da': json.dumps(series_signal, default=json_serial),
        'jsondata': prettify_json_data(list(json_data))
    }
    return render(request, 'stock_data.html', data)


def stock_signal_viewer(request, stock_id, signal):
    stock = Stock.objects.filter(id=stock_id)[0]
    signal_data = Signal.objects.filter(stock__id=stock_id, name=signal).order_by('-date').first()
    plot_data = Plot.objects.values_list('data').filter(signal__id=signal_data.id).first()
    # converts binary blob to json
    plot_data = get_json_plot(plot_data)

    parameters = Parameter.objects.values_list('value').filter(signal__id=signal_data.id).all()
    data = {
        'stock': stock,
        'title': signal_data.name + "({0})".format(", ".join(str(x[0]) for x in parameters)),
        'subtitle': "Calculated on:" + signal_data.date.isoformat(),
        'data': plot_data
    }

    return render(request, 'stock_signal_viewer.html', data)


def get_json_plot(plot_data):
    import binascii
    try:
        json_plot = zlib.decompress(base64.b64decode(plot_data[0])).decode('utf-8')
        return json_plot
    except binascii.Error:
        return [{}, {}, {}, {}]


def stock_signal_viewer_id(request, signal_id):
    signal_data = Signal.objects.filter(id=signal_id).first()
    stock = Stock.objects.filter(id=signal_data.stock_id).first()
    plot_data = Plot.objects.values_list('data').filter(signal__id=signal_id).first()
    plot_data = get_json_plot(plot_data)
    parameters = Parameter.objects.values_list('value').filter(signal__id=signal_id).all()
    data = {
        'stock': stock,
        'title': signal_data.name + "({0})".format(", ".join(str(x[0]) for x in parameters)),
        'subtitle': "Calculated on:" + signal_data.date.isoformat() + " - Refreshed on:" + signal_data.refresh_date.isoformat(),
        'data': plot_data
    }

    return render(request, 'stock_signal_viewer.html', data)


def stock_signal_today(request):
    signalsbuy = []
    signalssell = []
    first_date = None
    try:
        first_date = Signal.objects.latest('date')
    except:
        pass
    if first_date:
        max_year = first_date.date
        start_date = date(max_year.year, max_year.month, max_year.day)
        end_date = start_date + timedelta(days=1)
        signalsbuy = list(Signal.objects.values('stock__symbol', 'stock__id', 'status').
                          filter(date__range=[start_date, end_date]).
                          filter(status=2).
                          annotate(count=Count('status'),  average_rating=Avg('profit_in_percent')).
                          order_by('-average_rating', '-count'))

        signalssell = list(Signal.objects.values('stock__symbol', 'stock__id', 'status').
                           filter(date__range=[start_date, end_date]).
                           filter(status=-2).
                           annotate(count=Count('status'), average_rating=Avg('profit_in_percent')).
                           order_by('-average_rating', '-count'))
    data = {
        'signals': [["buy", signalsbuy], ["sell", signalssell]]
    }
    return render(request, 'stock_signal_today.html', data)
