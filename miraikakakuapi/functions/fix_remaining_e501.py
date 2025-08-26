#!/usr/bin/env python3
"""Fix remaining E501 errors by breaking long lines"""


def fix_remaining_e501(filename):
    with open(filename, "r") as f:
        lines = f.readlines()

    # Process specific long lines
    # Line 1972
    if len(lines) > 1971 and len(lines[1971]) > 79:
        if '"title":' in lines[1971]:
            lines[1971] = lines[1971].replace(
                '"title": "日経平均が3営業日連続上昇、半導体関連株が牽引し3万8000円台を回復",',
                '"title": (\n                    "日経平均が3営業日連続上昇、"\n                    "半導体関連株が牽引し3万8000円台を回復"\n                ),',
            )

    # Line 2668
    if len(lines) > 2667 and len(lines[2667]) > 79:
        if '"description":' in lines[2667]:
            lines[2667] = lines[2667].replace(
                '"description": "AIが駆動する取引システムが、投資の意思決定方法を変革。深層学習モデルの活用が広がる。",',
                '"description": (\n                    "AIが駆動する取引システムが、"\n                    "投資の意思決定方法を変革。"\n                    "深層学習モデルの活用が広がる。"\n                ),',
            )

    # Line 2693
    if len(lines) > 2692 and len(lines[2692]) > 79:
        if '"description":' in lines[2692]:
            lines[2692] = lines[2692].replace(
                '"description": "環境配慮型の投資戦略が主流となり、ESG投資への関心が急速に高まる。機関投資家の注目を集める。",',
                '"description": (\n                    "環境配慮型の投資戦略が主流となり、"\n                    "ESG投資への関心が急速に高まる。"\n                    "機関投資家の注目を集める。"\n                ),',
            )

    # Line 2719
    if len(lines) > 2718 and len(lines[2718]) > 79:
        if '"description":' in lines[2718]:
            lines[2718] = lines[2718].replace(
                '"description": "暗号資産と伝統的金融市場の統合が進行中。デジタル通貨の実用化が加速し、新しい投資機会を創出している。",',
                '"description": (\n                    "暗号資産と伝統的金融市場の統合が進行中。"\n                    "デジタル通貨の実用化が加速し、"\n                    "新しい投資機会を創出している。"\n                ),',
            )

    # Line 2734
    if len(lines) > 2733 and len(lines[2733]) > 79:
        if '"description":' in lines[2733]:
            lines[2733] = lines[2733].replace(
                '"description": "新興市場の成長率が先進国市場を上回る。東南アジア、アフリカ、南米の市場が投資家の注目を集める。",',
                '"description": (\n                    "新興市場の成長率が先進国市場を上回る。"\n                    "東南アジア、アフリカ、南米の市場が"\n                    "投資家の注目を集める。"\n                ),',
            )

    with open(filename, "w") as f:
        f.writelines(lines)

    print(f"Fixed remaining E501 errors")


if __name__ == "__main__":
    fix_remaining_e501("production_main.py")
