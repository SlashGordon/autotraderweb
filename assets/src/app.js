// JavaScript requirements
var $ = require('jquery');
window.jQuery = $;
var tether = require('tether');
var bootstrap = require('bootstrap');
var moment = require('moment');
window.moment = moment;
var bootstrap_select = require('bootstrap-select');
window.datetimepicker = require('tempusdominus-bootstrap-4');
var Highcharts = require('highcharts/highstock');
var HighchartsMore = require('highcharts/highcharts-more');
HighchartsMore(Highcharts);
window.Highcharts = Highcharts;
window.popper = require('popper.js');
window.tablesorter = require('tablesorter');
// SCSS includes
var scss = require('./scss/app.scss')
////////////////////////////////////////////////////////////////////////////
// Project specific JavaScript
////////////////////////////////////////////////////////////////////////////
var tooltips = require('./js/tooltips');
window.PortFolioDesigner = require('./js/portfoliodesigner').default;
window.portfoliomodal = require('./js/jquery.bootstrap.modal.forms').default;