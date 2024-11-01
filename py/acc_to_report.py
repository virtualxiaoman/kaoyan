import pandas as pd
import re
import matplotlib.pyplot as plt
import pickle
import numpy as np


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
            # print(columns)
            data = [re.split(r'\s*\|\s*', row.strip())[1:-1] for row in rows]
            df = pd.DataFrame(data[0:], columns=[column.strip() for column in columns])
            # print(df)
            self.df_list.append(df)

    def estimate_mastery(self, alpha_prior=1, beta_prior=1, start_row=4):
        """使用Beta分布估计各个板块的掌握程度"""
        mastery_results = []

        for df in self.df_list:
            section_mastery = {}
            for column in df.columns[start_row - 1:]:  # 从第start_row=4列开始是各个板块的掌握率
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

    def cal_acc(self):
        """计算每本书以及总的准确率"""
        acc_results = {}  # 存放最终结果

        for df in self.df_list:
            for column in df.columns[3:]:  # 跳过书名、次数、时间列
                correct_counts = []
                total_counts = []

                for row in df[column]:
                    if row == '-' or row == '':  # 跳过空数据
                        continue
                    try:
                        # 分离出 "正确数量/总数量" 部分
                        correct_total_part = row.split('=')[0]
                        correct, total = map(int, correct_total_part.split('/'))
                        correct_counts.append(correct)
                        total_counts.append(total)
                    except ValueError:
                        print(f"数据格式错误：{row}")
                        continue

                if correct_counts:
                    book_accs = [correct / total for correct, total in zip(correct_counts, total_counts)]
                    total_acc = sum(correct_counts) / sum(total_counts)

                    if column not in acc_results:
                        acc_results[column] = []

                    acc_results[column].append((*book_accs, total_acc))

        return acc_results


if __name__ == '__main__':
    analyzer = AccTableAnalyzer('../data/正确率.md')
    analyzer.read_md_tables()
    mastery_results = analyzer.estimate_mastery(beta_prior=1)
    acc_result = analyzer.cal_acc()

    print("---------------------------------------------------")
    # 输出掌握程度的估计结果
    for i, mastery in enumerate(mastery_results):
        print(f"Table {i + 1} mastery estimates:")
        for section, estimate in mastery.items():
            print(f"{section}: {estimate:.2%}" if estimate else f"{section}: No data")

    print(acc_result)

    with open('../data/pkl/acc_df_list.pkl', 'wb') as f:
        pickle.dump(analyzer.df_list, f)

    plt.rcParams['font.sans-serif'] = ['SimSun']
    plt.rcParams['axes.unicode_minus'] = False

    # 定义不同书的章节
    books = {
        '高数': ['高数全书', '极限与连续', '一元微分', '多元微分', '微分方程', '一元积分', '多元积分', '曲线曲面积分',
                 '无穷级数', '空间解析几何'],
        '线性代数': ['线代全书', '行列式', '矩阵', '向量', '线性方程组', '特征值', '二次型'],
        '概率论': ['概率论全书', '随机事件', '随机变量', '多维随机变量', '数字特征', '大数定律', '数理统计', '参数估计',
                   '假设检验']
    }


    # 复用函数绘制书的各章节准确率图
    def plot_book_accuracy(book_name, chapters):
        plt.figure()
        for chapter in chapters:
            if chapter in acc_result:
                scores = acc_result[chapter][0]
                x = np.arange(1, len(scores) + 1)
                plt.plot(x, scores, linestyle='-', marker='o', label=f"{chapter}")
                # plt.axhline(y=np.mean(scores), linestyle='-', linewidth=1.2,
                #             label=f"{chapter} (mean)")

        plt.title(f'{book_name} 准确率变化')
        plt.xticks(x)
        plt.xlabel('刷题次数')
        plt.ylabel('准确率')
        plt.ylim(0.5, 1.05)
        plt.legend(loc='best')
        plt.grid(True)
        plt.show()


    # 绘制三本书的准确率变化图
    for book_name, chapters in books.items():
        plot_book_accuracy(book_name, chapters)
