# BR 班號查詢

長榮航空（BR）台灣出發航線的班號速查頁，給用公司票查位的人用。iPhone 直接打開，不用安裝。

網址：https://mental812.github.io/br-lister/

## 目錄

```
docs/       網站本體（GitHub Pages 從這裡發佈）
  index.html  單一頁面，資料由 build.py 注入
  icon.png    主畫面圖示
  og.png      LINE／社群連結預覽圖
data/       原始資料
  data.json     班表（長榮官網時刻表）
  lf.json       載客率（民航局月報，最近 13 個月）
  holidays.json 放假日（行政機關辦公日曆）
scripts/    資料抓取與建置
  build.py          檢查 data/ 並注入 docs/index.html
  fetch_lf.py       抓民航局載客率 → data/lf.json
  fetch_holidays.py 抓辦公日曆 → data/holidays.json
```

## 更新資料

```bash
python -X utf8 scripts/fetch_lf.py        # 每月（民航局約 25 日更新）
python -X utf8 scripts/fetch_holidays.py  # 每年（明年日曆約 6 月公布）
python -X utf8 scripts/build.py           # 改完 data/ 一定要跑
```

班表（`data/data.json`）在長榮換季時（3 月底、10 月底）從官網時刻表重抓。

## 本機預覽

```bash
python -m http.server 8770 --directory docs
```
