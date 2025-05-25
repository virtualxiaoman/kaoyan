import os
import pandas as pd
from tabula import read_pdf


class PDFTableProcessor:
    def __init__(self, pdf_path, save_path):
        self.pdf_path = pdf_path
        self.save_path = save_path
        self.df = None

    def process_pdf(self):
        """读取PDF并处理表格数据"""
        try:
            # 读取所有页面的表格
            dfs = read_pdf(self.pdf_path, pages='all', lattice=True, multiple_tables=False)
            self.df = pd.concat(dfs).reset_index(drop=True)

            # 清理空行和列名问题
            self.df = self.df.dropna(how='all')
            if '考生编号' not in self.df.columns:
                self.df.columns = self.df.iloc[0]
                self.df = self.df[1:]
            self.df = self.df[self.df['考生编号'] != '考生编号']

            # 处理空考生编号
            self.df['考生编号'] = self.df['考生编号'].astype(str).str.strip()
            self.df = self.df[~self.df['考生编号'].isin(['', 'nan', 'None'])]

            # 新增功能1: 筛选专业为电子信息
            self.df['拟录取专业'] = self.df['拟录取专业'].str.strip()  # 去除前后空格
            self.df = self.df[self.df['拟录取专业'] == '电子信息']  # 精确匹配

            # 新增功能2: 按序号去重（保留第一条）
            self.df['序号'] = pd.to_numeric(self.df['序号'], errors='coerce')  # 强制转为数字
            self.df = self.df.dropna(subset=['序号'])  # 过滤无效序号
            self.df['序号'] = self.df['序号'].astype(int)  # 转为整数
            self.df = self.df.drop_duplicates(subset=['序号'], keep='first')

        except Exception as e:
            raise ValueError(f"PDF处理失败: {str(e)}")

    def save_to_excel(self):
        """保存DataFrame到Excel"""
        if self.df is None:
            raise ValueError("请先执行process_pdf()方法")

        print(f"[log] df的大小: {self.df.shape}")
        # 确保保存目录存在
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)

        try:
            self.df.to_excel(self.save_path, index=False, engine='openpyxl')
        except Exception as e:
            raise ValueError(f"Excel保存失败: {str(e)}")


def main(pdf_path, save_path):
    processor = PDFTableProcessor(
        pdf_path=pdf_path,
        save_path=save_path
    )
    processor.process_pdf()
    processor.save_to_excel()
    print("表格处理完成并已保存至Excel")


# 使用示例
if __name__ == "__main__":
    main(pdf_path="D:/HP/Desktop/小满の大学笔记/考研/资料/软微/软微2025年硕士招生拟录取公示名单.pdf",
         save_path="../data/rw/2025录取.xlsx")
    main(pdf_path="D:/HP/Desktop/小满の大学笔记/考研/资料/软微/软微2023年硕士招生拟录取公示名单.pdf",
         save_path="../data/rw/2023录取.xlsx")
