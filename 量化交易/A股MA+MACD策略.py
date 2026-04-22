#!/usr/bin/env python3
"""
A股 MA+MACD 自适应策略
========================================
数据源：baostock（免费，支持全部A股）

策略思路（从美股移植）：
1. 先用 ADX 筛选有趋势的股票（ADX > 25 才考虑入场）
2. 双均线 + MACD 组合：
   - 金叉买入 AND MACD柱由负转正
   - 死叉卖出 AND MACD柱由正转负
3. 无趋势股票（ADX < 20）跳过不操作
4. 对比：MA+MACD选股 vs 无筛选 vs 买入持有

同时扫描全市场，用 ADX > 25 的月份比例筛选出"有趋势的股票"
"""

import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import baostock as bs
import backtrader as bt
import time
import sys


# ============================================================
# 数据获取
# ============================================================
def 获取A股数据(code, start_date='2023-01-01', end_date='2025-12-31'):
    try:
        lg = bs.login()
        rs = bs.query_history_k_data_plus(
            code,
            'date,open,high,low,close,volume',
            start_date=start_date,
            end_date=end_date,
            frequency='d'
        )
        data = []
        while rs.next():
            data.append(rs.get_row_data())
        bs.logout()
        if not data:
            return None
        df = pd.DataFrame(data, columns=['date','open','high','low','close','volume'])
        df = df[df['volume'].notna() & (df['volume'] != '')]
        for col in ['close','open','high','low','volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['close','open'])
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        return df
    except Exception as e:
        return None


def 计算ADX(df, period=14):
    """手动计算 ADX（方向性指数）"""
    high = df['high'].values
    low  = df['low'].values
    close= df['close'].values

    # True Range
    tr1 = high[1:] - low[1:]
    tr2 = np.abs(high[1:] - close[:-1])
    tr3 = np.abs(low[1:] - close[:-1])
    tr = np.concatenate([[0], np.maximum(np.maximum(tr1, tr2), tr3)])

    # Directional Movement
    plus_dm = np.zeros(len(high))
    minus_dm = np.zeros(len(high))
    for i in range(1, len(high)):
        h_diff = high[i] - high[i-1]
        l_diff = low[i-1] - low[i]
        if h_diff > l_diff and h_diff > 0:
            plus_dm[i] = h_diff
        if l_diff > h_diff and l_diff > 0:
            minus_dm[i] = l_diff

    # 平滑（EMA）
    atr  = pd.Series(tr).ewm(alpha=1/period, adjust=False).mean().values
    plus_di = pd.Series(plus_dm).ewm(alpha=1/period, adjust=False).mean().values
    minus_di= pd.Series(minus_dm).ewm(alpha=1/period, adjust=False).mean().values

    # ADX
    dx = np.abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10) * 100
    adx = pd.Series(dx).ewm(alpha=1/period, adjust=False).mean().values

    return adx


# ============================================================
# 策略1：MA+MACD 自适应（移植美股思路）
# ============================================================
class A股MA_MACD策略(bt.Strategy):
    """
    A股版 MA+MACD 策略
    - ADX > 25（强趋势）：使用双均线
    - ADX < 20（震荡）：使用MACD确认
    - ADX 中间区域：两者结合
    - 无趋势时不入场（空仓）
    """
    params = dict(
        sma_short=5, sma_long=20,
        macd_fast=12, macd_slow=26, macd_signal=9,
        adx_period=14, adx_strong=25, adx_weak=20,
    )
    def __init__(self):
        self.order = None
        self.trades = []
        self.mode = None

        sma1 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_short)
        sma2 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_long)
        self.sma_cross = bt.indicators.CrossOver(sma1, sma2)

        self.macd = bt.indicators.MACD(
            self.datas[0].close,
            period_me1=self.params.macd_fast,
            period_me2=self.params.macd_slow,
            period_signal=self.params.macd_signal
        )
        self.macd_hist = self.macd.macd - self.macd.signal

        self.adx = bt.indicators.AverageDirectionalMovementIndex(
            self.datas[0], period=self.params.adx_period
        )
        self.adx_val = self.adx.adx

    def next(self):
        if self.order or len(self.adx_val) < self.params.adx_period:
            return

        adx  = self.adx_val[0]
        hist = self.macd_hist[0]
        prev_hist = self.macd_hist[-1]
        cross = self.sma_cross[0]

        # 模式判断
        if adx > self.params.adx_strong:
            mode = 'MA'
        elif adx < self.params.adx_weak:
            mode = 'MACD'
        else:
            mode = 'BOTH'

        # ---- 入场：无持仓时 ----
        if not self.position:
            if mode == 'MA' and cross > 0:
                self.order = self.buy()
                self.mode = mode
            elif mode == 'MACD' and (prev_hist < 0) and (hist > 0):
                self.order = self.buy()
                self.mode = mode
            elif mode == 'BOTH' and cross > 0 and hist > 0:
                self.order = self.buy()
                self.mode = mode

        # ---- 出场：有持仓时 ----
        else:
            if mode == 'MA' and cross < 0:
                self.order = self.sell()
                self.mode = None
            elif mode == 'MACD' and (prev_hist > 0) and (hist < 0):
                self.order = self.sell()
                self.mode = None
            elif mode == 'BOTH' and cross < 0 and hist < 0:
                self.order = self.sell()
                self.mode = None

    def notify_order(self, order):
        if order.status == order.Completed:
            self.trades.append({
                'action': 'BUY' if order.isbuy() else 'SELL',
                'price': order.executed.price,
                'mode': self.mode
            })
        self.order = None


# ============================================================
# 策略2：纯双均线（对照）
# ============================================================
class 纯双均线(bt.Strategy):
    params = (('sma_short', 5), ('sma_long', 20))
    def __init__(self):
        sma1 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_short)
        sma2 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_long)
        self.cross = bt.indicators.CrossOver(sma1, sma2)
        self.order = None
        self.trades = []
    def next(self):
        if self.order: return
        if self.cross > 0 and not self.position:
            self.order = self.buy()
        elif self.cross < 0 and self.position:
            self.order = self.sell()
    def notify_order(self, order):
        if order.status == order.Completed:
            self.trades.append({'action': 'BUY' if order.isbuy() else 'SELL', 'price': order.executed.price})
        self.order = None


# ============================================================
# 策略3：买入持有
# ============================================================
class 买入持有(bt.Strategy):
    def __init__(self): self.order = None
    def next(self):
        if not self.position: self.order = self.buy()
    def notify_order(self, order): self.order = None


# ============================================================
# 回测运行器
# ============================================================
def 运行回测(code, name='', start='2023-01-01', end='2025-12-31', initial_cash=100000):
    df = 获取A股数据(code, start, end)
    if df is None or len(df) < 60:
        return None

    stock_name = name or code

    print(f'\n{"="*62}')
    print(f'  📈 {stock_name} ({code})')
    print(f'{"="*62}')

    df_bt = df[['date','open','high','low','close','volume']].copy()
    df_bt.columns = ['datetime','open','high','low','close','volume']
    df_bt['datetime'] = pd.to_datetime(df_bt['datetime'])

    results = {}

    # MA+MACD 自适应
    cerebro1 = bt.Cerebro()
    cerebro1.addstrategy(A股MA_MACD策略)
    cerebro1.adddata(bt.feeds.PandasData(dataname=df_bt, datetime=0))
    cerebro1.broker.setcash(initial_cash)
    cerebro1.broker.setcommission(commission=0.001)
    cerebro1.addsizer(bt.sizers.AllInSizerInt)
    p1 = cerebro1.run()
    fv1 = cerebro1.broker.getvalue()
    ret1 = (fv1 - initial_cash) / initial_cash * 100
    t1 = len(p1[0].trades)
    results['MA+MACD'] = {'final': fv1, 'return': ret1, 'trades': t1}

    # 纯双均线
    cerebro2 = bt.Cerebro()
    cerebro2.addstrategy(纯双均线)
    cerebro2.adddata(bt.feeds.PandasData(dataname=df_bt, datetime=0))
    cerebro2.broker.setcash(initial_cash)
    cerebro2.broker.setcommission(commission=0.001)
    cerebro2.addsizer(bt.sizers.AllInSizerInt)
    cerebro2.run()
    fv2 = cerebro2.broker.getvalue()
    ret2 = (fv2 - initial_cash) / initial_cash * 100
    results['纯双均线'] = {'final': fv2, 'return': ret2, 'trades': t1}

    # 买入持有
    cerebro3 = bt.Cerebro()
    cerebro3.addstrategy(买入持有)
    cerebro3.adddata(bt.feeds.PandasData(dataname=df_bt, datetime=0))
    cerebro3.broker.setcash(initial_cash)
    cerebro3.broker.setcommission(commission=0.001)
    cerebro3.run()
    fv3 = cerebro3.broker.getvalue()
    ret3 = (fv3 - initial_cash) / initial_cash * 100
    results['买入持有'] = {'final': fv3, 'return': ret3, 'trades': 1}

    # 最大回撤
    close_arr = df['close'].values
    max_price = np.maximum.accumulate(close_arr)
    max_dd = ((close_arr - max_price) / max_price * 100).min()

    print(f'  {"策略":<12} {"最终资金":>13} {"收益率":>10} {"交易次数":>8}')
    print(f'  {"-"*46}')
    print(f'  {"MA+MACD":<12} {"¥"+f"{fv1:,.0f}":>13} {ret1:>+8.2f}%   {t1:>4}笔')
    print(f'  {"纯双均线":<12} {"¥"+f"{fv2:,.0f}":>13} {ret2:>+8.2f}%   {t1:>4}笔')
    print(f'  {"买入持有":<12} {"¥"+f"{fv3:,.0f}":>13} {ret3:>+8.2f}%   {"1":>4}笔')
    print(f'{"="*62}')
    print(f'  📉 最大回撤：{max_dd:.2f}%')

    best = max(results, key=lambda k: results[k]['return'])
    print(f'  🏆 最优：{best}  {results[best]["return"]:+.2f}%')

    return results


# ============================================================
# 主程序
# ============================================================
if __name__ == '__main__':
    print('''
╔══════════════════════════════════════════════════╗
║    🚀 A股 MA+MACD 策略 | baostock数据          ║
║    思路：从美股策略移植                      ║
║    ADX>25 → MA双均线                        ║
║    ADX<20 → MACD确认（无趋势时空仓）         ║
║    ADX中间 → 两者结合                        ║
╚══════════════════════════════════════════════════╝
''')

    标的池 = [
        ('sh.600519', '贵州茅台'),
        ('sh.601318', '中国平安'),
        ('sh.600036', '招商银行'),
        ('sh.000858', '五粮液'),
        ('sz.000001', '平安银行(深)'),
        ('sh.600276', '恒瑞医药'),
        ('sh.600030', '中信证券'),
        ('sh.601888', '中国中免'),
        ('sh.002475', '立讯精密'),
        ('sh.000858', '五粮液'),  # 重复测一次
    ]

    # 去重
    seen = set()
    unique = []
    for c, n in 标的池:
        if c not in seen:
            seen.add(c)
            unique.append((c, n))
    标的池 = unique

    print('测试标的：')
    for c, n in 标的池:
        print(f'  {c}  {n}')
    print()

    all_results = {}
    for code, name in 标的池:
        res = 运行回测(code, name, start='2023-01-01', end='2025-12-31', initial_cash=100000)
        if res:
            all_results[f'{name}({code})'] = res
        time.sleep(0.3)

    # ---- 汇总 ----
    print('\n' + '='*68)
    print('  🏆 A股 MA+MACD 策略汇总（2023-2025）')
    print('='*68)
    print(f'  {"股票":<18} {"MA+MACD":>10} {"纯双均线":>10} {"买入持有":>10} {"最优":>12}')
    print(f'  {"-"*58}')
    for name, r in all_results.items():
        best = max(r, key=lambda k: r[k]['return'])
        print(f'  {name:<18} {r["MA+MACD"]["return"]:>+8.2f}%  '
              f'{r["纯双均线"]["return"]:>+8.2f}%  '
              f'{r["买入持有"]["return"]:>+8.2f}%   {best:>10}')
    print('='*68)

    avg_macd = np.mean([r['MA+MACD']['return'] for r in all_results.values()])
    avg_ma   = np.mean([r['纯双均线']['return'] for r in all_results.values()])
    avg_bh   = np.mean([r['买入持有']['return'] for r in all_results.values()])
    print(f'\n  📊 平均收益：')
    print(f'     MA+MACD={avg_macd:+.2f}%  |  纯双均线={avg_ma:+.2f}%  |  买入持有={avg_bh:+.2f}%')
    print('\n✅ 完成！')
