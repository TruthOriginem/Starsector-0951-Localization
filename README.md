# Starsector-095-Localization

[TOC]

## Python环境: 3.8.5
| 文件                  | 作用                                                      |
| --------------------- | --------------------------------------------------------- |
| handleVariantNames    | 处理指定文件夹中所有装配名，并更新/使用映射json用于翻译。 |
| swapLangFile          | 用来更替汉化文件和英文文件的脚本。                        |
| FindDifference        | 查找俩个版本直接的差异。                                  |
| variant_name_map.json | 装配名映射文件，英文名对应汉化名，可后继继续更新。        |
## 文件夹内容
"版本号 + data"是游戏版本 data 文件夹

"localization" 指的是需要翻译的内容

"original" 指的是相应的英文原版内容，不要改动(如果有漏的就加进 original 和 localization)

## 注意
目前大内容只剩下 rules.csv 和校对，请希望帮助汉化的小伙伴们先联系汉化组。

通过 QQ 553816216 添加 议长 的好友，注明你的来历和英语水平。

添加需要翻译的内容时，先复制到**original**文件夹备份，然后再复制到**localization**文件夹进行翻译。

## 译名表
在这里放置统一译名。

| 英文名                  | 译名               |
| ----------------------- | ------------------ |
| hegemony                | 霸主               |
| Janus Device            | ""双面神""装置     |
| [REDACTED]              | [数据删除]         |
| Nav Buoy                | 导航浮标           |
| Sensor Jammer           | 传感干扰器         |
| Sensor Array            | 传感器阵列         |
| Comm Relay              | 通讯中继站         |
| Probe                   | 探测器             |
| Warning Beacon          | 警告航标           |
| Fusion Lamp             | 聚变射灯           |
| Yellow Star             | 黄矮星             |
| Orange Star             | 橙矮星             |
| Contacts                | 联络人             |
| Galatia Academy         | Galatia 学院       |
| Galatia Academy Station | Galatia 学院空间站 |
| mote                    | 光尘               |
| Hypershunt Tap          | 超分流阀门         |
| Coronal Hypershunt      | 星冕分流器         |


## 修正表
在这里放置统一译名。

| 英文名                  | 旧译名              |新译名             |理由              |
| ----------------------- | ------------------ | ------------------ | ----------------- |
| Enforcer                | 压迫者             | 执法者             |词不达意            |
| SafetyOverdrive         | 安全超载           | 安全协议超驰       |词不达意            |
| Gryphon                 | 鹰头狮             | 狮鹫               |遗留问题           |
| Graviton Beam           | 引力子激光         | 引力子束           |词不达意           |
