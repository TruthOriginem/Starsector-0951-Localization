import os
import pandas as pd

# 由于某些见鬼的原因，需要把rules里的某些未知字符，例如 ’ ‘ “ ”改掉(这几个编码是有问题的)
# 用windows 1252编码打开rules，然后通过中文键盘的单引号双引号来替换

rules_folder = "rules分段"
origin_rule_file = "rules.csv"
target_rule_file = "rules汉化校对测试样本(手动替换以测试).csv"

origin_rule_df = pd.read_csv(
    origin_rule_file, encoding='cp1252').set_index('id')
repeat_counting = {}

for root, sub_folders, filenames in os.walk(rules_folder):
    for file in filenames:
        if file.startswith("rules") and file.endswith(".csv"):
            filepath = os.path.join(root, file)
            print("正在聚集rule分段:"+file)
            single_rule_df = pd.read_csv(filepath).set_index('id')
            for id, item in origin_rule_df.iterrows():
                if id and str(id) != 'nan' and not str(id).startswith('#'):
                    try:
                        origin_rule_df.loc[id] = single_rule_df.loc[id]
                        repeat_counting[id] = repeat_counting.get(id, 0)+1
                    except:
                        pass
            print("该分段聚集完成")
origin_rule_df.to_csv(target_rule_file, encoding="utf-8")
for key, value in repeat_counting.items():
    if value > 1:
        print(key+"存在"+str(value-1)+"个重复段")

input("重新聚集完成，按任意键结束")
