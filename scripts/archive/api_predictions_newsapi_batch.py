#!/usr/bin/env python3
"""
NewsAPI.org Batch Collection Endpoint
バッチニュース収集用エンドポイント(api_predictions.pyに追加する予定)
"""

# api_predictions.pyに以下のエンドポイントを追加

"""
@app.post("/admin/collect-news-newsapi-batch")
def collect_news_newsapi_batch_endpoint(limit: int = 15):
    '''NewsAPI.orgを使用してバッチニュース収集（管理者用）'''
    '''
    日本株15銘柄のニュースを一括収集
    NewsAPI.org無料プラン: 100リクエスト/日
    シンボルマッピング済み: 15社
    '''
    try:
        import newsapi_collector

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 日本株銘柄をシンボルマッピング済みのものから取得
        # newsapi_collector.pyのsymbol_to_enに登録されている銘柄のみ
        supported_symbols = [
            '7203.T',  # Toyota
            '6758.T',  # Sony
            '9984.T',  # SoftBank
            '7974.T',  # Nintendo
            '7267.T',  # Honda
            '7201.T',  # Nissan
            '6752.T',  # Panasonic
            '8306.T',  # MUFG
            '8316.T',  # SMFG
            '8411.T',  # Mizuho
            '6861.T',  # Keyence
            '9983.T',  # Fast Retailing
            '8035.T',  # Tokyo Electron
            '6367.T',  # Daikin
            '4063.T'   # Shin-Etsu Chemical
        ]

        # 銘柄情報を取得
        placeholders = ','.join(['%s'] * len(supported_symbols))
        cur.execute(f"""
            SELECT symbol, company_name
            FROM stock_master
            WHERE symbol IN ({placeholders})
              AND is_active = TRUE
            ORDER BY symbol
            LIMIT %s
        """, (*supported_symbols, limit))

        symbols = cur.fetchall()
        cur.close()

        if not symbols:
            conn.close()
            return {
                "status": "error",
                "message": "No supported Japanese stocks found"
            }

        # バッチニュース収集
        collector = newsapi_collector.NewsAPICollector()
        results = []

        for symbol_info in symbols:
            symbol = symbol_info['symbol']
            company_name = symbol_info['company_name']

            try:
                result = collector.collect_news_for_symbol(symbol, company_name, days=7)
                results.append(result)

                # NewsAPI.org rate limit: 5 requests/second
                import time
                time.sleep(0.3)  # 300ms間隔 = 3.3 req/sec

            except Exception as e:
                results.append({
                    "symbol": symbol,
                    "company_name": company_name,
                    "status": "error",
                    "message": str(e)
                })

        conn.close()

        # 成功・失敗をカウント
        successful = [r for r in results if r.get('status') == 'success']
        failed = [r for r in results if r.get('status') != 'success']

        total_articles = sum(r.get('articles_saved', 0) for r in successful)

        return {
            "status": "success",
            "message": f"Batch news collection completed for {len(symbols)} Japanese stocks",
            "total_symbols": len(symbols),
            "successful": len(successful),
            "failed": len(failed),
            "total_articles_collected": total_articles,
            "results": results
        }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }
"""
