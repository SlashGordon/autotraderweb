const path = require('path');
const webpack = require('webpack');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const ProvidePlugin = require('webpack/lib/ProvidePlugin');
// Write output files (JS, CSS, images, fonts) to this path
const OUTPUT_DIR = path.resolve('./content/assets');

var babelOptions = {
  "presets": [
    [
      "es2015",
      {
          "modules": false
      }
    ],
    "es2016"
  ]
};

// Break CSS files into a separate bundle
// https://github.com/webpack-contrib/extract-text-webpack-plugin
const EXTRACT_SASS_RULES = new ExtractTextPlugin({
  filename: '[name].css',
  disable: process.env.NODE_ENV === 'development',
});

// Minify JavaScript files in production
// https://webpack.js.org/plugins/uglifyjs-webpack-plugin/
const JS_MINIFIER_OPTIONS = new webpack.optimize.UglifyJsPlugin({
  compressor: (process.env.NODE_ENV === 'production' ? { warnings: false } : false),
});


module.exports = {
  entry: {
    // This is the entry point to the application
    // This JavaScript file can import other files all of which will be processed
    // by webpack
    app: './assets/src/app.js',
  },
  output: {
    // This is where post-processed assets should be written
    filename: '[name].js',
    path: OUTPUT_DIR,
  },
  module: {
    rules: [{
      // When (S)CSS files are encountered while processing "entries",
      // process them and write them to a separate file ENTRY.css
      // Minify the CSS for production
      // https://webpack.js.org/loaders/css-loader/
      // https://webpack.js.org/loaders/sass-loader/
      test: /\.scss$/,
      loader: EXTRACT_SASS_RULES.extract({
        loader: [{
          loader: 'css-loader',
          options: { minimize: process.env.NODE_ENV === 'production' },
        }, {
          loader: 'sass-loader',
        }],
        // use style-loader in development
        fallback: 'style-loader',
      }),
    }, {
      // Font files are written directly to OUTPUT_DIR/fonts
      // https://webpack.js.org/loaders/file-loader/
      test: /\.(woff(2)?|ttf|eot|svg)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
      loader: 'file-loader?name=./webfonts/[name].[ext]',
    }, {
      // Image files are written directly to OUTPUT_DIR/img
      test: /\.(png|gif|jpg|jpeg)$/,
      loader: 'file-loader?name=./img/[name].[ext]'
    },{
      test: /\.ts$/,
      exclude: /node_modules/,
      use: [
        {
            loader: 'babel-loader',
            options: babelOptions
        },
        {
            loader: 'ts-loader'
        }
      ]
    },{
      test: /\.js$/,
      exclude: /node_modules/,
      use: [
        {
            loader: 'babel-loader',
            options: babelOptions
        }
      ]
    },{
        test: require.resolve('jquery'),
        use: [{
            loader: 'expose-loader',
            options: '$'
        }]
    }

    ],
  },
  plugins: [
    EXTRACT_SASS_RULES,
    JS_MINIFIER_OPTIONS,

    // Makes jQuery and Tether (required for bootstrap4) available to other JS includes
    // https://webpack.js.org/plugins/provide-plugin/
    new webpack.ProvidePlugin({
      jQuery: 'jquery',
      $: 'jquery',
      jquery: 'jquery',
    Tether: "tether",
    "window.Tether": "tether",
    tablesorter: "tablesorter",
    Popper: ['popper.js', 'default'],
    Highcharts: 'highcharts',
    'bootstrap-select': 'bootstrap-select',
    'moment': 'moment',
    'tempusdominus-bootstrap-4': 'tempusdominus-bootstrap-4',
    'PortFolioDesigner': 'PortFolioDesigner'
    })
  ],
  resolve: {
    modules: [ 'node_modules' ],
    alias: {
      styles: 'assets/src/scss',
    },
  },
};