# 從政府資料開放平臺「中華民國政府行政機關辦公日曆表」抓今年＋明年的放假日 → holidays.json
# 「是否放假」=2 的日子（含週末、國定假日、補假；補班日不算）
import json, re, sys, datetime, pathlib, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=60).read()

meta = json.loads(get('https://data.gov.tw/api/v2/rest/dataset/14718'))
dist = meta.get('result', meta)['distribution']
year = datetime.date.today().year
off = []
for roc in (year - 1911, year - 1910):
    # 同一年可能有修正版，取最後一個非 Google 行事曆版
    urls = [d['resourceDownloadUrl'] for d in dist
            if d['resourceDescription'].startswith(f'{roc}年') and 'Google' not in d['resourceDescription']]
    if not urls:
        print(f'{roc} 年辦公日曆還沒公布，略過', file=sys.stderr); continue
    text = get(urls[-1]).decode('utf-8-sig')
    for line in text.splitlines()[1:]:
        f = line.split(',')
        if len(f) >= 3 and f[2].strip() == '2' and re.fullmatch(r'\d{8}', f[0]):
            off.append(f'{f[0][:4]}-{f[0][4:6]}-{f[0][6:]}')
    print(f'{roc} 年 ok', file=sys.stderr)

assert off, '抓不到放假日'
(pathlib.Path(__file__).resolve().parent.parent / 'data' / 'holidays.json').write_text(json.dumps(sorted(set(off))), encoding='utf-8')
print(f'ok: {len(off)} 個放假日', file=sys.stderr)
