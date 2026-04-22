#!/usr/bin/env python3
"""
东方财富实时行情获取
通过东方财富 API 获取 A股实时价格，数据接近 T 日
"""
import urllib.request
import json
from datetime import datetime

# 东方财富 A股实时行情 API
# fields: f43=最新价, f44=最高, f45=最低, f46=今开, f47=昨收
# f48=成交量, f49=成交额, f50=时间, f57=代码, f58=名称
# f169=涨跌额, f170=涨跌幅, f171=涨跌, f172=总手, f173=现手
# f174=总额, f175=今开, f176=昨开, f177=最高, f178=最低

STOCKS = [
    ('sh.600519', '贵州茅台', '1.600519'),
    ('sh.601318', '中国平安', '1.601318'),
    ('sz.000858', '五粮液',  '0.000858'),
    ('sz.300750', '宁德时代', '0.300750'),
    ('sh.688981', '中芯国际', '1.688981'),
    ('sh.600036', '招商银行', '1.600036'),
    ('sz.300059', '东方财富', '0.300059'),
    ('sh.600276', '恒瑞医药', '1.600276'),
    ('sz.002594', '比亚迪',   '0.002594'),
]

FIELDS = 'f43,f44,f45,f46,f47,f48,f49,f50,f57,f58,f169,f170,f171,f172,f173,f174,f175,f176,f177,f178'

def fetch_realtime(stocks):
    secids = ','.join([s[2] for s in stocks])
    url = f'https://push2.eastmoney.com/api/qt/ulist.n/get?secids={secids}&fields={FIELDS}&ut=fa5fd1943c7b386f172d6893dbfba10b&fltt=2&invt=2'
    
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://quote.eastmoney.com/'
    })
    
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    
    return data.get('data', {}).get('diff', [])

def main():
    print(f'📅 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} A股实时行情（东方财富）')
    print('='*85)
    
    try:
        results = fetch_realtime(STOCKS)
    except Exception as e:
        print(f'❌ 获取数据失败: {e}')
        return
    
    if not results:
        print('❌ 无数据返回')
        return
    
    print(f'{"代码":>10s} {"名称":>8s} {"最新价":>10s} {"涨跌幅":>10s} {"涨跌额":>10s} {"最高":>10s} {"最低":>10s} {"成交量":>12s}')
    print('-'*85)
    
    stock_map = {s[2]: s for s in STOCKS}
    
    for item in results:
        secid = item.get('f57', '')
        if secid not in stock_map:
            continue
        name = item.get('f58', '')
        price = item.get('f43', 0)
        if price:
            price = price / 100.0
        change_pct = item.get('f170', 0) / 100.0
        change_val = item.get('f169', 0) / 100.0
        high = item.get('f44', 0) / 100.0
        low = item.get('f45', 0) / 100.0
        volume = item.get('f48', 0)  # 股
        
        if change_pct > 0:
            trend_icon = '🔴'
        elif change_pct < 0:
            trend_icon = '🟢'
        else:
            trend_icon = '⚪'
        
        print(f'{secid:>10s} {name:>8s} {price:>10.2f} {trend_icon}{change_pct:>+7.2f}% {change_val:>+10.2f} {high:>10.2f} {low:>10.2f} {volume:>12,.0f}')
    
    print()
    print('📊 字段说明: 🔴涨 🟢跌 ⚪平')
    print('📌 数据来源: 东方财富（接近实时 T 日行情）')

if __name__ == '__main__':
    main()
