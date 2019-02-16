from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView, CreateView

from stocks.forms.order_form import OrdersForm
from stocks.models import Orders


class OrderDeleteView(DeleteView):
    model = Orders
    fields = '__all__'
    template_name = 'delete.html'

    def get_success_url(self):
        portfolio = self.object.portfolio.id
        return reverse_lazy('stocks:strategy_view', kwargs={'id': portfolio})


class OrderCreateView(CreateView):
    object = None
    template_name = 'order_create.html'
    form_class = OrdersForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
