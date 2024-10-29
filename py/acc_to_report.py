import pandas as pd
import re
from scipy.stats import beta
import matplotlib.pyplot as plt


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


# 使用示例
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

plt.rcParams['font.sans-serif'] = ['SimSun']
plt.rcParams['axes.unicode_minus'] = False


# todo 有问题。1。全书没有化为三个课程。2。全画在第一个图上了。
def plot_acc_results(acc_result):
    # 设置画布和子图布局
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    course_titles = ['高等数学', '线性代数', '概率论']

    # 迭代每个课程，并在对应的子图上绘制
    for i, (course, ax) in enumerate(zip(course_titles, axes)):
        for section, acc_values in acc_result.items():
            if i < len(acc_values):
                # 前n个作为实线绘制
                ax.plot(acc_values[i][:-1], label=section, linestyle='-', marker='o')
                # 最后一个总准确率作为红色虚线
                ax.axhline(acc_values[i][-1], color='red', linestyle='--', label=f"{section} (总体)")

        # 设置图表属性
        ax.set_title(course)
        ax.set_xlabel("次数")
        ax.set_ylabel("准确率")
        ax.legend(loc='best')
        ax.grid(True)

    plt.tight_layout()
    plt.show()


# 调用绘图函数
plot_acc_results(acc_result)

# # 绘制每个板块的准确率曲线
# for section, acc_values in acc_result.items():
#     # 提取前 n 个值和总准确率
#     book_accs = acc_values[0][:-1]  # 前 n 个书籍的准确率
#     total_acc = acc_values[0][-1]   # 总准确率
#
#     # 绘制曲线
#     plt.figure(figsize=(8, 6))
#     plt.plot(range(1, len(book_accs) + 1), book_accs, marker='o', label='每本书的准确率')
#     plt.axhline(total_acc, color='r', linestyle='--', label='总准确率')
#
#     # 设置图例、标题和标签
#     plt.title(f"{section} - 准确率变化曲线")
#     plt.xlabel("书籍编号")
#     plt.ylabel("准确率")
#     plt.ylim(0, 1)
#     plt.legend()
#     plt.show()
