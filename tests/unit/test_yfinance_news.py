#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""yfinance ニューステスト"""
import yfinance as yf

# 日本株でテスト
symbols = ['7203.T', '9984.T', '6758.T']

for symbol in symbols:
    print(f"\n=== {symbol} ===")
    ticker = yf.Ticker(symbol)

    try:
        news = ticker.news
        print(f"News type: {type(news)}")
        print(f"News count: {len(news) if news else 0}")

        if news and len(news) > 0:
            print(f"First news: {news[0]}")
        else:
            print("No news available")
    except Exception as e:
        print(f"Error: {e}")
