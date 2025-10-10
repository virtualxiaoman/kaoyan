import csv
import re


def clean_newlines(text: str) -> str:
    """
    清理笔记中的换行符：
    - 单个换行替换为三个空格
    - 多个换行只保留一个
    """
    # 统一换行符格式
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # 将连续多个换行替换为占位符
    text = re.sub(r'\n{2,}', '[[NL]]', text)
    # 将剩余单个换行替换为三个空格
    text = text.replace('\n', '   ')
    # 恢复连续换行
    text = text.replace('[[NL]]', '\n')
    return text.strip()


def process_csv(input_path: str, output_path: str):
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        lines = []
        for row in reader:
            if len(row) < 3:
                continue  # 跳过不完整行
            index, word, note = row[0].strip(), row[1].strip(), row[2].strip()
            note_clean = clean_newlines(note)

            # 判断笔记首个单词是否与 word 一致
            first_word = re.match(r'[A-Za-z\-]+', note_clean)
            if first_word and first_word.group(0).lower() == word.lower():
                line = f"{index}. {note_clean}"
            else:
                line = f"{index}. {word} {note_clean}"

            lines.append(line)

    # 输出到 txt 文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(lines))  # 每个词条之间空一行，便于阅读


if __name__ == "__main__":
    process_csv("../data/note/English/不背单词笔记.csv",
                "../data/note/English/不背单词笔记.txt")
