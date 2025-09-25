# Import Path Update Guide

## 旧パスから新パスへの変更

### 共有ユーティリティ
```python
# 旧: from check_data_status import check_database_status
# 新: from shared.utils import check_database_status

# 旧: from add_new_symbols import add_symbols_to_database  
# 新: from shared.utils import add_symbols_to_database

# 旧: from clean_and_fix_constraints import clean_constraints
# 新: from shared.utils import clean_constraints

# 旧: from fix_database_constraints import fix_constraints
# 新: from shared.utils import fix_constraints
```

### API サービス
```python
# 旧: from separated_lstm_prediction_system import LSTMPredictionSystem
# 新: from miraikakakuapi.services.separated_lstm_prediction_system import LSTMPredictionSystem

# 旧: from unified_prediction_orchestrator import PredictionOrchestrator
# 新: from miraikakakuapi.services.unified_prediction_orchestrator import PredictionOrchestrator
```

### バッチ関数
```python
# 旧: from batch_1_symbol_collection import SymbolCollector
# 新: from miraikakakubatch.functions.batch_1_symbol_collection import SymbolCollector
```
