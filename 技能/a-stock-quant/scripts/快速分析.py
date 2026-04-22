import baostock as bs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

bs.login()
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

def get_kline(code):
    fields = 'date,code,open,high,low,close,volume'
    rs = bs.query_history_k_data_plus(code, fields, start_date=start_date, end_date=end_date, frequency='d')
    data = []
    while rs.error_code == '0' and rs.next():
        data.append(rs.get_row_data())
    if data:
        return pd.DataFrame(data, columns=rs.fields)
    return pd.DataFrame()

def calc_adx(df, period=14):
    for col in ['close', 'open', 'high', 'low', 'volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.sort_values('date').reset_index(drop=True)
    if len(df) < period + 2:
        return None
    high = df['high'].values
    low = df['low'].values
    close = df['close'].values
    tr = np.zeros(len(df))
    plus_dm = np.zeros(len(df))
    minus_dm = np.zeros(len(df))
    for i in range(1, len(df)):
        tr[i] = max(high[i], close[i-1]) - min(low[i], close[i-1])
        high_diff = high[i] - high[i-1]
        low_diff = low[i-1] - low[i]
        if high_diff > low_diff:
            plus_dm[i] = high_diff
        else:
            minus_dm[i] = low_diff
    atr = np.zeros(len(df))
    atr[0] = tr[0]
    for i in range(1, len(df)):
        atr[i] = (atr[i-1] * (period - 1) + tr[i]) / period
    plus_di = np.zeros(len(df))
    minus_di = np.zeros(len(df))
    for i in range(period, len(df)):
        plus_di[i] = (np.sum(plus_dm[i-period+1:i+1]) / (np.sum(tr[i-period+1:i+1]) + 1e-10)) * 100
        minus_di[i] = (np.sum(minus_dm[i-period+1:i+1]) / (np.sum(tr[i-period+1:i+1]) + 1e-10)) * 100
    dx = np.abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10) * 100
    adx = np.zeros(len(df))
    adx[period] = np.mean(dx[period:period*2])
    for i in range(period + 1, len(df)):
        adx[i] = (adx[i-1] * (period - 1) + dx[i]) / period
    return adx[-1]

stocks = [
    ('sh.600519', '贵州茅台'),
    ('sh.601318', '中国平安'),
    ('sz.000858', '五粮液'),
    ('sz.300750', '宁德时代'),
    ('sh.688981', '中芯国际'),
    ('sh.600036', '招商银行'),
    ('sz.300059', '东方财富'),
    ('sh.600276', '恒瑞医药'),
    ('sz.002594', '比亚迪'),
]

print(f'📅 {datetime.now().strftime("%Y-%m-%d %H:%M")} A股市场技术指标')
print('='*75)
results = []
for code, name in stocks:
    df = get_kline(code)
    if len(df) < 30:
        continue
    close = float(df['close'].iloc[-1])
    ma5 = float(df['close'].rolling(5).mean().iloc[-1])
    ma20 = float(df['close'].rolling(20).mean().iloc[-1])
    ma60_val = float(df['close'].rolling(60).mean().iloc[-1]) if len(df) >= 60 else None
    adx = calc_adx(df)
    has_ma60 = ma60_val is not None
    if has_ma60 and ma5 > ma20 and ma20 > ma60_val and adx and adx > 30:
        trend = '📈强势(MA多头)'
    elif has_ma60 and ma5 < ma20 and ma20 < ma60_val:
        trend = '📉弱势(MA空头)'
    else:
        trend = '➡️中性'
    results.append((name, close, ma5, ma20, ma60_val, adx, trend))

results.sort(key=lambda x: -x[5] if x[5] else 0)
for name, close, ma5, ma20, ma60_val, adx, trend in results:
    adx_str = f'{adx:.1f}' if adx else 'N/A'
    ma60_str = f'{ma60_val:.2f}' if ma60_val else 'N/A'
    print(f'{trend} {name:8s} 现价:{close:8.2f} MA5:{ma5:8.2f} MA20:{ma20:8.2f} MA60:{ma60_str}  ADX:{adx_str}')

print()
print('📊 策略参考:')
print('  ADX>30 + MA多头排列 → 趋势跟随策略(双均线金叉买入)')
print('  ADX<20 → 网格交易策略(跌2%买/涨2%卖)')
print('  ADX 20-30 → 观望，等待明确信号')
bs.logout()
