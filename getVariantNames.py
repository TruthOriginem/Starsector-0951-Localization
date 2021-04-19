# 此脚本用于从指定目录中获取所有去除重复的装配文件名
import os
import re
import json5

starsector_comment_line = re.compile(r'\s*#')

# Alex将 # 用在json文件中作为注释...


def getSSjsonString(file_path):
    json_string = ''
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        for line in lines:
            if starsector_comment_line.search(line):
                continue
            json_string += line
    return json_string


print("此脚本用于从指定目录中获取所有去除重复的装配文件名...")
# 在这里更改装配文件夹的目录
variants_path = "095-RC12 data/data/variants"
# 装配映射的文件
map_file_path = "variant_name_map.json"

print("当前处理目录为:" + variants_path)
print("保存映射文件为:" + map_file_path)

current_folder = os.path.dirname(os.path.realpath(__file__))
variant_folder = os.path.join(current_folder, variants_path)
variant_map_file = os.path.join(current_folder, map_file_path)

variant_name_list = list()

processed = 0
processed_not_duplicated = 0
for root, sub_folders, filenames in os.walk(variant_folder):
    for filename in filenames:
        file_path = os.path.join(root, filename)
        ignored, ext = os.path.splitext(file_path)
        if not ext == '.variant':
            continue
        json_object = json5.loads(getSSjsonString(file_path))
        if json_object:
            processed += 1
            display_name = json_object['displayName']
            if display_name and not variant_name_list.__contains__(display_name):
                processed_not_duplicated += 1
                print("\r已搜索{}个装配文件，已检索{}个独特装配名...".format(
                    processed, processed_not_duplicated), end=" ")
                variant_name_list.append(display_name)
print()

variant_name_list.sort()


for name in variant_name_list:
    print(name)

print("开始更新映射...")
variant_map_json = json5.load(open(variant_map_file, 'r', encoding='utf-8'))

for name in variant_name_list:
    if not variant_map_json.__contains__(name):
        variant_map_json[name] = ""

print(variant_map_json)
json5.dump(variant_map_json, open(
    variant_map_file, 'w+', encoding='utf-8'), indent=4, quote_keys=True, trailing_commas=False, sort_keys=True)
input("任意键退出")
