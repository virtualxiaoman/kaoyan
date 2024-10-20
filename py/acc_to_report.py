import pandas as pd
import re
from scipy.stats import beta


class AccTableAnalyzer:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df_list = []

    def read_md_tables(self):
        """读取文件中的表格，并存入self.df_list"""
        with open(self.filepath, 'r', encoding='utf-8') as file:
            content = file.read()

        # 找到所有<div class="acc-table"> ... </div> 之间的内容
        tables = re.findall(r'<div class="acc-table">([\s\S]*?)</div>', content)

        # 依次将表格转换为 DataFrame
        for table in tables:
            # 处理 markdown 表格为二维列表
            table = table.strip()
            rows = table.split('\n')[2:]  # 去除前两行表头定义
            # print(table)
            columns = table.split('\n')[0].split('|')[1:-1]
            print(columns)
            data = [re.split(r'\s*\|\s*', row.strip())[1:-1] for row in rows]
            df = pd.DataFrame(data[0:], columns=[column.strip() for column in columns])
            # print(df)
            self.df_list.append(df)

    def estimate_mastery(self, alpha_prior=1, beta_prior=1, start_row=4):
        """使用Beta分布估计各个板块的掌握程度"""
        mastery_results = []

        for df in self.df_list:
            section_mastery = {}
            for column in df.columns[start_row-1:]:  # 从第start_row=4列开始是各个板块的掌握率
                correct_total = df[column].str.extract(r'(\d+)/(\d+)', expand=True)
                correct_total = correct_total.dropna()  # 去除缺失数据，即为'-'的情况
                correct_total = correct_total.astype(float)

                if correct_total.empty:
                    section_mastery[column] = None  # 如果无数据，跳过
                    continue

                # 累加正确数和总数
                correct_sum = correct_total[0].sum()
                total_sum = correct_total[1].sum()

                # 更新贝叶斯后验分布的参数
                alpha_post = alpha_prior + correct_sum
                beta_post = beta_prior + (total_sum - correct_sum)

                # 计算Beta分布的期望值，作为掌握程度的估计
                estimated_mastery = alpha_post / (alpha_post + beta_post)
                section_mastery[column] = estimated_mastery

            mastery_results.append(section_mastery)

        return mastery_results


# 使用示例
analyzer = AccTableAnalyzer('../data/正确率.md')
analyzer.read_md_tables()
mastery_results = analyzer.estimate_mastery()

# 输出掌握程度的估计结果
for i, mastery in enumerate(mastery_results):
    print(f"Table {i + 1} mastery estimates:")
    for section, estimate in mastery.items():
        print(f"{section}: {estimate:.2%}" if estimate else f"{section}: No data")
