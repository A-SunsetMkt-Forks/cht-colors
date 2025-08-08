#!/usr/bin/env python3
#
# Extract colors from index.html and generate
# - data/cht-colors-pinyin.json
# - data/cht-colors.json
# - data/cht-colors-pinyin.scss
import os
import re
import json
from bs4 import BeautifulSoup
from pypinyin import lazy_pinyin

def hex_to_rgb(hex_code):
    '"ffffff" -> [255, 255, 255]. Invalid code -> None'
    hex_code = hex_code.lstrip('#')
    if not re.match('[0-9a-f]{6}', hex_code):
        return None
    else:
        return [int(i, 16) for i in (hex_code[0:2], hex_code[2:4], hex_code[4:6])]

scriptdir = os.path.dirname(os.path.abspath(__file__))
html_file = os.path.join(os.path.dirname(scriptdir), "index.html")
with open(html_file, "r", encoding="utf-8") as f:
    content = f.read()
soup = BeautifulSoup(content, "html.parser")

# Solve conflict
preset_pinyins = {
    '殷紅': 'yinhong1',
    '銀紅': 'yinhong2',

    '絳紫': 'jiangzi1',
    '醬紫': 'jiangzi2',

    '緇色': 'zise1',
    '紫色': 'zise2',

    '黧': 'li1',
    '黎': 'li2',
}
pinyin_dict = {}
colors = []

color_list_div = soup.find("div", id="colorList")
for dl in color_list_div.find_all("dl"):
    _colorname = dl.find("dt", class_="colorName")
    _colorbox = dl.find("dd", class_="colorBox")
    _colorvalue = dl.find("dd", class_="colorValue")

    name = _colorname.get_text()
    name_pinyin = ''.join(lazy_pinyin(name))

    value = _colorvalue.get_text()
    value_rgb = [int(m) for m in re.search(r"RGB: (\d+),(\d+),(\d+)", value).groups()]
    value_hex = re.search(r"HEX: (#[0-9a-f]{6})", value).groups()[0]

    box_style = _colorbox['style']
    box_rgb = [int(m) for m in re.search(r"rgb\((\d+), *(\d+), (\d+)\)", box_style).groups()]

    # Verification
    # CMYK is not verified because it doesn't match at all
    if value_rgb != box_rgb:
        print(f"WARNING: name={name} rgb_literal({value_rgb})!=background_color({box_rgb})")
    if hex_to_rgb(value_hex) != value_rgb:
        print(f"WARNING: name={name} rgb_literal=({value_rgb})!=hex({value_hex}={hex_to_rgb(value_hex)})")
    if name_pinyin in pinyin_dict:
        print(f"WARNING: Conflict pinyin {pinyin_dict[name_pinyin]} / {name}")

    # Detect pinyin conflict
    # Conflicted pinyin is curated in preset_pinyins
    curated_pinyin = preset_pinyins.get(name, name_pinyin)
    pinyin_dict[curated_pinyin] = name

    colors.append({
        'name': name,
        'pinyin': curated_pinyin,
        'rgb': value_rgb,
        'hex': value_hex,
    })

with open(os.path.join(scriptdir, 'cht-colors-pinyin.json'), 'w') as f:
    f.write(json.dumps({c['pinyin']:c['hex'] for c in colors}, indent=2))
    f.write('\n')
with open(os.path.join(scriptdir, 'cht-colors.json'), 'w') as f:
    f.write(json.dumps({c['name']:c['hex'] for c in colors}, indent=2, ensure_ascii=False))
    f.write('\n')
with open(os.path.join(scriptdir, 'cht-colors-pinyin.scss'), 'w') as f:
    for c in colors:
        f.write(f"${c['pinyin'].upper()}: {c['hex']};\n")


