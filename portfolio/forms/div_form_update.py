from bootstrap_modal_forms.forms import BSModalForm
from bootstrap_modal_forms.mixins import CreateUpdateAjaxMixin

from portfolio.models import Dividend
from tempus_dominus.widgets import DatePicker
from django.forms import DateTimeField


class DivFormUpdate(BSModalForm):

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

    def __init__(self, *args, **kwargs):
        super(DivFormUpdate, self).__init__(*args, **kwargs)
        self.fields['sum'].required = True
        self.fields['date'].required = True

    class Meta:
        model = Dividend
        fields = ['stock', 'sum', 'date']

    def save(self):
        my_div = super(CreateUpdateAjaxMixin, self).save()
        return my_div
