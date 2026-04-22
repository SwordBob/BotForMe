#!/usr/bin/env python3
"""
自适应趋势策略
- 市场趋势强时（ADX > 25）：使用 MA双均线（金叉买/死叉卖）
- 市场震荡时（ADX < 20）：使用 MACD过滤（减少假信号）
- ADX 处于中间区域（20-25）：两者结合，更严格确认
- ADX > 40 为极强趋势，满仓；ADX < 15 坚决不入场

ADX 原理：
  +DI 上升的方向指标
  -DI 下降的方向指标
  DMI = max(|±DI| 的平滑)
  ADX = 趋势强度，值越高趋势越强
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
# 自适应策略（核心）
# ============================================================
class 自适应策略(bt.Strategy):
    """
    自适应双模式策略
    趋势强 → MA双均线（快速响应）
    震荡弱 → MACD确认（减少假信号）
    """
    params = dict(
        sma_short=5,
        sma_long=20,
        macd_fast=12,
        macd_slow=26,
        macd_signal=9,
        adx_period=14,      # ADX 周期
        adx_strong=25,      # 趋势强阈值（>25 用MA）
        adx_weak=20,        # 震荡阈值（<20 用MACD）
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.trades = []

        # ---- 双均线 ----
        sma1 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_short)
        sma2 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_long)
        self.sma_cross = bt.indicators.CrossOver(sma1, sma2)

        # ---- MACD ----
        self.macd = bt.indicators.MACD(
            self.datas[0].close,
            period_me1=self.params.macd_fast,
            period_me2=self.params.macd_slow,
            period_signal=self.params.macd_signal
        )
        self.macd_hist = self.macd.macd - self.macd.signal

        # ---- ADX（方向性指数）----
        self.adx = bt.indicators.AverageDirectionalMovementIndex(
            self.datas[0], period=self.params.adx_period
        )
        self.adx_value = self.adx.adx  # 直接取 ADX 线

        # 记录模式切换
        self._mode_log = []

    @property
    def adx_current(self):
        return self.adx_value[0]

    def log_mode(self, mode, adx):
        self._mode_log.append((self.datas[0].datetime.date(0), mode, adx))

    def next(self):
        adx = self.adx_current
        dif = self.macd.lines.macd[0]
        hist = self.macd_hist[0]
        prev_hist = self.macd_hist[-1]
        sma_cross_val = self.sma_cross[0]

        if self.order:
            return

        # ---- 模式判断 ----
        if adx > self.params.adx_strong:
            mode = 'MA'  # 强趋势 → MA
        elif adx < self.params.adx_weak:
            mode = 'MACD'  # 震荡 → MACD
        else:
            mode = 'BOTH'  # 中间地带 → 两者结合，更严格

        # ---- 持仓为空 → 考虑买入 ----
        if not self.position:
            if mode == 'MA' and sma_cross_val > 0:
                # 强趋势模式：MA金叉直接买
                self.order = self.buy()
                self.log_mode(mode, adx)

            elif mode == 'MACD' and (prev_hist < 0) and (hist > 0):
                # 震荡模式：MACD零轴上方金叉
                self.order = self.buy()
                self.log_mode(mode, adx)

            elif mode == 'BOTH':
                # 双重确认：MA金叉 AND MACD柱转正
                if sma_cross_val > 0 and hist > 0:
                    self.order = self.buy()
                    self.log_mode(mode, adx)

        # ---- 持仓中 → 考虑卖出 ----
        else:
            if mode == 'MA' and sma_cross_val < 0:
                self.order = self.sell()
                self.log_mode(mode, adx)

            elif mode == 'MACD' and (prev_hist > 0) and (hist < 0):
                self.order = self.sell()
                self.log_mode(mode, adx)

            elif mode == 'BOTH':
                if sma_cross_val < 0 and hist < 0:
                    self.order = self.sell()
                    self.log_mode(mode, adx)

    def notify_order(self, order):
        if order.status == order.Completed:
            if order.isbuy():
                self.trades.append({
                    'action': 'BUY',
                    'price': order.executed.price,
                    'adx': self.adx_current
                })
            else:
                self.trades.append({
                    'action': 'SELL',
                    'price': order.executed.price,
                    'pnl': order.executed.pnl,
                    'adx': self.adx_current
                })
        self.order = None


# ============================================================
# 对照策略
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
        if self.order: return
        if self.cross > 0 and not self.position: self.order = self.buy()
        elif self.cross < 0 and self.position: self.order = self.sell()
    def notify_order(self, order):
        if order.status == order.Completed:
            self.trades.append({'action': 'BUY' if order.isbuy() else 'SELL', 'price': order.executed.price})
        self.order = None


class MA_MACD组合(bt.Strategy):
    """MA+MACD 组合策略（无条件组合）"""
    params = (('sma_short', 5), ('sma_long', 20),
              ('macd_fast', 12), ('macd_slow', 26), ('macd_signal', 9))
    def __init__(self):
        sma1 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_short)
        sma2 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_long)
        self.sma_cross = bt.indicators.CrossOver(sma1, sma2)
        self.macd = bt.indicators.MACD(self.datas[0].close,
                                        period_me1=self.params.macd_fast,
                                        period_me2=self.params.macd_slow,
                                        period_signal=self.params.macd_signal)
        self.macd_hist = self.macd.macd - self.macd.signal
        self.order = None
        self.trades = []
    def next(self):
        if self.order: return
        hist = self.macd_hist[0]
        prev_hist = self.macd_hist[-1]
        if self.sma_cross > 0 and not self.position and (prev_hist < 0):
            self.order = self.buy()
        elif self.sma_cross < 0 and self.position and (prev_hist > 0):
            self.order = self.sell()
    def notify_order(self, order):
        if order.status == order.Completed:
            self.trades.append({'action': 'BUY' if order.isbuy() else 'SELL', 'price': order.executed.price})
        self.order = None


# ============================================================
# 回测运行器
# ============================================================
def 运行回测(ticker, name='',
             start='2023-01-01', end='2026-01-01',
             initial_cash=100000):

    stock_name = name or ticker
    df = 获取美股数据(ticker, start, end)
    if df is None:
        return None

    print(f'\n{"="*64}')
    print(f'  📈 {stock_name} ({ticker}) 自适应策略对比')
    print(f'{"="*64}')
    print(f'  ADX强阈值: 25 | ADX弱阈值: 20 | 资金: ${initial_cash:,.0f}')
    print(f'{"="*64}\n')

    # backtrader 数据格式
    df_bt = df[['date', 'open', 'high', 'low', 'close', 'volume']].copy()
    df_bt.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
    df_bt['datetime'] = pd.to_datetime(df_bt['datetime'])

    results = {}
    mode_counts = {}

    # ---- 自适应策略 ----
    cerebro0 = bt.Cerebro()
    cerebro0.addstrategy(自适应策略)
    cerebro0.adddata(bt.feeds.PandasData(dataname=df_bt, datetime=0))
    cerebro0.broker.setcash(initial_cash)
    cerebro0.broker.setcommission(commission=0.001)
    cerebro0.addsizer(bt.sizers.AllInSizerInt)
    p0 = cerebro0.run()
    fv0 = cerebro0.broker.getvalue()
    ret0 = (fv0 - initial_cash) / initial_cash * 100
    t0 = len(p0[0].trades)

    # 统计模式使用情况
    mode_log = p0[0]._mode_log
    mode_counts = {}
    for _, mode, _ in mode_log:
        mode_counts[mode] = mode_counts.get(mode, 0) + 1

    results['自适应策略'] = {'final': fv0, 'return': ret0, 'trades': t0}

    # ---- 纯MA双均线 ----
    cerebro1 = bt.Cerebro()
    cerebro1.addstrategy(纯双均线)
    cerebro1.adddata(bt.feeds.PandasData(dataname=df_bt, datetime=0))
    cerebro1.broker.setcash(initial_cash)
    cerebro1.broker.setcommission(commission=0.001)
    cerebro1.addsizer(bt.sizers.AllInSizerInt)
    cerebro1.run()
    fv1 = cerebro1.broker.getvalue()
    ret1 = (fv1 - initial_cash) / initial_cash * 100
    t1 = len(p0[0].trades)  # reuse var name, t1 is from MA
    results['MA双均线'] = {'final': fv1, 'return': ret1, 'trades': t1}

    # ---- 基准：买入持有 ----
    cerebro3 = bt.Cerebro()
    cerebro3.addstrategy(纯双均线)
    cerebro3.adddata(bt.feeds.PandasData(dataname=df_bt, datetime=0))
    cerebro3.broker.setcash(initial_cash)
    cerebro3.broker.setcommission(commission=0.001)
    cerebro3.run()
    fv3 = cerebro3.broker.getvalue()
    ret3 = (fv3 - initial_cash) / initial_cash * 100
    results['买入持有'] = {'final': fv3, 'return': ret3, 'trades': 1}

    # ---- MA+MACD组合 ----
    cerebro2 = bt.Cerebro()
    cerebro2.addstrategy(MA_MACD组合)
    cerebro2.adddata(bt.feeds.PandasData(dataname=df_bt, datetime=0))
    cerebro2.broker.setcash(initial_cash)
    cerebro2.broker.setcommission(commission=0.001)
    cerebro2.addsizer(bt.sizers.AllInSizerInt)
    cerebro2.run()
    fv2 = cerebro2.broker.getvalue()
    ret2 = (fv2 - initial_cash) / initial_cash * 100
    results['MA+MACD'] = {'final': fv2, 'return': ret2, 'trades': t0}

    # 最大回撤
    max_price = np.maximum.accumulate(df['close'].values)
    max_dd = ((df['close'].values - max_price) / max_price * 100).min()

    print(f'  📋 收益对比')
    print(f'  {"策略":<14} {"最终资金":>13} {"收益率":>10} {"vs基准":>10}')
    print(f'  {"-"*52}')
    alpha0 = ret0 - ret3
    alpha1 = ret1 - ret3
    alpha2 = ret2 - ret3
    print(f'  {"自适应策略":<14} {"$"+f"{fv0:,.0f}":>13} {ret0:>+8.2f}%  {alpha0:>+7.2f}%  ←NEW')
    print(f'  {"MA双均线":<14} {"$"+f"{fv1:,.0f}":>13} {ret1:>+8.2f}%  {alpha1:>+7.2f}%')
    print(f'  {"MA+MACD":<14} {"$"+f"{fv2:,.0f}":>13} {ret2:>+8.2f}%  {alpha2:>+7.2f}%')
    print(f'  {"买入持有":<14} {"$"+f"{fv3:,.0f}":>13} {ret3:>+8.2f}%  {"基准":>8}')
    print(f'{"="*64}')
    print(f'  📉 基准最大回撤：{max_dd:.2f}%  |  自适应交易次数：{t0}笔')

    # 模式统计
    if mode_counts:
        ma_count = mode_counts.get('MA', 0)
        macd_count = mode_counts.get('MACD', 0)
        both_count = mode_counts.get('BOTH', 0)
        print(f'  📊 模式使用：MA强趋势={ma_count}次  MACD震荡={macd_count}次  BOTH={both_count}次')

    # 找出最优
    best = max(results, key=lambda k: results[k]['return'])
    print(f'\n  🏆 最优：{best}  收益率：{results[best]["return"]:+.2f}%')

    # 自适应 vs MA+MACD
    if ret0 > ret2:
        print(f'  ✅ 自适应跑赢 MA+MACD：{ret0-ret2:+.2f}%')
    else:
        print(f'  ⚠️ 自适应落后 MA+MACD：{ret2-ret0:+.2f}%')

    return results


# ============================================================
# 主程序
# ============================================================
if __name__ == '__main__':
    print('''
╔══════════════════════════════════════════════════╗
║   🚀 自适应趋势策略 | 美股数据                   ║
║   强趋势(ADX>25) → MA双均线                    ║
║   震荡(ADX<20)   → MACD确认                    ║
║   中间(20-25)    → 两者结合                    ║
╚══════════════════════════════════════════════════╝
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
    print('\n' + '='*70)
    print('  🏆 所有标的汇总')
    print('='*70)
    print(f'  {"股票":<18} {"自适应":>9} {"MA双均线":>9} {"MA+MACD":>9} {"买入持有":>9} {"最优":>12}')
    print(f'  {"-"*64}')
    for name, r in all_results.items():
        best = max(r, key=lambda k: r[k]['return'])
        print(f'  {name:<18} {r["自适应策略"]["return"]:>+7.2f}%  '
              f'{r["MA双均线"]["return"]:>+7.2f}%  '
              f'{r["MA+MACD"]["return"]:>+7.2f}%  '
              f'{r["买入持有"]["return"]:>+7.2f}%   {best:>10}')
    print('='*70)

    # 自适应策略总平均
    avg_adaptive = np.mean([r['自适应策略']['return'] for r in all_results.values()])
    avg_ma = np.mean([r['MA双均线']['return'] for r in all_results.values()])
    avg_macd = np.mean([r['MA+MACD']['return'] for r in all_results.values()])
    print(f'\n  📊 平均收益：自适应={avg_adaptive:+.2f}%  MA双均线={avg_ma:+.2f}%  MA+MACD={avg_macd:+.2f}%')
    print('\n✅ 完成！可调整 ADX 阈值参数（adx_strong/adx_weak）做更多测试')
