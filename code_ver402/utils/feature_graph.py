import json
import matplotlib.pyplot as plt
from pathlib import Path
from collections import Counter, OrderedDict

# JSON 파일 읽기 함수
def read_json(file_path):
    with Path(file_path).open('r', encoding='utf-8') as file:
        return json.load(file)

# 파일 이름에서 학생 이름 추출 함수
def get_student_name(file_path):
    return Path(file_path).stem.split('_')[0]

# 작업 이름 변경을 위한 사전
rename_dict = {
    '추가': 'Add',
    '쉘': 'Shell',
    '자르기': 'Union Trim',
    '제거': 'Remove',
    '홈': 'Groove',
    '챔퍼': 'Chamfer',
    '미러': 'Mirror',
    'RectPattern': 'Rectangular Pattern',
    '이동': 'Translate',
    '어셈블': 'Assemble',
    '두께': 'Thickness'
}

# 작업 분류 및 이름 변경 함수
def classify_and_rename_operation(name):
    operation = name.split('.')[0]
    return rename_dict.get(operation, operation)

# 작업을 Plus, Minus, Other로 분류
def classify_operation(name):
    plus_operations = ['Pad', 'Shaft', 'Add', 'Rib', 'Multi-sections Solid', 'Solid Combine']
    minus_operations = ['Pocket', 'Groove', 'Hole', 'Remove', 'Intersect', 'Union Trim', 'Remove Slot', 'Remove Lump', 'Shell', 'Draft']
    if name in plus_operations:
        return 'Plus'
    elif name in minus_operations:
        return 'Minus'
    else:
        return 'Other'

# 데이터 처리 함수
def process_data(data):
    operations = []
    for key in data:
        if 'work_history' in data[key]:
            operations.extend([classify_and_rename_operation(item['name']) for item in data[key]['work_history']])
    
    operation_counts = Counter(operations)
    classifications = [classify_operation(op) for op in operations]
    classification_counts = Counter(classifications)
    
    return operation_counts, classification_counts
'''
    ax1.barh(y_pos, left_counts, align='center', color='thistle')
    ax1.barh(y_pos, right_counts, align='center', color='mediumorchid')

    colors = {
        'Plus': ('#FA8072', '#F84330'),  
        'Minus': ('#B5BFDD', '#6C7FBC'), 
        'Other': ('#AEE4C6', '#36A468')  
    }

'''

def plot_comparison(student1, counts1, class_counts1, student2, counts2, class_counts2, used_operations, max_count, max_class_count, margin=0.5, bar_width=0.8, axis_fontsize=16, title_fontsize=16, label_fontsize=20):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

    # 첫 번째 그래프: 사용된 작업 비교
    y_pos = range(len(used_operations))

    left_counts = [-counts1.get(op, 0) for op in used_operations]
    right_counts = [counts2.get(op, 0) for op in used_operations]

    ax1.barh(y_pos, left_counts, align='center', color='thistle', height=bar_width)
    ax1.barh(y_pos, right_counts, align='center', color='mediumorchid', height=bar_width)

    ax1.set_yticks([])  # y축 눈금 제거
    for i, operation in enumerate(used_operations):
        ax1.text(0, i, operation, ha='center', va='center', fontsize=label_fontsize)

    ax1.invert_yaxis()
    ax1.set_xlabel('Count', fontsize=axis_fontsize)
    ax1.set_title(f'Comparison of Operations Between {student1} and {student2}', fontsize=title_fontsize)

    ax1.set_xlim(-max_count-margin, max_count+margin)
    ax1.set_xticks(range(-max_count, max_count+1, max(1, max_count//5)))
    ax1.set_xticklabels([abs(x) for x in ax1.get_xticks()], fontsize=axis_fontsize)

    ax1.legend([student1, student2], fontsize=label_fontsize)
    ax1.axvline(x=0, color='gray', linestyle='-', linewidth=0.5)

    # 두 번째 그래프: Plus, Minus, Other 분류 비교
    categories = ['Other', 'Minus', 'Plus']
    colors = {
        'Plus': ('#FA8072', '#F84330'),  
        'Minus': ('#B5BFDD', '#6C7FBC'), 
        'Other': ('#AEE4C6', '#36A468')  
    }

    for i, category in enumerate(categories):
        left_count = -class_counts1.get(category, 0)
        right_count = class_counts2.get(category, 0)
        
        ax2.barh(i, left_count, align='center', color=colors[category][0], height=bar_width, label=f'{student1} {category}')
        ax2.barh(i, right_count, align='center', color=colors[category][1], height=bar_width, label=f'{student2} {category}')

    ax2.set_yticks([])  # y축 눈금 제거
    for i, category in enumerate(categories):
        ax2.text(0, i, category, ha='center', va='center', fontsize=label_fontsize)

    ax2.set_xlabel('Count', fontsize=axis_fontsize)
    ax2.set_title(f'Comparison of Operation Categories Between {student1} and {student2}', fontsize=title_fontsize)

    ax2.set_xlim(-max_class_count-margin, max_class_count+margin)
    ax2.set_xticks(range(-max_class_count, max_class_count+1, max(1, max_class_count//5)))
    ax2.set_xticklabels([abs(x) for x in ax2.get_xticks()], fontsize=axis_fontsize)

    ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, fontsize=label_fontsize)
    ax2.axvline(x=0, color='gray', linestyle='-', linewidth=0.5)

    plt.tight_layout()
    plt.show()


# 파일 경로
file_path1 = r'C:\Users\gusu4\Desktop\3DCAD과제_중립포맷추가\paper_testcase\ModelAnswer_history.json'
file_paths = [
    r'C:\Users\gusu4\Desktop\3DCAD과제_중립포맷추가\paper_testcase\Student1_history.json',
    r'C:\Users\gusu4\Desktop\3DCAD과제_중립포맷추가\paper_testcase\Student10_history.json',
    r'C:\Users\gusu4\Desktop\3DCAD과제_중립포맷추가\paper_testcase\Student13_history.json',
    r'C:\Users\gusu4\Desktop\3DCAD과제_중립포맷추가\paper_testcase\Student21_history.json',
    r'C:\Users\gusu4\Desktop\3DCAD과제_중립포맷추가\paper_testcase\Student24_history.json',
    r'C:\Users\gusu4\Desktop\3DCAD과제_중립포맷추가\paper_testcase\Student26_history.json',
    r'C:\Users\gusu4\Desktop\3DCAD과제_중립포맷추가\paper_testcase\Student27_history.json',
    r'C:\Users\gusu4\Desktop\3DCAD과제_중립포맷추가\paper_testcase\Student29_history.json',
    r'C:\Users\gusu4\Desktop\3DCAD과제_중립포맷추가\paper_testcase\Student34_history.json',
    r'C:\Users\gusu4\Desktop\3DCAD과제_중립포맷추가\paper_testcase\Student35_history.json',
    r'C:\Users\gusu4\Desktop\3DCAD과제_중립포맷추가\paper_testcase\Student37_history.json',
    r'C:\Users\gusu4\Desktop\3DCAD과제_중립포맷추가\paper_testcase\Student40_history.json',
]

# 모든 파일에서 사용된 작업 추출
all_used_operations = set()


# 메인 코드 부분에서 최대값 계산
max_count = 0
max_class_count = 0

# 학생 1 데이터 처리
student1 = get_student_name(file_path1)
data1 = read_json(file_path1)
counts1, class_counts1 = process_data(data1)
all_used_operations.update(counts1.keys())
max_count = max(max_count, max(counts1.values()))
max_class_count = max(max_class_count, max(class_counts1.values()))

# 다른 학생들 데이터 처리 및 사용된 작업 추출
other_students_data = []
for file_path in file_paths:
    student = get_student_name(file_path)
    data = read_json(file_path)
    counts, class_counts = process_data(data)
    all_used_operations.update(counts.keys())
    other_students_data.append((student, counts, class_counts))
    max_count = max(max_count, max(counts.values()))
    max_class_count = max(max_class_count, max(class_counts.values()))

# 사용된 작업을 정렬된 리스트로 변환
used_operations = sorted(list(all_used_operations))

# 다른 학생들과 비교하여 그래프 그리기
for student2, counts2, class_counts2 in other_students_data:
    plot_comparison(student1, counts1, class_counts1, student2, counts2, class_counts2, used_operations, max_count, max_class_count)
