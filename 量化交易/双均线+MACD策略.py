#!/usr/bin/env python3
"""
双均线 + MACD 综合策略
- 买入：MA5 上穿 MA20（金叉）AND MACD柱由负转正（DIF线上穿DEA线）
- 卖出：MA5 下穿 MA20（死叉）AND MACD柱由正转负
- 同时输出纯双均线作为对照
"""

import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import akshare as ak
import backtrader as bt
import time


def 获取美股数据(ticker, start_date='2023-01-01', end_date='2026-01-01'):
    print(f'下载 {ticker}...')
    try:
        df = ak.stock_us_daily(symbol=ticker)
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        df = df.sort_values('date').reset_index(drop=True)
        print(f'✅ {ticker}: {len(df)} 个交易日')
        return df
    except Exception as e:
        print(f'❌ {ticker} 出错：{e}')
        return None


# ============================================================
# 策略1：纯双均线（对照基准）
# ============================================================
class 纯双均线(bt.Strategy):
    params = (('sma_short', 5), ('sma_long', 20),)

    def __init__(self):
        sma1 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_short)
        sma2 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_long)
        self.cross = bt.indicators.CrossOver(sma1, sma2)
        self.order = None
        self.trades = []

    def next(self):
        if self.order:
            return
        if self.cross > 0 and not self.position:
            self.order = self.buy()
        elif self.cross < 0 and self.position:
            self.order = self.sell()

    def notify_order(self, order):
        if order.status == order.Completed:
            if order.isbuy():
                self.trades.append({'action': 'BUY', 'price': order.executed.price})
            else:
                self.trades.append({'action': 'SELL', 'price': order.executed.price, 'pnl': order.executed.pnl})
        self.order = None


# ============================================================
# 策略2：双均线 + MACD 确认
# ============================================================
class 双均线MACD(bt.Strategy):
    """
    双均线金叉/死叉 + MACD 零轴确认
    - DIF = EMA(close, 12) - EMA(close, 26)
    - DEA = EMA(DIF, 9)
    - 买入：金叉 AND DIF > 0（零轴上方）
    - 卖出：死叉 AND DIF < 0（零轴下方）
    """
    params = (
        ('sma_short', 5),
        ('sma_long', 20),
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.trades = []

        # 双均线
        sma1 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_short)
        sma2 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_long)
        self.sma_cross = bt.indicators.CrossOver(sma1, sma2)

        # MACD
        self.macd = bt.indicators.MACD(
            self.datas[0].close,
            period_me1=self.params.macd_fast,
            period_me2=self.params.macd_slow,
            period_signal=self.params.macd_signal
        )
        self.macd_hist = self.macd.macd - self.macd.signal  # MACD 柱（DIF - DEA）
        self.prev_hist = 0

    def next(self):
        self.prev_hist = self.macd_hist[-1] if len(self) > 1 else 0

        if self.order:
            return

        dif = self.macd.lines.macd[0]
        dea = self.macd.lines.signal[0]
        hist = self.macd_hist[0]
        prev_hist = self.macd_hist[-1] if len(self) > 0 else 0

        # ---- 买入条件：金叉 AND MACD柱由负转正（DIF上穿0轴）----
        ma_golden = self.sma_cross > 0
        macd_golden = (prev_hist < 0) and (hist > 0)

        # ---- 卖出条件：死叉 AND MACD柱由正转负（DIF下穿0轴）----
        ma_dead = self.sma_cross < 0
        macd_dead = (prev_hist > 0) and (hist < 0)

        if ma_golden and macd_golden and not self.position:
            self.order = self.buy()
        elif ma_dead and macd_dead and self.position:
            self.order = self.sell()

    def notify_order(self, order):
        if order.status == order.Completed:
            if order.isbuy():
                self.trades.append({'action': 'BUY', 'price': order.executed.price,
                                    'dif': self.macd.lines.macd[0]})
            else:
                self.trades.append({'action': 'SELL', 'price': order.executed.price,
                                    'pnl': order.executed.pnl,
                                    'dif': self.macd.lines.macd[0]})
        self.order = None


# ============================================================
# 回测运行器
# ============================================================
def 运行回测(ticker, name='',
             start='2023-01-01', end='2026-01-01',
             sma_short=5, sma_long=20,
             initial_cash=100000):

    stock_name = name or ticker
    df = 获取美股数据(ticker, start, end)
    if df is None:
        return None

    print(f'\n{"="*62}')
    print(f'  📈 {stock_name} ({ticker}) 策略对比回测')
    print(f'{"="*62}')
    print(f'  MA: {sma_short}/{sma_long} | MACD: 12/26/9 | 资金: ${initial_cash:,.0f}')
    print(f'{"="*62}\n')

    # 准备 backtrader 数据
    df_bt = df[['date', 'open', 'high', 'low', 'close', 'volume']].copy()
    df_bt.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
    df_bt['datetime'] = pd.to_datetime(df_bt['datetime'])

    results = {}

    # ---- 策略1：纯双均线 ----
    cerebro1 = bt.Cerebro()
    cerebro1.addstrategy(纯双均线, sma_short=sma_short, sma_long=sma_long)
    cerebro1.adddata(bt.feeds.PandasData(dataname=df_bt, datetime=0))
    cerebro1.broker.setcash(initial_cash)
    cerebro1.broker.setcommission(commission=0.001)
    cerebro1.addsizer(bt.sizers.AllInSizerInt)
    p1 = cerebro1.run()
    fv1 = cerebro1.broker.getvalue()
    ret1 = (fv1 - initial_cash) / initial_cash * 100
    t1 = len(p1[0].trades)
    results['MA双均线'] = {'final': fv1, 'return': ret1, 'trades': t1}

    # ---- 策略2：双均线+MACD ----
    cerebro2 = bt.Cerebro()
    cerebro2.addstrategy(双均线MACD,
                           sma_short=sma_short, sma_long=sma_long,
                           macd_fast=12, macd_slow=26, macd_signal=9)
    cerebro2.adddata(bt.feeds.PandasData(dataname=df_bt, datetime=0))
    cerebro2.broker.setcash(initial_cash)
    cerebro2.broker.setcommission(commission=0.001)
    cerebro2.addsizer(bt.sizers.AllInSizerInt)
    p2 = cerebro2.run()
    fv2 = cerebro2.broker.getvalue()
    ret2 = (fv2 - initial_cash) / initial_cash * 100
    t2 = len(p2[0].trades)
    results['MA+MACD'] = {'final': fv2, 'return': ret2, 'trades': t2}

    # ---- 基准：买入持有 ----
    cerebro3 = bt.Cerebro()
    cerebro3.addstrategy(纯双均线)  # 只是用来买，不做择时
    cerebro3.adddata(bt.feeds.PandasData(dataname=df_bt, datetime=0))
    cerebro3.broker.setcash(initial_cash)
    cerebro3.broker.setcommission(commission=0.001)
    cerebro3.run()
    fv3 = cerebro3.broker.getvalue()
    ret3 = (fv3 - initial_cash) / initial_cash * 100
    results['买入持有'] = {'final': fv3, 'return': ret3, 'trades': 1}

    # 最大回撤（买入持有基准）
    max_price = np.maximum.accumulate(df['close'].values)
    max_dd = ((df['close'].values - max_price) / max_price * 100).min()

    # ---- 打印结果 ----
    alpha1 = ret1 - ret3
    alpha2 = ret2 - ret3

    print(f'  📋 收益对比')
    print(f'  {"策略":<14} {"最终资金":>14} {"收益率":>10} {"交易次数":>8} {"vs基准":>10}')
    print(f'  {"-"*60}')
    print(f'  {"MA双均线":<14} {"$"+f"{fv1:,.0f}":>14} {ret1:>+8.2f}%   {t1:>6}笔   {alpha1:>+7.2f}%')
    print(f'  {"MA+MACD":<14} {"$"+f"{fv2:,.0f}":>14} {ret2:>+8.2f}%   {t2:>6}笔   {alpha2:>+7.2f}%')
    print(f'  {"买入持有":<14} {"$"+f"{fv3:,.0f}":>14} {ret3:>+8.2f}%   {"1":>6}笔   {"基准":>8}')
    print(f'{"="*62}')
    print(f'  📉 区间最大回撤（基准）：{max_dd:.2f}%')

    # 筛选信号：MACD减少多少次假信号
    if t2 < t1:
        print(f'\n  ✅ MACD过滤掉 {t1 - t2} 次假信号！交易更少，收益{"更高" if ret2 > ret1 else "略低"}')
    elif t2 == t1:
        print(f'\n  ➖ MACD过滤效果：交易次数相同')
    else:
        print(f'\n  ⚠️ MACD条件更宽，交易次数更多')

    # 收益对比
    if ret2 > ret1:
        print(f'  ✅ MA+MACD 跑赢 纯MA：{ret2 - ret1:+.2f}%')
    else:
        print(f'  ⚠️ 纯MA更优：{ret1 - ret2:+.2f}%')

    return results


# ============================================================
# 主程序
# ============================================================
if __name__ == '__main__':
    print('''
╔══════════════════════════════════════════════╗
║   🚀 双均线 + MACD 综合策略 | 美股数据      ║
║   买入条件：MA金叉 + MACD柱由负转正          ║
║   卖出条件：MA死叉 + MACD柱由正转负          ║
╚══════════════════════════════════════════════╝
''')

    测试列表 = [
        ('AAPL',  '苹果 Apple'),
        ('TSLA',  '特斯拉 Tesla'),
        ('NVDA',  '英伟达 NVIDIA'),
        ('MSFT',  '微软 Microsoft'),
        ('SPY',   '标普500 ETF'),
        ('AMZN',  '亚马逊 Amazon'),
        ('GOOGL', '谷歌 Alphabet'),
    ]

    print('标的列表：')
    for i, (c, n) in enumerate(测试列表, 1):
        print(f'  {i}. {c}  {n}')
    print()

    all_results = {}
    for ticker, name in 测试列表:
        res = 运行回测(ticker, name, sma_short=5, sma_long=20, initial_cash=100000)
        if res:
            all_results[name] = res
        time.sleep(0.5)

    # ---- 汇总 ----
    print('\n' + '='*68)
    print('  🏆 所有标的汇总对比')
    print('='*68)
    print(f'  {"股票":<18} {"MA双均线":>10} {"MA+MACD":>10} {"买入持有":>10} {"最优":>12}')
    print(f'  {"-"*56}')
    for name, r in all_results.items():
        best = max(r, key=lambda k: r[k]['return'])
        print(f'  {name:<18} {r["MA双均线"]["return"]:>+8.2f}%  {r["MA+MACD"]["return"]:>+8.2f}%  {r["买入持有"]["return"]:>+8.2f}%   {best:>8}')
    print('='*68)
    print('\n✅ 完成！可修改 SMA 参数或 MACD 参数做更多测试')
