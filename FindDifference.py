#!/usr/bin/env python
# -*- coding:utf8 -*-
import difflib
import hashlib
import os
import shutil
import codecs


def getPaths(file_dir):
    paths = []
    for root, dirs, files in os.walk(file_dir):
        strip_root = root[len(file_dir) + 1:]
        # print(root)
        for file in files:
            paths.append(os.path.join(strip_root, file))
    return paths


def convertPathToFilename(path):
    result = str(path)
    result = result.replace("/", '-')
    result = result.replace("\\", '-')
    result = result.replace(".", '-')
    return result


def findDiff():
    print("用于查找Source文件夹和Target文件夹的不同，以此来判断更新内容")
    print("最终结果会保存至logs文件夹")
    print()
    source_folder = '095-RC15 data'
    target_folder = '0951-RC6 data'
    general_change_filepath = 'logs/file_changes.log'
    detail_folder = 'logs/details'

    if not os.path.exists(source_folder):
        input('[停止]不存在Original_old文件夹')
        exit()

    new_files_list = []
    changed_files_list = []

    paths = getPaths(target_folder)

    for path in paths:
        target_path = os.path.join(target_folder, path)
        source_path = os.path.join(source_folder, path)
        if not os.path.exists(source_path):
            new_files_list.append(path)
        else:
            md5_original = hashlib.md5(open(target_path,
                                            'rb').read()).hexdigest()
            md5_old = hashlib.md5(open(source_path, 'rb').read()).hexdigest()
            if md5_original != md5_old:
                changed_files_list.append(path)

    general_change_writer = "有变更的文件:\n"
    if changed_files_list:
        general_change_writer += '\n'.join(changed_files_list)
    else:
        general_change_writer += "无\n"

    general_change_writer += "\n新增加的文件:\n"
    if new_files_list:
        general_change_writer += '\n'.join(new_files_list)
    else:
        general_change_writer += "无\n"

    print(general_change_writer)
    with open(general_change_filepath, 'w+', encoding='utf-8') as f:
        f.write(general_change_writer)
        print('已保存至' + general_change_filepath)

    if_continue = input('是否需要生成详细细节?输入y保存至logs/details文件夹(会在这之前清空)，其他键退出\n')
    if if_continue == 'y':
        try:
            if os.path.exists(detail_folder):
                shutil.rmtree(detail_folder)
            os.makedirs(detail_folder)
        except Exception:
            input("请关闭后台的logs/details文件夹")
            exit()
        else:
            d = difflib.HtmlDiff()
            for path in changed_files_list:
                target_path = os.path.join(target_folder, path)
                source_path = os.path.join(source_folder, path)

                with codecs.open(target_path,
                                 'r',
                                 encoding='utf-8',
                                 errors='ignore') as target_f, codecs.open(
                                     source_path,
                                     'r',
                                     encoding='utf-8',
                                     errors='ignore') as source_f:
                    target_content = target_f.readlines()
                    source_content = source_f.readlines()

                with open(os.path.join(detail_folder,
                                       convertPathToFilename(path) + '.html'),
                          'w+',
                          encoding='utf-8') as f:
                    f.write(d.make_file(source_content, target_content))
                    print(path + '生成diff成功')
        input('按任意键退出')


if __name__ == '__main__':
    findDiff()
