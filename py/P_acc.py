# 正确率处理

import pandas as pd
import re
import numpy as np


class AccuracyProcessor:
    def __init__(self, file_path):
        self.file_path = file_path  # "../data/xlsx/正确率-高数2024.xlsx"
        self.df = pd.read_excel(file_path)
        self.subject = file_path.split('-')[-1].split('.')[0].split('2')[0]  # 2是年份，如2024
        # print(f"[log] 正在处理 {self.subject} 的正确率数据...")
        self.validate_correct_rate()

    def validate_correct_rate(self):
        """
        检查正确率是否准确，并输出错误的元素
        """
        error_elements = []
        for i, row in self.df.iterrows():
            # 选择第四列（全书正确率）
            full_book_correct = row.iloc[3]
            if full_book_correct == '-':  # 如果是"-"表示没有该题目，跳过
                continue
            full_book_x, full_book_y = map(int, full_book_correct.split('=')[0].split('/'))
            full_book_acc = float(full_book_correct.split('=')[1].strip('%')) / 100
            full_book_calculated_rate = full_book_x / full_book_y
            if abs(full_book_calculated_rate - full_book_acc) > 0.01:
                error_elements.append((i, 3, full_book_correct, 'x/y比例错误'))

            for col in self.df.columns[4:]:
                if isinstance(row[col], str):  # 确保该列是类似 '92/109=84.4%' 的格式
                    if '-' in row[col]:  # 如果是"-"表示没有该题目，跳过
                        # print(f"注意：第{i}行的第{col}列为'-'")
                        continue
                    try:
                        x, y_rate = row[col].split('=')
                        x_num, y_num = map(int, x.split('/'))
                        rate = float(y_rate.strip('%')) / 100

                        # 检查比例是否一致
                        if abs(x_num / y_num - rate) > 0.01:  # 如果差异大于0.01，就认为是错误的
                            error_elements.append((i, col, row[col], 'x/y比例错误'))

                        # 检查与全书的x/y比例是否一致
                        sum_x = sum([int(x.split('/')[0]) for x in row[4:].dropna() if isinstance(x, str) and '/' in x])
                        sum_y = sum([int(x.split('/')[1].split('=')[0]) for x in row[4:].dropna() if
                                     isinstance(x, str) and '/' in x])
                        if sum_x != full_book_x or sum_y != full_book_y:
                            error_elements.append((i, col, row[col],
                                                   f'与全书x/y比例不一致,sum_x={sum_x}, sum_y={sum_y}'))

                    except Exception as e:
                        error_elements.append((i, col, row[col]))
                        print(f"\033[91m [Error] parsing value {row[col]} in row {i}, column {col}: {e}\033[0m")

        # 输出错误的元素
        for item in error_elements:
            print(f"\033[91m [ERROR] Row {item[0]} - Column {item[1]}: {item[2]}-错误类型: {item[3]}\033[0m")

    def extract_and_calculate_accuracy(self):
        # 遍历表格的每一列（从第4列开始，包含每个学科的正确率信息）
        for col in self.df.columns[3:]:
            correct_column = f"{col}-正确题数"
            total_column = f"{col}-总题数"
            accuracy_column = f"{col}-正确率"

            # 提取正确题数和总题数
            correct_nums = []
            total_nums = []
            accuracies = []

            for value in self.df[col]:
                match = re.search(r'(\d+)/(\d+)', str(value))
                if match:
                    correct = int(match.group(1))
                    total = int(match.group(2))
                    correct_nums.append(correct)
                    total_nums.append(total)
                    accuracy = round(correct / total, 4)  # 计算正确率，保留四位小数
                    accuracies.append(accuracy)
                else:
                    correct_nums.append(None)
                    total_nums.append(None)
                    accuracies.append(None)

            # 将提取的数据添加到DataFrame中
            self.df[correct_column] = correct_nums
            self.df[total_column] = total_nums
            self.df[accuracy_column] = accuracies

        # 计算各列的总和，并添加一行"Sum"
        sum_row = {'书名': 'Sum', '次数': np.nan, '时间': np.nan}  # '书名'列为Sum，'次数'和'时间'列为NaN

        # 对正确题数和总题数列进行求和
        for col in self.df.columns[3:]:
            if col.endswith('-正确题数'):
                sum_row[col] = self.df[col].sum()
            elif col.endswith('-总题数'):
                sum_row[col] = self.df[col].sum()
            elif col.endswith('-正确率'):
                # 正确率不求和，直接计算最后一行的正确率
                correct_column = col.replace('-正确率', '-正确题数')  # 查找对应的"正确题数"列
                total_column = col.replace('-正确率', '-总题数')
                sum_row[col] = round(sum_row[correct_column] / sum_row[total_column], 4)

        # 将 sum_row 转换为 DataFrame，并使用 pd.concat() 来添加
        sum_row_df = pd.DataFrame([sum_row])  # 将 sum_row 转换为 DataFrame
        self.df = pd.concat([self.df, sum_row_df], ignore_index=True)

        # 删除原先的各科目列
        if self.subject == '高数':
            columns_to_remove = ['高数全书', '极限与连续', '一元微分', '多元微分',
                                 '微分方程', '一元积分', '多元积分', '曲线曲面积分',
                                 '无穷级数', '空间解析几何']
        elif self.subject == '线代':
            columns_to_remove = ['线代全书', '行列式', '矩阵', '向量', '线性方程组', '特征值', '二次型']
        elif self.subject == '概率论':
            columns_to_remove = ['概率论全书', '随机事件', '随机变量', '多维随机变量', '数字特征', '大数定律',
                                 '数理统计', '参数估计', '假设检验']
        else:
            columns_to_remove = []
            print("[ERROR] 未知学科，无法删除列")

        self.df.drop(columns=columns_to_remove, inplace=True)

    def save_processed_file(self):
        # 生成保存路径，文件名前加上 'P-'
        save_path = self.file_path.replace('正确率', 'P-正确率')
        self.df.to_excel(save_path, index=False)
        print(f"[log] 文件已保存为: {save_path}")


def main(path):
    file_path = path
    processor = AccuracyProcessor(file_path)
    processor.extract_and_calculate_accuracy()
    processor.save_processed_file()


if __name__ == "__main__":
    main("../data/xlsx/正确率-高数2024.xlsx")
    main("../data/xlsx/正确率-线代2024.xlsx")
    main("../data/xlsx/正确率-概率论2024.xlsx")
