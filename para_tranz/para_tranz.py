import dataclasses
import json
import logging
import re
from _csv import writer
from csv import DictReader, reader
from dataclasses import dataclass
from pathlib import Path

from typing import Set, Dict, Tuple, List, Union

# 设置日志输出
logging.root.setLevel(logging.NOTSET)
logger = logging.getLogger('ParaTranz.py')

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(name)s][%(levelname)s] %(message)s")

ch.setFormatter(formatter)
logger.addHandler(ch)

# 设置游戏原文，译文和Paratranz数据文件路径
PROJECT_DIRECTORY = Path(__file__).parent.parent
ORIGINAL_PATH = PROJECT_DIRECTORY / 'original'
TRANSLATION_PATH = PROJECT_DIRECTORY / 'localization'
PARA_TRANZ_PATH = PROJECT_DIRECTORY / 'para_tranz' / 'output'
CONFIG_PATH = PROJECT_DIRECTORY / 'para_tranz' / 'para_tranz_map.json'


# 尝试计算相对于根目录的位置
def relative_path(path: Path) -> Path:
    try:
        return path.relative_to(PROJECT_DIRECTORY)
    except Exception as _:
        return path


# 用于表示词条的数据结构，创建后为只读
@dataclass(frozen=True)
class String:
    key: str
    original: str
    translation: str
    stage: int = 0  # 词条翻译状态，0为未翻译，1为已翻译，2为已校对

    def as_dict(self) -> Dict:
        d = dataclasses.asdict(self)
        return d


# 用于表示游戏原文、译文文件的抽象类
class DataFile:
    def __init__(self, path: Path, original_path: Path = None, translation_path: Path = None):
        self.path = Path(path)  # 相对 original 或者 localization 文件夹的路径
        self.original_path = ORIGINAL_PATH / Path(original_path if original_path else path)
        self.translation_path = TRANSLATION_PATH / Path(
            translation_path if translation_path else path)
        self.para_tranz_path = PARA_TRANZ_PATH / self.path.with_suffix('.json')

    def get_strings(self) -> Set[String]:
        pass

    def update_strings(self, strings: Set[String]):
        pass


# 用于表示csv格式游戏原文、译文文件的类
class CsvFile(DataFile):
    def __init__(self, path: Path, id_column_name: str, text_column_names: Set[str],
                 original_path: Path = None, translation_path: Path = None):
        super().__init__(path, original_path, translation_path)
        # csv 中作为 id 的列名
        self.id_column_name = id_column_name  # type:Union[str, List[str]] # 作为id的列名，可能为多个
        self.text_column_names = text_column_names  # type:Set[str]  # 包含要翻译文本的列名

        self.column_names = []  # type:List[str]

        # 原文数据，以及id列内容到数据的映射
        self.original_data = []  # type:List[Dict]
        self.original_id_data = {}  # type:Dict[str, Dict]
        # 译文数据，以及id列内容到数据的映射
        self.translation_data = []  # type:List[Dict]
        self.translation_id_data = {}  # type:Dict[str, Dict]

        self.load_original_and_translation_data()

        self.validate()

    # 从原文和译文csv中读取数据
    def load_original_and_translation_data(self) -> None:
        self.column_names, self.original_data, self.original_id_data = self.load_csv(
            self.original_path,
            self.id_column_name)
        logger.info(
            f'从 {relative_path(self.original_path)} 中加载了 {len(self.original_data)} 行原文数据，其中未被注释且不为空的行数为 {len(self.original_id_data)}')
        if self.translation_path.exists():
            _, self.translation_data, self.translation_id_data = self.load_csv(
                self.translation_path,
                self.id_column_name)
            logger.info(
                f'从 {relative_path(self.translation_path)} 中加载了 {len(self.translation_data)} 行译文数据，其中未被注释且不为空的行数为 {len(self.translation_id_data)}')

    # 读取完毕后检查数据有效性
    def validate(self):
        # 检查指定的id列和文字列在游戏文件中是否存在
        if (type(self.id_column_name) == str and self.id_column_name not in self.column_names) and (
                not set(self.id_column_name).issubset(set(self.column_names))):
            raise ValueError(
                f'从 {self.path} 中未找到指定的id列 "{self.id_column_name}"，请检查配置文件中的设置。可用的列包括： {self.column_names}')
        if not set(self.text_column_names).issubset(set(self.column_names)):
            raise ValueError(
                f'从 {self.path} 中未找到指定的文字列 {self.text_column_names}，请检查配置文件中的设置。可用的列包括： {self.column_names}')
        # 检查原文与译文数量是否匹配
        if len(self.original_data) != len(self.translation_data):
            logger.warning(
                f'文件 {relative_path(self.path)} 所加载的原文与译文数据量不匹配：加载原文 {len(self.original_data)} 条，译文 {len(self.translation_data)} 条')
        if len(self.original_id_data) != len(self.translation_id_data):
            logger.warning(
                f'文件 {relative_path(self.path)} 所加载的未被注释且不为空的原文与译文在去数据量不匹配：加载有效原文 {len(self.original_id_data)} 条，有效译文 {len(self.translation_id_data)} 条')

    # 将数据转换为 ParaTranz 词条数据对象
    def get_strings(self) -> Set[String]:
        strings = set()
        for row_id, row in self.original_id_data.items():
            first_column = row[list(row.keys())[0]]
            if first_column and not first_column[0] == '#':  # 只导出不为空且没有被注释行内的词条
                for col in self.text_column_names:
                    key = f'{self.path.name}#{row_id}${col}'  # 词条的id由 文件名-行id-列名 组成
                    original = row[col]
                    translation = ''
                    stage = 1
                    if row_id in self.translation_id_data:
                        translation = self.translation_id_data[row_id][col]
                        # 如果尚未翻译（不包含中文），则将翻译结果设置为空
                        if not contains_chinese(translation):
                            translation = ''
                            stage = 0
                        # 特殊规则：如果rules.csv里的script列中不包含'"'（双引号），则视为已翻译
                        if (self.path.name == 'rules.csv') and (col == 'script') and (
                                '"' not in original):
                            stage = 1
                    strings.add(String(key, original, translation, stage))
        return strings

    # 将数据转换为 ParaTranz 词条数据对象，并保存到json文件中
    def save_strings_json(self, ensure_ascii=False, indent=4) -> None:
        strings = [s for s in self.get_strings() if s.original]  # 只导出原文不为空的词条

        self.para_tranz_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.para_tranz_path, 'w') as f:
            data = []
            for string in strings:
                data.append(string.as_dict())
            json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)

        logger.info(
            f'从 {relative_path(self.path)} 中导出了 {len(strings)} 个词条到 {relative_path(self.para_tranz_path)}')

    # 将传入的 ParaTranz 词条数据对象中的译文数据合并到现有数据中
    def update_strings(self, strings: Set[String]) -> None:
        for s in strings:
            _, id, column = re.split('[#$]', s.key)
            if id in self.translation_id_data:
                self.translation_id_data[id][
                    column] = s.translation if s.translation else s.original

    # 从json文件读取 ParaTranz 词条数据对象中的译文数据合并到现有数据中
    def update_strings_from_json(self) -> None:
        if self.para_tranz_path.exists():
            strings = set()
            with open(self.para_tranz_path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)  # type:List[Dict]
            for d in data:
                # ParaTranz 下载的文件把 \n 转义成了 \\n，需要转回来
                original = d['original'].replace('\\n', '\n')
                translation = d.get('translation', '').replace('\\n', '\n')
                strings.add(String(d['key'], original, translation))
            self.update_strings(strings)
            logger.info(
                f'从 {relative_path(self.para_tranz_path)} 加载了 {len(strings)} 个词条到 {relative_path(self.translation_path)}')
        else:
            logger.warning(f'未找到 {self.path} 所对应的 ParaTranz 数据 ({self.para_tranz_path})，未更新词条')

    # 将译文数据写回译文csv中
    def save_translation_data(self) -> None:
        with open(self.translation_path, 'r', newline='') as f:
            csv = reader(f)
            real_column_names = csv.__next__()

        # 由于部分csv包含多个空列，在用DictReader读取时会被丢弃，为了与源文件保持一致，在此根据原文件重新添加
        real_column_index = {col: real_column_names.index(col) for col in self.column_names if col}

        rows = [real_column_names]

        for dict_row in self.translation_data:
            row = ['' for _ in range(len(real_column_names))]
            for col, value in dict_row.items():
                if col:
                    row[real_column_index[col]] = value
            rows.append(row)
        with open(self.translation_path, 'w', newline='') as f:
            writer(f).writerows(rows)

    @staticmethod
    def load_csv(path: Path, id_column_name: Union[str, List[str]]) -> Tuple[
        List[str], List[Dict], Dict[str, Dict]]:
        """
        从csv中读取数据，并返回列名列表，数据以及id列内容到数据的映射
        :param path: csv文件路径
        :param id_column_name: id列名称，只有一列的话传入列名，有多列传入列名list
        :return: (列名列表, 数据list, id列内容到数据的映射dict)
        """
        data = []
        id_data = {}
        with open(path, 'r', errors="surrogateescape") as csv_file:
            csv_lines = [replace_weird_chars(l) for l in csv_file]
            rows = list(DictReader(csv_lines))
            columns = list(rows[0].keys())
            for i, row in enumerate(rows):
                if type(id_column_name) == str:
                    row_id = row[id_column_name]  # type:str
                else:  # 存在多个 id column
                    row_id = str(tuple([row[id] for id in id_column_name]))  # type:str
                first_column = row[columns[0]]
                # 只在 id-row mapping 中存储不为空且没有被注释的行
                if first_column and not first_column[0] == '#':
                    if row_id in id_data:
                        raise ValueError(f'文件 {path} 第 {i} 行 {id_column_name}="{row_id}" 的值在文件中不唯一')
                    id_data[row_id] = row
                data.append(row)
        return columns, data, id_data


# https://segmentfault.com/a/1190000017940752
# 判断是否包含中文字符
def contains_chinese(s: str) -> bool:
    for _char in s:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False


def load_csv_files() -> List[CsvFile]:
    """
    根据 para_tranz_map.json 设置，批量读取原文、译文csv文件
    :return: CsvFile文件对象列表

    para_tranz_map.json 的格式如下：
    [
        {
            "path": "csv文件路径，使用'/'作分隔符.csv",
            "id_column_name": "csv中作为id的列名",
            "text_column_names": [
              "需要翻译列的列名1",
              "需要翻译列的列名2"
            ]
        },
        {
            "path": "csv文件路径，使用'/'作分隔符.csv",
            "id_column_name": ["作为id的列名1", "作为id的列名2"],
            "text_column_names": [
              "需要翻译列的列名1",
              "需要翻译列的列名2"
            ]
        }
    ]
    """
    logger.info('开始读取游戏原文与译文数据')
    with open(CONFIG_PATH) as f:
        d = json.load(f)
    files = [CsvFile(**mapping) for mapping in d]
    logger.info('游戏原文与译文数据读取完成')
    return files


def csv_to_paratranz():
    for file in load_csv_files():
        file.save_strings_json()
    logger.info('ParaTranz 词条导出完成')


def paratranz_to_csv():
    for file in load_csv_files():
        file.update_strings_from_json()
        file.save_translation_data()
    logger.info('ParaTranz 词条导入到译文数据完成')


# From processWithWiredChars.py
# 由于游戏原文文件中可能存在以Windows-1252格式编码的字符（如前后双引号等），所以需要进行转换
def replace_weird_chars(s: str) -> str:
    return s.replace('\udc94', '""').replace('\udc93', '""').replace('\udc92', "'").replace(
        '\udc85', '...')


if __name__ == '__main__':
    print('欢迎使用 远行星号 ParaTranz 词条导入导出工具')
    print('请选择您要进行的操作：')
    print('1 - 从原始和汉化文件导出 ParaTranz 词条')
    print('2 - 将 ParaTranz 词条写回汉化文件')

    while True:
        option = int(input('请输入选项数字：'))
        if option == 1:
            csv_to_paratranz()
            break
        elif option == 2:
            paratranz_to_csv()
            break
        else:
            print('无效选项！')

    input('程序执行完毕，请按任意键退出')
