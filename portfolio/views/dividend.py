from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from portfolio.forms.div_form import DivForm
from portfolio.forms.div_form_update import DivFormUpdate
from portfolio.models import Portfolio, Dividend

from stocks.models import Stock


class DividendDeleteView(BSModalDeleteView):
    model = Dividend
    fields = '__all__'
    template_name = 'delete.html'
    success_message = 'Success: Dividend was deleted.'

    def get_success_url(self):
        portfolio = self.object.portfolio.id
        return reverse_lazy('portfolio:portfolio_viewer', kwargs={'id': portfolio})


class DividendEditView(BSModalUpdateView):
    template_name = 'post.html'
    form_class = DivFormUpdate
    success_message = 'Success: Dividend was updated.'
    dividend = None
    portfolio = None
    model = Dividend

    def dispatch(self, request, *args, **kwargs):
        self.dividend = get_object_or_404(Dividend, id=kwargs['pk'])
        self.portfolio = get_object_or_404(Portfolio, id=self.dividend.portfolio_id, user=request.user)
        return super(DividendEditView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DividendEditView, self).get_context_data(**kwargs)
        context['headline'] = 'Update dividend {}'.format(self.dividend.id)
        context['btn_txt'] = 'Save'
        return context


class DividendCreateView(BSModalCreateView):
    portfolio = None
    stock = None
    template_name = 'post.html'
    form_class = DivForm
    dividend = None

    def dispatch(self, request, *args, **kwargs):
        self.portfolio = get_object_or_404(Portfolio, id=kwargs['portfolio_id'], user=request.user)
        self.stock = get_object_or_404(Stock, id=kwargs['stock_id'])
        return super(DividendCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DividendCreateView, self).get_context_data(**kwargs)
        context['headline'] = 'Add dividends for {} ({})'.format(self.stock.symbol, self.stock.name)
        context['btn_txt'] = 'Add'
        return context

    def get_form_kwargs(self):
        kwargs = super(DividendCreateView, self).get_form_kwargs()
        kwargs['stock_id'] = self.stock.id
        kwargs['portfolio_id'] = self.portfolio.id
        return kwargs

    def get_success_url(self):
        return reverse_lazy('portfolio:portfolio_viewer', kwargs={'id': self.portfolio.id})

