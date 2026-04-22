#!/usr/bin/env python3
"""
A股选股系统 v3 | 精简快速版
========================================
均线多头排列（MA5>MA20>MA60）+ ADX>30 筛选强势股
"""

import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import baostock as bs
import time


# ---- 精简股票池（各行业龙头，约50只）----
STOCKS = [
    ('sh.600519', '贵州茅台'), ('sh.600036', '招商银行'), ('sh.601318', '中国平安'),
    ('sh.600276', '恒瑞医药'), ('sh.601888', '中国中免'), ('sh.600030', '中信证券'),
    ('sh.600048', '保利发展'), ('sh.600309', '万华化学'), ('sh.600028', '中国石化'),
    ('sh.600019', '宝钢股份'), ('sh.600050', '中国联通'), ('sh.600104', '上汽集团'),
    ('sh.600009', '上海机场'), ('sh.600900', '长江电力'), ('sh.600028', '中国石化'),
    ('sh.600585', '海螺水泥'), ('sh.601012', '隆基绿能'), ('sh.600690', '海尔智家'),
    ('sh.601668', '中国建筑'), ('sh.601328', '交通银行'), ('sh.601398', '工商银行'),
    ('sh.601939', '建设银行'), ('sh.601988', '中国银行'), ('sh.601186', '中国铁建'),
    ('sh.601390', '中国中铁'), ('sh.601857', '中国石油'), ('sh.600150', '中国船舶'),
    ('sh.600887', '伊利股份'), ('sh.603288', '海天味业'),
    ('sh.600438', '通威股份'), ('sh.000858', '五粮液'), ('sh.000895', '双汇发展'),
    ('sh.000568', '泸州老窖'), ('sh.600887', '伊利股份'),
    ('sh.688012', '中微公司'), ('sh.603259', '药明康德'), ('sh.688981', '中芯国际'),
    ('sh.688111', '金山办公'), ('sh.300750', '宁德时代'), ('sh.002594', '比亚迪'),
    ('sz.000001', '平安银行'), ('sz.000002', '万科A'), ('sz.000333', '美的集团'),
    ('sz.000651', '格力电器'), ('sz.002415', '海康威视'), ('sz.002304', '洋河股份'),
    ('sz.002475', '立讯精密'), ('sz.300760', '迈瑞医疗'), ('sz.300059', '东方财富'),
    ('sh.510300', '沪深300ETF'), ('sh.510050', '上证50ETF'), ('sz.159915', '创业板ETF'),
]


def 获取数据(code, days=300):
    try:
        lg = bs.login()
        end = pd.Timestamp.now().strftime('%Y-%m-%d')
        start = (pd.Timestamp.now() - pd.Timedelta(days=days)).strftime('%Y-%m-%d')
        rs = bs.query_history_k_data_plus(code,
            'date,open,high,low,close,volume',
            start_date=start, end_date=end, frequency='d')
        data = []
        while rs.next(): data.append(rs.get_row_data())
        bs.logout()
        if not data: return None
        df = pd.DataFrame(data, columns=['date','open','high','low','close','volume'])
        for c in ['close','open','high','low','volume']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna(subset=['close'])
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values('date').reset_index(drop=True)
    except:
        return None


def 计算指标(df):
    """计算 MA5/MA20/MA60 和 ADX（向量化）"""
    close = df['close'].values
    high  = df['high'].values
    low   = df['low'].values
    n = len(close)

    df['ma5']  = pd.Series(close).rolling(5).mean()
    df['ma20'] = pd.Series(close).rolling(20).mean()
    df['ma60'] = pd.Series(close).rolling(60).mean()

    # ADX（14日）
    p = 14
    tr = np.maximum(high[1:] - low[1:], np.abs(high[1:] - close[:-1]))
    tr = np.concatenate([[high[0]-low[0]], tr])

    h_diff = np.diff(high, prepend=high[0])
    l_diff = np.diff(-low,  prepend=-low[0])
    plus_dm  = np.where(h_diff > l_diff, np.maximum(h_diff, 0), 0)
    minus_dm = np.where(l_diff > h_diff, np.maximum(l_diff, 0), 0)

    atr  = pd.Series(tr).ewm(alpha=1/p, adjust=False).mean().values
    pdi  = pd.Series(plus_dm).ewm(alpha=1/p, adjust=False).mean().values / (atr+1e-10) * 100
    mdi  = pd.Series(minus_dm).ewm(alpha=1/p, adjust=False).mean().values / (atr+1e-10) * 100
    dx   = np.abs(pdi - mdi) / (pdi + mdi + 1e-10) * 100
    adx  = pd.Series(dx).ewm(alpha=1/p, adjust=False).mean().values
    df['adx'] = adx

    return df


def 筛选(df):
    """是否满足：MA5>MA20>MA60 且 ADX>30"""
    if df is None or len(df) < 65:
        return False
    r = df.iloc[-1]
    if np.isnan(r['ma5']) or np.isnan(r['ma20']) or np.isnan(r['ma60']):
        return False
    return (r['ma5'] > r['ma20'] > r['ma60']) and (r['adx'] > 30)


def 趋势回测(df, fee=0.001):
    """双均线MA5/MA20趋势策略（2023-2025）"""
    df = df[df['date'] >= '2023-01-01'].copy()
    if len(df) < 300:
        return None
    close = df['close'].values
    ma5   = df['ma5'].values
    ma20  = df['ma20'].values
    if np.isnan(ma5[-1]) or np.isnan(ma20[-1]):
        return None
    cash, pos = 100000.0, 0
    prev = ma5[0] > ma20[0]
    for i in range(1, len(df)):
        if np.isnan(ma5[i]) or np.isnan(ma20[i]): continue
        cur = ma5[i] > ma20[i]
        if cur and not prev and pos == 0:
            sh = int(cash / close[i] / 100) * 100
            cost = sh * close[i] * (1+fee)
            if cash >= cost and sh > 0: cash -= cost; pos += sh
        elif not cur and prev and pos > 0:
            cash += pos * close[i] * (1-fee); pos = 0
        prev = cur
    if pos > 0: cash += pos * close[-1] * (1-fee)
    ret = (cash - 100000) / 100000 * 100
    bh  = (close[-1] / close[0] - 1) * 100
    return {'return': float(ret), 'buy_hold': float(bh)}


if __name__ == '__main__':
    print('''
╔══════════════════════════════════════════════════╗
║  🚀 A股选股系统 | 均线多头 + ADX趋势筛选      ║
║  条件：MA5 > MA20 > MA60  且  ADX > 30        ║
╚══════════════════════════════════════════════════╝
''')

    # 去重
    seen, pool = set(), []
    for c, n in STOCKS:
        if c not in seen: seen.add(c); pool.append((c, n))
    print(f'股票池：{len(pool)} 只\n')

    print('阶段1：扫描强势股...')
    screened = []
    for i, (code, name) in enumerate(pool):
        df = 获取数据(code, days=300)
        if df is None: continue
        df = 计算指标(df)
        if 筛选(df):
            r = df.iloc[-1]
            screened.append({
                'code': code, 'name': name,
                'close': round(float(r['close']), 2),
                'ma5': round(float(r['ma5']), 2),
                'ma20': round(float(r['ma20']), 2),
                'ma60': round(float(r['ma60']), 2),
                'adx': round(float(r['adx']), 1),
                'df': df.copy(),
            })
        if (i+1) % 20 == 0:
            print(f'  进度 {i+1}/{len(pool)} | 强势股 {len(screened)} 只')
        time.sleep(0.08)

    if not screened:
        print('未找到符合条件的股票（MA5>MA20>MA60 且 ADX>30）')
        print('注：当前A股震荡市，符合条件的股票本来就很少，可适当降低ADX阈值')
        # 改用较低阈值重扫
        print('\n降低阈值重扫（ADX>25）...')
        for code, name in pool:
            df = 获取数据(code, days=300)
            if df is None: continue
            df = 计算指标(df)
            r = df.iloc[-1]
            if not (np.isnan(r.get('ma5', np.nan)) or np.isnan(r.get('adx', np.nan))):
                if (r.get('ma5', 0) > r.get('ma20', 0) > r.get('ma60', 0)) and r.get('adx', 0) > 25:
                    screened.append({
                        'code': code, 'name': name,
                        'close': round(float(r['close']), 2),
                        'ma5': round(float(r['ma5']), 2),
                        'ma20': round(float(r['ma20']), 2),
                        'ma60': round(float(r['ma60']), 2),
                        'adx': round(float(r['adx']), 1),
                        'df': df.copy(),
                    })
        print(f'降低阈值后找到 {len(screened)} 只')

    if screened:
        screened.sort(key=lambda x: x['adx'], reverse=True)
        print(f'\n{"="*70}')
        print(f'  📋 强势股筛选结果（{len(screened)} 只）')
        print(f'{"="*70}')
        print(f'  {"代码":<12} {"名称":<10} {"价":>8} {"MA5":>8} {"MA20":>8} {"MA60":>8} {"ADX":>6}')
        print(f'  {"-"*70}')
        for s in screened:
            print(f'  {s["code"]:<12} {s["name"]:<10} {s["close"]:>8.2f} '
                  f'{s["ma5"]:>8.2f} {s["ma20"]:>8.2f} {s["ma60"]:>8.2f} {s["adx"]:>6.1f}')
        print(f'{"="*70}')

        print('\n阶段2：趋势跟随回测（MA5/MA20 · 2023-2025）...')
        results = []
        for s in screened:
            res = 趋势回测(s['df'])
            if res:
                res['code'], res['name'] = s['code'], s['name']
                results.append(res)
            time.sleep(0.1)

        if results:
            results.sort(key=lambda x: x['return'], reverse=True)
            print(f'\n{"="*66}')
            print(f'  📈 选股后趋势跟随回测结果')
            print(f'{"="*66}')
            print(f'  {"股票":<14} {"趋势策略":>10} {"买入持有":>10} {"超额":>10} {"结论":>8}')
            print(f'  {"-"*58}')
            for r in results:
                alpha = r['return'] - r['buy_hold']
                icon = '✅WIN' if alpha > 0 else '⚠️LOSE'
                print(f'  {r["name"]:<10}({r["code"][-6:]}){r["return"]:>+8.2f}%  '
                      f'{r["buy_hold"]:>+8.2f}%  {alpha:>+8.2f}%  {icon:>6}')
            print(f'{"="*66}')
            avg_t = np.mean([r['return'] for r in results])
            avg_b = np.mean([r['buy_hold'] for r in results])
            wins  = sum(1 for r in results if r['return'] > r['buy_hold'])
            print(f'\n  📊 均值：趋势策略={avg_t:+.2f}%  买入持有={avg_b:+.2f}%  '
                  f'超额={avg_t-avg_b:+.2f}%')
            print(f'  🏆 趋势跑赢：{wins}/{len(results)} 只')
            print(f'\n  🔥 ADX最强（趋势最确定）：')
            for s in screened[:3]:
                print(f'     {s["name"]} ADX={s["adx"]}  MA多头排列确认')
    else:
        print('\n未筛选到任何股票')

    print('\n✅ 完成')
