from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse

from portfolio.forms.order_form import OrderForm
from portfolio.forms.order_form_update import OrderFormUpdate
from portfolio.models import Portfolio, Orders

from stocks.models import Stock


class OrderDeleteView(BSModalDeleteView):
    model = Orders
    fields = '__all__'
    success_message = 'Success: Order was deleted.'
    template_name = 'delete.html'

    def get_success_url(self):
        portfolio = self.object.portfolio.id
        return reverse_lazy('portfolio:portfolio_viewer', kwargs={'id': portfolio})


class OrderUpdateView(BSModalUpdateView):
    template_name = 'post.html'
    form_class = OrderFormUpdate
    success_message = 'Success: Order was updated.'
    order = None
    portfolio = None
    model = Orders

    def dispatch(self, request, *args, **kwargs):
        self.order = get_object_or_404(Orders, id=kwargs['pk'])
        self.portfolio = get_object_or_404(Portfolio, id=self.order.portfolio_id, user=request.user)
        return super(OrderUpdateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(OrderUpdateView, self).get_context_data(**kwargs)
        context['headline'] = 'Update order {}'.format(self.order.id)
        context['btn_txt'] = 'Save'
        return context


class OrderCreateView(BSModalCreateView):
    portfolio = None
    stock = None
    is_sell = True
    template_name = 'post.html'
    form_class = OrderForm

    def dispatch(self, request, *args, **kwargs):
        self.portfolio = get_object_or_404(Portfolio, id=kwargs['portfolio_id'], user=request.user)
        self.is_sell = '/sell/' in request.path
        self.stock = None
        if self.is_sell:
            self.stock = get_object_or_404(Stock, id=kwargs['stock_id'])
        return super(OrderCreateView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(OrderCreateView, self).get_form_kwargs()
        kwargs['sell'] = self.is_sell
        kwargs['stock_id'] = None if self.stock is None else self.stock.id
        kwargs['portfolio_id'] = self.portfolio.id
        kwargs['max_size'] = sum(order.size for order in self.portfolio.orders_set.all() if order.stock == self.stock)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(OrderCreateView, self).get_context_data(**kwargs)
        if self.is_sell:
            context['headline'] = "Create sell order for {} ({})".format(self.stock.symbol, self.stock.name)
        else:
            context['headline'] = "Create buy order"
        context['btn_txt'] = 'Create'
        return context

    def get_success_url(self):
        portfolio = self.object.portfolio.id
        return reverse_lazy('portfolio:portfolio_viewer', kwargs={'id': portfolio})
