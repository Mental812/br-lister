# 檢查 data/*.json 後把資料塞進 docs/index.html 的 /*DATA*/.../*END*/ 之間
import json, re, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
data, site = root / 'data', root / 'docs'
d = json.loads((data / 'data.json').read_text(encoding='utf-8'))
F = d['flights']
TW = {'TPE', 'TSA', 'KHH', 'RMQ'}

assert {f[6] for f in F} == set(d['cities']), {f[6] for f in F} ^ set(d['cities'])
for f in F:
    assert len(f) == 8 and re.fullmatch(r'\d{3}', f[0]), f
    assert (f[1] in TW) != (f[2] in TW), f  # 一端必須是台灣
    assert re.fullmatch(r'\d\d:\d\d', f[3]) and re.fullmatch(r'\d\d:\d\d(\+\d)?', f[4]), f
    assert f[5] and set(f[5]) <= set('0123456'), f

# 載客率（fetch_lf.py 產生，可有可無）
lf_path = data / 'lf.json'
if lf_path.exists():
    lf = json.loads(lf_path.read_text(encoding='utf-8'))
    assert all(len(v['go']) == len(v['back']) == len(lf['months']) for v in lf['ap'].values())
    d['lf'] = lf

# 放假日（fetch_holidays.py 產生，可有可無）
hol_path = data / 'holidays.json'
if hol_path.exists():
    d['hol'] = json.loads(hol_path.read_text(encoding='utf-8'))
    assert all(re.fullmatch(r'\d{4}-\d\d-\d\d', x) for x in d['hol'])

html = (site / 'index.html').read_text(encoding='utf-8')
new = re.sub(r'/\*DATA\*/.*?/\*END\*/', lambda _: '/*DATA*/' + json.dumps(d, ensure_ascii=False, separators=(',', ':')) + '/*END*/', html, flags=re.S)
assert new != html or '/*DATA*/' + json.dumps(d, ensure_ascii=False, separators=(',', ':')) in html
(site / 'index.html').write_text(new, encoding='utf-8')
print(f'ok: {len(F)} 班, {len(d["cities"])} 航點')
