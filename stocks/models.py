# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
# find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
# find . -path "*/migrations/*.pyc"  -delete

# python manage.py inspectdb --database=autotrader > stocks/models.py
# python manage.py makemigrations
# python manage.py migrate
from __future__ import unicode_literals

from django.db import models
from django.urls import reverse


class Exchange(models.Model):
    name = models.CharField(unique=True, max_length=100)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    symbol_short = models.CharField(max_length=5)

    class Meta:
        managed = False
        db_table = 'exchange'


class Filter(models.Model):
    value = models.FloatField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=40)
    status = models.IntegerField()
    stock = models.ForeignKey('Stock', related_name='filter',  blank=True, null=True, on_delete=models.PROTECT)

    class Meta:
        managed = False
        db_table = 'filter'


class Index(models.Model):
    feed_quality = models.CharField(max_length=250)
    symbol = models.CharField(unique=True, max_length=250, blank=True, null=True)
    stocks = models.ManyToManyField('Stock', through='IndexToStock')

    class Meta:
        managed = False
        db_table = 'index'


class IndexToStock(models.Model):
    index = models.ForeignKey(Index, blank=True, null=True, on_delete=models.PROTECT)
    stock = models.ForeignKey('Stock', blank=True, null=True, on_delete=models.PROTECT)

    class Meta:
        managed = False
        db_table = 'index_to_stock'


class Jsondata(models.Model):
    date = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=40)
    data = models.TextField(blank=True, null=True)
    stock = models.ForeignKey('Stock', blank=True, null=True, on_delete=models.PROTECT)

    class Meta:
        managed = False
        db_table = 'jsondata'


class LookupTable(models.Model):
    lookup_id = models.CharField(max_length=100)
    type = models.CharField(max_length=50, blank=True, null=True)
    stock = models.ForeignKey('Stock', blank=True, null=True, on_delete=models.PROTECT)

    class Meta:
        managed = False
        db_table = 'lookup_table'


class Orders(models.Model):
    date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=9)
    order_type = models.CharField(max_length=12)
    order_uuid = models.CharField(max_length=36)
    size = models.IntegerField()
    expire_date = models.DateTimeField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    commission = models.FloatField(blank=True, null=True)
    price_complete = models.FloatField(blank=True, null=True)
    is_sell = models.IntegerField(blank=True, null=True)
    stock = models.ForeignKey('Stock', blank=True, null=True, on_delete=models.PROTECT)
    portfolio = models.ForeignKey('Strategy', blank=True, null=True, on_delete=models.PROTECT)
    signal = models.ForeignKey('Signal', blank=True, null=True, on_delete=models.PROTECT)
    orders = models.ForeignKey('self', null=True, related_name='children', related_query_name='child', on_delete=models.PROTECT)

    class Meta:
        managed = False
        db_table = 'orders'

    def get_delete_url(self):
        return reverse('stocks:order_delete_view', kwargs={'pk': self.pk})

    def get_absolute_url(self):
        return reverse('stocks:strategy_view', kwargs={'id': self.portfolio.pk})

    def get_template_name(self):
        return self.__class__.__name__


class Parameter(models.Model):
    value = models.FloatField(blank=True, null=True)
    signal = models.ForeignKey('Signal', blank=True, null=True, on_delete=models.PROTECT)

    class Meta:
        managed = False
        db_table = 'parameter'


class Plot(models.Model):
    signal = models.ForeignKey('Signal', blank=True, null=True, on_delete=models.PROTECT)
    data = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plot'


class Strategy(models.Model):
    name = models.CharField(max_length=40)
    user = models.CharField(max_length=40)
    cash = models.FloatField(blank=True, null=True)
    initial_cash = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'portfolio'

    def get_delete_url(self):
        return reverse('stocks:strategy_delete_view', kwargs={'pk': self.pk})

    def get_absolute_url(self):
        return reverse('stocks:strategies')

    def get_template_name(self):
        return self.__class__.__name__

    def __str__(self):
        return self.name


class Region(models.Model):
    region = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'region'


class Series(models.Model):
    priceopen = models.FloatField(blank=True, null=True)
    priceclose = models.FloatField(blank=True, null=True)
    pricehigh = models.FloatField(blank=True, null=True)
    pricelow = models.FloatField(blank=True, null=True)
    volume = models.BigIntegerField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    resolution = models.CharField(max_length=15)
    stock = models.ForeignKey('Stock', blank=True, null=True, on_delete=models.PROTECT)
    index = models.ForeignKey(Index, blank=True, null=True, on_delete=models.PROTECT)

    class Meta:
        managed = False
        db_table = 'series'
        unique_together = (('date', 'stock', 'resolution'),)


class Signal(models.Model):
    profit_in_percent = models.FloatField(blank=True, null=True)
    probability = models.FloatField(blank=True, null=True)
    probability_30 = models.FloatField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    refresh_date = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=40)
    info = models.CharField(max_length=80, blank=True, null=True)
    status = models.IntegerField()
    stock = models.ForeignKey('Stock', blank=True, null=True, on_delete=models.PROTECT)

    class Meta:
        managed = False
        db_table = 'signal'


class Stock(models.Model):
    feed_quality = models.CharField(max_length=250)
    symbol = models.CharField(max_length=250, blank=True, null=True)
    name = models.CharField(unique=True, max_length=100)
    category = models.CharField(max_length=15)
    exchange = models.ForeignKey(Exchange, blank=True, null=True, on_delete=models.PROTECT)
    region = models.ForeignKey(Region, blank=True, null=True, on_delete=models.PROTECT)
    tags = models.ManyToManyField('Tag', through='TagToStock')

    class Meta:
        managed = False
        db_table = 'stock'

    def __str__(self):
        return '{} ({})'.format(self.symbol, self.name)

class Tag(models.Model):
    tag = models.CharField(unique=True, max_length=250)
    category = models.CharField(max_length=15)
    stocks = models.ManyToManyField('Stock', through='TagToStock')

    class Meta:
        managed = False
        db_table = 'tag'


class TagToStock(models.Model):
    tag = models.ForeignKey(Tag, blank=True, null=True, on_delete=models.PROTECT)
    stock = models.ForeignKey(Stock, blank=True, null=True, on_delete=models.PROTECT)

    class Meta:
        managed = False
        db_table = 'tag_to_stock'
