import dataclasses
import json
import logging
from csv import DictReader, DictWriter
from dataclasses import dataclass
from pathlib import Path

from typing import Set, Dict, Tuple, List

logging.basicConfig()
logging.root.setLevel(logging.NOTSET)
logger = logging.getLogger(__name__)
logger.setLevel(logging.NOTSET)

PROJECT_DIRECTORY = Path(__file__).parent
ORIGINAL_PATH = PROJECT_DIRECTORY / 'original'
TRANSLATION_PATH = PROJECT_DIRECTORY / 'localization'
PARA_TRANZ_PATH = PROJECT_DIRECTORY / 'para_tranz'


def relative_path(path: Path) -> Path:
    try:
        return path.relative_to(PROJECT_DIRECTORY)
    except Exception as _:
        return path


@dataclass(frozen=True)
class String:
    key: str
    original: str
    translation: str

    def as_dict(self) -> Dict:
        d = dataclasses.asdict(self)
        # 如果翻译为空，则不导出该值
        if not self.translation:
            d.pop('translation')
        return d


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


class CsvFile(DataFile):
    def __init__(self, path: Path, id_column_name: str, text_column_names: Set[str],
                 original_path: Path = None, translation_path: Path = None):
        super().__init__(path, original_path, translation_path)
        self.id_column_name = id_column_name  # csv 中作为 id 的列名
        self.text_column_names = text_column_names  # 包含要翻译文本的列名

        self.column_names = []

        self.original_data = []
        self.original_id_data = {}
        self.translation_data = []
        self.translation_id_data = {}

        self.load_original_and_translation_data()

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
        if len(self.original_data) != len(self.translation_data):
            logger.warning(
                f'文件 {relative_path(self.path)} 所加载的原文与译文数据量不匹配：加载原文 {len(self.original_data)} 条，译文 {len(self.translation_data)} 条')
        if len(self.original_id_data) != len(self.translation_id_data):
            logger.warning(
                f'文件 {relative_path(self.path)} 所加载的未被注释且不为空的原文与译文在去数据量不匹配：加载有效原文 {len(self.original_id_data)} 条，有效译文 {len(self.translation_id_data)} 条')

    def get_strings(self) -> Set[String]:
        strings = set()
        for row_id, row in self.original_id_data.items():
            first_column = row[list(row.keys())[0]]
            if first_column and not first_column[0] == '#':  # 只导出不为空且没有被注释行内的词条
                for col in self.text_column_names:
                    key = f'{self.path.stem}#{row_id}${col}'  # 词条的id由 文件名-行id-列名 组成
                    original = row[col]
                    translation = ''
                    if row_id in self.translation_id_data:
                        translation = self.translation_id_data[row_id][col]
                        # 如果尚未翻译（不包含中文），则将翻译结果设置为空
                        if not contains_chinese(translation):
                            translation = ''
                    strings.add(String(key, original, translation))
        return strings

    def update_strings(self, strings: Set[String]) -> None:
        for s in strings:
            key = s.key  # type:str
            column = key.split('$')[-1]
            if key in self.translation_id_data:
                self.translation_id_data[key][
                    column] = s.translation if s.translation else s.original

    def update_strings_from_json(self) -> None:
        if self.para_tranz_path.exists():
            strings = set()
            with open(self.para_tranz_path, 'r') as f:
                data = json.load(f)  # type:List[Dict]
                for d in data:
                    strings.add(String(d['key'], d['original'], d.get('translation', '')))
            self.update_strings(strings)
            logger.info(
                f'从 {relative_path(self.para_tranz_path)} 加载了 {len(strings)} 个词条到 {relative_path(self.translation_path)}')
        else:
            logger.warning(f'未找到 {self.path} 所对应的 ParaTranz 数据 ({self.para_tranz_path})，未更新词条')

    def save_strings_json(self, ensure_ascii=False) -> None:
        strings = [s for s in self.get_strings() if s.original]  # 只导出原文不为空的词条

        self.para_tranz_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.para_tranz_path, 'w') as f:
            data = []
            for string in strings:
                data.append(string.as_dict())
            json.dump(data, f, ensure_ascii=ensure_ascii)

        logger.info(
            f'从 {relative_path(self.path)} 中导出了 {len(strings)} 个词条到 {relative_path(self.para_tranz_path)}')

    def save_translation_data(self) -> None:
        with open(self.translation_path, 'w', newline='') as f:
            writer = DictWriter(f, fieldnames=self.column_names, lineterminator='\r\n')
            writer.writeheader()
            writer.writerows(self.translation_data)

    @staticmethod
    def load_csv(path: Path, id_column_name: str) -> Tuple[List[str], List[Dict], Dict[str, Dict]]:
        data = []
        id_data = {}
        with open(path, 'r', errors='ignore') as csv_file:
            rows = list(DictReader(csv_file))
            columns = list(rows[0].keys())
            for i, row in enumerate(rows):
                row_id = row[id_column_name]  # type:str
                first_column = row[columns[0]]
                # 只在 id-row mapping 中存储不为空且没有被注释的行
                if first_column and not first_column[0] == '#':
                    if row_id in id_data:
                        raise ValueError(f'文件 {path} 第 {i} 行 {id_column_name}="{row_id}" 的值在文件中不唯一')
                    id_data[row_id] = row
                data.append(row)
        return columns, data, id_data


# https://segmentfault.com/a/1190000017940752
def contains_chinese(s: str) -> bool:
    for _char in s:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False


def load_csv_files() -> List[CsvFile]:
    logger.info('开始读取游戏原文与译文数据')
    with open(PROJECT_DIRECTORY / 'para_tranz_map.json') as f:
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


if __name__ == '__main__':
    print('欢迎使用 远行星号 ParaTranz 词条导入导出工具')
    print('请选择您要进行的操作：')
    print('1 - 从原始和汉化文件导出 ParaTranz 词条')
    print('2 - 将 ParaTranz 词条写回汉化文件')

    while True:
        option = int(input('请输入选项：'))
        if option == 1:
            csv_to_paratranz()
            break
        elif option == 2:
            paratranz_to_csv()
            break
        else:
            print('无效选项！')
