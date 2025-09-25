#!/usr/bin/env python3
"""
拡張銘柄リストファイル作成
既存の365銘柄 + 新規181銘柄 = 546銘柄のファイルを作成
"""

def create_expanded_file():
    # 既存銘柄を読み込み
    with open('/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/real_data_source_symbols.txt', 'r') as f:
        existing_symbols = set(line.strip() for line in f if line.strip())

    print(f"既存銘柄数: {len(existing_symbols)}")

    # 新規追加銘柄（実際に検証で成功した181銘柄）
    new_symbols = [
        'TRX-GBP', 'ASML', '8058.T', 'DLTR', 'TD.TO', 'EBAY', '9020.T', 'LTC-EUR', '9021.T', 'BT-A.L',
        'FANG', 'FLOW-USD', 'CBA.AX', 'BP', '9202.T', 'TNA', 'WBD', 'EOS-USD', 'NIO', 'PCAR',
        'XLM-USD', '9532.T', 'BABA', 'EOS-GBP', 'VET-USD', 'EA', 'TCEHY', 'XME', '6753.T', 'RY.TO',
        '051910.KS', 'THETA-GBP', 'THETA-EUR', 'XTZ-USD', 'MANA-JPY', 'CHTR', 'IDXX', 'NESN.SW', 'LTC-USD',
        'ICP-JPY', 'XLM-EUR', 'LINK-GBP', 'FAST', 'LCID', '2768.T', 'ULVR.L', 'VOW3.DE', 'XNTK',
        'HBAR-EUR', '006400.KS', 'MNST', 'VET-JPY', 'BMW.DE', '005930.KS', 'SHOP.TO', 'SPXS', 'BHP.AX',
        'UPRO', 'AZN', 'SHEL', 'ETC-USD', 'BCH-USD', 'KHC', 'GEHC', 'KDP', 'LTC-JPY', '7270.T',
        'FLOW-JPY', '6976.T', 'FIL-JPY', 'BAS.DE', 'ETC-EUR', 'ATOM-GBP', 'SPXU', 'ICP-USD', 'BIDU',
        'SAND-GBP', 'TRX-EUR', 'HBAR-USD', 'XLM-JPY', '9502.T', 'ON', '6981.T', 'NAB.AX', 'XTN',
        'ETC-JPY', 'BCH-EUR', 'VET-GBP', '035420.KS', '6779.T', 'EOS-JPY', 'LTC-GBP', '9503.T', 'BARC.L',
        'CTSH', 'SIRI', 'BNS.TO', '7269.T', 'FLOW-EUR', 'HBAR-JPY', 'LINK-JPY', 'XLM-GBP', 'LINK-EUR',
        'USO', 'NTES', '9501.T', 'UNG', 'HBAR-GBP', 'VRSK', 'LINK-USD', 'MANA-USD', 'SAND-JPY',
        'NOVO-B.CO', 'WBC.AX', 'ALGO-GBP', 'RIVN', 'MC.PA', 'ATOM-USD', 'SIE.DE', 'VET-EUR', 'CCEP',
        'ICP-EUR', 'SPXL', '6857.T', 'CPRT', 'BCH-JPY', '6954.T', 'PANW', '7201.T', 'MTCH', 'ANZ.AX',
        'FIL-USD', '9531.T', 'ODFL', 'OR.PA', 'TRX-USD', 'SAND-USD', 'EOS-EUR', 'THETA-USD', 'XTZ-GBP',
        'PDD', 'PAYX', 'ROST', '8628.T', '7267.T', 'SLV', 'SAP', 'ICP-GBP', '7211.T', 'ATOM-JPY',
        'XEL', 'ETC-GBP', 'BCH-GBP', '000660.KS', 'LULU', 'THETA-JPY', 'TTWO', 'ALGO-USD', 'ATOM-EUR',
        'TRX-JPY', 'ALGN', '8316.T', 'LI', '9983.T', 'TZA', 'XTZ-JPY', '8601.T', 'JD', 'ALGO-EUR',
        'SAND-EUR', 'FIL-EUR', 'ALGO-JPY', 'XPEV', 'MBG.DE', 'MANA-EUR', 'CNR.TO', 'VOD.L', 'XTZ-EUR',
        'FIL-GBP', 'MANA-GBP'
    ]

    print(f"新規銘柄数: {len(new_symbols)}")

    # 重複チェック
    overlap = existing_symbols.intersection(set(new_symbols))
    if overlap:
        print(f"重複銘柄: {overlap}")

    # 全銘柄を結合
    all_symbols = list(existing_symbols) + new_symbols
    unique_symbols = sorted(set(all_symbols))

    print(f"合計ユニーク銘柄数: {len(unique_symbols)}")

    # ファイルに書き込み
    output_file = '/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/expanded_verified_symbols.txt'
    with open(output_file, 'w') as f:
        for symbol in unique_symbols:
            f.write(f"{symbol}\n")

    print(f"✅ 拡張銘柄リストを保存: {output_file}")
    print(f"最終銘柄数: {len(unique_symbols)}")

if __name__ == "__main__":
    create_expanded_file()