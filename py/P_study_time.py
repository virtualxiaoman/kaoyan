import pandas as pd
from datetime import datetime


class StudyTimeProcessor:
    def __init__(self, input_path, output_path, current_year):
        """
        初始化
        :param input_path: 输入的Excel文件路径
        :param output_path: 输出的Excel文件路径
        """
        self.input_path = input_path
        self.output_path = output_path
        self.current_year = current_year

    # 解析时间段
    def _parse_time(self, time_range):
        """
        解析时间段，返回起始时间和结束时间的小时数。
        :param time_range: 形如 '9:30-11:30' 的时间段字符串
        :return: 起始时间和结束时间的小时数
        """
        start, end = time_range.split('-')
        start_hour, start_minute = map(int, start.split(':'))
        end_hour, end_minute = map(int, end.split(':'))
        start_time = start_hour + start_minute / 60
        end_time = end_hour + end_minute / 60
        return start_time, end_time

    # 计算时间段的时长
    def _calculate_time_periods(self, time_ranges):
        """
        计算上、下、晚的时长，并返回总时长。
        :param time_ranges: 形如 '9:30-11:30, 14:00-17:00' 的时间段字符串
        :return: 返回上午、下午、晚上的时长（单位：小时）
        """
        morning_time = afternoon_time = evening_time = 0

        # 处理每个时间段
        for time_range in time_ranges.split(','):
            start_time, end_time = self._parse_time(time_range.strip())

            # 计算上午（0:00 - 12:00）
            if 0 <= start_time < 12:
                if end_time <= 12:
                    morning_time += end_time - start_time
                else:
                    morning_time += 12 - start_time
                    afternoon_time += end_time - 12  # 超过12点的部分算下午，假设不会超过17:30
            # 计算下午（12:00 - 17:30）
            elif 12 <= start_time < 17.5:
                if end_time <= 17.5:
                    afternoon_time += end_time - start_time
                else:
                    afternoon_time += 17.5 - start_time
                    evening_time += end_time - 17.5  # 超过17:30的部分算晚上
            # 计算晚上（17:30 - 24:00）
            elif start_time >= 17.5 and end_time <= 24:
                evening_time += end_time - start_time  # 这里没有超时的可能，我不熬夜
            else:
                print(f"时间段错误：start_time={start_time}, end_time={end_time}")

        # 返回精确到5位小数的时间
        return round(morning_time, 5), round(afternoon_time, 5), round(evening_time, 5)

    # 处理学习时间
    def process_study_time(self):
        """
        读取表格文件，处理时间段并保存到新的文件中。
        """
        # 读取Excel文件，注意不要把9.10解析成9.1了，所以设置日期属性为字符串类型
        df = pd.read_excel(self.input_path, dtype={'日期': str})

        # 将日期列转换为datetime类型
        df['日期'] = pd.to_datetime(df['日期'], format='%m.%d')

        # 为了便于后续操作，假设表格列名为'日期', '时间段', '备注'
        new_columns = ['日期', '总时长', '时间段', '上午', '下午', '晚上', '备注']
        new_data = []

        for index, row in df.iterrows():
            date = row['日期']
            time_range = row['时间段']
            remark = row['备注']

            # 计算每个时间段的上午、下午、晚上的时长
            morning_time, afternoon_time, evening_time = self._calculate_time_periods(time_range)

            # 计算总时长
            total_time = morning_time + afternoon_time + evening_time

            # 添加新的一行数据
            new_data.append([date, total_time, time_range, morning_time, afternoon_time, evening_time, remark])

        # 将新的数据转换为DataFrame
        new_df = pd.DataFrame(new_data, columns=new_columns)

        return new_df

    # 处理DataFrame，合并相同日期的行
    def process_df(self, new_df):
        # 处理空值，将NaN替换为空字符串
        new_df['备注'] = new_df['备注'].fillna('')

        # 对于备注非空的行，说明这是某本书写完了，现在对这本书的学习时长进行统计
        # # 找出所有备注非空的行的索引
        non_empty_remarks_indices = new_df[new_df['备注'] != ''].index
        print(f"备注非空的行索引：{non_empty_remarks_indices}")
        start_index = 0
        #
        # 遍历备注非空的行，统计与之相关联的学习时长
        for end_index in non_empty_remarks_indices:
            # print(f"start_index={start_index}, end_index={end_index}")
            # 统计从start_index到end_index之间的学习时长，使用'总时长'列的值相加
            total_study_time = new_df.loc[start_index:end_index, '总时长'].sum()
            # 更新备注，添加统计的学习时长。注意，因为同时可能开两本书，而学习时长没有体现这个，所以只是本阶段的学习时长。
            new_df.loc[end_index, '备注'] += f'。本阶段总计{total_study_time:.2f}h'
            # 更新start_index
            start_index = end_index + 1

        # 合并相同日期的行
        aggregated_df = new_df.groupby('日期').agg(
            {
                '总时长': 'sum',  # 对总时长进行求和
                '时间段': ', '.join,  # 合并时间段字符串
                '上午': 'sum',  # 对上午时长求和
                '下午': 'sum',  # 对下午时长求和
                '晚上': 'sum',  # 对晚上时长求和
                '备注': ', '.join  # 合并备注字符串
            }).reset_index()

        # 按日期排序
        aggregated_df = aggregated_df.sort_values(by='日期')
        # 将日期列还原为 'YYYY.MM.DD' 格式
        aggregated_df['日期'] = aggregated_df['日期'].dt.strftime(f'{self.current_year}.%m.%d')
        # 如果有一行的备注是`, `，就替换为空字符串
        aggregated_df['备注'] = aggregated_df['备注'].replace(', ', '', regex=True)

        # 将新的DataFrame保存为新的Excel文件
        aggregated_df.to_excel(self.output_path, index=False)

        print(f"处理完成，结果保存为 {self.output_path}")


# 用法示例
if __name__ == "__main__":
    # 使用示例
    input_file = '../data/xlsx/学习时长-数学2024.xlsx'
    output_file = '../data/xlsx/P-学习时长-数学2024.xlsx'
    processor = StudyTimeProcessor(input_file, output_file, 2024)
    new_df = processor.process_study_time()
    # print(new_df.head(50))
    processor.process_df(new_df)
