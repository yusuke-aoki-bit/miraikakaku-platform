"""
Japanese company name mapping utility for batch jobs
"""

def get_japanese_company_name(symbol, english_name=None):
    """
    Convert stock symbol to Japanese company name

    Args:
        symbol (str): Stock symbol (e.g., 'AAPL', '7203.T')
        english_name (str): Optional English company name as fallback

    Returns:
        str: Japanese company name or fallback to English name
    """
    japanese_names = {
        # 大手日本企業
        "7203.T": "トヨタ自動車",
        "6758.T": "ソニーグループ",
        "9984.T": "ソフトバンクグループ",
        "6861.T": "キーエンス",
        "4063.T": "信越化学工業",
        "6954.T": "ファナック",
        "9432.T": "日本電信電話",
        "7974.T": "任天堂",
        "4502.T": "武田薬品工業",
        "8316.T": "三井住友フィナンシャルグループ",
        "8411.T": "みずほフィナンシャルグループ",
        "1802.T": "大林組",
        "1928.T": "積水ハウス",
        "2914.T": "日本たばこ産業",
        "8001.T": "伊藤忠商事",
        "8058.T": "三菱商事",
        "9613.T": "エヌ・ティ・ティ・データ",
        "6501.T": "日立製作所",
        "6902.T": "デンソー",
        "7267.T": "ホンダ",
        "7751.T": "キヤノン",

        # 米国株
        "AAPL": "アップル",
        "MSFT": "マイクロソフト",
        "GOOGL": "アルファベット（グーグル）",
        "GOOG": "アルファベット（グーグル）",
        "AMZN": "アマゾン",
        "TSLA": "テスラ",
        "META": "メタ（フェイスブック）",
        "NVDA": "エヌビディア",
        "NFLX": "ネットフリックス",
        "PYPL": "ペイパル",
        "ORCL": "オラクル",
        "CRM": "セールスフォース",
        "ADBE": "アドビ",
        "INTC": "インテル",
        "CSCO": "シスコシステムズ",
        "IBM": "アイビーエム",
        "HPE": "ヒューレット・パッカード・エンタープライズ",
        "DIS": "ウォルト・ディズニー",
        "KO": "コカ・コーラ",
        "PEP": "ペプシコ",
        "MCD": "マクドナルド",
        "NKE": "ナイキ",
        "V": "ビザ",
        "MA": "マスターカード",
        "JPM": "JPモルガン・チェース",
        "GS": "ゴールドマン・サックス",
        "BAC": "バンク・オブ・アメリカ",

        # 暗号通貨
        "BTC-USD": "ビットコイン",
        "ETH-USD": "イーサリアム",
        "BNB-USD": "バイナンスコイン",
        "ADA-USD": "カルダノ",
        "XRP-USD": "リップル",
        "SOL-USD": "ソラナ",
        "DOT-USD": "ポルカドット",
        "DOGE-USD": "ドージコイン",
        "AVAX-USD": "アバランチ",
        "MATIC-USD": "ポリゴン",
        "LINK-USD": "チェーンリンク",
        "UNI-USD": "ユニスワップ",
        "LTC-USD": "ライトコイン",
        "BCH-USD": "ビットコインキャッシュ",
        "XLM-USD": "ステラルーメン",

        # ETF
        "SPY": "SPDR S&P 500 ETF",
        "QQQ": "インベスコQQQ信託シリーズ1",
        "VTI": "バンガード・トータル・ストック・マーケットETF",
        "VOO": "バンガード・S&P 500 ETF",
        "IVV": "iシェアーズ・コア S&P 500 ETF",
        "VEA": "バンガード・FTSE先進国市場ETF",
        "VWO": "バンガード・FTSE新興国市場ETF",
        "VTI": "バンガード・トータル・ストック・マーケットETF",
        "IEFA": "iシェアーズ・コア MSCI先進国市場IMI インデックスETF",
        "VIG": "バンガード・配当貴族ETF",

        # 商品・先物
        "GLD": "SPDR ゴールド・シェア",
        "SLV": "iシェアーズ・シルバートラスト",
        "USO": "米国石油ファンド",
        "UNG": "米国天然ガスファンド",
        "DBA": "インベスコ DB 農業ファンド",

        # 債券
        "TLT": "iシェアーズ20年超米国債ETF",
        "IEF": "iシェアーズ7-10年米国債ETF",
        "SHY": "iシェアーズ1-3年米国債ETF",
        "LQD": "iシェアーズ投資適格社債ETF",
        "HYG": "iシェアーズ・ハイイールド社債ETF",

        # 不動産
        "VNQ": "バンガード・リートETF",
        "IYR": "iシェアーズ米国不動産ETF",
        "RWR": "SPDR ダウ・ジョーンズ・リートETF",

        # 中国株
        "BABA": "アリババ・グループ・ホールディング",
        "JD": "京東",
        "BIDU": "百度",
        "NIO": "蔚来",
        "XPEV": "小鵬汽車",
        "LI": "理想汽車",
        "PDD": "拼多多",
        "BILI": "哔哩哔哩",
        "TME": "騰訊音楽娯楽集団",

        # その他アジア株
        "005930.KS": "サムスン電子",
        "000660.KS": "SKハイニックス",
        "035420.KS": "ネイバー",
        "035720.KS": "カカオ",
        "2330.TW": "台湾セミコンダクター",
        "2454.TW": "メディアテック",
        "2317.TW": "鴻海精密工業",
    }

    # シンボルに基づく日本語名を返す
    japanese_name = japanese_names.get(symbol)
    if japanese_name:
        return japanese_name

    # フォールバック：英語名があればそれを返す、なければシンボルを返す
    return english_name if english_name else symbol


def format_japanese_company_info(symbol, english_name=None, include_symbol=True):
    """
    Format company information with Japanese name and symbol

    Args:
        symbol (str): Stock symbol
        english_name (str): Optional English name
        include_symbol (bool): Whether to include symbol in output

    Returns:
        str: Formatted company information
    """
    japanese_name = get_japanese_company_name(symbol, english_name)

    if include_symbol and japanese_name != symbol:
        return f"{japanese_name} ({symbol})"
    else:
        return japanese_name


def is_japanese_stock(symbol):
    """
    Check if the symbol represents a Japanese stock

    Args:
        symbol (str): Stock symbol

    Returns:
        bool: True if it's a Japanese stock symbol
    """
    # Japanese stocks typically end with .T
    return symbol.endswith('.T')


def get_market_category(symbol):
    """
    Get market category for the symbol

    Args:
        symbol (str): Stock symbol

    Returns:
        str: Market category in Japanese
    """
    if symbol.endswith('.T'):
        return "日本株"
    elif symbol.endswith('.KS'):
        return "韓国株"
    elif symbol.endswith('.TW'):
        return "台湾株"
    elif '-USD' in symbol:
        return "暗号通貨"
    elif symbol in ['SPY', 'QQQ', 'VTI', 'VOO', 'IVV', 'VEA', 'VWO', 'IEFA', 'VIG', 'GLD', 'SLV', 'TLT', 'IEF', 'SHY', 'LQD', 'HYG', 'VNQ', 'IYR', 'RWR', 'USO', 'UNG', 'DBA']:
        return "ETF・投資信託"
    else:
        return "米国株"