#!/usr/bin/env python3
"""
双均线策略回测 - 美股真实数据
- 买入信号：MA5 上穿 MA20（金叉）
- 卖出信号：MA5 下穿 MA20（死叉）
- 数据来源：akshare → Yahoo Finance
"""

import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import akshare as ak
import backtrader as bt
import time


def 获取美股数据(ticker, start_date='2023-01-01', end_date='2026-01-01'):
    """获取美股历史数据，返回 DataFrame"""
    print(f'正在下载 {ticker} 历史数据...')
    try:
        df = ak.stock_us_daily(symbol=ticker)
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        df = df.sort_values('date').reset_index(drop=True)
        print(f'✅ 成功：{len(df)} 个交易日 ({df["date"].min()} ~ {df["date"].max()})')
        return df
    except Exception as e:
        print(f'❌ 出错：{e}')
        return None


class 双均线策略(bt.Strategy):
    params = (('sma_short', 5), ('sma_long', 20),)

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.trades_log = []
        sma1 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_short)
        sma2 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_long)
        self.crossover = bt.indicators.CrossOver(sma1, sma2)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status == order.Completed:
            if order.isbuy():
                self.trades_log.append({'action': 'BUY', 'price': order.executed.price})
            else:
                self.trades_log.append({'action': 'SELL', 'price': order.executed.price, 'pnl': order.executed.pnl})
        self.order = None

    def next(self):
        if self.order:
            return
        if self.crossover > 0 and not self.position:
            self.order = self.buy()
        elif self.crossover < 0 and self.position:
            self.order = self.sell()


class 买入持有(bt.Strategy):
    def __init__(self): pass
    def next(self):
        if not self.position:
            self.order = self.buy()


def 运行回测(ticker, name='',
             start='2023-01-01', end='2026-01-01',
             sma_short=5, sma_long=20,
             initial_cash=100000):

    stock_name = name or ticker
    df = 获取美股数据(ticker, start, end)
    if df is None:
        return None

    print(f'\n{"="*58}')
    print(f'  📈 {stock_name} ({ticker}) 双均线回测')
    print(f'{"="*58}')
    print(f'  参数：MA{sma_short} / MA{sma_long} | 初始资金：${initial_cash:,.0f}')
    print(f'  时间：{start} ~ {end}')
    print(f'{"="*58}\n')

    # backtrader 格式
    df_bt = df[['date', 'open', 'high', 'low', 'close', 'volume']].copy()
    df_bt.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
    df_bt['datetime'] = pd.to_datetime(df_bt['datetime'])

    results = {}

    # 双均线
    print('▶ 双均线策略回测...')
    cerebro1 = bt.Cerebro()
    cerebro1.addstrategy(双均线策略, sma_short=sma_short, sma_long=sma_long)
    cerebro1.adddata(bt.feeds.PandasData(dataname=df_bt, datetime=0))
    cerebro1.broker.setcash(initial_cash)
    cerebro1.broker.setcommission(commission=0.001)
    cerebro1.addsizer(bt.sizers.AllInSizerInt)
    p1 = cerebro1.run()
    fv1 = cerebro1.broker.getvalue()
    ret1 = (fv1 - initial_cash) / initial_cash * 100
    trades = len(p1[0].trades_log)
    print(f'  ✅ 资金：${fv1:,.2f} | 收益率：{ret1:+.2f}% | {trades}笔交易')

    # 买入持有
    print('▶ 买入持有基准...')
    cerebro2 = bt.Cerebro()
    cerebro2.addstrategy(买入持有)
    cerebro2.adddata(bt.feeds.PandasData(dataname=df_bt, datetime=0))
    cerebro2.broker.setcash(initial_cash)
    cerebro2.broker.setcommission(commission=0.001)
    cerebro2.run()
    fv2 = cerebro2.broker.getvalue()
    ret2 = (fv2 - initial_cash) / initial_cash * 100

    alpha = ret1 - ret2
    max_price = np.maximum.accumulate(df['close'].values)
    max_dd = ((df['close'].values - max_price) / max_price * 100).min()

    print(f'\n{"="*58}')
    print(f'  📋 收益对比')
    print(f'{"="*58}')
    print(f'  {"策略":<12} {"最终资金":>14} {"收益率":>10} {"vs基准":>10}')
    print(f'  {"-"*46}')
    print(f'  {"双均线":<12} {"$"+f"{fv1:,.0f}":>14} {ret1:>+8.2f}%  {alpha:>+7.2f}%')
    print(f'  {"买入持有":<12} {"$"+f"{fv2:,.0f}":>14} {ret2:>+8.2f}%  {"基准":>8}')
    print(f'{"="*58}')
    print(f'  📉 区间最大回撤：{max_dd:.2f}%')
    print(f'\n  {"✅ 双均线跑赢！" if alpha > 0 else "⚠️ 买入持有更优"}  超额收益：{alpha:+.2f}%')

    return {'双均线': ret1, '买入持有': ret2, 'alpha': alpha}


if __name__ == '__main__':
    print('''
╔══════════════════════════════════════════════╗
║     🚀 双均线量化策略 | 美股真实数据         ║
║     数据来源：akshare (Yahoo Finance)        ║
╚══════════════════════════════════════════════╝
''')

    测试列表 = [
        ('AAPL',  '苹果 Apple'),
        ('TSLA',  '特斯拉 Tesla'),
        ('NVDA',  '英伟达 NVIDIA'),
        ('MSFT',  '微软 Microsoft'),
        ('SPY',   '标普500 ETF'),
    ]

    print('可选标的：')
    for i, (c, n) in enumerate(测试列表, 1):
        print(f'  {i}. {c}  {n}')
    print()

    results_all = {}
    for ticker, name in 测试列表:
        res = 运行回测(ticker, name, sma_short=5, sma_long=20, initial_cash=100000)
        if res:
            results_all[name] = res
        time.sleep(1)  # 礼貌性延迟，避免请求过快

    print('\n' + '='*60)
    print('  🏆 所有标的汇总')
    print('='*60)
    print(f'  {"股票":<20} {"双均线收益":>12} {"买入持有":>12} {"超额收益":>10}')
    print(f'  {"-"*56}')
    for name, r in results_all.items():
        print(f'  {name:<20} {r["双均线"]:>+10.2f}%   {r["买入持有"]:>+10.2f}%   {r["alpha"]:>+8.2f}%')
    print('='*60)
    print('\n✅ 全部完成！')
