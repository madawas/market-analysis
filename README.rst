Python Library for Extracting Stock Market Data From Multiple Sources
=====================================================================

.. image:: https://travis-ci.org/madawas/market-analysis.svg?branch=main
    :target: https://travis-ci.org/madawas/market-analysis

.. image:: https://codecov.io/gh/madawas/market-analysis/branch/main/graphs/badge.svg?branch=main
    :target: https://codecov.io/gh/madawas/market-analysis

This python package allows extracting stock market data from multiple sources such as `IEXCloud <https://iexcloud
.io/>`_, `Alpha Vantage <https://www.alphavantage.co/>`_ `Yahoo! Finance <https://finance.yahoo.com>`_ and other
custom sources which can be defined in the configuration.

Quick Start
-----------

Ticker Module
^^^^^^^^^^^^^

The ``Ticker`` module enables extracting market data using the data source of your choice.

.. code-block:: python

        from marketdata import Ticker

        aapl = Ticker('AAPL', 'IEXCloud')
        summary = aapl.get_summary()