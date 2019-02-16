from bootstrap_modal_forms.forms import BSModalForm

from portfolio.models import Dividend
from tempus_dominus.widgets import DatePicker
from django.forms import DateTimeField, FloatField, NumberInput


class DivForm(BSModalForm):

    date = DateTimeField(
        widget=DatePicker(
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
    sum = FloatField(required=True,  min_value=0, widget=NumberInput(attrs={'type': 'number', 'step': "0.01"}))

    def __init__(self, *args, **kwargs):
        self.stock_id = kwargs.pop('stock_id')
        self.portfolio_id = kwargs.pop('portfolio_id')
        super(DivForm, self).__init__(*args, **kwargs)
        self.fields['sum'].required = True
        self.fields['date'].required = True

    def clean(self):
        self.instance.portfolio_id = self.portfolio_id
        self.instance.stock_id = self.stock_id
        return super(DivForm, self).clean()

    class Meta:
        model = Dividend
        exclude = ['stock', 'portfolio']

