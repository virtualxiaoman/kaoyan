import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.ticker import MaxNLocator

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
# 设置pd列全部显示
pd.set_option('display.max_columns', None)


class ExamScoreAnalyzer:
    def __init__(self, df_path):
        self.df_path = df_path

    def read_and_filter_data(self):
        # 读取Excel文件
        df = pd.read_excel(self.df_path)
        print(df)
        # 提取指定的四列
        filtered_df = df[['序号', '初试成绩', '复试成绩', '总成绩']]
        return filtered_df

    def compute_descriptive_statistics(self, df):
        # 计算描述性统计信息，包括均值、中位数、75%分位数等
        stats_summary = df.describe()
        # 计算标准差、偏度、峰度等更多统计量
        extended_stats = pd.DataFrame({
            'mean': df.mean(),
            'median': df.median(),
            '75%_percentile': df.quantile(0.75),
            'min': df.min(),
            'max': df.max(),
            'std': df.std(),
            'skewness': df.skew(),
            'kurtosis': df.kurtosis()
        })
        return extended_stats

    def analyze_score_relationships(self, df):
        # 计算成绩之间的相关性
        # 使用皮尔逊相关系数
        pearson_corr = df.corr(method='pearson')
        # 使用斯皮尔曼秩相关系数
        spearman_corr = df.corr(method='spearman')
        return pearson_corr, spearman_corr

    def visualize_score_distributions(self, df):
        # 绘制成绩分布的箱线图和直方图
        fig, axs = plt.subplots(1, 2, figsize=(14, 6))

        # 箱线图
        sns.boxplot(data=df.drop(columns=['序号']), ax=axs[0])
        axs[0].set_title('成绩分布箱线图')
        axs[0].set_xticklabels(['初试成绩', '复试成绩', '总成绩'], rotation=45)

        # 直方图
        axs[1].hist([df['初试成绩'], df['复试成绩'], df['总成绩']],
                    label=['初试成绩', '复试成绩', '总成绩'],
                    bins=10,
                    stacked=True)
        axs[1].set_title('成绩分布直方图')
        axs[1].legend()

        plt.tight_layout()
        plt.show()

    def visualize_score_correlations(self, df):
        # 绘制成绩之间的散点图矩阵
        sns.pairplot(df.drop(columns=['序号']))
        plt.suptitle('成绩之间的关系散点图矩阵')
        plt.tight_layout()
        plt.show()

    def visualize_score_correlation_map(self, pearson_corr):
        # 绘制相关性热图
        plt.figure(figsize=(8, 6))
        sns.heatmap(pearson_corr, annot=True, cmap='coolwarm',
                    cbar_kws={'label': '皮尔逊相关系数'})
        plt.title('成绩之间的相关性热图')
        plt.show()

    def visualize_score_line_chart(self, df):
        # 将序号作为横轴，绘制各成绩的折线图
        plt.figure(figsize=(12, 6))
        plt.plot(df['序号'], df['初试成绩'], 'o-', label='初试成绩')
        plt.plot(df['序号'], df['复试成绩'], 's-', label='复试成绩')
        plt.plot(df['序号'], df['总成绩'], 'D-', label='总成绩')
        plt.title('各考生三类成绩对比')
        plt.xlabel('序号')
        plt.ylabel('成绩')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.show()

    def run_analysis(self):
        # 执行完整的分析流程
        filtered_df = self.read_and_filter_data()

        # 计算统计特征
        stats = self.compute_descriptive_statistics(filtered_df)
        print("描述性统计信息:")
        print(stats)
        print("\n")

        # 分析成绩之间的关系
        pearson_corr, spearman_corr = self.analyze_score_relationships(filtered_df)
        print("皮尔逊相关系数:")
        print(pearson_corr)
        print("\n斯皮尔曼相关系数:")
        print(spearman_corr)
        print("\n")

        # 可视化成绩分布
        self.visualize_score_distributions(filtered_df)

        # 可视化成绩关系
        self.visualize_score_correlations(filtered_df)

        # 绘制相关性热图
        self.visualize_score_correlation_map(pearson_corr)

        # 绘制各考生三类成绩对比图
        self.visualize_score_line_chart(filtered_df)

        # 将结果转化为JSON格式返回
        return {
            'descriptive_statistics': stats.to_dict(),
            'pearson_correlation': pearson_corr.to_dict(),
            'spearman_correlation': spearman_corr.to_dict()
        }


# 使用示例
if __name__ == "__main__":
    analyzer = ExamScoreAnalyzer(df_path="../data/rw/2025录取.xlsx")
    analysis_results = analyzer.run_analysis()
    import json

    # 打印JSON格式的分析结果
    print(json.dumps(analysis_results, indent=4, ensure_ascii=False))