from bootstrap_modal_forms.forms import BSModalForm
from portfolio.models import Orders
from tempus_dominus.widgets import DateTimePicker
from django.forms import DateTimeField, DecimalField


class OrderForm(BSModalForm):

    date = DateTimeField(
        widget=DateTimePicker(
            options={
                'useCurrent': True,
                'collapse': False,
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        )
    )

    commission = DecimalField(required=False, max_digits=6, min_value=0)
    price = DecimalField(required=False, min_value=0)

    def __init__(self, *args, **kwargs):
        self.is_sell = kwargs.pop('sell')
        self.max_size = kwargs.pop('max_size')
        self.stock_id = kwargs.pop('stock_id')
        if self.stock_id is not None:
            del self.base_fields['stock']
        self.portfolio_id = kwargs.pop('portfolio_id')
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['price'].required = True
        self.fields['commission'].required = True
        self.fields['date'].required = True
        if self.stock_id is not None:
            self.fields['size'] = DecimalField(required=True, max_digits=6, min_value=0,
                                               max_value=self.max_size)
        else:
            self.fields['size'] = DecimalField(required=True, max_digits=6, min_value=0)

    class Meta:
        model = Orders
        fields = ['date', 'size', 'price', 'commission', 'stock']

    def clean(self):
        self.instance.portfolio_id = self.portfolio_id
        if self.stock_id is not None:
            self.instance.stock_id = self.stock_id
        if self.is_sell:
            self.instance.size = int(self.data['size']) * -1
        return super(OrderForm, self).clean()
