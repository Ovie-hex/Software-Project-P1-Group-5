# ======================================================================================================
# 서비스 구성 및 실행 흐름
# ======================================================================================================
# main.py
# - 프로그램 실행 진입점이다. service 패키지에서 GUI를 가져와 GUI 인스턴스를 만든다.
# - GUI.__init__이 Window, Page, Widget을 구성하고 마지막에 Tk mainloop를 시작한다.
#
# service/__init__.py
# - gui_manager의 GUI 클래스를 패키지 외부에 공개한다.
#
# service/data_manager.py : DataManager (저장소와 파일 입출력)

# - records.json, foods.json의 실제 경로와 메모리 캐시를 관리한다.

# - Records는 {"TARGET_CALORIES": 숫자, "records": {"YYYY-MM-DD": 기록}} 구조로 읽고 쓴다.
#   각 날짜 기록에는 체중과 아침·점심·저녁·야식 음식 ID 목록이 저장된다.

# - Foods는 음식 ID를 키로 하며 음식 이름, 열량 등의 정보를 보관한다.

# - transaction()은 재진입 가능한 잠금으로 데이터 읽기/쓰기를 보호한다.
#   transaction_active는 데이터 트랜잭션이 진행 중인지 나타낸다.
# - loadData()는 JSON을 읽고 이전 Records 형식은 새 형식으로 이전한다.

#   최초 로딩에 실패하면 가장 최근의 정상 백업을 찾아 복원하고,
#   백업도 읽지 못하면 기본 목표 열량과 빈 Records/Foods로 초기화한다.

# - loadData()가 시작한 백업 스케줄러는 5분마다 records.json과 foods.json을 복사한다.
#   백업은 data/backup/YYYY-MM-DD/HH-MM-SS 아래에 두며 Windows 숨김 속성을 적용한다.

# - 백업이 성공하면 현재 시각과 "백업 완료"를 출력한다.
# - saveRecords(), saveFoods(), saveTargetCalories()가 파일 저장을 맡는다.
#   Records 날짜 키와 Foods 숫자형 ID는 저장 전에 정렬한다.

# - getRecordsSnapshot(), getFoodsSnapshot()은 트랜잭션 안에서 복사본을 돌려줘
#   호출자가 원본 캐시를 직접 바꾸지 않도록 한다.
#

# service/operation_manager.py : OperationManager (업무 규칙과 데이터 중개)

# - GUI가 JSON 구조나 저장 세부사항을 직접 다루지 않도록 DataManager를 감싼다.

# - 날짜 문자열, 선택 날짜, 달력 범위와 달력 셀 상태를 계산한다.
#   getCalendar()는 날짜 기록 여부, 요일 종류, 활성화 상태, 배치 좌표를 반환한다.

# - getManagementData(), getMealItems(), getAvailableFoods()는 화면에 필요한
#   음식 이름·열량·체중·총 열량 등의 표시용 데이터를 구성한다.

# - beginRecordManage()/setWeight()/addFood()/removeFood()는 편집 중인 기록 초안을
#   갱신한다. commitRecordManage()에서만 Records 파일에 반영하고,
#   cancelRecordManage()는 저장 전 편집 내용을 버린다.

# - beginFoodManage()/searchFoods()/addFoodToQueue()/removeFoodFromQueue()는
#   시간대 음식 선택과 대기열을 관리한다. commitFoodManage()는 대기열을 기록 초안에
#   반영하며 실제 파일 저장은 기록 관리 페이지의 확인 단계에서 이루어진다.

# - createFood(), confirmDeleteFood()는 Foods를 저장하고 음식 ID 및 기존 기록 연결을
#   관리한다. 삭제 확인 상태는 5초 카운트다운과 토큰으로 관리한다.

# - setTargetCalories(), getDailyResult(), getRecentWeightSummary()는 목표 열량,
#   목표 달성 결과, 오늘부터 7일 전까지 기록된 체중 비교 문자열을 제공한다.

# - getMealCardLayout(), getMealReadColumnLayout()은 GUI에서 쓸 카드 배치 자료를 제공한다.
#
# service/gui_manager.py : GUI와 화면 구성 계층
# - Widget은 Tk 위젯을 감싸 이름, 스타일, 부모/자식 관계, 배치, sync, event를 관리한다.
#   syncWidget()은 자식 위젯부터 재귀적으로 동기화한 뒤 현재 위젯의 sync를 호출한다.
#   버튼 등의 event는 사용자 동작을 OperationManager에 전달하는 콜백이다.

# - Page는 한 화면과 그 안의 최상위 Widget들을 관리하고, Window는 페이지 전환과
#   Tk 창의 생명주기를 관리한다. 페이지 이동 시 이전 페이지를 숨기고 새 페이지를 보인다.

# - GUI.__init__은 화면 계층과 event/sync 연결을 구성한다. 데이터 조회·검증·계산은
#   OperationManager를 거치며, GUI.__init__ 안에서는 라이브러리를 import하지 않는다.
#

# 일반 데이터 흐름
# - 사용자의 입력/클릭 -> GUI event -> OperationManager 업무 처리 -> DataManager 저장소
# - 화면 갱신 -> Widget.syncWidget() -> 해당 sync 함수가 OperationManager 값을 조회해 표시
# - 기록 관리 중에는 초안으로 유지하고 확인을 눌렀을 때만 저장한다.


# ======================================================================================================
# gui_manager 화면 안내: 페이지별 기능, 위젯, sync 및 event
# ======================================================================================================
# 공통 안내


# - 아래 위젯 이름은 gui_manager.py에서 사용하는 실제 Widget name이다.

# - no_sync는 고정 표시용 위젯에 연결되는 빈 동기화 함수다.

# - sync는 OperationManager에서 받은 값을 위젯 스타일/텍스트/목록에 적용한다.

# - event는 버튼 클릭을 처리한다. 달력 날짜 버튼은 draw_calendar 계열 함수가
#   날짜 범위에 따라 활성화, 색상, 날짜 선택 event를 갱신한다.

# - 스크롤 목록은 Frame 안의 Canvas, Scrollbar, "목록 내용" Frame으로 구성된다.
#   목록 sync가 자식 Label/Frame을 다시 만들고 Canvas 스크롤 영역을 갱신한다.
#
# ------------------------------------------------------------------------------------------------------
# defaultPage : 오늘/선택 날짜의 요약과 바로가기
# ------------------------------------------------------------------------------------------------------
# 1) "날짜 메뉴" Frame

#    - "날짜 제목" Label: 날짜 영역의 고정 제목, sync=no_sync.

#    - "날짜" Label: 선택 날짜를 표시, sync=sync_main_date.

#    - "조회" Button: event=onRecordReadButton. calendarReadPage를 열고 선택 날짜의
#      달력/식단 조회를 시작한다.

#    - "관리" Button: event=onRecordManageButton. 선택 날짜로 기록 초안을 시작하고
#      recordManagePage로 이동한다.

# 2) "식단표 타이틀" Label: 식단표 섹션 제목, sync 없음.

# 3) "식단표 프레임" Frame

#    - "시간대 식단" Frame 안에 아침·점심·저녁·야식 카드 네 개를 2x2로 배치한다.

#    - 각 시간대 Frame의 "제목" Label은 시간대 이름을 표시한다(no_sync).

#    - 각 시간대의 "음식 목록 영역" 안에는 "스크롤 프레임", "목록 캔버스",
#      "세로 스크롤", "목록 내용"이 있다. "목록 내용" sync는
#      sync_main_meal_list(widget, meal)이며 해당 날짜의 음식명/열량 또는 빈 목록 안내를 표시한다.

#    - "일일 요약" Label은 sync_main_meal_summary로 총 섭취 열량과 체중을 표시한다.

# 4) "체중 현황 타이틀" Label: 최근 체중 변화 섹션 제목, sync 없음.

#    "체중 현황" Label은 sync_main_weight_status로 오늘부터 7일 전까지의 체중 기록 날짜,
#    경과 일수, 비교값과 증감폭을 표시한다.

# 5) "목표 열량 프레임"

#    - "목표 열량 안내" Label과 "목표 열량 입력" Entry는 안내 및 사용자 입력용(no_sync).

#    - "목표 열량 확인" Button은 event=confirm_main_target_calories로 입력값을 검증·저장한다.

#    - "현재 목표 열량" Label은 sync_main_target_calories로 저장된 목표 kcal을 표시한다.

# 6) "결과" Label은 sync_main_result로 선택 날짜의 목표 달성 결과 또는 식단 미등록 상태를 표시한다.
#
# ------------------------------------------------------------------------------------------------------
# calendarReadPage : 저장된 날짜 기록 조회
# ------------------------------------------------------------------------------------------------------
# 최상위 "달력 프레임" Frame 안에 달력, 월 이동, 식단 카드, 요약, 결정 버튼이 있다.

# - "달력 월" Label은 draw_calendar가 OperationManager의 월 제목으로 갱신한다.

# - "요일 및 날짜" Frame은 요일 Label과 6x7 날짜 Button을 담는다.
#   날짜 버튼 이름은 "날짜 행-열"이다. draw_calendar가 날짜 범위/기록 여부에 따라
#   색상과 활성 상태를 정하고, event에서 show_food_for_date(selected)를 호출한다.
#   요일 Label은 "요일 일"부터 "요일 토"까지이며 고정(no_sync)이다.

# - "달력 이동 메뉴" Frame의 "이전 달"/"다음 달" Button은 change_month(-1/+1)을 호출한다.

# - "조회 식단 제목" Label은 sync_calendar_food_title로 선택 날짜 제목을 표시한다.

# - "조회 식단 목록" Frame은 아침·점심·저녁·야식 네 카드를 한 행 4열로 배치한다.
#   각 카드의 "제목" Label은 시간대명이고, "음식 목록 영역"의 Canvas/Scrollbar/
#   "목록 내용"은 sync_calendar_meal_list(widget, meal)로 음식명과 열량을 갱신한다.
#   날짜 미선택/해당 시간대 음식 없음 상태도 목록 안에 안내한다.

# - "조회 식단 요약" Label은 sync_calendar_meal_summary로 선택 날짜의 총 섭취 열량과
#   체중을 표시한다. show_food_for_date가 제목, 네 음식 목록, 요약을 함께 동기화한다.

# - "조회 결정 메뉴"의 "확인" Button은 event=confirm_selected_date로 선택 날짜를
#   OperationManager에 저장하고 defaultPage로 돌아간다.

# - "메인으로 돌아가기" Button은 event에서 선택 확정 없이 defaultPage로 이동한다.
#
# ------------------------------------------------------------------------------------------------------
# recordManagePage : 날짜별 기록 초안 편집 및 저장
# ------------------------------------------------------------------------------------------------------
# 최상위 "관리 화면 프레임" 안에 다음 위젯들이 있다.

# 1) "날짜 메뉴" Frame

#    - "관리 날짜" Label: sync_managed_date로 편집 대상 날짜 표시.

#    - "조회" Button: event=open_write_calendar. 현재 체중 입력을 초안에 반영한 뒤
#      calendarWritePage를 연다.

#    - "삭제" Button: sync_record_delete_button이 해당 날짜에 저장된 체중 또는 음식 기록
#      유무와 확인 상태를 표시한다.
#      event=click_record_delete는 첫 클릭 뒤 5초 카운트다운을 시작하고, 제한 시간 내
#      재클릭 시 해당 날짜의 기록 전체를 삭제한 뒤 defaultPage로 이동한다.


# 2) "시간대 식단" Frame에는 2x2 아침·점심·저녁·야식 카드가 있다.
#    - 각 카드의 "제목 메뉴" 안 "제목" Label은 시간대명, "음식 관리" Button은
#      event=open_food_manage(meal)로 해당 시간대의 foodManagePage를 연다.

#    - "음식 목록 영역"의 Canvas/Scrollbar/"목록 내용"은 sync_meal_list(widget, meal)로
#      현재 음식 목록을 표시한다. 각 항목은 "음식 정보" Label과 오른쪽 "음식 삭제" Button을 가진다.
#      삭제 Button event는 remove_meal_food(meal, index)로 초안에서 항목을 제거한다.


# 3) "총 열량" Label은 sync_total_calories로 현재 초안의 합계를 표시한다.

# 4) "체중 입력 메뉴" Frame

#    - "체중 제목" Label은 입력 단위를 안내한다.

#    - "체중 입력" Entry는 sync_weight_entry로 저장된/초안 체중을 채운다.

#    - "체중 반영값" Label은 sync_weight_value로 저장값인지 확인 전 초안값인지 표시한다.

#    - "체중 저장" Button은 event=save_management_weight. 숫자 검증 후 초안에 반영하고
#      페이지 표시를 갱신한다. 이 버튼만으로 Records 파일에 확정 저장하지 않는다.

# 5) "관리 결정 메뉴" Frame의 "확인" Button은 event=save_weight_and_return으로 체중을
#    포함한 초안을 저장하고 defaultPage로 이동한다. "메인으로 돌아가기" Button은
#    event=cancel_record_management로 미저장 초안을 취소하고 돌아간다.
#
# ------------------------------------------------------------------------------------------------------
# calendarWritePage : 기록 대상 날짜 선택
# ------------------------------------------------------------------------------------------------------

# - "달력 프레임" Frame의 "달력 월" Label, "요일 및 날짜" Frame, 요일 Label 및
#   "날짜 행-열" Button은 조회 달력과 같은 달력 구조다.

# - draw_write_calendar가 월/날짜 색상과 활성 상태, 선택 날짜 강조를 갱신한다.
#   활성 날짜 Button event는 select_write_date(selected)로 임시 선택일을 바꾼다.

# - "달력 이동 메뉴"의 "이전 달"/"다음 달" Button event는 change_write_month(-1/+1)이다.

# - "선택 날짜" Label은 sync_write_date로 현재 임시 선택일을 표시한다.

# - "기록 날짜 결정 메뉴"의 "확인" Button은 event=confirm_write_date로 선택일을
#   OperationManager와 recordManagePage 편집 상태에 반영하고 recordManagePage로 복귀한다.

# - "취소" Button은 날짜 변경을 확정하지 않고 recordManagePage로 돌아간다.
#
# ------------------------------------------------------------------------------------------------------
# foodManagePage : 시간대 식단의 음식 선택, 음식 사전 관리
# ------------------------------------------------------------------------------------------------------
# 최상위 "음식 관리 프레임" 안에 다음 위젯들이 있다.

# 1) "검색 메뉴" Frame

#    - "검색 입력" Entry는 sync_food_search_entry로 OperationManager의 검색어를 복구한다.

#    - "검색 버튼" Button은 sync_food_search_results로 표시 스타일을 적용하고,
#      event=submit_food_search로 검색 결과를 갱신한다.


# 2) "검색 결과 목록"은 Canvas/Scrollbar/"목록 내용" 스크롤 영역이다.

#    - 목록 내용 sync=sync_food_results. 검색 결과가 없으면 안내 Label을 만든다.

#    - 각 "검색 결과 N" Frame에는 "음식 정보" Label, "대기열 추가" Button, "음식 삭제" Button이 있다.

#    - + Button event는 add_food_to_queue(food_id)로 선택 음식을 대기열에 추가한다.

#    - X Button event는 click_food_delete(food_id). 5초 재확인 후 Foods와 참조 기록에서 삭제한다.


# 3) "음식 추가 프레임"

#    - "음식 이름 제목"/"열량 제목" Label은 입력 항목을 설명한다.

#    - "음식 이름 입력"/"열량 입력" Entry는 sync_clear_entry로 초기화한다.

#    - "추가" Button은 sync_food_add_button, event=create_new_food이다. 음식 이름과 열량을
#      검증해 즉시 Foods에 저장한다. 현재 음식 관리 중이면 대기열에도 넣고,
#      성공 안내 Label을 2초 표시한다.

#    - "추가 성공 메시지" Label은 저장 성공 때 입력 행 대신 잠시 표시된다.


# 4) "대기열 제목" Label은 sync_food_manage_title로 날짜와 시간대 식단 제목을 표시한다.

#    "식단 대기열 목록"의 Canvas/Scrollbar/"목록 내용"은 sync_food_queue로 대기 항목을 만든다.
#    각 "대기 음식 N" Frame에는 "음식 정보" Label과 "대기열에서 제거" Button이 있으며,
#    제거 event는 remove_queued_food(index)다. 대기열 변경은 아직 Records 파일에 저장되지 않는다.

# 5) "확인 취소 메뉴"의 "확인" Button은 event=confirm_food_manage로 대기열을 기록 초안에
#    반영하고 recordManagePage로 돌아간다. 실제 기록 파일 저장은 기록 관리 확인 단계에서 한다.
#    "취소" Button은 event=cancel_food_manage로 대기열 변경을 버리고 recordManagePage로 돌아간다.


# -------------------------------------------------------------------------------------------------------
# 프로그램 실행
# -------------------------------------------------------------------------------------------------------

from service import GUI

GUI()
