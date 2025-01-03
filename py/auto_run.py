import subprocess
import sys
import os

# 获取虚拟环境中的 Python 路径
venv_python = os.path.join(sys.prefix, 'Scripts', 'python.exe')

# 脚本列表
scripts = [
    'md2xlsx.py',
    'P_study_time.py',
    'P_acc.py',
    'R_study_time.py',
    'R_acc.py',
]

# 依次执行每个脚本
for script in scripts:
    print(f"正在运行 {script}...")
    subprocess.run([venv_python, script])  # 使用虚拟环境中的 Python 解释器
    print(f"{script} 运行完成\n\n\n")
