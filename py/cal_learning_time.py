import pandas as pd
import re
import pickle


class StudyTimeProcessor:
    def __init__(self, path, target_path, current_year):
        self.path = path
        self.target_path = target_path
        self.df_list = []
        self.current_year = current_year

    def _parse_time(self, time_range):
        """解析时间段，返回起始时间和结束时间的小时数。"""
        start, end = time_range.split('-')
        start_hour, start_minute = map(int, start.split(':'))
        end_hour, end_minute = map(int, end.split(':'))
        start_time = start_hour + start_minute / 60
        end_time = end_hour + end_minute / 60
        return start_time, end_time

    def _calculate_time_periods(self, time_ranges):
        """计算上、下、晚的时长，并返回总时长。"""
        morning_time = afternoon_time = evening_time = 0

        for time_range in time_ranges.split(','):
            start_time, end_time = self._parse_time(time_range.strip())

            if 6 <= start_time < 12:
                # 上时段 6:00-12:00
                morning_time += min(end_time, 12) - start_time
            if 12 <= start_time < 17.5:
                # 下时段 12:00-17:30
                afternoon_time += min(end_time, 17.5) - max(start_time, 12)
            if start_time >= 17.5 or end_time > 17.5:
                # 晚时段 17:30-24:00
                evening_time += end_time - max(start_time, 17.5)

        total_time = morning_time + afternoon_time + evening_time
        return round(morning_time, 2), round(afternoon_time, 2), round(evening_time, 2), round(total_time, 2)

    def _parse_table(self, table_str):
        """将表格字符串转换为DataFrame"""
        lines = table_str.strip().split('\n')[2:]  # 跳过标题行和分隔符行
        data = [line.split('|')[1:-1] for line in lines]
        df = pd.DataFrame(data, columns=['日期', '时间段', '备注'])
        # 对df的每个元素进行strip()操作，去掉字符串两端的空格
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
        # 为了方便后续计算，将日期转为标准日期格式
        df['日期'] = pd.to_datetime(f'{self.current_year}.' + df['日期'], format='%Y.%m.%d', errors='coerce')

        return df

    def _convert_df(self, df):
        """处理DataFrame，计算上、下、晚时长，并更新总时长"""
        df[['上', '下', '晚', '总时长(h)']] = df['时间段'].apply(self._calculate_time_periods).apply(pd.Series)
        df = df[['日期', '时间段', '上', '下', '晚', '总时长(h)', '备注']]  # 重排列顺序
        return df

    def _replace_table(self, match):
        """回调函数，用于将表格替换为新表格"""
        table_str = match.group(1)
        df = self._parse_table(table_str)  # 解析表格
        new_df = self._convert_df(df)  # 计算上下晚和更新总时长
        # 将日期时间列转换为只有日期的字符串
        new_df['日期'] = new_df['日期'].dt.date.astype(str)
        # print(new_df)
        # print(new_df.describe())
        self.df_list.append(new_df)  # 保存处理后的DataFrame
        table_md = new_df.to_markdown(index=False)  # 转为markdown格式
        return f"<div class=\"time-table\">\n\n{table_md}\n\n</div>"

    def process(self):
        # 读取文件内容
        with open(self.path, 'r', encoding='utf-8') as f:
            content = f.read()
        # 使用回调函数逐个替换匹配到的表格
        content = re.sub(r'<div class="time-table">([\s\S]*?)</div>', self._replace_table, content)
        # 写入新的md文件
        with open(self.target_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # for df in self.df_list:
        #     print(df)


if __name__ == '__main__':
    processor = StudyTimeProcessor('../data/学习时长.md', "../data/学习时长_export.md", 2024)
    processor.process()
    with open('../data/pkl/study_time_df_list.pkl', 'wb') as f:
        pickle.dump(processor.df_list, f)
