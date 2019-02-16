# python manage.py makemigrations portfolio
# python manage.py migrate
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from stocks.models import Stock


class Portfolio(models.Model):
    name = models.CharField(max_length=40)
    cash = models.FloatField()
    initial_cash = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        db_table = 'user_portfolio'

    def get_delete_url(self):
        return reverse('portfolio:portfolio_delete_view', kwargs={'pk': self.pk})

    def get_absolute_url(self):
        return reverse('portfolio:portfolio_list')

    def get_template_name(self):
        return self.__class__.__name__

    def __str__(self):
        return self.name


class Orders(models.Model):
    date = models.DateTimeField()
    size = models.IntegerField()
    price = models.FloatField()
    commission = models.FloatField()
    stock = models.ForeignKey(Stock, on_delete=models.PROTECT, related_name='stocks_of_order')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.PROTECT)

    class Meta:
        db_table = 'user_orders'

    def get_delete_url(self):
        return reverse('portfolio:order_delete_view', kwargs={'pk': self.pk})

    def get_absolute_url(self):
        return reverse('portfolio:portfolio_viewer', kwargs={'id': self.portfolio.pk})

    def get_template_name(self):
        return self.__class__.__name__


class Dividend(models.Model):
    date = models.DateTimeField()
    sum = models.FloatField()
    stock = models.ForeignKey(Stock, on_delete=models.PROTECT)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.PROTECT)

    class Meta:
        db_table = 'user_dividend'

    def get_template_name(self):
        return self.__class__.__name__

    def get_delete_url(self):
        return reverse('portfolio:dividend_delete_view', kwargs={'pk': self.pk})

    def get_absolute_url(self):
        return reverse('portfolio:portfolio_viewer', kwargs={'id': self.portfolio.id})
