# pip install pdfplumber pandas tabulate

import pdfplumber
import pandas as pd
from tabulate import tabulate
from collections import defaultdict
import csv

def extract_tables_from_pdf(pdf_path, folder_name):
    """
    PDF 파일에서 테이블 추출 함수
    """
    # PDF 파일 열기
    with pdfplumber.open(pdf_path) as pdf:
        all_tables = []
        for page_num, page in enumerate(pdf.pages):
            # 페이지에서 테이블 추출
            tables = page.extract_tables()
            for table_num, table in enumerate(tables):
                # 테이블을 pandas DataFrame으로 변환
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append((page_num + 1, table_num + 1, df))

    # # 모든 테이블 출력
    # for page_num, table_num, table in all_tables:
    #     print(f"Page {page_num}, Table {table_num}")
    #     print(tabulate(table, headers='keys', tablefmt='grid'))
    #     print("\n")

    # 모든 테이블을 CSV 파일로 저장
    for idx, (page_num, table_num, table) in enumerate(all_tables):
        filename = f"{folder_name}/table_{idx + 1}.csv"
        table.to_csv(filename, index=False, encoding='utf-8-sig')

def display_csv_file(csv_file_path):
    """
    csv 파일 데이터프레임 출력 함수
    """
    # CSV 파일 불러오기
    df = pd.read_csv(csv_file_path)

    # 데이터프레임 출력
    display(df)

def add_courses_to_csv(file_name, courses):
    """
    csv 파일에 추가하는 함수
    """
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        for course in courses:
            writer.writerow(course)

def extract_courses_from_table(csv_file_path, start_num, curri_map_year, course_name_col, course_type_required_col, course_number_col, course_credit_col):
    """
    표에서 교과목 추출 및 저장 함수
    """
    # CSV 파일 불러오기
    df = pd.read_csv(csv_file_path, header=None)

    # 현재 표에서 이수체계도 요소 저장
    current_curriculum_map = []

    for index, row in df.iterrows():
        if index < 1:  # 첫 번째 행(인덱스 0) 스킵
            continue

        # 교과목명 저장
        check_nl_in_name = False
        course_name = str(row[course_name_col])
        if "\n" in course_name:
            # '\n'이 처음으로 나타나는 위치까지 문자열 자르기
            course_name = course_name.split("\n", 1)[0]
            check_nl_in_name = True

        # 학수번호 저장
        course_number = str(row[course_number_col + int(check_nl_in_name)])
        if "\n" in course_number:
            # '\n'이 처음으로 나타나는 위치까지 문자열 자르기
            course_number = course_number.split("\n", 1)[0]

        # 과목 구분 및 필수 여부 저장
        if course_type_required_col < 0:
            course_type = "전공" if (course_number.startswith("CSE")) else "교양"
            course_required = "필수"
        else:
            course_type_required = str(row[course_type_required_col])
            course_type = "전공" if (course_type_required[0] == '전') else "교양"
            course_required = "필수" if (course_type_required[1] == '필') else "선택"

        # 과목 학점 저장
        course_credit = row[course_credit_col]

        # 각 행에 대해 '○' 문자가 있는 열을 찾고 해당 학기에 교과목 추가
        for col_index in range(start_num, start_num + 8):
            if row[col_index] == '○':
                current_curriculum_map.append([
                    curri_map_year,
                    (col_index - start_num + 2) // 2, # 학년
                    (col_index - start_num) % 2 + 1,  # 학기
                    course_name,
                    course_type,
                    course_required,
                    course_number,
                    course_credit
                ])

    add_courses_to_csv('curriculum_map.csv', current_curriculum_map)

"""
이수체계도 pdf에서 표 추출
"""
# 2024학년도 이수체계도
extract_tables_from_pdf("2024_curri.pdf", "2024_curri")
# 2023학년도 이수체계도
extract_tables_from_pdf("2023_curri.pdf", "2023_curri")
# 2019~2022학년도 이수체계도
extract_tables_from_pdf("2019~2022_curri.pdf", "2019~2022_curri")

"""
커리큘럼 csv 파일로 정리
"""
# 데이터 정의
curriculum_map_data = [
    ["학년도", "학년", "학기", "교과목명", "구분", "필수 여부", "학수번호", "학점"],
    # 필요한 데이터 추가 가능
]

# CSV 파일 생성
csv_filename = 'curriculum_map.csv'
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(curriculum_map_data)

print(f"CSV 파일 '{csv_filename}'이(가) 생성되었습니다.")

# CSV 파일에 작성
# 처리할 파일과 연도 매핑
files_and_years = [
    #2024학년도 이수체계도
    ('2024_curri/table_3.csv', 4, 2024, 2, 3, 1, 16),  # 전공 교과목 편성표
    ('2024_curri/table_1.csv', 8, 2024, 4, -1, 3, 7),  # 교육과정
    #2023학년도 이수체계도
    ('2023_curri/table_3.csv', 4, 2023, 2, 3, 1, 16),
    ('2023_curri/table_2.csv', 8, 2023, 4, -1, 3, 7),
    #2022학년도 이수체계도
    ('2019~2022_curri/table_80.csv', 4, 2022, 2, 3, 1, 16),
    ('2019~2022_curri/table_79.csv', 8, 2022, 4, -1, 3, 7),
    #2021학년도 이수체계도
    ('2019~2022_curri/table_62.csv', 4, 2021, 2, 3, 1, 16),
    ('2019~2022_curri/table_61.csv', 8, 2021, 4, -1, 3, 7),
    #2020학년도 이수체계도
    ('2019~2022_curri/table_32.csv', 5, 2020, 2, 3, 1, 17),
    ('2019~2022_curri/table_31.csv', 8, 2020, 5, -1, 3, 7),
    #2019학년도 이수체계도
    ('2019~2022_curri/table_2.csv', 5, 2019, 2, 3, 1, 17),
    ('2019~2022_curri/table_1.csv', 8, 2019, 5, -1, 3, 7),
]

# 각 파일에 대해 처리 함수 호출
for curri_info in files_and_years:
    csv_file_path, start_num, curri_map_year, course_name_col, course_type_required_col, course_number_col, course_credit_col = curri_info
    extract_courses_from_table(csv_file_path, start_num, curri_map_year, course_name_col, course_type_required_col, course_number_col, course_credit_col)

# CSV 파일 읽기
display_csv_file(csv_filename)
