import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import os
import seaborn as sns
from sklearn.linear_model import LinearRegression


class StudyTimePlotter:
    def __init__(self, file_path):
        # 设置matplotlib字体为Times New Roman (TNR)
        plt.rcParams['font.family'] = 'Times New Roman'

        # 读取表格数据
        self.df = pd.read_excel(file_path)
        self.file_name = os.path.basename(file_path)
        print(f"读取文件：{self.file_name}")

        self._init_df()
        self._init_subject()
        self._init_time()

    # 初始化数据
    def _init_df(self):
        # 确保日期列是日期格式
        df = self.df.copy()
        df['日期'] = pd.to_datetime(df['日期'])

        # 获取最小和最大日期
        min_date = df['日期'].min()
        max_date = df['日期'].max()

        # 生成完整的日期范围
        all_dates = pd.date_range(min_date, max_date, freq='D')

        # 创建一个新的DataFrame，包含所有日期
        complete_df = pd.DataFrame({'日期': all_dates})

        # 合并原始数据和完整的日期数据，然后按日期排序
        merged_df = pd.merge(complete_df, df, on='日期', how='left')
        merged_df = merged_df.sort_values(by='日期')

        # 填充缺失值，如果没有记录就说明是没有学习，时长是0
        merged_df['总时长'] = merged_df['总时长'].fillna(0)
        merged_df['时间段'] = merged_df['时间段'].fillna('')
        merged_df['上午'] = merged_df['上午'].fillna(0)
        merged_df['下午'] = merged_df['下午'].fillna(0)
        merged_df['晚上'] = merged_df['晚上'].fillna(0)
        merged_df['备注'] = merged_df['备注'].fillna('')

        # 删除重复的日期行
        merged_df = merged_df.drop_duplicates(subset='日期', keep='first')

        self.df = merged_df
        # # 查看第70-80行
        # print(self.df.iloc[65:72])

    def _init_time(self):
        self.df['日期'] = pd.to_datetime(self.df['日期'], format='%Y.%m.%d')  # 将日期列转换为日期时间格式
        # 提取星期几信息
        self.df['星期'] = self.df['日期'].dt.day_name()  # 获取星期几（英文）

        # 提取年份和月份信息
        self.df['Year'] = self.df['日期'].dt.year
        self.df['Month'] = self.df['日期'].dt.month
        self.df['Week'] = self.df['日期'].dt.isocalendar().week  # 获取ISO周编号
        self.df['Weekday'] = self.df['日期'].dt.weekday + 1  # 0 = Monday, 6 = Sunday (调整为1-7，方便映射)

        # 手动调整最后几天的周次（2024年12月31日至2024年12月29日），不然ISO周次会出错（当成2025年的第一周）
        last_week_start_date = pd.to_datetime('2024-12-30')
        last_week_end_date = pd.to_datetime('2024-12-31')

        # 选择日期在2024年12月30日至31日之间的数据，修改为最后一周
        self.df.loc[(self.df['日期'] >= last_week_start_date) & (
                self.df['日期'] <= last_week_end_date), 'Week'] = 53  # 改为53
        self.df.loc[(self.df['日期'] >= last_week_start_date) & (
                self.df['日期'] <= last_week_end_date), 'Year'] = 2024  # 确保年份为2024

        # # 打印结果检查
        # print(self.df[['日期', 'Year', 'Month', 'Week', '星期']])

    # 初始化科目名称
    def _init_subject(self):
        subject_name = os.path.splitext(self.file_name)[0].split('-')[-1]  # 假设文件名结构是“P-学习时长-科目年份.xlsx”
        # print(subject_name)
        # 科目名称的替换字典
        subject_dict = {
            '数学2024': 'Math2024',
            '英语2024': 'English2024',
            '政治2024': 'Politics2024',
            '计算机2024': 'CS2024',
            '数学2025': 'Math2025',
            '英语2025': 'English2025',
            '政治2025': 'Politics2025',
            '计算机2025': 'CS2025'
        }
        # 替换为英文
        self.subject = subject_dict.get(subject_name, subject_name)
        print(f"科目：{self.subject}")

    # 绘制总时长折线图
    def plot_total_study_time(self):
        # 对总时长进行线性回归，然后绘制到图像上
        X = self.df.index.values.reshape(-1, 1)
        X = X - X.min()  # 从0开始
        y = self.df['总时长'].values
        lr = LinearRegression()
        lr.fit(X, y)
        # 提取回归直线的斜率和截距
        k = lr.coef_[0]
        b = lr.intercept_

        # 计算总时长的和
        total_study_time = y.sum()

        # 绘制总时长的折线图
        plt.figure(figsize=(10, 6))
        plt.plot(self.df['日期'], self.df['总时长'], label='Total Study Time', color='black',
                 linestyle='-', linewidth=2)
        # 绘制回归直线
        plt.plot(self.df['日期'], k * X + b, label=f'Linear Fit: y={k:.3f}x+{b:.2f}', color='orange',
                 linestyle='-', linewidth=1)

        # 在图上显示总时长的和
        plt.text(0.95, 0.95, f'Total Time: {total_study_time:.2f} hours',
                 horizontalalignment='right', verticalalignment='top',
                 transform=plt.gca().transAxes, fontsize=16, color='red', weight='bold')  # 使用坐标轴相对位置

        plt.xlabel('Date')
        plt.ylabel('Total Time (hours)')
        plt.title(f'{self.subject} - Total Study Time')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()

        # 保存图像
        plt.tight_layout()
        plt.savefig(f'../data/pic/学习时长/{self.subject}-all.png', dpi=900)
        plt.close()

    # 按月绘制学习时长折线图
    def plot_monthly_study_time(self):
        # 按月分组并绘制
        for month in self.df['Month'].unique():
            month_data = self.df[self.df['Month'] == month]
            month_str = f"{self.df['Year'].iloc[0]}-{month:02d}"  # 例如 "2024-09"

            X = month_data.index.values.reshape(-1, 1)
            # 找到X的最小值，然后减去这个最小值，这样X就从0开始了
            X = X - X.min()
            print(X)
            y = month_data['总时长'].values
            lr = LinearRegression()
            lr.fit(X, y)
            # 提取回归直线的斜率和截距
            k = lr.coef_[0]
            b = lr.intercept_

            # 计算总时长的和
            total_study_time = y.sum()

            plt.figure(figsize=(10, 6))
            plt.plot(month_data['日期'], month_data['总时长'], label='Total Time', color='black', linestyle='-',
                     linewidth=2)
            plt.plot(month_data['日期'], month_data['上午'], label='Morning', color='blue', linestyle='--')
            plt.plot(month_data['日期'], month_data['下午'], label='Afternoon', color='red', linestyle='--')
            plt.plot(month_data['日期'], month_data['晚上'], label='Evening', color='green', linestyle='--')

            # 绘制回归直线
            plt.plot(month_data['日期'], k * X + b, label=f'Linear Fit: y={k:.3f}x+{b:.2f}', color='purple',
                     linestyle='-', linewidth=1)

            # 在图上显示总时长的和
            plt.text(0.95, 0.95, f'Total Time: {total_study_time:.2f} hours',
                     horizontalalignment='right', verticalalignment='top',
                     transform=plt.gca().transAxes, fontsize=16, color='red', weight='bold')

            plt.xlabel('Date')
            plt.ylabel('Time (hours)')
            plt.title(f'{self.subject} - {month_str}')
            plt.xticks(rotation=45)
            plt.legend()
            plt.grid(True)

            # 保存图像
            plt.tight_layout()
            plt.savefig(f'../data/pic/学习时长/{self.subject}-{month}月.png', dpi=600)
            plt.close()

    # 按周绘制学习时长折线图
    def plot_weekly_study_time(self):
        # 按周分组并绘制
        weekly_data = self.df.groupby('Week').agg({
            '总时长': 'sum',
            '上午': 'sum',
            '下午': 'sum',
            '晚上': 'sum'
        }).reset_index()

        X = weekly_data['Week'].values.reshape(-1, 1)
        X = X - X.min()  # 从0开始
        y = weekly_data['总时长'].values
        # print(weekly_data)
        lr = LinearRegression()
        lr.fit(X, y)
        # 提取回归直线的斜率和截距
        k = lr.coef_[0]
        b = lr.intercept_

        # 计算总时长的和
        total_study_time = y.sum()

        # 绘制图像
        plt.figure(figsize=(10, 6))
        plt.plot(weekly_data['Week'], weekly_data['总时长'], label='Total Time', color='black', linestyle='-',
                 linewidth=2)
        plt.plot(weekly_data['Week'], weekly_data['上午'], label='Morning', color='blue', linestyle='--')
        plt.plot(weekly_data['Week'], weekly_data['下午'], label='Afternoon', color='red', linestyle='--')
        plt.plot(weekly_data['Week'], weekly_data['晚上'], label='Evening', color='green', linestyle='--')

        # 绘制回归直线
        plt.plot(weekly_data['Week'], k * X + b, label=f'Linear Fit: y={k:.3f}x+{b:.2f}', color='orange',
                 linestyle='-', linewidth=1)

        # 在图上显示总时长的和
        plt.text(0.95, 0.95, f'Total Time: {total_study_time:.2f} hours',
                 horizontalalignment='right', verticalalignment='top',
                 transform=plt.gca().transAxes, fontsize=16, color='red', weight='bold')

        plt.xlabel('Week')
        plt.ylabel('Time (hours)')
        plt.title(f'{self.subject} - Weekly Study Time')
        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))  # 设置x轴刻度为整数
        plt.legend()
        plt.grid(True)

        # 保存图像
        plt.tight_layout()
        plt.savefig(f'../data/pic/学习时长/{self.subject}-weekly.png', dpi=900)
        plt.close()

        # 输出按周统计的数据
        # for week, row in weekly_data.iterrows():
        #     print(f"Week {row['Week']}: Total={row['总时长']:.2f}h, 上午={row['上午']:.2f}h, "
        #           f"下午={row['下午']:.2f} hours, 晚上={row['晚上']:.2f} hours")

    # 按周几绘制学习时长折线图
    def plot_weekday_study_time(self):
        # 按周几分组并绘制
        weekday_data = self.df.groupby('Weekday').agg({
            '总时长': 'sum',
            '上午': 'sum',
            '下午': 'sum',
            '晚上': 'sum'
        }).reindex([1, 2, 3, 4, 5, 6, 7])  # 保证顺序为周一到周日

        # 绘制图像
        plt.figure(figsize=(10, 6))
        plt.plot(weekday_data.index, weekday_data['总时长'], label='Total Time', color='black', linestyle='-',
                 marker='o')
        plt.plot(weekday_data.index, weekday_data['上午'], label='Morning', color='blue', linestyle='--', marker='o')
        plt.plot(weekday_data.index, weekday_data['下午'], label='Afternoon', color='red', linestyle='--', marker='o')
        plt.plot(weekday_data.index, weekday_data['晚上'], label='Evening', color='green', linestyle='--', marker='o')

        plt.xlabel('Weekday (1=Mon, 7=Sun)')
        plt.ylabel('Time (hours)')
        plt.title(f'{self.subject} - Weekday Study Time')
        plt.xticks(weekday_data.index, ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])  # 让横坐标显示周一到周日
        plt.legend()
        plt.grid(True)

        # 保存图像
        plt.tight_layout()
        plt.savefig(f'../data/pic/学习时长/{self.subject}-week_day.png', dpi=600)
        plt.close()

        # 输出按周几统计的数据
        for day, row in weekday_data.iterrows():
            print(f"星期{day}: Total={row['总时长']:.2f}h, 上午{row['上午']:.2f}h, "
                  f"下午{row['下午']:.2f}h, 晚上{row['晚上']:.2f}h")

    def plot_corr(self):
        # 对总时长、上午、下午、晚上进行相关性分析
        df_corr = self.df[['总时长', '上午', '下午', '晚上']].corr()
        print("相关性矩阵：")
        print(df_corr)
        # 绘制相关性矩阵热力图
        plt.figure(figsize=(6, 6))
        sns.heatmap(df_corr, annot=True, cmap='coolwarm', fmt=".2f",
                    xticklabels=['Total', 'Morning', 'Afternoon', 'Evening'],
                    yticklabels=['Total', 'Morning', 'Afternoon', 'Evening'])
        plt.title(f'{self.subject} - Correlation Matrix')
        plt.tight_layout()
        plt.savefig(f'../data/pic/学习时长/{self.subject}-corr.png', dpi=600)
        plt.close()


# 使用示例
if __name__ == "__main__":
    file_path = '../data/xlsx/P-学习时长-数学2024.xlsx'
    plotter = StudyTimePlotter(file_path)

    plotter.plot_total_study_time()  # 绘制总时长图
    plotter.plot_monthly_study_time()  # 绘制每月图
    plotter.plot_weekly_study_time()  # 绘制每周图
    plotter.plot_weekday_study_time()  # 绘制每周几图
    plotter.plot_corr()  # 绘制相关性矩阵
