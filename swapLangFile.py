import os


def main():
    print("Swap lang file, please put git project folder in the same position with 'starsector-core' folder.")
    print("Modified from Originem by AnyIDElse")
    cin = input("Enter E to use English files, other to use CN files")

    dir_path = os.path.dirname(os.path.realpath(__file__))
    current_folder = dir_path.split('\\').pop()

    source = 'localization'
    if cin.lower() == 'e':
        source = 'original'

    dir_path = os.path.join(dir_path, source)
    for root, sub_folders, filenames in os.walk(dir_path):
        for file_name in filenames:
            original_file_path = os.path.join(root, file_name)
            new_file_path = os.path.join(root.replace(os.path.join(current_folder, source), 'starsector-core'), file_name)
            print(original_file_path)
            print(new_file_path)

            os.rename(original_file_path, new_file_path)

    print("Lang was changed to " + source)
    input("Press any key to exit.")


if __name__ == '__main__':
    main()
