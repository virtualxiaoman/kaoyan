import pandas as pd
import pickle
import matplotlib.pyplot as plt
import numpy as np
import os
from sklearn.preprocessing import StandardScaler
import seaborn as sns


class DataFrameMerger:
    def __init__(self, df_list):
        self.df_list = df_list
        self.df_all = None

    def merge_dfs(self):
        # 去掉每个df中的 "时间段" 列，防止后续合并冲突
        dfs_cleaned = [df.drop(columns=['时间段'], errors='ignore') for df in self.df_list]

        df_all = pd.concat(dfs_cleaned)  # 将所有DataFrame合并为一个

        # 按 "日期" 进行分组，"上"、"下"、"晚"、"总时长(h)" 进行求和，"备注" 字符串拼接
        df_grouped = df_all.groupby("日期", as_index=False).agg({
            "上": "sum",  # 上午时长求和
            "下": "sum",  # 下午时长求和
            "晚": "sum",  # 晚上时长求和
            "总时长(h)": "sum",  # 总时长求和
            "备注": lambda x: '  '.join(filter(None, x))  # 拼接备注，忽略空值
        })
        # print(df_grouped)
        # # 将日期格式转化为标准日期格式，手动添加年份（如2024年）
        # df_grouped['日期'] = pd.to_datetime(f'{current_year}.' + df_grouped['日期'].astype(str), format='%Y.%m.%d',
        #                                     errors='coerce')
        # print(df_grouped)
        # 按照日期进行排序
        df_grouped = df_grouped.sort_values(by='日期').reset_index(drop=True)

        # 将排序后的df_grouped保存到self.df_all
        self.df_all = df_grouped


class StudyTimeAnalyzer:
    def __init__(self, df):
        self.df = df
        self.df['日期'] = pd.to_datetime(self.df['日期'])  # 确保日期是datetime类型
        self.df.set_index('日期', inplace=True)  # 将日期设置为索引，方便后续操作

    def plot_total_time(self):
        """绘制全过程的总时长曲线，并保存到文件"""
        plt.figure(figsize=(10, 5))
        plt.plot(self.df.index, self.df['总时长(h)'], label="总时长", color="blue")
        plt.grid(True)
        plt.title('Total Study Time Over Time')
        plt.ylabel('Total Hours (h)')
        plt.xlabel('Date')
        plt.tight_layout()

        # 保存图像
        if not os.path.exists('../data/pic'):
            os.makedirs('../data/pic')
        plt.savefig('../data/pic/study_time_all.png')
        plt.close()

    def plot_monthly_analysis(self):
        """对每个月进行早中晚、总时长的绘制"""
        for year_month, group in self.df.groupby(self.df.index.to_period('M')):
            plt.figure(figsize=(12, 6))

            # 画出各个时间段的曲线
            plt.plot(group.index, group['总时长(h)'], label="Total Hours", color="black", linestyle='-', linewidth=2)
            plt.plot(group.index, group['上'], label="Morning", color="blue", linestyle='--')
            plt.plot(group.index, group['下'], label="Afternoon", color="green", linestyle='--')
            plt.plot(group.index, group['晚'], label="Evening", color="red", linestyle='--')

            plt.title(f'Study Time Analysis for {year_month}')
            plt.ylabel('Hours (h)')
            plt.xlabel('Date')
            plt.legend(loc='upper left')
            plt.grid(True)

            # 旋转x轴标签，方便查看
            plt.xticks(rotation=45)
            plt.tight_layout()

            # 保存图像
            save_path = f'../data/pic/study_time_{year_month}.png'
            plt.savefig(save_path)
            plt.close()

    def analyze_corr(self):
        """计算各个时间段的相关性，并进行标准化分析"""
        # 去掉备注列
        df_numeric = self.df[['上', '下', '晚', '总时长(h)']]

        # 标准化处理
        scaler = StandardScaler()
        df_scaled = scaler.fit_transform(df_numeric)
        df_scaled = pd.DataFrame(df_scaled, columns=df_numeric.columns, index=self.df.index)

        # 相关性矩阵
        corr_matrix = df_numeric.corr()

        # 打印相关性矩阵
        print("相关性矩阵:")
        print(corr_matrix)

        # 绘制热力图
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f",
                    xticklabels=['Morning', 'Afternoon', 'Evening', 'Total Hours'],
                    yticklabels=['Morning', 'Afternoon', 'Evening', 'Total Hours'])
        plt.title("Correlation Heatmap")
        plt.savefig("../data/pic/correlation_heatmap.png")  # 保存热力图

        return corr_matrix


if __name__ == '__main__':
    with open('../data/pkl/study_time_df_list.pkl', 'rb') as f:
        df_list = pickle.load(f)

    merger = DataFrameMerger(df_list)
    merger.merge_dfs()
    print(merger.df_all)

    with open('../data/pkl/study_time_df_all.pkl', 'wb') as f:
        pickle.dump(merger.df_all, f)

    with open('../data/pkl/study_time_df_all.pkl', 'rb') as f:
        df_all = pickle.load(f)

    analyzer = StudyTimeAnalyzer(df_all)
    analyzer.plot_total_time()  # 绘制全过程的总时长曲线
    analyzer.plot_monthly_analysis()  # 绘制每个月的学习时长分析图
    corr_matrix = analyzer.analyze_corr()  # 进行相关性分析
