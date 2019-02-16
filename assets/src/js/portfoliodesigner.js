class PortfolioDesigner {
    static createDataListBySelector(id) {
        var dataList = new Map()
        $('#' + id + ' optgroup').each(function () {
            var label = $(this).attr('label');
            var stocksOfLabel = [];
            $('#' + id + ' optgroup[label="' + label + '"] option').each(function () {
                var stockOfLabel = $(this).val();
                stocksOfLabel.push(stockOfLabel);

            });
            dataList.set(label, stocksOfLabel);
        });
        return dataList;
    }

    static updateTable(selectorIds, tableIds) {
        var selectedTextItems = $(selectorIds).find("option:selected");
        var items = new Set();
        for (var i = 0; i < selectedTextItems.length; ++i)
        {
            var value = selectedTextItems[i].value;
            items.add(value)
            gOrderDict.set(value, selectedTextItems[i].text)
        }

        var tableContent = "";

        var myItems = Array.from(items)

        for (var i = 0; i < myItems.length; ++i) {
            var price = gOrderDict.has(myItems[i] + '_PRICE') ? gOrderDict.get(myItems[i] + '_PRICE') : "0.0";
            var amount = gOrderDict.has(myItems[i] + '_AMOUNT') ? gOrderDict.get(myItems[i] + '_AMOUNT') : "0.0";
            var commission = gOrderDict.has(myItems[i] + '_COMMISSION') ? gOrderDict.get(myItems[i] + '_COMMISSION') : "10.0";
            var date = gOrderDict.has(myItems[i] + '_DATE') ? gOrderDict.get(myItems[i] + '_DATE') : moment();
            tableContent += "<tr>";
            tableContent += '<td>' + gOrderDict.get(myItems[i]) + '</td>';
            tableContent += '<td><input class="form-control amountField" type="text" placeholder="0" id="' + myItems[i] + '_AMOUNT" value="' + amount + '"></td>';
            tableContent += '<td><div class="input-group mb-3"><input class="form-control priceField" type="text" placeholder="0" id="' + myItems[i] + '_PRICE" value="' + price + '"><div class="input-group-append"><span class="input-group-text">€</span></div></div></td>';
            tableContent += '<td><div class="input-group mb-3"><input class="form-control commissionField" type="text" placeholder="0" id="' + myItems[i] + '_COMMISSION" value="' + commission + '"><div class="input-group-append"><span class="input-group-text">€</span></div></div></td>';
            tableContent += '<td><div class="input-group date" id="' + myItems[i] + '_DATE"  data-target-input="nearest"><input type="text" class="form-control datetimepicker-input" data-target="#' + myItems[i] + '_DATE"/><div class="input-group-append" data-target="#' + myItems[i] + '_DATE" data-toggle="datetimepicker"><div class="input-group-text"><i class="fa fa-calendar"></i></div></div></div></td>';
            tableContent += "</tr>";
        }
        $(tableIds).html(tableContent);

        for (var i = 0; i < myItems.length; ++i)
        {
            var date = gOrderDict.has(myItems[i] + '_DATE') ? gOrderDict.get(myItems[i] + '_DATE') : moment();
            $('#' + myItems[i] + '_DATE').datetimepicker({
                defaultDate: date,
                format: 'YYYY-MM-DD'
            });
        }
    }
    static calculatePercentage(val, amount, sum) {
        return (val * amount * 100) / sum;
    }

    static calculateSum(orderDict) {
        var priceSum = 0;
        for (let [k, v] of orderDict) {
            var id = this.getId(k);
            var amount = id + '_AMOUNT';
            var price = id + '_PRICE';
            if (orderDict.has(amount) && orderDict.has(price) && k == price) {
                priceSum += parseInt(orderDict.get(price)) * parseInt(orderDict.get(amount));
            }
        }
        return priceSum;
    }

    static getData(orderDict, withId) {
        var data = []
        for (let [k, v] of orderDict) {
            var id = this.getId(k)
            var amount = id + '_AMOUNT';
            var price = id + '_PRICE';
            var percentage = id + '_PERCENTAGE';
            var commission = id + '_COMMISSION';
            if (orderDict.has(amount) && orderDict.has(price) && orderDict.has(percentage) && orderDict.has(commission) &&  k == price) {
                var entry = { 'name': orderDict.get(id), 'y': orderDict.get(percentage) }
                if(withId)
                {
                    entry['id'] = id;
                }
                data.push(entry)
            }
        }
        return data;
    }

    static updateCharts(myCharts) {
        for (const chart of myCharts) {
            chart['chart'].update({
                series: [{
                    name: 'Stocks',
                    colorByPoint: true,
                    data: chart['data']
                }]
            });
        }
    }
    
    static getId(id)
    {
        return id.replace('_AMOUNT', '').replace('_PRICE', '').replace('_DATE', '').replace('_COMMISSION', '');
    }

    static orderComplete(orderDict, id) {
        var id = this.getId(id);
        var amount = id + '_AMOUNT';
        var price = id + '_PRICE';
        var date = id + '_DATE';
        var commission = id + '_COMMISSION'
        if(orderDict.has(amount) && orderDict.has(price) && orderDict.has(date) && orderDict.has(commission))
        {
            return true;
        }
        return false;
    }


    static updateOrderDict(orderDict) {
        var sum = this.calculateSum(orderDict);
        for (let [k, v] of orderDict) {
            var id = this.getId(k);
            var amount = id + '_AMOUNT';
            var price = id + '_PRICE';
            var percentage = id + '_PERCENTAGE';
            var commission = id + '_COMMISSION';
            if (orderDict.has(amount) && orderDict.has(price) && k == price) {
                var percentageVal = this.calculatePercentage(orderDict.get(price), orderDict.get(amount), sum);
                orderDict.set(percentage, percentageVal);
            }
        }
        return orderDict;
    }


    static orderDictToJson(orderDict) {
        var myList = [];
        for (let [k1, v1] of orderDict) 
        {   
            if(k1.includes('_PRICE'))
            {
                var id = this.getId(k1);
                var entry = {'id': id};
                for (let [k2, v2] of orderDict) 
                {
                    if(k2.includes(id))
                    {
                        if(k2.includes('PRICE'))
                        {
                            entry['price'] = v2;
        
                        }
                        else if(k2.includes('AMOUNT'))
                        {
                            entry['amount'] = v2;
                        }
                        else if(k2.includes('DATE'))
                        {
                            entry['date'] = v2;
                        }
                        else if(k2.includes('COMMISSION'))
                        {
                            entry['commission'] = v2;
                        }
                    }
                }
                myList.push(entry)
            }
        }

        return JSON.stringify(myList);
    }


    static printMap(orderDict) {
        for (let [k, v] of orderDict) {
            console.log(k + ':' + v);
        }
    }

    static getDataCategory(categoryData, orderDict) {
        var dataStocks = this.getData(orderDict, true);
        var data = [];
        for (let [kCategory, vCategory] of categoryData) {
            var categoryPerc = 0;
            for (let v of dataStocks) {
                if (vCategory.includes(v['id'])) {
                    categoryPerc += parseInt(v['y']);
                }
            }
            if (categoryPerc > 0) {
                data.push({ 'name': kCategory, 'y': categoryPerc })
            }
        }
        return data;
    }

    static createChartOptionsData(title, myData) {
        var chartOption = {
            credits: false,
            chart: {
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                type: 'pie'
            },
            title: {
                text: title
            },
            tooltip: {
                pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: true,
                        format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                        style: {
                            color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                        }
                    }
                }
            },
            series: [{
                name: 'Brands',
                colorByPoint: true,
                data: myData
            }]
        }
        return chartOption;
    }

    static createChartOptions(title) {
        return this.createChartOptionsData(title, [])
    }
}

export default PortfolioDesigner;