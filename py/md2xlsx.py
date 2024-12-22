# md转xlxs

import os
import re
import pandas as pd


class MarkdownTableProcessor:
    def __init__(self, md_file_path, output_dir='../data/xslx', table_class_prefix='acc-table'):
        """
        初始化Markdown表格处理类
        :param md_file_path: Markdown文件路径
        :param output_dir: 保存Excel文件的目录
        :param table_class_prefix: 表格div标签的class前缀
        """
        self.md_file_path = md_file_path
        self.output_dir = output_dir
        self.table_class_prefix = table_class_prefix

        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def _extract_tables(self):
        """
        从Markdown文件中提取所有表格数据
        :return: 一个字典，其中键是表格名称，值是表格的DataFrame
        """
        with open(self.md_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # 使用正则表达式提取所有表格的内容和表格名称
        # 这里修改了正则表达式，确保匹配整个<div>标签里的表格内容
        table_pattern = re.compile(r'<div class="([^"]+?)">([\s\S]+?)</div>', re.DOTALL)
        tables = re.findall(table_pattern, md_content)

        table_data = {}
        for table in tables:
            # 提取表格的名称（如 acc-table-高数2024）
            table_name = table[0].split('-')[-1]
            print(f"正在处理表格 '{table_name}'")
            table_content = table[1].strip()
            # print(table_content)

            # 直接提取表格内容并解析
            table_df = self._parse_markdown_table(table_content)
            table_data[table_name] = table_df
            # print(f"已提取表格 '{table_name}'")
            # print(table_df)

        return table_data

    def _parse_markdown_table(self, table_content):
        """
        解析Markdown表格为DataFrame
        :param table_content: Markdown表格的纯文本内容
        :return: DataFrame 格式的表格数据
        """
        # 提取表格的每一行
        rows = table_content.strip().split('\n')

        # 获取列名（表头行），可以假设第一个非空行是表头行
        columns = [col.strip() for col in rows[0].split('|') if col.strip()]

        # 提取表格数据
        data = []
        for row in rows[2:]:  # 跳过表头和分隔行
            # 将每一行按 '|' 分割，并且确保每列都有值（包括空值列，用空字符串填充）
            cells = [cell.strip() if cell.strip() else '' for cell in row.split('|')]
            # print(cells)
            # 去掉cells的首尾空字符串，这是通过 '|' strip多出来的两个
            if cells and cells[0] == '':
                cells = cells[1:]
            if cells and cells[-1] == '':
                cells = cells[:-1]

            # 如果行中的列数与表头列数一致，就加入数据，否则跳过该行
            if len(cells) == len(columns):
                data.append(cells)

        # 返回一个DataFrame
        df = pd.DataFrame(data, columns=columns)
        # print(df)
        return df

    def save_tables_to_excel(self, file_prefix):
        """
        提取所有表格并保存为Excel文件
        :param file_prefix: 文件名前缀
        """
        # 获取所有表格数据
        tables = self._extract_tables()

        for table_name, df in tables.items():
            # 定义文件名
            output_file = os.path.join(self.output_dir, f"{file_prefix}-{table_name}.xlsx")
            # 将DataFrame保存为Excel
            df.to_excel(output_file, index=False)
            print(f"表格 '{table_name}' 已保存至 {output_file}")


class CorrectRateTableProcessor(MarkdownTableProcessor):
    def __init__(self, md_file_path, output_dir='../data/xslx'):
        """
        初始化用于处理正确率表格的类
        :param md_file_path: Markdown文件路径
        :param output_dir: 保存Excel文件的目录
        """
        # 使用父类的构造方法
        super().__init__(md_file_path, output_dir, table_class_prefix='acc-table')

    def save_tables_to_excel(self, file_prefix='正确率'):
        """
        提取正确率表格并保存为Excel文件，文件名前缀为 '正确率'
        """
        super().save_tables_to_excel(file_prefix)


class StudyTimeTableProcessor(MarkdownTableProcessor):
    def __init__(self, md_file_path, output_dir='../data/xslx'):
        """
        初始化用于处理学习时长表格的类
        :param md_file_path: Markdown文件路径
        :param output_dir: 保存Excel文件的目录
        """
        # 使用父类的构造方法
        super().__init__(md_file_path, output_dir, table_class_prefix='time-table')

    def save_tables_to_excel(self, file_prefix='学习时长'):
        """
        提取学习时长表格并保存为Excel文件，文件名前缀为 '学习时长'
        """
        super().save_tables_to_excel(file_prefix)


if __name__ == '__main__':
    # 处理正确率表格
    correct_rate_processor = CorrectRateTableProcessor(md_file_path='../data/正确率.md')
    correct_rate_processor.save_tables_to_excel()

    # 处理学习时长表格
    study_duration_processor = StudyTimeTableProcessor(md_file_path='../data/学习时长.md')
    study_duration_processor.save_tables_to_excel()
