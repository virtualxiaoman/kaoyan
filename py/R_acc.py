# 正确率分析与绘图

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize


class AccuracyAnalyzer:
    def __init__(self, file_path):
        """
        初始化AccuracyAnalyzer类，读取正确率表格并准备数据
        :param file_path: 输入文件路径，假设文件是处理过的P-正确率-xxx.xlsx格式
        """
        self.file_path = file_path
        # 读取数据
        self.df = pd.read_excel(file_path)

        # 提取文件名中的学科信息并生成保存路径
        self.subject = file_path.split('-')[-1].split('.')[0]
        self.save_path = f"../data/pic/正确率/{self.subject}.png"

        # 初始化空的DataFrame用于正确率数据
        self.acc_df = self.df.filter(regex=r'正确率')  # 获取所有包含"正确率"的列

        # 获取最后一行 'Sum' 数据
        self.acc_sum_df = self.acc_df[self.df['书名'] == 'Sum']
        # 删除最后一行 'Sum' 数据
        self.acc_df = self.acc_df[self.df['书名'] != 'Sum']

        # print(self.acc_sum_df)
        # print("-"*50)
        # print(self.acc_df)

    def plot_correct_rate(self):
        """
        绘制正确率随刷题次数的变化曲线图
        """
        plt.rcParams['font.sans-serif'] = ['SimSun']  # 设置中文显示
        plt.rcParams['axes.unicode_minus'] = False  # 处理负号显示问题

        # 将x设为index+df的'书名'列，这样就可以显示次数+书名
        df_temp = self.df[self.df['书名'] != 'Sum'].copy()
        x = df_temp.index + 1
        x = x.astype(str) + '-' + df_temp['书名']
        # # 在x最前面加上一个0，这样就可以显示legend
        # x = np.insert(x.values, 0, '0')
        # print(x)
        # x = np.arange(1, len(self.acc_df) + 1)  # 横轴为刷题次数，假设每一行代表一次刷题

        # 绘制全书的正确率
        full_book_rate = self.acc_df.iloc[:, 0]  # 假设第一个章节为全书
        full_book_acc_sum = float(self.acc_sum_df.iloc[:, 0].values[0])
        print(f"[log] {self.subject}全书平均正确率：{full_book_acc_sum:.5f}")
        plt.figure(figsize=(10, 6))
        plt.plot(x, full_book_rate, linestyle='-', color='#66CCFF', linewidth=4, marker='o',
                 label=f'全书-{full_book_acc_sum:.3f}')
        plt.fill_between(x, full_book_rate, alpha=0.1, color='red')

        # # 设置颜色映射，确保在0到1之间
        # norm = Normalize(vmin=-0.15, vmax=0.15)  # 使用一个较小的范围来增加颜色差异
        # cmap = plt.get_cmap('Spectral')  # 选择Spectral颜色映射，或者你可以用 'RdYlGn' 或其他
        norm = Normalize(vmin=-0.15, vmax=0.1)  # 通过调整范围，让颜色对比更明显
        cmap = plt.get_cmap('RdYlGn')  # 使用'RdYlGn'颜色映射，红色表示差，绿色表示好

        score_diff_list = list()  # 存储每个章节的正确率与全书的差距

        # 绘制其他章节的正确率
        for col in self.acc_df.columns[1:]:  # 从第二列开始绘制其他章节
            chapter_rate = self.acc_df[col]
            # 计算该章节正确率的平均值
            avg_chapter_rate = self.acc_sum_df[col].values[0]  # 取Sum行的正确率
            # 计算与全书正确率的差距
            score_diff = (avg_chapter_rate - full_book_acc_sum) / full_book_acc_sum

            # 这个代码是为了防止重复的颜色
            for sd in score_diff_list:
                if abs(score_diff - sd) < 0.03:
                    score_diff -= 0.02

            score_diff_list.append(score_diff)

            # 映射差距为颜色并提取正确的颜色格式
            color = cmap(norm(score_diff))  # 获取RGBA格式的颜色
            color = color[:3]  # 取RGB（去掉透明度）

            col_name = col.split('-')[0]
            label_str = f"{col_name}-{avg_chapter_rate:.2f}"
            # 绘制章节正确率曲线
            plt.plot(x, chapter_rate, linestyle='--', marker='o', color=color,
                     label=label_str, alpha=0.7)

        # # 绘制平均正确率曲线
        # avg_rate = self.acc_df.mean(axis=1)
        # plt.plot(x, avg_rate, linestyle='-', color='blue', linewidth=2, marker='s', label='平均正确率')
        # plt.fill_between(x, avg_rate, alpha=0.1, color='blue')

        # 设置图表
        plt.xlabel('刷题次数')
        plt.ylabel('正确率')
        plt.xlim(-1, len(self.acc_df)-1)  # 设置从-1开始时为了显示legend，不然好挤啊
        plt.xticks(rotation=45, fontsize=8)  # 设置旋转45度
        plt.ylim(0.4, 1.05)
        plt.grid(True)
        plt.legend(loc='upper left')
        plt.title(f'{self.subject} 正确率随练习的变化')
        plt.tight_layout()

        # 保存图表为PNG文件
        plt.savefig(self.save_path, dpi=900)
        # plt.show()


def main(path):
    file_path = path
    analyzer = AccuracyAnalyzer(file_path)
    analyzer.plot_correct_rate()


if __name__ == '__main__':
    main("../data/xlsx/P-正确率-高数2024.xlsx")
    main("../data/xlsx/P-正确率-线代2024.xlsx")
    main("../data/xlsx/P-正确率-概率论2024.xlsx")
