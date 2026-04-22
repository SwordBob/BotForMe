#!/usr/bin/env python3
"""
趋势线止损策略（均线止损）
========================================
入场后以20日均线作为动态止损线：
  - 持仓期间，价格从未收盘跌破20日均线 → 持有
  - 收盘价跌破20日均线 → 立即止损/止盈离场

配合双均线入场信号：
  - 买入：MA5 上穿 MA20（金叉）
  - 卖出：MA5 下穿 MA20（死叉）或 收盘跌破20日均线（止损）

对比三种卖出方式：
  1. 纯MA死叉（传统）
  2. MA死叉 + 收盘跌破20日均线（保守）
  3. 收盘跌破20日均线即卖（激进趋势跟踪）
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
# 策略1：纯MA死叉（传统）
# ============================================================
class 纯MA死叉(bt.Strategy):
    """MA5/MA20金叉买，死叉卖——最经典的趋势跟踪"""
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
# 策略2：MA死叉 + 跌破20日均线止损（保守）
# ============================================================
class MA死叉均线止损(bt.Strategy):
    """
    双保险离场：
    - 正常：MA死叉卖出
    - 保险：收盘价跌破20日均线，立即止损（哪怕还没死叉）
    目的：在大跌时保住更多利润
    """
    params = (('sma_short', 5), ('sma_long', 20), ('sma_stop', 20))
    def __init__(self):
        sma1 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_short)
        sma2 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_long)
        self.sma20 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_stop)
        self.cross = bt.indicators.CrossOver(sma1, sma2)
        self.order = None
        self.trades = []
        self.entry_price = 0
        self.stop_reason = ''
    def next(self):
        if self.order: return
        close = self.datas[0].close[0]
        sma20_val = self.sma20[0]
        cross_val = self.cross[0]
        # 止损：收盘跌破20日均线（下跌趋势确认）
        if self.position and close < sma20_val:
            self.stop_reason = 'MA20止损'
            self.order = self.sell()
        elif cross_val > 0 and not self.position:
            self.stop_reason = '金叉入场'
            self.order = self.buy()
            self.entry_price = close
        elif cross_val < 0 and self.position:
            self.stop_reason = '死叉卖出'
            self.order = self.sell()
    def notify_order(self, order):
        if order.status == order.Completed:
            self.trades.append({
                'action': 'BUY' if order.isbuy() else 'SELL',
                'price': order.executed.price,
                'reason': self.stop_reason
            })
        self.order = None


# ============================================================
# 策略3：纯均线止损（激进趋势跟踪）
# ============================================================
class 纯均线止损(bt.Strategy):
    """
    纯趋势跟踪止损——没有死叉概念：
    - 买入：MA5 上穿 MA20（金叉）
    - 卖出：收盘价跌破20日均线（不管有没有死叉）

    逻辑：死叉太慢，等死叉确认时利润已经回吐很多。
    用20日均线止损能更早锁定利润。
    """
    params = (('sma_short', 5), ('sma_long', 20), ('sma_stop', 20))
    def __init__(self):
        sma1 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_short)
        sma2 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_long)
        self.sma20 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_stop)
        self.cross = bt.indicators.CrossOver(sma1, sma2)
        self.order = None
        self.trades = []
        self.entry_price = 0
        self.stop_reason = ''
    def next(self):
        if self.order: return
        close = self.datas[0].close[0]
        sma20_val = self.sma20[0]
        cross_val = self.cross[0]
        if not self.position:
            if cross_val > 0:  # 金叉买入
                self.stop_reason = '金叉入场'
                self.order = self.buy()
                self.entry_price = close
        else:
            if close < sma20_val:  # 跌破20日均线，无条件止损
                self.stop_reason = 'MA20止损离场'
                self.order = self.sell()
    def notify_order(self, order):
        if order.status == order.Completed:
            self.trades.append({
                'action': 'BUY' if order.isbuy() else 'SELL',
                'price': order.executed.price,
                'reason': self.stop_reason
            })
        self.order = None


# ============================================================
# 策略4：均线止损 + MA死叉双重确认（双重确认）
# ============================================================
class 均线止损双重确认(bt.Strategy):
    """
    最严格出场——需要两个条件同时满足才卖：
    - MA死叉 AND 收盘跌破20日均线

    避免在震荡行情中被来回打脸（假死叉），
    但代价是：真正大跌时反应更慢
    """
    params = (('sma_short', 5), ('sma_long', 20), ('sma_stop', 20))
    def __init__(self):
        sma1 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_short)
        sma2 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_long)
        self.sma20 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_stop)
        self.cross = bt.indicators.CrossOver(sma1, sma2)
        self.order = None
        self.trades = []
        self.stop_reason = ''
    def next(self):
        if self.order: return
        close = self.datas[0].close[0]
        sma20_val = self.sma20[0]
        cross_val = self.cross[0]
        if not self.position:
            if cross_val > 0:
                self.stop_reason = '金叉入场'
                self.order = self.buy()
        else:
            # 双重确认：死叉 AND 跌破MA20
            if cross_val < 0 and close < sma20_val:
                self.stop_reason = '双重复核卖出'
                self.order = self.sell()
    def notify_order(self, order):
        if order.status == order.Completed:
            self.trades.append({
                'action': 'BUY' if order.isbuy() else 'SELL',
                'price': order.executed.price,
                'reason': self.stop_reason
            })
        self.order = None


# ============================================================
# 买入持有
# ============================================================
class 买入持有(bt.Strategy):
    def __init__(self): self.order = None
    def next(self):
        if not self.position: self.order = self.buy()
    def notify_order(self, order): self.order = None


# ============================================================
# 回测运行器
# ============================================================
def 运行回测(ticker, name='', start='2023-01-01', end='2026-01-01', initial_cash=100000):

    stock_name = name or ticker
    df = 获取美股数据(ticker, start, end)
    if df is None:
        return None

    print(f'\n{"="*68}')
    print(f'  📈 {stock_name} ({ticker}) 趋势线止损策略对比')
    print(f'{"="*68}')
    print(f'  均线止损：收盘价 < MA20 即止损 | 初始资金：${initial_cash:,.0f}')
    print(f'{"="*68}\n')

    df_bt = df[['date', 'open', 'high', 'low', 'close', 'volume']].copy()
    df_bt.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
    df_bt['datetime'] = pd.to_datetime(df_bt['datetime'])

    results = {}

    strategies = [
        ('纯MA死叉',           纯MA死叉,           {}),
        ('MA死叉+均线止损',    MA死叉均线止损,      {}),
        ('纯均线止损',         纯均线止损,          {}),
        ('双重确认卖出',       均线止损双重确认,    {}),
    ]

    for name_str, strat_cls, strat_params in strategies:
        cerebro = bt.Cerebro()
        cerebro.addstrategy(strat_cls, **strat_params)
        cerebro.adddata(bt.feeds.PandasData(dataname=df_bt, datetime=0))
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=0.001)
        cerebro.addsizer(bt.sizers.AllInSizerInt)
        p = cerebro.run()
        fv = cerebro.broker.getvalue()
        ret = (fv - initial_cash) / initial_cash * 100
        trades_list = p[0].trades
        results[name_str] = {'final': fv, 'return': ret, 'trades': len(trades_list), 'log': trades_list}

    # 买入持有
    cerebro_bh = bt.Cerebro()
    cerebro_bh.addstrategy(买入持有)
    cerebro_bh.adddata(bt.feeds.PandasData(dataname=df_bt, datetime=0))
    cerebro_bh.broker.setcash(initial_cash)
    cerebro_bh.broker.setcommission(commission=0.001)
    cerebro_bh.run()
    fv_bh = cerebro_bh.broker.getvalue()
    ret_bh = (fv_bh - initial_cash) / initial_cash * 100
    results['买入持有'] = {'final': fv_bh, 'return': ret_bh, 'trades': 1}

    max_price = np.maximum.accumulate(df['close'].values)
    max_dd = ((df['close'].values - max_price) / max_price * 100).min()

    print(f'  📋 收益对比')
    print(f'  {"策略":<16} {"最终资金":>13} {"收益率":>10} {"交易次数":>8} {"vs基准":>10}')
    print(f'  {"-"*62}')
    for strat_name, r in results.items():
        alpha = r['return'] - ret_bh
        marker = '  ←NEW' if strat_name in ['纯均线止损', 'MA死叉+均线止损'] else ''
        money_str = "$" + f"{r['final']:,.0f}"
        print(f'  {strat_name:<16} {money_str:>13} {r["return"]:>+8.2f}%   {r["trades"]:>4}笔   {alpha:>+7.2f}%{marker}')
    print(f'{"="*68}')
    print(f'  📉 基准最大回撤：{max_dd:.2f}%')

    best = max(results, key=lambda k: results[k]['return'])
    winner = results[best]
    print(f'\n  🏆 最优：{best}  收益率：{winner["return"]:+.2f}%')

    # 均线止损专项对比
    ma_cross_return = results['纯MA死叉']['return']
    ma_stop_return  = results['MA死叉+均线止损']['return']
    pure_stop_return = results['纯均线止损']['return']

    if ma_cross_return != ma_stop_return:
        diff = ma_stop_return - ma_cross_return
        print(f'\n  🛡️ 均线止损效果（vs纯死叉）：{"+" if diff > 0 else ""}{diff:.2f}%')
        if diff > 0:
            print(f'     均线止损保住利润，在大跌时起作用！')
        else:
            print(f'     均线止损过于敏感，过早离场踏空')

    return results


# ============================================================
# 主程序
# ============================================================
if __name__ == '__main__':
    print('''
╔══════════════════════════════════════════════════════╗
║    🚀 趋势线止损策略 | 均线止损 vs 死叉对比         ║
║                                                  ║
║    策略1 纯MA死叉    ：死叉即卖（经典）           ║
║    策略2 MA死叉+均线  ：死叉卖 OR 跌破MA20卖      ║
║    策略3 纯均线止损   ：跌破MA20就卖（激进）      ║
║    策略4 双重确认卖出 ：死叉 AND 跌破MA20 才卖    ║
╚══════════════════════════════════════════════════════╝
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
        res = 运行回测(ticker, name, initial_cash=100000)
        if res:
            all_results[name] = res
        time.sleep(0.5)

    # ---- 汇总 ----
    print('\n' + '='*72)
    print('  🏆 所有标的汇总')
    print('='*72)
    header = f'  {"股票":<18} {"纯MA死叉":>9} {"+均线止损":>10} {"纯均线止":>9} {"双重确认":>9} {"买入持有":>9} {"最优":>12}'
    print(header)
    print(f'  {"-"*72}')
    for name, r in all_results.items():
        best = max(r, key=lambda k: r[k]['return'])
        try:
            ma_ret    = r['纯MA死叉']['return']
            stop_ret  = r['MA死叉+均线止损']['return']
            pure_ret  = r['纯均线止损']['return']
            both_ret  = r['双重确认卖出']['return']
            bh_ret    = r['买入持有']['return']
            print(f'  {name:<18} {ma_ret:>+7.2f}%  '
                  f'{stop_ret:>+8.2f}%  '
                  f'{pure_ret:>+7.2f}%  '
                  f'{both_ret:>+7.2f}%  '
                  f'{bh_ret:>+7.2f}%   {best:>10}')
        except KeyError:
            pass
    print('='*72)

    # 平均
    def avg_key(key):
        vals = [r[key]['return'] for r in all_results.values() if key in r]
        return np.mean(vals) if vals else 0

    avg_ma    = avg_key('纯MA死叉')
    avg_stop  = avg_key('MA死叉+均线止损')
    avg_pure  = avg_key('纯均线止损')
    avg_both  = avg_key('双重确认卖出')
    avg_bh    = avg_key('买入持有')
    print(f'\n  📊 平均收益：')
    print(f'     纯MA死叉={avg_ma:+.2f}%  |  +均线止损={avg_stop:+.2f}%  |  纯均线止损={avg_pure:+.2f}%')
    print(f'     双重确认={avg_both:+.2f}%  |  买入持有={avg_bh:+.2f}%')

    best_avg = max([('纯MA死叉', avg_ma), ('+均线止损', avg_stop),
                     ('纯均线止损', avg_pure), ('双重确认', avg_both)],
                    key=lambda x: x[1])
    print(f'\n  🏆 平均最优策略：{best_avg[0]} ({best_avg[1]:+.2f}%)')
    print('\n✅ 完成！可调整 MA 周期（默认5/20）或 MA止损周期（默认20）')
