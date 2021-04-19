import os
# 用于进行中文和英文的互换，注意不会替换字库，字库要自己安装


def main():
    print("Swap lang file, please put this script and 'localization' folder and 'original' in the same position with 'starsector-core'.")
    print("Modified from Originem by AnyIDElse")
    cin = input("Enter E to use English files, other to use CN files")

    dir_path = os.path.dirname(os.path.realpath(__file__))
    current_folder = dir_path.split('\\').pop() + '\\'
    source = 'localization'
    if cin.lower() == 'e':
        source = 'original'

    dir_path = os.path.join(dir_path, source)
    for root, sub_folders, filenames in os.walk(dir_path):
        changed = []

        for file_name in filenames:
            file_path = os.path.join(root, file_name)
            if file_path in changed:
                continue

            (pure_file_name, extension) = os.path.splitext(file_name)
            original_file_path = os.path.join(root, pure_file_name + extension)
            new_file_path = os.path.join(root.replace(
                current_folder + source, 'starsector-core'), pure_file_name + extension)
            print(original_file_path)
            print(new_file_path)

            os.rename(original_file_path, new_file_path)

    print("Lang was changed to " + source)
    input("Press Any key To Exit.")


if __name__ == '__main__':
    main()
