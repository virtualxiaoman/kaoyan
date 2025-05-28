import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class ExamAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.read_excel(file_path)
        self.year = self._extract_year()

        # 验证必要列存在
        self.required_cols = ['科目1成绩', '科目2成绩', '科目3成绩', '科目4成绩', '总成绩']
        self._validate_columns()

    def _extract_year(self):
        """从文件路径中提取年份"""
        # 使用正则表达式匹配文件名中的年份数字
        match = re.search(r"\d+", os.path.basename(self.file_path))
        if match:
            return match.group(0)
        return "未知年份"

    def _validate_columns(self):
        """验证数据是否包含必要的列"""
        missing_cols = [col for col in self.required_cols if col not in self.df.columns]
        if missing_cols:
            raise ValueError(f"数据缺失必要列: {missing_cols}")

    def describe_scores(self):
        """计算描述性统计"""
        stats = self.df[self.required_cols].agg(['mean', 'median',
                                                 lambda x: x.quantile(0.75),
                                                 'min', 'max', 'std'])
        # 将stats的列名改为：政治、英语、数学、408、总成绩
        stats.columns = ['政治', '英语', '数学', '408', '总成绩']
        return stats.rename(index={'<lambda>': '75%'}).round(2)

    def calculate_correlation(self):
        """计算相关性矩阵"""
        return self.df[self.required_cols].corr()

    def save_corr_heatmap(self, output_dir="../data/pic/软微-初试/"):
        """绘制并保存相关系数热力图"""
        # 计算相关系数矩阵
        corr = self.calculate_correlation()

        # 创建热力图
        plt.figure(figsize=(10, 8))
        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(
            corr,
            annot=True,
            fmt=".2f",
            cmap='coolwarm',
            center=0,
            mask=mask,
            vmin=-1,
            vmax=1,
            linewidths=0.5
        )
        plt.title(f"{self.year}年初试成绩相关系数矩阵", fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{self.year}-corr.png")

        # 保存图像
        plt.tight_layout()
        plt.savefig(output_path, dpi=900, bbox_inches='tight')
        plt.close()
        return output_path


def main(file_path):
    try:
        print(f"\n{'=' * 50}")
        print(f"分析文件: {file_path}")

        # 创建分析器实例
        analyzer = ExamAnalyzer(file_path)

        # 计算并显示描述性统计
        stats = analyzer.describe_scores()
        print("\n=== 成绩描述性统计 ===")
        print(stats)

        # 计算并显示相关性矩阵
        corr = analyzer.calculate_correlation()
        # print("\n=== 成绩相关性矩阵 ===")
        # print(corr)

        # 保存相关系数热力图
        output_path = analyzer.save_corr_heatmap()
        print(f"\n相关系数热力图已保存至: {output_path}")

        return stats, corr

    except Exception as e:
        print(f"分析文件 {file_path} 时出错: {str(e)}")
        return None, None


if __name__ == "__main__":
    # 分析多个年份的数据
    years_files = [
        # "../data/rw/2025初试.xlsx",
        "../data/rw/2024初试.xlsx",
        # "../data/rw/2023初试.xlsx",
        "../data/rw/2022初试.xlsx",
        "../data/rw/2021初试.xlsx",
        "../data/rw/2020初试.xlsx"
    ]

    all_stats = {}
    all_corrs = {}

    for file_path in years_files:
        stats, corr = main(file_path)
        if stats is not None:
            year = re.search(r"\d+", os.path.basename(file_path)).group(0)
            all_stats[year] = stats
            all_corrs[year] = corr

    # 可选：保存所有统计结果到Excel
    if all_stats:
        with pd.ExcelWriter("../data/rw/初试成绩分析汇总.xlsx") as writer:
            for year, stats_df in all_stats.items():
                stats_df.to_excel(writer, sheet_name=f"{year}年统计")
            for year, corr_df in all_corrs.items():
                corr_df.to_excel(writer, sheet_name=f"{year}年相关性")
        print("\n所有年份的分析结果已保存至: ../data/rw/初试成绩分析汇总.xlsx")
