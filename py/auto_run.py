import subprocess
import sys
import os

# 获取虚拟环境中的 Python 路径
venv_python = os.path.join(sys.prefix, 'Scripts', 'python.exe')
print(f"虚拟环境中的 Python 路径为：{venv_python}")

# 脚本列表
scripts = [
    'md2xlsx.py',
    'P_study_time.py',
    'P_acc.py',
    'R_study_time.py',
    'R_acc.py',
    'P_acc_eng.py',
]

# 依次执行每个脚本
for script in scripts:
    print(f"\033[94m正在运行 {script}...\033[0m")  # 输出蓝色文字
    subprocess.run([venv_python, script])  # 使用虚拟环境中的 Python 解释器
    print(f"\033[32m{script} 运行完成\033[0m\n\n\n")  # 输出绿色文字
