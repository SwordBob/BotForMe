#!/usr/bin/env python3
"""
A股综合分析系统（实时+技术指标）
- 实时行情：新浪财经 API（T 日盘中数据）
- 技术指标：baostock 历史数据（90天，ADX + 均线）
- 数据融合：一次查询，同时输出实时价格 + 技术信号
"""
import baostock as bs
import pandas as pd
import numpy as np
import urllib.request
import re
from datetime import datetime, timedelta

# ============================================================
# 配置
# ============================================================
STOCKS = [
    ('sh.600519', '贵州茅台'),
    ('sh.601318', '中国平安'),
    ('sz.000858', '五粮液'),
    ('sz.300750', '宁德时代'),
    ('sh.688981', '中芯国际'),
    ('sh.600036', '招商银行'),
    ('sz.300059', '东方财富'),
    ('sh.600276', '恒瑞医药'),
    ('sz.002594', '比亚迪'),
]

HISTORY_DAYS = 90  # 历史数据天数（用于计算MA/ADX）

# ============================================================
# 实时行情（新浪财经）
# ============================================================
def fetch_sina_realtime():
    """从新浪财经获取实时价格"""
    codes = ','.join([code.replace('.', '') for code, _ in STOCKS])
    url = f'https://hq.sinajs.cn/list={codes}'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://finance.sina.com.cn'
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        content = resp.read().decode('gbk', errors='replace')

    result = {}
    for code, name in STOCKS:
        m = re.search(rf'hq_str_{code.replace(".", "")}="(.+?)"', content)
        if not m:
            continue
        fields = m.group(1).split(',')
        try:
            open_p = float(fields[1])
            prev_close = float(fields[2])
            cur_p = float(fields[3])
            high_p = float(fields[4])
            low_p = float(fields[5])
            vol = float(fields[6])
            date = fields[30] if len(fields) > 30 else ''
            time = fields[31] if len(fields) > 31 else ''
            chg = cur_p - prev_close
            chg_pct = (chg / prev_close) * 100
            result[code] = {
                'name': name, 'cur_p': cur_p, 'prev_close': prev_close,
                'chg': chg, 'chg_pct': chg_pct,
                'open_p': open_p, 'high_p': high_p, 'low_p': low_p,
                'vol': vol, 'date': date, 'time': time
            }
        except Exception:
            continue
    return result

# ============================================================
# 历史数据（baostock）
# ============================================================
def calc_adx(df, period=14):
    """计算 ADX"""
    for col in ['close', 'open', 'high', 'low']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.sort_values('date').reset_index(drop=True)
    if len(df) < period + 2:
        return None
    high = df['high'].values
    low = df['low'].values
    close = df['close'].values
    tr = np.zeros(len(df))
    plus_dm = np.zeros(len(df))
    minus_dm = np.zeros(len(df))
    for i in range(1, len(df)):
        tr[i] = max(high[i], close[i-1]) - min(low[i], close[i-1])
        high_diff = high[i] - high[i-1]
        low_diff = low[i-1] - low[i]
        if high_diff > low_diff:
            plus_dm[i] = high_diff
        else:
            minus_dm[i] = low_diff
    atr = np.zeros(len(df))
    atr[0] = tr[0]
    for i in range(1, len(df)):
        atr[i] = (atr[i-1] * (period - 1) + tr[i]) / period
    plus_di = np.zeros(len(df))
    minus_di = np.zeros(len(df))
    for i in range(period, len(df)):
        plus_di[i] = (np.sum(plus_dm[i-period+1:i+1]) / (np.sum(tr[i-period+1:i+1]) + 1e-10)) * 100
        minus_di[i] = (np.sum(minus_dm[i-period+1:i+1]) / (np.sum(tr[i-period+1:i+1]) + 1e-10)) * 100
    dx = np.abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10) * 100
    adx = np.zeros(len(df))
    adx[period] = np.mean(dx[period:period*2])
    for i in range(period + 1, len(df)):
        adx[i] = (adx[i-1] * (period - 1) + dx[i]) / period
    return adx[-1]

def get_kline_hist(code):
    """从 baostock 获取历史K线"""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=HISTORY_DAYS + 30)).strftime('%Y-%m-%d')
    fields = 'date,code,open,high,low,close,volume'
    rs = bs.query_history_k_data_plus(code, fields, start_date=start_date, end_date=end_date, frequency='d')
    data = []
    while rs.error_code == '0' and rs.next():
        data.append(rs.get_row_data())
    if data:
        df = pd.DataFrame(data, columns=rs.fields)
        for col in ['close', 'open', 'high', 'low', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df.sort_values('date').reset_index(drop=True)
    return pd.DataFrame()

# ============================================================
# 主程序
# ============================================================
def main():
    bs.login()
    print(f'📅 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} A股综合分析（实时+技术指标）')
    print('='*100)

    # 1. 实时行情
    realtime = fetch_sina_realtime()

    # 2. 技术指标
    results = []
    for code, name in STOCKS:
        df = get_kline_hist(code)
        if len(df) < 30:
            print(f'⚠️  {name} 历史数据不足，跳过')
            continue

        # MA
        ma5 = float(df['close'].rolling(5).mean().iloc[-1])
        ma20 = float(df['close'].rolling(20).mean().iloc[-1])
        ma60_val = float(df['close'].rolling(60).mean().iloc[-1]) if len(df) >= 60 else None

        # ADX
        adx = calc_adx(df)

        # 实时数据
        rt = realtime.get(code, {})
        cur_p = rt.get('cur_p', None)
        chg_pct = rt.get('chg_pct', None)
        chg = rt.get('chg', None)
        open_p = rt.get('open_p', None)
        high_p = rt.get('high_p', None)
        low_p = rt.get('low_p', None)
        time_str = rt.get('time', '')
        vol = rt.get('vol', None)

        # 趋势判断
        has_ma60 = ma60_val is not None
        if has_ma60 and ma5 > ma20 and ma20 > ma60_val and adx and adx > 30:
            trend = '📈强势(多头)'
        elif has_ma60 and ma5 < ma20 and ma20 < ma60_val:
            trend = '📉弱势(空头)'
        elif adx and adx > 30:
            trend = '📈强趋势'
        elif adx and adx < 20:
            trend = '➡️震荡(网格)'
        else:
            trend = '➡️中性'

        results.append({
            'name': name, 'code': code,
            'cur_p': cur_p, 'chg': chg, 'chg_pct': chg_pct,
            'open_p': open_p, 'high_p': high_p, 'low_p': low_p,
            'vol': vol, 'time': time_str,
            'ma5': ma5, 'ma20': ma20, 'ma60': ma60_val,
            'adx': adx, 'trend': trend
        })

    # 排序：ADX 高的排前面
    results.sort(key=lambda x: -x['adx'] if x['adx'] else 0)

    # 输出
    print(f'{"股票":>8s} {"最新价":>10s} {"涨跌幅":>9s} {"MA5":>10s} {"MA20":>10s} {"MA60":>10s} {"ADX":>6s} {"信号":>12s}')
    print('-'*100)
    for r in results:
        if r['cur_p'] is None:
            continue
        chg_icon = '🔴' if r['chg_pct'] and r['chg_pct'] > 0 else ('🟢' if r['chg_pct'] and r['chg_pct'] < 0 else '⚪')
        chg_str = f"{chg_icon}{r['chg_pct']:+.2f}%" if r['chg_pct'] is not None else 'N/A'
        adx_str = f"{r['adx']:.1f}" if r['adx'] else 'N/A'
        ma60_str = f"{r['ma60']:.2f}" if r['ma60'] else 'N/A'
        print(f"{r['name']:>8s} {r['cur_p']:>10.2f} {chg_str:>9s} {r['ma5']:>10.2f} {r['ma20']:>10.2f} {ma60_str:>10s} {adx_str:>6s} {r['trend']:>12s}")

    print()
    print('📊 策略参考:')
    print('  📈 ADX>30 + MA多头排列 → 趋势跟随策略（双均线金叉买入）')
    print('  ➡️ ADX<20 → 网格交易策略（跌2%买/涨2%卖）')
    print('  ➡️ ADX 20-30 → 观望，等待明确信号')
    print()

    # 操作建议
    print('🤖 操作建议:')
    for r in results:
        if r['cur_p'] is None or r['adx'] is None:
            continue
        sigs = []
        if r['adx'] > 30 and r['ma60'] and r['ma5'] > r['ma20'] > r['ma60']:
            sigs.append('✅趋势多头信号，关注双均线金叉买入点')
        elif r['adx'] < 20:
            sigs.append(f'📊网格候选(ADX={r["adx"]:.1f}，低趋势，适合网格)')
        if sigs:
            print(f'  {r["name"]:>8s}: {"; ".join(sigs)}')

    bs.logout()

if __name__ == '__main__':
    main()
