import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="계과 학점 판독기", page_icon="⚙️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #e9ecef; }
    .stButton>button:hover { background-color: #dee2e6; color: #007bff; }
    .stat-box { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚙️ 계과 학점 판독기")
st.caption("기계공학부 전용 학점 관리 및 졸업 시뮬레이터")

# --- [추가된 기능: 글로벌 데이터 저장소] ---
@st.cache_resource
def get_global_stats():
    return {
        "2,3학년": {"overall": [], "major": []},
        "4학년": {"overall": [], "major": []}
    }

global_data = get_global_stats()
# ------------------------------------------

# 2. 데이터 초기화
if 'my_courses' not in st.session_state:
    st.session_state.my_courses = []

grade_points = {
    "A+": 4.5, "A0": 4.0, "B+": 3.5, "B0": 3.0, 
    "C+": 2.5, "C0": 2.0, "D+": 1.5, "D0": 1.0, "F": 0.0, "P": "Pass"
}

major_core = ["고체역학", "열역학", "동역학", "유체역학", "기계재료", "공학기초수학1", "공학기초수학2", "기계공학프로그래밍", "열전달", "동적시스템모델링및해석", "CAE/CFD", "에너지와 환경", "기계공학도를 위한 전기전자입문", "기계요소설계"]
major_deep = ["재료거동학", "탄성학", "복합재료", "항공우주추진", "자동차공학", "미래모빌리티공학", "생산공학", "기구학", "최적설계", "응용유체역학", "응용고체역학", "소성공학", "윤활공학", "바이오공학입문", "모바일시스템제어", "계측공학", "로봇공학입문", "동적시스템제어", "기계공학도를 위한 인공지능입문", "글로벌캡스톤디자인", "졸업논문연구", "기계시스템수치해석", "공학수치해석"]
major_lab = ["고역실", "열유실", "진동실", "기설실", "기공실", "종설", "스종설"]

# 3. 사이드바
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

# 4. 학점 계산 로직
def calculate_stats():
    earned_total_crd = 0
    gpa_total_crd = 0
    total_pts = 0
    major_earned_crd = 0
    major_gpa_crd = 0
    major_pts = 0
    
    for c in st.session_state.my_courses:
        crd = c['credit']
        grd = c['grade']
        is_major = c['type'] in ["전공코어", "전공심화", "실험실습", "특수전공"]
        if grd != "F":
            earned_total_crd += crd
            if is_major: major_earned_crd += crd
        if grd != "P":
            pts = grade_points[grd]
            gpa_total_crd += crd
            total_pts += (crd * pts)
            if is_major:
                major_gpa_crd += crd
                major_pts += (crd * pts)
                
    overall_gpa = total_pts / gpa_total_crd if gpa_total_crd > 0 else 0
    major_gpa = major_pts / major_gpa_crd if major_gpa_crd > 0 else 0
    return earned_total_crd, overall_gpa, major_gpa

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

# 5. 과목 선택 구역
st.subheader("📍 과목 선택")
tab1, tab2, tab3, tab4 = st.tabs(["전공 코어", "전공 심화", "실험/실습", "URP/COOP"])

def add_course(name, type, credit, grade="A+"):
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
        new_crd = cols[2].number_input("학점", 1, 6, course['credit'], key=f"crd_{i}")
        st.session_state.my_courses[i]['credit'] = new_crd
        options = list(grade_points.keys())
        new_grd = cols[3].selectbox("성적", options, index=options.index(course['grade']), key=f"grd_{i}")
        st.session_state.my_courses[i]['grade'] = new_grd
        if cols[4].button("❌", key=f"del_{i}"):
            st.session_state.my_courses.pop(i)
            st.rerun()

# 7. 계평 (계과 평점 통계) 기능
st.divider()
st.subheader("📊 계평 (계과 평점 통계)")

# --- 수정한 부분: 안내 문구 추가 ---
st.info("📌 **25-2학기까지의 학점을 등록해 주세요. 정확한 정보를 위해 1인당 한 번씩만!**")
# -----------------------------------

c1, c2, c3 = st.columns([2, 2, 4])
with c1:
    user_grade = st.selectbox("내 학년 선택", ["2,3학년", "4학년"])
with c2:
    if st.button("🚀 내 평점 등록하기"):
        if overall_gpa > 0:
            global_data[user_grade]["overall"].append(overall_gpa)
            global_data[user_grade]["major"].append(major_gpa)
            st.success("등록 완료!")
        else:
            st.warning("먼저 과목을 추가하고 성적을 입력해주세요.")

# 평균 계산 및 표시
with st.container():
    st.write(f"#### 🔥 현재까지 집계된 {user_grade} 평균")
    avg_col1, avg_col2 = st.columns(2)
    
    grade_list = global_data[user_grade]
    avg_overall = sum(grade_list["overall"]) / len(grade_list["overall"]) if grade_list["overall"] else 0
    avg_major = sum(grade_list["major"]) / len(grade_list["major"]) if grade_list["major"] else 0
    
    with avg_col1:
        st.markdown(f"""<div class='stat-box'><b>전체 평점 평균</b><br><span style='font-size:24px; color:#007bff;'>{avg_overall:.2f}</span></div>""", unsafe_allow_html=True)
    with avg_col2:
        st.markdown(f"""<div class='stat-box'><b>전공 평점 평균</b><br><span style='font-size:24px; color:#28a745;'>{avg_major:.2f}</span></div>""", unsafe_allow_html=True)
    
    st.caption(f"현재 총 {len(grade_list['overall'])}명의 데이터가 반영되어 있습니다.")

if st.button("모든 데이터 초기화 (내 목록만)"):
    st.session_state.my_courses = []
    st.rerun()
