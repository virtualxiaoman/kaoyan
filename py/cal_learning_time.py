import re
from datetime import datetime

# 读取md文件
input_file = "../data/学习时长.md"
output_file = "../data/学习时长_更新.md"

# 时间段正则表达式匹配
time_pattern = r"(\d{1,2}:\d{2})-(\d{1,2}:\d{2})"


# 计算时间段的时长
def calculate_time_duration(start_time, end_time):
    time_format = "%H:%M"
    start = datetime.strptime(start_time, time_format)
    end = datetime.strptime(end_time, time_format)
    duration = (end - start).seconds / 3600  # 转换为小时
    return duration


# 读取Markdown文件
with open(input_file, "r", encoding="utf-8") as file:
    lines = file.readlines()

# 处理文件内容并计算每一行的总时长
new_lines = []
for line in lines:
    # 查找时间段
    time_segments = re.findall(time_pattern, line)
    if time_segments:
        total_hours = sum(calculate_time_duration(start, end) for start, end in time_segments)
        # 更新总时长
        new_line = re.sub(r"\|\s*\d+(\.\d+)?\s*\|", f"| {total_hours:.2f} |", line, count=1)
        new_lines.append(new_line)
    else:
        new_lines.append(line)

# 写入新的Markdown文件
with open(output_file, "w", encoding="utf-8") as file:
    file.writelines(new_lines)

print(f"总时长已计算并写入: {output_file}")
