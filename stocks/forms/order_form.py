import uuid

from django.forms import ModelForm, DateTimeField
from tempus_dominus.widgets import DateTimePicker

from stocks.models import Orders


class OrdersForm(ModelForm):
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
        ),
    )

    def __init__(self, *args, **kwargs):
        super(OrdersForm, self).__init__(*args, **kwargs)
        self.fields['price'].required = True
        self.fields['commission'].required = True

    class Meta:
        model = Orders
        fields = ['stock', 'portfolio', 'size', 'price',  'commission', 'date']

    def save(self, commit=True):
        my_order = super(OrdersForm, self).save(commit=False)
        data = self.cleaned_data
        my_order.status = 'completed'
        my_order.order_type = 'market'
        my_order.order_uuid = uuid.uuid4()
        my_order.price_complete = float(data['price']) * float(data['size'])
        my_order.is_sell = False
        if commit:
            my_order.save()
        return my_order

