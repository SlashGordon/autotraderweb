from bootstrap_modal_forms.forms import BSModalForm
from bootstrap_modal_forms.mixins import CreateUpdateAjaxMixin

from portfolio.models import Orders
from tempus_dominus.widgets import DateTimePicker
from django.forms import DateTimeField, DecimalField


class OrderFormUpdate(BSModalForm):

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
        super(OrderFormUpdate, self).__init__(*args, **kwargs)
        self.fields['price'].required = True
        self.fields['commission'].required = True
        self.fields['size'].required = True
        self.fields['date'].required = True

    class Meta:
        model = Orders
        fields = ['stock', 'date', 'size', 'price', 'commission']

    def save(self):
        my_order = super(CreateUpdateAjaxMixin, self).save()
        return my_order
