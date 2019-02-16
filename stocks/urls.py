from django.conf.urls import url

from stocks.views import strategy, orders
from stocks.views import misc

app_name = 'stocks'

urlpatterns = [
    url(r'^index[/]*$', misc.stock_list_index, name='stock_list_index'),
    url(r'^region[/]*$', misc.stock_list_region, name='stock_list_region'),
    url(r'^signals[/]*$', misc.stock_signal, name='stock_signal'),
    url(r'^signal/view/(?P<signal_id>\d+)[/]*$',
        misc.stock_signal_viewer_id, name='stock_signal_viewer_id'),
    url(r'^portfolio/(?P<id>\w+)[/]*$',
        strategy.strategy_viewer, name='portfolio_viewer'),
    url(r'^signals/performance[/]*$', misc.stock_signal_performance,
        name='stock_signal_performance'),
    url(r'^signals/today[/]*$', misc.stock_signal_today,
        name='stock_signal_today'),
    url(r'^(?P<stock_id>[\d]+)[/]*$', misc.stock_data, name='stock_data'),
    url(r'^filter/stock_is_hot[/]*$', misc.stock_list_filter_stock_is_hot,
        name='stock_list_filter_stock_is_hot'),
    url(r'^filter/piotroski[/]*$', misc.stock_list_filter_piotroski,
        name='stock_list_filter_piotroski'),
    url(r'^filter/levermann[/]*$', misc.stock_list_filter_levermann,
        name='stock_list_filter_levermann'),
    url(r'^filter[/]*$', misc.stock_list_filter,
        name='stock_list_filter'),
    url(r'^strategies[/]*$', strategy.strategy_list, name='strategies'),
    url(r'^strategy/view/(?P<id>\w+)[/]*$', strategy.strategy_viewer, name='strategy_view'),
    url(r'^order/view/(?P<order_id>\d+)[/]*$',
        misc.order_view, name='order_viewer_id'),
    url(r'^order/delete/(?P<pk>\d+)/', orders.OrderDeleteView.as_view(), name='order_delete_view'),
    url(r'^order/add/', orders.OrderCreateView.as_view(), name='order_create_view'),
    url(r'^strategy/delete/(?P<pk>\d+)/', strategy.StrategyDeleteView.as_view(), name='strategy_delete_view'),
]