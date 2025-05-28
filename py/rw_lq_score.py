# 总成绩＝0.6*初试/5＋0.4*复试

import os
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class AdmissionDataAnalyzer:
    def __init__(self, df_path):
        self.df_path = df_path
        self.year = self._extract_year_from_path()
        self.df = self._load_data()
        self.analysis_columns = ['序号', '初试成绩', '复试成绩', '总成绩']
        self.analysis_df = self.df[self.analysis_columns]

    def _extract_year_from_path(self):
        """从文件路径中提取年份"""
        match = re.search(r"\d+", os.path.basename(self.df_path))
        if not match:
            raise ValueError("文件名中未找到年份数字")
        return match.group()

    def _load_data(self):
        """加载Excel数据"""
        return pd.read_excel(self.df_path)

    def _ensure_dir_exists(self, path):
        """确保目录存在"""
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def save_pairplot(self):
        """绘制并保存pairplot"""
        plt.figure(figsize=(10, 8))
        g = sns.pairplot(self.analysis_df.drop(columns=['序号']))
        output_path = f"../data/pic/软微-录取/{self.year}-pairplot.png"
        self._ensure_dir_exists(output_path)
        g.savefig(output_path, dpi=900)
        plt.close()

    def save_corr_heatmap(self):
        """绘制并保存相关系数热力图"""
        plt.figure(figsize=(8, 6))
        corr = self.analysis_df.corr()
        sns.heatmap(corr, annot=True, cmap='coolwarm')
        plt.title(f"{self.year} 成绩相关系数矩阵")
        output_path = f"../data/pic/软微-录取/{self.year}-corr.png"
        self._ensure_dir_exists(output_path)
        plt.savefig(output_path, dpi=900)
        plt.close()

    def save_split_axis_plot(self):
        """绘制分轴折线图（含回归方程）"""
        plt.figure(figsize=(12, 8))
        gs = gridspec.GridSpec(2, 1, height_ratios=[1, 1], hspace=0.05)

        ax1 = plt.subplot(gs[0])
        ax2 = plt.subplot(gs[1])

        x = self.analysis_df['序号']
        line_style = '--'
        line_alpha = 0.6

        # 初试成绩部分
        y1 = self.analysis_df['初试成绩']
        ax1.plot(x, y1, color='tab:blue', label='初试成绩')

        # 计算并添加回归线
        slope1, intercept1 = np.polyfit(x, y1, 1)
        reg_label1 = f'y={slope1:.3f}x+{intercept1:.1f}'
        ax1.plot(x, slope1 * x + intercept1,
                 color='tab:blue', linestyle=line_style,
                 alpha=line_alpha, label=reg_label1)

        # 复试成绩部分
        y2 = self.analysis_df['复试成绩']
        ax2.plot(x, y2, color='tab:orange', label='复试成绩')

        # 计算并添加回归线
        slope2, intercept2 = np.polyfit(x, y2, 1)
        reg_label2 = f'y={slope2:.3f}x+{intercept2:.1f}'
        ax2.plot(x, slope2 * x + intercept2,
                 color='tab:orange', linestyle=line_style,
                 alpha=line_alpha, label=reg_label2)

        # 总成绩部分
        y3 = self.analysis_df['总成绩']
        ax2.plot(x, y3, color='tab:green', label='总成绩')

        # 计算并添加回归线
        slope3, intercept3 = np.polyfit(x, y3, 1)
        reg_label3 = f'y={slope3:.3f}x+{intercept3:.1f}'
        ax2.plot(x, slope3 * x + intercept3,
                 color='tab:green', linestyle=line_style,
                 alpha=line_alpha, label=reg_label3)

        # 坐标轴设置
        ax1.set_ylim(340, 450)
        ax1.legend(loc='upper right', ncol=2, fontsize=9)
        ax1.tick_params(labelbottom=False)

        ax2.set_ylim(70, 100)
        ax2.legend(loc='upper right', ncol=3, fontsize=9)

        # 断轴效果（保持原样）
        d = 0.5
        kwargs = dict(marker=[(-1, -d), (1, d)], markersize=12,
                      linestyle="none", color='k', mec='k', mew=1, clip_on=False)
        ax1.plot([0, 1], [0, 0], transform=ax1.transAxes, **kwargs)
        ax2.plot([0, 1], [1, 1], transform=ax2.transAxes, **kwargs)

        output_path = f"../data/pic/软微-录取/{self.year}-scores.png"
        self._ensure_dir_exists(output_path)
        plt.savefig(output_path, dpi=900)
        plt.close()

    def calculate_statistics(self):
        """计算并返回统计指标"""
        # 去掉序号这一列
        df_stats = self.analysis_df.drop(columns=['序号'])
        stats = {
            'mean': df_stats.mean(),
            'median': df_stats.median(),
            '75%': df_stats.quantile(0.75),
            'min': df_stats.min(),
            'max': df_stats.max(),
            'std': df_stats.std()
        }
        return pd.DataFrame(stats).round(2)


def main(path):
    analyzer = AdmissionDataAnalyzer(path)

    # 绘制图形
    analyzer.save_pairplot()
    analyzer.save_corr_heatmap()
    analyzer.save_split_axis_plot()

    # 计算并显示统计量
    stats_df = analyzer.calculate_statistics()
    print("统计分析结果：")
    print(stats_df)


# 使用示例
if __name__ == "__main__":
    main(path="../data/rw/2025录取.xlsx")
    main(path="../data/rw/2024录取.xlsx")
    main(path="../data/rw/2023录取.xlsx")
    main(path="../data/rw/2022录取.xlsx")
    main(path="../data/rw/2021录取.xlsx")
    main(path="../data/rw/2020录取.xlsx")
