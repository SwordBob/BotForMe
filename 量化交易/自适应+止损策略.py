#!/usr/bin/env python3
"""
自适应 + ATR动态止损策略
========================================
在自适应策略基础上加入 ATR 止损/止盈：

入场后设置动态止损：
  - 初始止损：入场价 - 2×ATR
  - 跟踪止损：最高价回落 3×ATR 止损
  - 止盈：涨幅 > 6×ATR 且 ADX 持续走弱

同时记录每笔交易是哪个模式（MA/MACD/BOTH）触发的
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
# 自适应 + ATR 止损（核心）
# ============================================================
class 自适应ATR止损(bt.Strategy):
    """
    自适应策略 + ATR 动态止损/止盈
    - ATR周期：14（标准）
    - 初始止损：入场价 - 2×ATR
    - 跟踪止损：最高价回落 3×ATR
    - 止盈：涨幅 > 6×ATR 且 ADX < 20（趋势减弱）
    """
    params = dict(
        sma_short=5,
        sma_long=20,
        macd_fast=12,
        macd_slow=26,
        macd_signal=9,
        adx_period=14,
        adx_strong=25,   # 强趋势用MA
        adx_weak=20,     # 震荡用MACD
        atr_period=14,   # ATR周期
        atr_stop=2.0,    # 初始止损 ATR倍数
        atr_trail=3.0,   # 跟踪止损 ATR倍数
        atr_target=6.0,  # 止盈 ATR倍数
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.trades = []
        self.mode = None  # 'MA', 'MACD', 'BOTH'

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
        self.macd_hist = self.macd.macd - self.macd.signal

        # ADX
        self.adx = bt.indicators.AverageDirectionalMovementIndex(
            self.datas[0], period=self.params.adx_period
        )
        self.adx_value = self.adx.adx

        # ATR
        self.atr = bt.indicators.AverageTrueRange(
            self.datas[0], period=self.params.atr_period
        )

        # 持仓状态
        self.entry_price = 0
        self.highest_since_entry = 0
        self._mode_log = []

    @property
    def adx_current(self):
        return self.adx_value[0]

    def log_trade(self, action, price, mode, reason=''):
        self.trades.append({
            'action': action,
            'price': price,
            'mode': mode,
            'reason': reason,
            'adx': self.adx_current,
            'atr': self.atr[0],
        })

    def try_buy(self, mode):
        """尝试买入（mode: MA/MACD/BOTH）"""
        adx = self.adx_current
        dif = self.macd.lines.macd[0]
        hist = self.macd_hist[0]
        prev_hist = self.macd_hist[-1]
        sma_cross_val = self.sma_cross[0]

        if self.position:
            return

        if mode == 'MA' and sma_cross_val > 0:
            self.order = self.buy()
            self.entry_price = self.dataclose[0]
            self.highest_since_entry = self.entry_price
            self.mode = mode
            self.log_trade('BUY', self.entry_price, mode, 'MA金叉')

        elif mode == 'MACD' and (prev_hist < 0) and (hist > 0):
            self.order = self.buy()
            self.entry_price = self.dataclose[0]
            self.highest_since_entry = self.entry_price
            self.mode = mode
            self.log_trade('BUY', self.entry_price, mode, 'MACD零轴上穿')

        elif mode == 'BOTH' and sma_cross_val > 0 and hist > 0:
            self.order = self.buy()
            self.entry_price = self.dataclose[0]
            self.highest_since_entry = self.entry_price
            self.mode = mode
            self.log_trade('BUY', self.entry_price, mode, 'MA金叉+MACD确认')

    def try_sell(self, mode):
        """尝试卖出/止损（mode: MA/MACD/BOTH）"""
        if not self.position:
            return False

        adx = self.adx_current
        dif = self.macd.lines.macd[0]
        hist = self.macd_hist[0]
        prev_hist = self.macd_hist[-1]
        sma_cross_val = self.sma_cross[0]
        current_price = self.dataclose[0]
        atr = self.atr[0]

        # ---- 更新最高价 ----
        if current_price > self.highest_since_entry:
            self.highest_since_entry = current_price

        # ---- 止损检查 ----
        # 1. 固定止损：跌破入场价 - 2×ATR
        stop_price = self.entry_price - self.params.atr_stop * atr
        if current_price < stop_price:
            self.order = self.sell()
            self.log_trade('SELL', current_price, self.mode, f'止损-{self.params.atr_stop}ATR')
            self.mode = None
            return True

        # 2. 跟踪止损：最高价回落 3×ATR
        trail_stop = self.highest_since_entry - self.params.atr_trail * atr
        if current_price < trail_stop and self.highest_since_entry > self.entry_price * 1.05:
            self.order = self.sell()
            self.log_trade('SELL', current_price, self.mode, f'跟踪止损-{self.params.atr_trail}ATR')
            self.mode = None
            return True

        # 3. 止盈：涨幅 > 6×ATR 且 ADX < 20（趋势衰竭）
        target_price = self.entry_price + self.params.atr_target * atr
        if adx < 20 and current_price >= target_price:
            self.order = self.sell()
            self.log_trade('SELL', current_price, self.mode, f'止盈-{self.params.atr_target}ATR+ADX<20')
            self.mode = None
            return True

        # ---- 常规卖出信号 ----
        sold = False
        if mode == 'MA' and sma_cross_val < 0:
            self.order = self.sell()
            self.log_trade('SELL', current_price, self.mode, 'MA死叉')
            sold = True
        elif mode == 'MACD' and (prev_hist > 0) and (hist < 0):
            self.order = self.sell()
            self.log_trade('SELL', current_price, self.mode, 'MACD零轴下穿')
            sold = True
        elif mode == 'BOTH' and sma_cross_val < 0 and hist < 0:
            self.order = self.sell()
            self.log_trade('SELL', current_price, self.mode, 'MA死叉+MACD确认')
            sold = True

        if sold:
            self.mode = None
            return True

        return False

    def next(self):
        if self.order:
            return

        adx = self.adx_current

        # 模式判断
        if adx > self.params.adx_strong:
            mode = 'MA'
        elif adx < self.params.adx_weak:
            mode = 'MACD'
        else:
            mode = 'BOTH'

        if not self.position:
            self.try_buy(mode)
        else:
            self.try_sell(mode)

    def notify_order(self, order):
        if order.status == order.Completed:
            pass  # 日志在 try_buy/try_sell 中记录了
        self.order = None


# ============================================================
# 对照：纯自适应（无止损）
# ============================================================
class 纯自适应(bt.Strategy):
    params = dict(
        sma_short=5, sma_long=20,
        macd_fast=12, macd_slow=26, macd_signal=9,
        adx_period=14, adx_strong=25, adx_weak=20,
    )
    def __init__(self):
        self.order = None
        self.trades = []
        sma1 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_short)
        sma2 = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_long)
        self.sma_cross = bt.indicators.CrossOver(sma1, sma2)
        self.macd = bt.indicators.MACD(self.datas[0].close,
                                        period_me1=self.params.macd_fast,
                                        period_me2=self.params.macd_slow,
                                        period_signal=self.params.macd_signal)
        self.macd_hist = self.macd.macd - self.macd.signal
        self.adx = bt.indicators.AverageDirectionalMovementIndex(self.datas[0], period=self.params.adx_period)
    def next(self):
        if self.order: return
        adx = self.adx.adx[0]
        hist = self.macd_hist[0]
        prev_hist = self.macd_hist[-1]
        cross = self.sma_cross[0]
        mode = 'MA' if adx > self.params.adx_strong else ('MACD' if adx < self.params.adx_weak else 'BOTH')
        if not self.position:
            if mode == 'MA' and cross > 0: self.order = self.buy()
            elif mode == 'MACD' and prev_hist < 0 and hist > 0: self.order = self.buy()
            elif mode == 'BOTH' and cross > 0 and hist > 0: self.order = self.buy()
        else:
            if mode == 'MA' and cross < 0: self.order = self.sell()
            elif mode == 'MACD' and prev_hist > 0 and hist < 0: self.order = self.sell()
            elif mode == 'BOTH' and cross < 0 and hist < 0: self.order = self.sell()
    def notify_order(self, order):
        if order.status == order.Completed:
            self.trades.append({'action': 'BUY' if order.isbuy() else 'SELL', 'price': order.executed.price})
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

    print(f'\n{"="*66}')
    print(f'  📈 {stock_name} ({ticker}) 自适应+ATR止损 策略对比')
    print(f'{"="*66}')
    print(f'  ATR止损: -2.0ATR | 跟踪: -3.0ATR | 止盈: +6.0ATR+ADX<20')
    print(f'  ADX强>25:MA | 弱<20:MACD | 中间:BOTH')
    print(f'{"="*66}\n')

    df_bt = df[['date', 'open', 'high', 'low', 'close', 'volume']].copy()
    df_bt.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
    df_bt['datetime'] = pd.to_datetime(df_bt['datetime'])

    results = {}

    # 1. 自适应+ATR止损
    cerebro0 = bt.Cerebro()
    cerebro0.addstrategy(自适应ATR止损)
    cerebro0.adddata(bt.feeds.PandasData(dataname=df_bt, datetime=0))
    cerebro0.broker.setcash(initial_cash)
    cerebro0.broker.setcommission(commission=0.001)
    cerebro0.addsizer(bt.sizers.AllInSizerInt)
    p0 = cerebro0.run()
    fv0 = cerebro0.broker.getvalue()
    ret0 = (fv0 - initial_cash) / initial_cash * 100
    trades0 = p0[0].trades
    results['自适应+ATR'] = {'final': fv0, 'return': ret0, 'trades': len(trades0), 'trade_log': trades0}

    # 2. 纯自适应（对照）
    cerebro1 = bt.Cerebro()
    cerebro1.addstrategy(纯自适应)
    cerebro1.adddata(bt.feeds.PandasData(dataname=df_bt, datetime=0))
    cerebro1.broker.setcash(initial_cash)
    cerebro1.broker.setcommission(commission=0.001)
    cerebro1.addsizer(bt.sizers.AllInSizerInt)
    cerebro1.run()
    fv1 = cerebro1.broker.getvalue()
    ret1 = (fv1 - initial_cash) / initial_cash * 100
    results['纯自适应'] = {'final': fv1, 'return': ret1, 'trades': 0}

    # 3. 买入持有
    cerebro3 = bt.Cerebro()
    cerebro3.addstrategy(买入持有)
    cerebro3.adddata(bt.feeds.PandasData(dataname=df_bt, datetime=0))
    cerebro3.broker.setcash(initial_cash)
    cerebro3.broker.setcommission(commission=0.001)
    cerebro3.run()
    fv3 = cerebro3.broker.getvalue()
    ret3 = (fv3 - initial_cash) / initial_cash * 100
    results['买入持有'] = {'final': fv3, 'return': ret3, 'trades': 1}

    # 基准最大回撤
    max_price = np.maximum.accumulate(df['close'].values)
    max_dd = ((df['close'].values - max_price) / max_price * 100).min()

    # ATR止损统计
    stop_stats = {}
    for t in trades0:
        reason = t.get('reason', '')
        if '止损' in reason or '跟踪止' in reason:
            stop_stats[reason] = stop_stats.get(reason, 0) + 1

    alpha0 = ret0 - ret3

    print(f'  📋 收益对比')
    print(f'  {"策略":<14} {"最终资金":>13} {"收益率":>10} {"交易次数":>8} {"vs基准":>10}')
    print(f'  {"-"*58}')
    print(f'  {"自适应+ATR":<14} {"$"+f"{fv0:,.0f}":>13} {ret0:>+8.2f}%   {len(trades0):>4}笔   {alpha0:>+7.2f}%  ←NEW')
    print(f'  {"纯自适应":<14} {"$"+f"{fv1:,.0f}":>13} {ret1:>+8.2f}%   {len(trades0):>4}笔   {ret1-ret3:>+7.2f}%')
    print(f'  {"买入持有":<14} {"$"+f"{fv3:,.0f}":>13} {ret3:>+8.2f}%   {"1":>4}笔   {"基准":>8}')
    print(f'{"="*66}')
    print(f'  📉 基准最大回撤：{max_dd:.2f}%')

    if stop_stats:
        print(f'  🛡️ 止损触发：' + ' | '.join([f'{k}:{v}次' for k,v in stop_stats.items()]))
    if len(trades0) > 0:
        wins = [t['pnl'] for t in trades0 if 'pnl' in t and t['pnl'] > 0]
        losses = [abs(t['pnl']) for t in trades0 if 'pnl' in t and t.get('pnl', 0) < 0]
        win_rate = len(wins) / len(trades0) * 100 if trades0 else 0
        avg_win = np.mean(wins) if wins else 0
        avg_loss = np.mean(losses) if losses else 0
        print(f'  📊 交易统计：胜率{win_rate:.0f}%({len(wins)}胜/{len(losses)}负) | 均胜${avg_win:,.0f} | 均亏${avg_loss:,.0f}')

    best = max(results, key=lambda k: results[k]['return'])
    print(f'\n  🏆 最优：{best}  收益率：{results[best]["return"]:+.2f}%')

    if ret0 > ret1:
        print(f'  ✅ ATR止损有效！超额收益：{ret0-ret1:+.2f}%')
    else:
        print(f'  ⚠️ ATR止损拖累收益：{ret1-ret0:+.2f}%')

    return results


# ============================================================
# 主程序
# ============================================================
if __name__ == '__main__':
    print('''
╔══════════════════════════════════════════════════════╗
║    🚀 自适应 + ATR动态止损策略 | 美股数据           ║
║    止损：入场价 - 2×ATR（固定）                    ║
║    跟踪：最高价回落 3×ATR 止损                     ║
║    止盈：涨幅 > 6×ATR + ADX<20 止盈               ║
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

    print('\n' + '='*70)
    print('  🏆 所有标的汇总')
    print('='*70)
    print(f'  {"股票":<18} {"自适应+ATR":>10} {"纯自适应":>10} {"买入持有":>10} {"最优":>12}')
    print(f'  {"-"*60}')
    for name, r in all_results.items():
        best = max(r, key=lambda k: r[k]['return'])
        print(f'  {name:<18} {r["自适应+ATR"]["return"]:>+8.2f}%  '
              f'{r["纯自适应"]["return"]:>+8.2f}%  '
              f'{r["买入持有"]["return"]:>+8.2f}%   {best:>10}')
    print('='*70)

    avg_atr = np.mean([r['自适应+ATR']['return'] for r in all_results.values()])
    avg_adp = np.mean([r['纯自适应']['return'] for r in all_results.values()])
    avg_bh  = np.mean([r['买入持有']['return'] for r in all_results.values()])
    print(f'\n  📊 平均收益：自适应+ATR={avg_atr:+.2f}%  纯自适应={avg_adp:+.2f}%  买入持有={avg_bh:+.2f}%')
    print('\n✅ 完成！可调整 ATR 倍数（atr_stop/trail/target）做更多测试')
