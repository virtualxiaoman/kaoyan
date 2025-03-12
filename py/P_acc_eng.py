import re
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

plt.rcParams['font.sans-serif'] = ['SimSun']  # 设置中文显示
plt.rcParams['axes.unicode_minus'] = False  # 处理负号显示问题


def get_content(md_file_path, subject="未设置"):
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 正则匹配并去除所有空格
    pattern = fr'<div\s+class="acc-table-{subject}">\s*(.*?)\s*</div>'
    matches = re.findall(pattern, md_content, re.DOTALL)

    if not matches:
        return ""

    # 去除所有中间空格
    acc_data = matches[0].strip().replace(" ", "").replace("\n", "")
    return acc_data


def draw_accuracy_plot(data, question_per=5, subject="未设置"):
    # 将字符串转换为数字列表
    correct_counts = [int(c) for c in data]
    print(f"总共{len(correct_counts)}题")

    # 计算正确率（百分比）
    correct_rates = [(c / question_per) * 100 for c in correct_counts]
    # print(f"正确率：{correct_rates}")

    # 平均正确率，对correct_counts求和，然后除以总题数(在per相同的情况下其实等价np.mean(correct_rates))
    correct_mean_all = (sum(correct_counts) / len(correct_counts)) / question_per * 100

    x = np.arange(1, len(correct_rates) + 1)
    plt.figure(figsize=(12, 6))

    # 绘制正确率折线
    plt.plot(x, correct_rates, label=f'正确率= {correct_mean_all:.2f}%',
             marker='o', markersize=4, linestyle='-', linewidth=2, alpha=0.8)

    # 绘制线性回归线
    lr = LinearRegression()
    lr.fit(x.reshape(-1, 1), correct_rates)
    # 使用模型预测以生成回归线
    regression_line = lr.predict(x.reshape(-1, 1))
    # y = ax + b
    k = lr.coef_[0]
    b = lr.intercept_
    # 绘制线性回归线
    plt.plot(x, regression_line, color='red', linestyle='--',
             label=f'Linear Fit: y={k:.3f}x+{b:.2f}')
    # coeffs = np.polyfit(x, correct_rates, 1)
    # regression_line = np.polyval(coeffs, x)
    # plt.plot(x, regression_line,
    #          color='red',
    #          linestyle='--',
    #          label='线性回归趋势')

    # 每10题标注一次正确率
    for i in range(0, len(correct_rates), 10):
        start = i
        end = min(i + 10, len(correct_rates))
        chunk = correct_rates[start:end]
        # 计算区间平均正确率
        avg_rate = float(np.mean(chunk))
        # 计算标准差
        std_rate = float(np.std(chunk))

        # 计算标注位置（区间中间）
        mid_x = (start + end + 1) / 2
        plt.text(mid_x, avg_rate, f'{avg_rate:.0f}%±{std_rate:.0f}%', ha='center', va='bottom',
                 fontsize=8, bbox=dict(facecolor='white', alpha=0.6))

    plt.xlabel('文章序号', fontsize=12)
    plt.ylabel('正确率 (%)', fontsize=12)
    plt.title(f"{subject}正确率变化趋势", fontsize=14)
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    # plt.show()
    plt.savefig(f'../data/pic/正确率/英语{subject}.png', dpi=900)
    plt.close()


def main(subject, question_per):
    data = get_content("../data/正确率.md", subject=subject)
    print(f"提取{subject}的原始数据：{data}")
    # 绘制分析图（假设每个数字对应5题）
    draw_accuracy_plot(data, question_per=question_per, subject=subject)


if __name__ == '__main__':
    main("阅读", 5)
