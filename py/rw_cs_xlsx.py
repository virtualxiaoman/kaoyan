import pandas as pd
from tabula import read_pdf
import numpy as np


class PDFProcessor:
    def __init__(self, pdf_path, save_path):
        self.pdf_path = pdf_path
        self.save_path = save_path
        self.expected_columns = [
            '序号', '考生姓名', '考生编号', '复试专业',
            '科目1成绩', '科目2成绩', '科目3成绩', '科目4成绩',
            '总成绩', '备注'
        ]
        self.df = None

    def process_pdf(self):
        # 读取PDF表格
        dfs = read_pdf(self.pdf_path, pages='all', lattice=True, multiple_tables=False)

        # 合并所有表格
        self.df = pd.concat(dfs).reset_index(drop=True)
        print(self.df.shape)

        # 检查并修正列名
        if list(self.df.columns) != self.expected_columns:
            if len(self.df.columns) == len(self.expected_columns):
                self.df.columns = self.expected_columns
            else:
                raise ValueError(f"列数不匹配! 预期{len(self.expected_columns)}列，实际{len(self.df.columns)}列")

        # 数据清洗和处理
        self._clean_data()

        # 保存为Excel
        self.df.to_excel(self.save_path, index=False)
        print(f"文件已保存至: {self.save_path}")
        return self.df

    def _clean_data(self):
        """执行数据清洗操作"""
        # 筛选电子信息专业
        self.df['复试专业'] = self.df['复试专业'].str.strip()
        self.df = self.df[self.df['复试专业'] == '电子信息']

        # 处理序号列
        self.df['序号'] = pd.to_numeric(self.df['序号'], errors='coerce')
        self.df = self.df.dropna(subset=['序号'])
        self.df['序号'] = self.df['序号'].astype(int)

        # 按序号去重
        self.df = self.df.drop_duplicates(subset=['序号'], keep='first')

        # 确保成绩列为数值类型
        score_cols = ['科目1成绩', '科目2成绩', '科目3成绩', '科目4成绩', '总成绩']
        for col in score_cols:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

        # 处理备注列缺失值
        self.df['备注'] = self.df['备注'].replace({np.nan: None})


def main(pdf_path, save_path):
    processor = PDFProcessor(
        pdf_path=pdf_path,
        save_path=save_path
    )
    processed_df = processor.process_pdf()


# 使用示例
if __name__ == "__main__":
    main(pdf_path="D:/HP/Desktop/小满の大学笔记/考研/资料/软微/软微2025年硕士研究生复试名单.pdf",
         save_path="../data/rw/2025初试.xlsx")
    main(pdf_path="D:/HP/Desktop/小满の大学笔记/考研/资料/软微/软微2024年硕士研究生复试名单.pdf",
         save_path="../data/rw/2024初试.xlsx")
    main(pdf_path="D:/HP/Desktop/小满の大学笔记/考研/资料/软微/软微2022年硕士研究生复试名单.pdf",
         save_path="../data/rw/2022初试.xlsx")
    main(pdf_path="D:/HP/Desktop/小满の大学笔记/考研/资料/软微/软微2021年硕士研究生复试名单.pdf",
         save_path="../data/rw/2021初试.xlsx")
    main(pdf_path="D:/HP/Desktop/小满の大学笔记/考研/资料/软微/软微2020年硕士研究生复试名单.pdf",
         save_path="../data/rw/2020初试.xlsx")
