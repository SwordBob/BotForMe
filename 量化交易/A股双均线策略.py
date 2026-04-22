#!/usr/bin/env python3
"""
A股双均线策略 | baostock 数据源
========================================
- 数据源：baostock（免费开源，支持全部A股）
- 买入信号：MA5 上穿 MA20（金叉）
- 卖出信号：MA5 下穿 MA20（死叉）
- 对比：纯双均线 vs 买入持有
- 支持：上证指数、沪深个股、ETF
"""

import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import baostock as bs
import backtrader as bt
import time


def 获取A股数据(code, name='', start_date='2023-01-01', end_date='2025-12-31'):
    """
    baostock 个股数据获取
    code 格式：sh.600519（上海） / sz.000001（深圳）
    """
    print(f'下载 {name or code} ({code})...')
    try:
        lg = bs.login()
        if lg.error_code != '0':
            print(f'❌ 登录失败：{lg.error_msg}')
            return None

        rs = bs.query_history_k_data_plus(
            code,
            'date,open,high,low,close,volume,amount',
            start_date=start_date,
            end_date=end_date,
            frequency='d'
        )

        if rs.error_code != '0':
            print(f'❌ 查询失败：{rs.error_msg}')
            bs.logout()
            return None

        data = []
        while rs.next():
            data.append(rs.get_row_data())
        bs.logout()

        if not data:
            print(f'❌ 无数据')
            return None

        df = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 'volume', 'amount'])
        # 过滤停牌日期（volume为空的行）
        df = df[df['volume'].notna() & (df['volume'] != '')]
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['open']  = pd.to_numeric(df['open'],  errors='coerce')
        df['high']  = pd.to_numeric(df['high'],  errors='coerce')
        df['low']   = pd.to_numeric(df['low'],   errors='coerce')
        df['volume']= pd.to_numeric(df['volume'], errors='coerce')
        df = df.dropna(subset=['close', 'open'])
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)

        print(f'✅ 成功：{len(df)} 个交易日 ({df["date"].min().date()} ~ {df["date"].max().date()})')
        return df

    except Exception as e:
        print(f'❌ 出错：{e}')
        return None


# ============================================================
# 策略1：双均线
# ============================================================
class 双均线策略(bt.Strategy):
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
            self.trades.append({
                'action': 'BUY' if order.isbuy() else 'SELL',
                'price': order.executed.price,
                'pnl': getattr(order.executed, 'pnl', 0)
            })
        self.order = None


# ============================================================
# 策略2：买入持有
# ============================================================
class 买入持有(bt.Strategy):
    def __init__(self): self.order = None
    def next(self):
        if not self.position: self.order = self.buy()
    def notify_order(self, order): self.order = None


# ============================================================
# 回测运行器
# ============================================================
def 运行回测(stock_code, stock_name='', start='2023-01-01', end='2025-12-31', initial_cash=100000):

    name = stock_name or stock_code
    df = 获取A股数据(stock_code, name, start, end)
    if df is None or len(df) == 0:
        return None

    print(f'\n{"="*60}')
    print(f'  📈 {name} ({stock_code}) 双均线回测')
    print(f'{"="*60}')
    print(f'  MA5 / MA20 | 初始资金：¥{initial_cash:,.0f}')
    print(f'{"="*60}\n')

    # backtrader 格式
    df_bt = df[['date', 'open', 'high', 'low', 'close', 'volume']].copy()
    df_bt.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
    df_bt['datetime'] = pd.to_datetime(df_bt['datetime'])

    results = {}

    # 双均线
    cerebro1 = bt.Cerebro()
    cerebro1.addstrategy(双均线策略)
    cerebro1.adddata(bt.feeds.PandasData(dataname=df_bt, datetime=0))
    cerebro1.broker.setcash(initial_cash)
    cerebro1.broker.setcommission(commission=0.001)  # 手续费万1
    cerebro1.addsizer(bt.sizers.AllInSizerInt)
    p1 = cerebro1.run()
    fv1 = cerebro1.broker.getvalue()
    ret1 = (fv1 - initial_cash) / initial_cash * 100
    trades1 = p1[0].trades
    results['双均线'] = {'final': fv1, 'return': ret1, 'trades': len(trades1)}

    # 买入持有
    cerebro2 = bt.Cerebro()
    cerebro2.addstrategy(买入持有)
    cerebro2.adddata(bt.feeds.PandasData(dataname=df_bt, datetime=0))
    cerebro2.broker.setcash(initial_cash)
    cerebro2.broker.setcommission(commission=0.001)
    cerebro2.run()
    fv2 = cerebro2.broker.getvalue()
    ret2 = (fv2 - initial_cash) / initial_cash * 100
    results['买入持有'] = {'final': fv2, 'return': ret2, 'trades': 1}

    # 最大回撤
    close_arr = df['close'].values
    max_price = np.maximum.accumulate(close_arr)
    max_dd = ((close_arr - max_price) / max_price * 100).min()

    # 交易统计
    wins  = [t['pnl'] for t in trades1 if t.get('pnl', 0) > 0]
    losses= [abs(t['pnl']) for t in trades1 if t.get('pnl', 0) < 0]
    win_rate = len(wins) / len(trades1) * 100 if trades1 else 0

    alpha = ret1 - ret2

    print(f'  📋 收益对比')
    print(f'  {"策略":<10} {"最终资金":>14} {"收益率":>10} {"交易次数":>8}')
    print(f'  {"-"*46}')
    print(f'  {"双均线":<10} {"¥"+f"{fv1:,.0f}":>14} {ret1:>+8.2f}%   {len(trades1):>4}笔')
    print(f'  {"买入持有":<10} {"¥"+f"{fv2:,.0f}":>14} {ret2:>+8.2f}%   {"1":>4}笔')
    print(f'{"="*60}')
    print(f'  📉 最大回撤：{max_dd:.2f}%')
    print(f'  📊 胜率：{win_rate:.0f}%（{len(wins)}胜/{len(losses)}负）')
    print(f'  🏆 双均线 vs 买入持有：{alpha:+.2f}%')

    if ret1 > ret2:
        print(f'  ✅ 双均线跑赢！{"+" if alpha > 0 else ""}{alpha:.2f}%')
    else:
        print(f'  ⚠️ 双均线跑输：{alpha:.2f}%')

    return results


# ============================================================
# 主程序
# ============================================================
if __name__ == '__main__':
    print('''
╔══════════════════════════════════════════════╗
║     🚀 A股双均线策略 | baostock 数据        ║
║     数据源：baostock（免费，支持全部A股）   ║
╚══════════════════════════════════════════════╝
''')

    # A股测试标的
    测试列表 = [
        ('sh.600519', '贵州茅台'),
        ('sh.000001', '平安银行（深市）'),
        ('sh.000858', '五粮液'),
        ('sh.601318', '中国平安'),
        ('sh.600036', '招商银行'),
        ('sh.000858', '五粮液'),
        ('sh.000300', '沪深300 ETF'),
        ('sh.000016', '上证50 ETF'),
    ]

    print('可选标的：')
    for i, (c, n) in enumerate(测试列表, 1):
        print(f'  {i}. {c}  {n}')
    print()

    # 只测沪深主要股票 + 指数
    标的池 = [
        ('sh.600519', '贵州茅台'),
        ('sh.601318', '中国平安'),
        ('sh.600036', '招商银行'),
        ('sh.000858', '五粮液'),
        ('sz.000001', '平安银行'),
        ('sh.000300', '沪深300'),
    ]

    all_results = {}
    for code, name in 标的池:
        res = 运行回测(code, name, start='2023-01-01', end='2025-12-31', initial_cash=100000)
        if res:
            all_results[f'{name}({code})'] = res
        time.sleep(0.5)

    print('\n' + '='*64)
    print('  🏆 A股标的汇总（2023-2025）')
    print('='*64)
    print(f'  {"股票":<20} {"双均线":>10} {"买入持有":>10} {"超额收益":>10}')
    print(f'  {"-"*52}')
    for name, r in all_results.items():
        alpha = r['双均线']['return'] - r['买入持有']['return']
        print(f'  {name:<18} {r["双均线"]["return"]:>+8.2f}%  '
              f'{r["买入持有"]["return"]:>+8.2f}%  '
              f'{alpha:>+8.2f}%')
    print('='*64)

    avg_ma = np.mean([r['双均线']['return'] for r in all_results.values()])
    avg_bh = np.mean([r['买入持有']['return'] for r in all_results.values()])
    print(f'\n  📊 平均收益：双均线={avg_ma:+.2f}%  买入持有={avg_bh:+.2f}%')
    print('\n✅ 全部完成！')
