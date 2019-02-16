from django.conf.urls import url

from portfolio.views import portfolio_designer, portfolio, orders, dividend


app_name = 'portfolio'

urlpatterns = [
    url(r'^view/(?P<id>\d+)[/]*$', portfolio.portfolio_viewer, name='portfolio_viewer'),
    url(r'^list[/]*$', portfolio.portfolio_list, name='portfolio_list'),
    url(r'^designer[/]*$', portfolio_designer.portfolio_designer, name='portfolio_designer'),
    url(r'^save/', portfolio_designer.save_portfolio, name='save_portfolio'),
    url(r'^order/delete/(?P<pk>\d+)/', orders.OrderDeleteView.as_view(), name='order_delete_view'),
    url(r'^order/add/', orders.OrderCreateView.as_view(), name='order_create_view'),
    url(r'^order/buy/(?P<portfolio_id>\d+)/', orders.OrderCreateView.as_view(), name='buy'),
    url(r'^order/sell/(?P<portfolio_id>\d+)/(?P<stock_id>\d+)/', orders.OrderCreateView.as_view(), name='sell'),
    url(r'^dividend/add/(?P<portfolio_id>\d+)/(?P<stock_id>\d+)/', dividend.DividendCreateView.as_view(), name='dividend'),
    url(r'^dividend/edit/(?P<pk>\d+)/', dividend.DividendEditView.as_view(), name='div_edit'),
    url(r'^dividend/delete/(?P<pk>\d+)/', dividend.DividendDeleteView.as_view(), name='div_delete'),
    url(r'^order/edit/(?P<pk>\d+)/', orders.OrderUpdateView.as_view(), name='edit'),
    url(r'^delete/(?P<pk>\d+)/', portfolio.PortfolioDeleteView.as_view(), name='portfolio_delete_view')
]