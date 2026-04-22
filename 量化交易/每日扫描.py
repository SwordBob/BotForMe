#!/usr/bin/env python3
"""
每日A股扫描 - 创业板焦点 + 自选监控
输出到 /Users/niejq/.openclaw/workspace/量化交易/daily_scan_latest.txt
"""

import warnings; warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import baostock as bs
import time, sys, datetime

# ============ 股票池 ============
STOCKS = [
    # 创业板重点 (sz.300xxx)
    ('sz.300750', '宁德时代'),
    ('sz.300760', '迈瑞医疗'),
    ('sz.300059', '东方财富'),
    ('sz.300122', '智飞生物'),
    ('sz.300015', '爱尔眼科'),
    ('sz.300274', '阳光电源'),
    ('sz.300124', '汇川技术'),
    ('sz.300496', '中科创达'),
    ('sz.300454', '深信服'),
    ('sz.300408', '三环集团'),
    ('sz.300782', '卓胜微'),
    ('sz.300896', '爱美客'),
    ('sz.300347', '泰格医药'),
    ('sz.300999', '金龙鱼'),
    ('sz.300033', '同花顺'),
    # 沪深300 ETF（大盘基准）
    ('sh.510300', '沪深300ETF'),
    # 证券ETF
    ('sz.512880', '证券ETF'),
]

def get_data(code):
    try:
        lg = bs.login()
        rs = bs.query_history_k_data_plus(code,
            'date,close,high,low', frequency='d',
            fields='date,close,high,low')
        data = []
        while rs.next(): data.append(rs.get_row_data())
        bs.logout()
        if not data: return None
        df = pd.DataFrame(data, columns=['date','close','high','low'])
        for c in ['close','high','low']: df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(subset=['close'])
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values('date').reset_index(drop=True)
    except:
        return None

def calc_indicators(df):
    close = df['close'].values
    high  = df['high'].values
    low   = df['low'].values
    n = len(close)
    df['ma5']  = pd.Series(close).rolling(5).mean()
    df['ma20'] = pd.Series(close).rolling(20).mean()
    df['ma60'] = pd.Series(close).rolling(60).mean()
    p = 14
    tr = np.maximum(high[1:]-low[1:], np.abs(high[1:]-close[:-1]))
    tr = np.concatenate([[high[0]-low[0]], tr])
    h_d = np.concatenate([[0], np.diff(high)])
    l_d = np.concatenate([[0], np.diff(-low)])
    plus  = np.where(h_d > l_d, np.maximum(h_d, 0), 0)
    minus = np.where(l_d > h_d, np.maximum(l_d, 0), 0)
    atr = pd.Series(tr).ewm(alpha=1/p, adjust=False).mean().values
    pdi = pd.Series(plus).ewm(alpha=1/p, adjust=False).mean().values / (atr + 1e-10) * 100
    mdi = pd.Series(minus).ewm(alpha=1/p, adjust=False).mean().values / (atr + 1e-10) * 100
    dx  = np.abs(pdi - mdi) / (pdi + mdi + 1e-10) * 100
    adx = pd.Series(dx).ewm(alpha=1/p, adjust=False).mean().values
    df['adx'] = adx
    return df

def grid_signal(df, grid_pct=0.02):
    """计算网格信号：最近低点/高点距当前价格%"""
    close = df['close'].values
    high  = df['high'].values
    low   = df['low'].values
    cur   = close[-1]
    # 最近30日高低
    recent_high = np.max(high[-30:])
    recent_low  = np.min(low[-30:])
    upper = (recent_high - cur) / cur * 100
    lower = (cur - recent_low) / cur * 100
    # 网格线（2%一格）
    upper_grid = round(upper / (grid_pct*100)) * (grid_pct*100)
    lower_grid = round(lower / (grid_pct*100)) * (grid_pct*100)
    return {
        'price': round(float(cur), 2),
        'recent_high': round(float(recent_high), 2),
        'recent_low': round(float(recent_low), 2),
        'upper_pct': round(float(upper), 2),
        'lower_pct': round(float(lower), 2),
        'upper_grid': round(float(upper_grid), 2),
        'lower_grid': round(float(lower_grid), 2),
    }

def trend_backtest(df, fee=0.001):
    """MA5/MA20 趋势策略回测（近2年）"""
    df2 = df[df['date'] >= (df['date'].max() - pd.Timedelta(days=730))].copy()
    if len(df2) < 200: return None
    close = df2['close'].values
    ma5   = df2['ma5'].values
    ma20  = df2['ma20'].values
    if np.isnan(ma5[-1]) or np.isnan(ma20[-1]): return None
    cash, pos, prev = 100000.0, 0, ma5[0] > ma20[0]
    for i in range(1, len(df2)):
        if np.isnan(ma5[i]) or np.isnan(ma20[i]): continue
        cur = ma5[i] > ma20[i]
        if cur and not prev and pos == 0:
            sh = int(cash / close[i] / 100) * 100
            cost = sh * close[i] * (1 + fee)
            if cash >= cost and sh > 0: cash -= cost; pos += sh
        elif not cur and prev and pos > 0:
            cash += pos * close[i] * (1 - fee); pos = 0
        prev = cur
    if pos > 0: cash += pos * close[-1] * (1 - fee)
    ret = (cash - 100000) / 100000 * 100
    bh  = (close[-1] / close[0] - 1) * 100
    return {'ret': round(float(ret), 1), 'bh': round(float(bh), 1)}

# ============ 主扫描 ============
print("=" * 60)
print(f"  A股每日扫描 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 60)

output = []
output.append(f"## A股每日扫描 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

signals = []  # (priority, text)

for code, name in STOCKS:
    df = get_data(code)
    if df is None or len(df) < 65: continue
    df = calc_indicators(df)
    r  = df.iloc[-1]
    if np.isnan(r.get('ma5', np.nan)): continue

    ma_ok  = r['ma5'] > r['ma20'] > r['ma60']
    adx    = float(r['adx'])
    grid   = grid_signal(df)
    bt     = trend_backtest(df)

    tag = '✅' if ma_ok and adx > 25 else ('⚠️' if ma_ok else '')
    print(f"{tag} {name:<10} 价={grid['price']}  MA5>{float(r['ma5']):.1f}>MA20>{float(r['ma20']):.1f}>MA60  ADX={adx:.1f}  网格上:{grid['upper_grid']:.0f}% 下:{grid['lower_grid']:.0f}%")

    item = {
        'code': code, 'name': name,
        'price': grid['price'],
        'ma5': float(r['ma5']), 'ma20': float(r['ma20']), 'ma60': float(r['ma60']),
        'adx': adx, 'ma_ok': ma_ok,
        'grid': grid, 'bt': bt,
    }

    # 优先信号：MA多头 + ADX高
    if ma_ok and adx > 30:
        signals.append((0, f"🚨【{name}】强趋势信号！MA多头排列，ADX={adx:.1f}，近期涨幅{grid['upper_pct']:.1f}%，注意追高风险"))
    elif ma_ok and adx > 25:
        signals.append((1, f"✅【{name}】上升趋势，MA多头，ADX={adx:.1f}，网格下方{grid['lower_grid']:.0f}%"))

    # 网格信号（价格距高低点很近）
    if grid['upper_pct'] <= 4:
        signals.append((2, f"📈【{name}】价格距前高仅{grid['upper_pct']:.1f}%，触及网格可能回落（证券ETF注意）"))
    if grid['lower_pct'] <= 4:
        signals.append((3, f"📉【{name}】价格距前低仅{grid['lower_pct']:.1f}%，网格下沿，关注支撑"))

    output.append(f"### {name} (`{code}`)\n")
    output.append(f"- 现价: **{grid['price']}** | ADX: {adx:.1f} | {'✅ MA多头' if ma_ok else '⚠️ 非多头'}\n")
    output.append(f"- MA5={grid['ma5']:.1f} > MA20={grid['ma20']:.1f} > MA60={grid['ma60']:.1f}\n")
    output.append(f"- 网格: 距前高 {grid['upper_pct']:.1f}% | 距前低 {grid['lower_pct']:.1f}%\n")
    if bt:
        output.append(f"- 趋势回测(2y): 策略 {bt['ret']:+.1f}% vs 持有 {bt['bh']:+.1f}%\n")
    output.append("\n")

    time.sleep(0.06)

# 按优先级排序
signals.sort(key=lambda x: x[0])
if signals:
    print("\n### 📋 今日信号\n")
    for _, s in signals:
        print(s)
        output.append(s + "\n")
else:
    print("\n⚠️ 今日无明确信号，建议观望。")

# 写文件
out_path = "/Users/niejq/.openclaw/workspace/量化交易/daily_scan_latest.txt"
with open(out_path, 'w') as f:
    f.write('\n'.join(output))

print(f"\n✅ 扫描完成，结果已保存")
