#!/usr/bin/env python3
"""
A股网格交易策略 | 简化快速版
========================================
- 每跌 grid_pct 买一手，每涨 grid_pct 卖一手
- 首日收盘价为基准
"""

import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import baostock as bs
import time


def 获取数据(code):
    try:
        lg = bs.login()
        rs = bs.query_history_k_data_plus(
            code, 'date,close', start_date='2023-01-01', end_date='2025-12-31', frequency='d')
        data = []
        while rs.next(): data.append(rs.get_row_data())
        bs.logout()
        if not data: return None
        df = pd.DataFrame(data, columns=['date','close'])
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df = df.dropna()
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values('date').reset_index(drop=True)
    except:
        return None


def 网格回测(df, grid_pct=0.02, n_grids=10, cash0=100000, fee=0.001):
    """网格回测 - 核心逻辑"""
    if df is None or len(df) < 20:
        return None

    prices = df['close'].values
    base = float(prices[0])

    # 网格边界：-n_grids到+n_grids，共2*n_grids+1个边界
    boundaries = [base * (1 + grid_pct * i) for i in range(-n_grids, n_grids + 1)]

    # 持仓格数（正=持有格数，负=做空格数，但A股只能做多）
    # 每格金额
    unit = cash0 / n_grids  # 每格初始等额资金
    grid_position = 0  # 持仓格数（正数=持有，0=空仓）
    cash = cash0
    position = 0  # 持股数量
    trades = []

    for price in prices:
        prev_grid = grid_position
        # 当前价格所在的格（0=基准，负=低于基准，正=高于基准）
        current_grid = 0
        for i, bound in enumerate(boundaries):
            if price <= bound:
                current_grid = i - n_grids
                break
        else:
            current_grid = n_grids

        if current_grid == prev_grid:
            continue

        # 下跌：格数变小 → 买入（每降一格买入1/n_grids份）
        if current_grid < prev_grid:
            units_to_buy = prev_grid - current_grid  # 买几格
            for _ in range(units_to_buy):
                invest = min(unit, cash * 0.95)
                if invest > 0:
                    shares = int(invest / price)
                    cost = shares * price * (1 + fee)
                    if cash >= cost and shares > 0:
                        cash -= cost
                        position += shares
                        grid_position += 1
                        trades.append(('BUY', price, shares))

        # 上涨：格数变大 → 卖出（每升一格卖出1/n_grids份）
        elif current_grid > prev_grid:
            units_to_sell = current_grid - prev_grid
            for _ in range(units_to_sell):
                if grid_position > 0:
                    sell_shares = position // grid_position if grid_position > 0 else 0
                    sell_shares = min(sell_shares, int(unit / price) * 3)
                    if sell_shares > 0:
                        proceeds = sell_shares * price * (1 - fee)
                        cash += proceeds
                        position -= sell_shares
                        grid_position -= 1
                        trades.append(('SELL', price, sell_shares))

    # 最终价值
    final_price = prices[-1]
    final_value = cash + position * final_price
    ret = (final_value - cash0) / cash0 * 100
    bh_ret = (final_price / base - 1) * 100

    # 回撤
    equity = [cash0]
    tmp_pos = 0
    tmp_cash = cash0
    for price in prices:
        equity.append(tmp_cash + tmp_pos * price)

    # 简化回撤计算
    ret_arr = np.array(equity)
    running_max = np.maximum.accumulate(ret_arr)
    max_dd = np.min((ret_arr - running_max) / running_max * 100)

    return {
        'return': float(ret),
        'buy_hold': float(bh_ret),
        'max_dd': float(max_dd),
        'trades': len(trades),
        'final_value': final_value,
        'base': base,
        'grid_pct': grid_pct,
        'n_grids': n_grids,
    }


if __name__ == '__main__':
    print('''
╔══════════════════════════════════════════════╗
║    🚀 A股网格交易策略                      ║
║    每跌2%买，每涨2%卖                      ║
╚══════════════════════════════════════════════╝
''')

    stocks = [
        ('sh.600519', '贵州茅台'),
        ('sh.000858', '五粮液'),
        ('sh.601318', '中国平安'),
        ('sh.600036', '招商银行'),
        ('sh.000300', '沪深300'),
        ('sh.000016', '上证50'),
        ('sh.600276', '恒瑞医药'),
        ('sh.601888', '中国中免'),
        ('sh.600030', '中信证券'),
    ]

    # 参数：固定 2% / 10格
    GRID_PCT = 0.02
    N_GRIDS = 10

    print(f'参数：{GRID_PCT*100:.0f}%间距 / {N_GRIDS}格\n')

    results = {}
    for code, name in stocks:
        print(f'处理 {name}...', end=' ', flush=True)
        df = 获取数据(code)
        if df is None:
            print('失败')
            continue
        res = 网格回测(df, grid_pct=GRID_PCT, n_grids=N_GRIDS)
        if res:
            results[f'{name}({code})'] = res
            alpha = res['return'] - res['buy_hold']
            icon = '✅' if alpha > 0 else '⚠️'
            print(f'网格{res["return"]:>+6.1f}% vs 持有{res["buy_hold"]:>+6.1f}% (超额{alpha:>+6.1f}%) {icon}')
        time.sleep(0.2)

    print('\n' + '='*60)
    print('  🏆 汇总')
    print('='*60)
    print(f'  {"股票":<18} {"网格":>10} {"买入持有":>10} {"超额":>10} {"回撤":>10}')
    print(f'  {"-"*58}')
    for nm, r in results.items():
        alpha = r['return'] - r['buy_hold']
        icon = '✅' if alpha > 0 else '⚠️'
        print(f'  {nm:<18} {r["return"]:>+8.2f}%  {r["buy_hold"]:>+8.2f}%  '
              f'{alpha:>+8.2f}%  {r["max_dd"]:>8.2f}%  {icon}')
    print('='*60)

    avg_g = np.mean([r['return'] for r in results.values()])
    avg_b = np.mean([r['buy_hold'] for r in results.values()])
    wins = sum(1 for r in results.values() if r['return'] > r['buy_hold'])
    print(f'\n  平均：网格={avg_g:+.2f}%  买入持有={avg_b:+.2f}%  '
          f'超额={avg_g-avg_b:+.2f}%')
    print(f'  网格跑赢：{wins}/{len(results)}只')
    best = max(results, key=lambda k: results[k]['return'])
    print(f'  最优：{best}  {results[best]["return"]:+.2f}%')
    print('\n✅ 完成')
