import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="계과 학점 판독기", page_icon="⚙️", layout="wide")

# CSS로 스타일링 (글꼴 및 레이아웃)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #e9ecef; }
    .stButton>button:hover { background-color: #dee2e6; color: #007bff; }
    .metric-container { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("⚙️ 계과 학점 판독기")
st.caption("기계공학부 전용 학점 관리 및 졸업 시뮬레이터")

# 2. 데이터 초기화 (Session State)
if 'my_courses' not in st.session_state:
    st.session_state.my_courses = []

# 성적 배점
grade_points = {
    "A+": 4.5, "A0": 4.0, "B+": 3.5, "B0": 3.0, 
    "C+": 2.5, "C0": 2.0, "D+": 1.5, "D0": 1.0, "F": 0.0, "P": "Pass"
}

# 과목 데이터베이스
major_core = ["고체역학", "열역학", "동역학", "유체역학", "기계재료", "공학기초수학1", "공학기초수학2", "기계공학프로그래밍", "열전달", "동적시스템모델링및해석", "CAE/CFD", "에너지와 환경", "기계공학도를 위한 전기전자입문", "기계요소설계"]
major_deep = ["재료거동학", "탄성학", "복합재료", "항공우주추진", "자동차공학", "미래모빌리티공학", "생산공학", "기구학", "최적설계", "응용유체역학", "응용고체역학", "소성공학", "윤활공학", "바이오공학입문", "모바일시스템제어", "계측공학", "로봇공학입문", "동적시스템제어", "기계공학도를 위한 인공지능입문", "글로벌캡스톤디자인", "졸업논문연구", "기계시스템수치해석", "공학수치해석"]
major_lab = ["고역실", "열유실", "진동실", "기설실", "기공실", "종설", "스종설"]

# 3. 사이드바: 목표 설정 및 비전공 추가
with st.sidebar:
    st.header("🎯 목표 설정")
    target_overall = st.number_input("목표 전체 평점", 0.0, 4.5, 4.0, 0.1)
    target_major = st.number_input("목표 전공 평점", 0.0, 4.5, 4.0, 0.1)
    
    st.divider()
    st.header("➕ 비전공/기타 추가")
    non_major_name = st.text_input("과목명", placeholder="교양/BSM 등")
    non_major_crd = st.selectbox("학점", [1, 2, 3], index=2)
    if st.button("비전공 과목 추가"):
        if non_major_name:
            st.session_state.my_courses.append({"name": non_major_name, "type": "비전공", "credit": non_major_crd, "grade": "A+"})
            st.rerun()

# 4. 상단 대시보드 (학점 카운터 및 GPA)
def calculate_stats():
    total_crd = 0
    gpa_crd = 0 # P 제외 학점
    total_pts = 0
    
    major_crd = 0
    major_gpa_crd = 0
    major_pts = 0
    
    for c in st.session_state.my_courses:
        crd = c['credit']
        pts = grade_points.get(c['grade'], 0)
        
        total_crd += crd
        if c['type'] in ["전공코어", "전공심화", "실험실습", "특수전공"]:
            major_crd += crd
            
        if pts != "Pass":
            total_pts += (crd * pts)
            gpa_crd += crd
            if c['type'] in ["전공코어", "전공심화", "실험실습", "특수전공"]:
                major_pts += (crd * pts)
                major_gpa_crd += crd
                
    overall_gpa = total_pts / gpa_crd if gpa_crd > 0 else 0
    major_gpa = major_pts / major_gpa_crd if major_gpa_crd > 0 else 0
    return total_crd, overall_gpa, major_gpa

total_crd, overall_gpa, major_gpa = calculate_stats()

m1, m2, m3 = st.columns(3)
with m1:
    st.metric("이수 학점 현황", f"{total_crd} / 130")
    st.progress(min(total_crd / 130, 1.0))
with m2:
    st.metric("현재 전체 평점", f"{overall_gpa:.2f}", f"{overall_gpa - target_overall:.2f}")
with m3:
    st.metric("현재 전공 평점", f"{major_gpa:.2f}", f"{major_gpa - target_major:.2f}")

st.divider()

# 5. 과목 선택 구역 (Subject Bank)
st.subheader("📍 과목 선택")
tab1, tab2, tab3, tab4 = st.tabs(["전공 코어", "전공 심화", "실험/실습", "URP/COOP"])

def add_course(name, type, credit, grade="A+"):
    # 중복 추가 방지
    if not any(c['name'] == name for c in st.session_state.my_courses):
        st.session_state.my_courses.append({"name": name, "type": type, "credit": credit, "grade": grade})
        st.rerun()

with tab1:
    cols = st.columns(4)
    for i, course in enumerate(major_core):
        if cols[i % 4].button(course, key=f"core_{i}"):
            add_course(course, "전공코어", 3)

with tab2:
    cols = st.columns(4)
    for i, course in enumerate(major_deep):
        if cols[i % 4].button(course, key=f"deep_{i}"):
            add_course(course, "전공심화", 3)

with tab3:
    cols = st.columns(4)
    for i, course in enumerate(major_lab):
        # 실험실습은 보통 1~2학점이므로 여기서는 기본 2학점 설정 (필요시 수정)
        if cols[i % 4].button(course, key=f"lab_{i}"):
            add_course(course, "실험실습", 2)

with tab4:
    c1, c2, c3 = st.columns(3)
    if c1.button("URP (2학점)"): add_course("URP", "특수전공", 2)
    if c2.button("학기중 COOP (2학점/P)"): add_course("학기중 COOP", "특수전공", 2, "P")
    if c3.button("방학중 COOP (3학점/P)"): add_course("방학중 COOP", "특수전공", 3, "P")

# 6. 수강 목록 및 성적 입력
st.divider()
st.subheader("📋 내 수강 목록 (성적을 입력하세요)")

if not st.session_state.my_courses:
    st.info("위의 과목 버튼을 눌러 수강한 과목을 추가하세요.")
else:
    for i, course in enumerate(st.session_state.my_courses):
        cols = st.columns([4, 2, 2, 2, 1])
        cols[0].write(f"**{course['name']}**")
        cols[1].caption(course['type'])
        
        # 학점 수정 (비전공이나 예외 과목 대응)
        new_crd = cols[2].number_input("학점", 1, 6, course['credit'], key=f"crd_{i}")
        st.session_state.my_courses[i]['credit'] = new_crd
        
        # 성적 선택
        if course['grade'] == "P":
            cols[3].write("Pass (P)")
        else:
            options = list(grade_points.keys())
            options.remove("P") # 일반 과목은 P 선택 불가
            new_grd = cols[3].selectbox("성적", options, index=options.index(course['grade']), key=f"grd_{i}")
            st.session_state.my_courses[i]['grade'] = new_grd
            
        if cols[4].button("❌", key=f"del_{i}"):
            st.session_state.my_courses.pop(i)
            st.rerun()

# 7. 초기화 버튼
if st.button("모든 데이터 초기화"):
    st.session_state.my_courses = []
    st.rerun()
