# 從民航局「國際及兩岸定期航線班機載客率─按航點及航空公司分」抓長榮最近 13 個月載客率 → lf.json
# 出境 = 台灣出發（去程）、入境 = 回台灣（回程）。用 .ods（zip+xml）解析，只用標準函式庫。
import json, re, sys, zipfile, io, pathlib, urllib.request, xml.etree.ElementTree as ET

MONTHS = 13
BASE = 'https://www.caa.gov.tw/'
# 民航局航點名 → 機場代碼（只列長榮有飛的；同城多機場要分開）
POINT = {
    '香港': 'HKG', '澳門': 'MFM', '東京成田': 'NRT', '東京羽田': 'HND', '大阪': 'KIX', '神戶': 'UKB',
    '福岡': 'FUK', '札幌': 'CTS', '沖繩': 'OKA', '仙台': 'SDJ', '青森': 'AOJ', '小松': 'KMQ', '松山': 'MYJ',
    '首爾仁川': 'ICN', '首爾金浦': 'GMP', '釜山': 'PUS',
    '曼谷蘇凡納布': 'BKK', '新加坡': 'SIN', '吉隆坡': 'KUL', '胡志明市': 'SGN', '河內': 'HAN', '峴港': 'DAD',
    '馬尼拉': 'MNL', '宿霧': 'CEB', '克拉克': 'CRK', '雅加達': 'CGK', '峇里島': 'DPS', '清邁': 'CNX', '金邊': 'KTI',
    '德里': 'DEL', '上海浦東': 'PVG', '上海虹橋': 'SHA', '北京': 'PEK', '廣州': 'CAN', '杭州': 'HGH', '成都雙流': 'CTU',
    '洛杉磯': 'LAX', '舊金山': 'SFO', '西雅圖': 'SEA', '溫哥華': 'YVR', '紐約': 'JFK', '芝加哥': 'ORD',
    '休士頓': 'IAH', '達拉斯': 'DFW', '多倫多': 'YYZ', '華盛頓杜勒斯': 'IAD',
    '倫敦': 'LHR', '巴黎': 'CDG', '阿姆斯特丹': 'AMS', '維也納': 'VIE', '慕尼黑': 'MUC', '米蘭': 'MXP', '布里斯本': 'BNE',
}

T = '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}'
O = '{urn:oasis:names:tc:opendocument:xmlns:office:1.0}'
P = '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p'

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=60).read()

def rows(ods_bytes):
    root = ET.fromstring(zipfile.ZipFile(io.BytesIO(ods_bytes)).read('content.xml'))
    for r in next(root.iter(T + 'table')).iter(T + 'table-row'):
        row = []
        for c in r:
            if c.tag not in (T + 'table-cell', T + 'covered-table-cell'): continue
            v = c.get(O + 'value')
            if v is None: v = ''.join(''.join(p.itertext()) for p in c.iter(P)).strip()
            row += [v] * min(int(c.get(T + 'number-columns-repeated', '1')), 20)
        yield row + [''] * 15

def eva(ods_bytes):
    """回傳 {機場代碼: (去程%, 回程%)}，以及沒對應到的航點名"""
    out, unknown, point = {}, set(), None
    for r in rows(ods_bytes):
        if r[1] and not r[2]: point = r[1].strip()
        if r[2].strip() == '長榮' and point:
            code = POINT.get(point)
            if not code: unknown.add(point); continue
            pct = lambda s: round(float(s), 1) if s not in ('', '-') else None
            out[code] = (pct(r[14]), pct(r[10]))  # 出境=去程, 入境=回程
    return out, unknown

idx = get(BASE + 'article.aspx?a=1752&lang=1').decode('utf-8')
files = re.findall(r'FileAtt\.ashx\?lang=1&(?:amp;)?id=(\d+)"[^>]*title="(\d+)年(\d+)月\.ods"', idx)[:MONTHS]
files.reverse()  # 舊 → 新
months, data, unknown = [], {}, set()
for i, (fid, y, m) in enumerate(files):
    label = f'{int(y) + 1911}-{int(m):02d}'
    print('下載', label, file=sys.stderr)
    got, unk = eva(get(f'{BASE}FileAtt.ashx?lang=1&id={fid}'))
    unknown |= unk
    months.append(label)
    for code, (go, back) in got.items():
        d = data.setdefault(code, {'go': [None] * len(files), 'back': [None] * len(files)})
        d['go'][i], d['back'][i] = go, back

assert len(months) == MONTHS and data, '抓不到資料'
lf = {'months': months, 'ap': dict(sorted(data.items()))}
(pathlib.Path(__file__).resolve().parent.parent / 'data' / 'lf.json').write_text(json.dumps(lf, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print(f'ok: {months[0]} ~ {months[-1]}，{len(data)} 個機場', file=sys.stderr)
if unknown: print('未對應的航點（略過）:', '、'.join(sorted(unknown)), file=sys.stderr)
