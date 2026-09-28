import calendar
import time
from copy import deepcopy
from datetime import date, datetime, timedelta
from math import isfinite

from .data_manager import DataManager as Data


class OperationManager:
    _displayed_month = (datetime.now().year, datetime.now().month)
    _selected_date = None
    _delete_confirmations = {}
    _delete_confirmation_sequence = 0
    _food_manage_date = None
    _food_manage_meal = None
    _food_manage_queue = []
    _food_search_query = ""
    _new_food_cooldown_until = 0.0
    _record_manage_drafts = {}
    _record_manage_dirty = set()
    _record_manage_weight_dirty = set()

    @staticmethod
    def GetSource(sourcefile: str):
        try:
            return Data.source[sourcefile]
        except:
            return None

    @staticmethod
    def getDate(selected_date: date | datetime | None = None):
        if selected_date is None:
            selected_date = datetime.now().date()
        elif isinstance(selected_date, datetime):
            selected_date = selected_date.date()
        weekdays = ("월", "화", "수", "목", "금", "토", "일")
        return f"{selected_date:%Y-%m-%d} ({weekdays[selected_date.weekday()]})"

    @staticmethod
    def getSelectedDate():
        return OperationManager._selected_date or datetime.now().date()

    @staticmethod
    def setSelectedDate(selected_date: date | datetime):
        if isinstance(selected_date, datetime):
            selected_date = selected_date.date()
        if not isinstance(selected_date, date):
            raise TypeError("selected_date must be a date or datetime")
        OperationManager._selected_date = selected_date
        return selected_date

    @staticmethod
    def getFoodTitle(selected_date: date | datetime | None = None):
        if selected_date is None:
            return "날짜별 식단표"
        return f"{OperationManager.getDate(selected_date)} 식단표"

    @staticmethod
    def getCalendar(selected_date: date | datetime | None = None):
        if isinstance(selected_date, datetime):
            selected_date = selected_date.date()
        highlighted_date = selected_date
        year, month = OperationManager._displayed_month
        minimum_date = OperationManager.getMinimumDate()
        weeks = calendar.Calendar(firstweekday=6).monthdayscalendar(year, month)
        weeks.extend([[0] * 7 for _ in range(6 - len(weeks))])
        weekday_labels = ("일", "월", "화", "수", "목", "금", "토")
        weekday_types = (
            "sunday",
            "weekday",
            "weekday",
            "weekday",
            "weekday",
            "weekday",
            "saturday",
        )
        records_snapshot = Data.getRecordsSnapshot()
        if not isinstance(records_snapshot, dict):
            records_snapshot = {}
        weekdays = []
        for column, label in enumerate(weekday_labels):
            weekdays.append(
                {
                    "text": label,
                    "place": {
                        "relx": column / 7,
                        "rely": 0,
                        "relwidth": 1 / 7,
                        "relheight": 1 / 7,
                        "x": 2,
                        "y": 2,
                        "width": -4,
                        "height": -4,
                    },
                }
            )
        days = []
        for row, week in enumerate(weeks, start=1):
            for column, day in enumerate(week):
                cell_date = date(year, month, day) if day else None
                is_in_range = cell_date is not None and cell_date >= minimum_date
                calendar_record = None
                if is_in_range:
                    date_key = cell_date.isoformat()
                    calendar_record = OperationManager._record_manage_drafts.get(
                        date_key, records_snapshot.get(date_key)
                    )
                days.append(
                    {
                        "text": str(day) if day else "",
                        "state": "normal" if is_in_range else "disabled",
                        "date": cell_date,
                        "in_range": is_in_range,
                        "selected": cell_date == highlighted_date
                        if cell_date is not None
                        else False,
                        "has_record": OperationManager._recordHasData(calendar_record),
                        "has_food": OperationManager._recordHasFood(calendar_record),
                        "weekday_type": weekday_types[column],
                        "row": row,
                        "column": column,
                        "place": {
                            "relx": column / 7,
                            "rely": row / 7,
                            "relwidth": 1 / 7,
                            "relheight": 1 / 7,
                            "x": 2,
                            "y": 2,
                            "width": -4,
                            "height": -4,
                        },
                    }
                )

        minimum_month = minimum_date.year * 12 + minimum_date.month - 1
        displayed_month = year * 12 + month - 1
        return {
            "title": f"{year}년 {month}월",
            "weekdays": weekdays,
            "days": days,
            "can_previous": displayed_month > minimum_month,
        }

    @staticmethod
    def showCalendarMonth(selected_date: date | datetime | None = None):
        if isinstance(selected_date, datetime):
            selected_date = selected_date.date()
        if not isinstance(selected_date, date):
            selected_date = OperationManager.getSelectedDate()
        minimum_date = OperationManager.getMinimumDate()
        selected_date = max(selected_date, minimum_date)
        OperationManager._displayed_month = (selected_date.year, selected_date.month)
        return OperationManager.getCalendar(selected_date)

    @staticmethod
    def getMinimumDate():
        today = datetime.now().date()
        try:
            previous_year_date = today.replace(year=today.year - 1)
        except ValueError:
            previous_year_date = today.replace(year=today.year - 1, day=28)
        return previous_year_date + timedelta(days=1)

    @staticmethod
    def changeCalendarMonth(offset: int, selected_date: date | datetime | None = None):
        year, month = OperationManager._displayed_month
        month_index = year * 12 + month - 1 + offset
        minimum_date = OperationManager.getMinimumDate()
        minimum_month_index = minimum_date.year * 12 + minimum_date.month - 1
        month_index = max(month_index, minimum_month_index)
        year, month_index = divmod(month_index, 12)
        OperationManager._displayed_month = (year, month_index + 1)
        return OperationManager.getCalendar(selected_date)

    @staticmethod
    def _blankRecord():
        return {
            "체중": None,
            "시간대": {meal: [] for meal in ("아침", "점심", "저녁", "야식")},
        }

    @staticmethod
    def _normalizeRecord(record):
        if not isinstance(record, dict):
            record = OperationManager._blankRecord()
        else:
            record = deepcopy(record)
        record.setdefault("체중", None)
        meals = record.get("시간대")
        if not isinstance(meals, dict):
            meals = {}
            record["시간대"] = meals
        for meal in ("아침", "점심", "저녁", "야식"):
            if not isinstance(meals.get(meal), list):
                meals[meal] = (
                    list(meals.get(meal, []))
                    if isinstance(meals.get(meal), tuple)
                    else []
                )
        return record

    @staticmethod
    def beginRecordManage(selected_date: date | datetime):
        selected_date = OperationManager._normalizeDate(selected_date)
        date_key = selected_date.isoformat()
        if date_key not in OperationManager._record_manage_drafts:
            committed = Data.getRecordsSnapshot()
            OperationManager._record_manage_drafts[date_key] = (
                OperationManager._normalizeRecord(
                    committed.get(date_key) if isinstance(committed, dict) else None
                )
            )
        return OperationManager.getManagementData(selected_date)

    @staticmethod
    def cancelRecordManage():
        OperationManager._record_manage_drafts.clear()
        OperationManager._record_manage_dirty.clear()
        OperationManager._record_manage_weight_dirty.clear()

    @staticmethod
    def commitRecordManage():
        dirty_dates = set(OperationManager._record_manage_dirty)
        if not dirty_dates:
            OperationManager.cancelRecordManage()
            return True
        with Data.transaction():
            Data.loadData(force=True)
            if not isinstance(Data.data, dict):
                raise ValueError("Records 데이터 형식이 올바르지 않습니다.")
            for date_key in sorted(dirty_dates):
                draft = OperationManager._record_manage_drafts.get(date_key)
                if draft is not None:
                    Data.data[date_key] = deepcopy(draft)
            Data.data = Data.sortRecords(Data.data)
            Data.saveRecords()
        OperationManager.cancelRecordManage()
        return True

    @staticmethod
    def _getFoodRecord(selected_date: date):
        date_key = selected_date.isoformat()
        if date_key in OperationManager._record_manage_drafts:
            return deepcopy(OperationManager._record_manage_drafts[date_key])
        records = Data.getRecordsSnapshot()
        if isinstance(records, dict):
            for key in (date_key, selected_date.strftime("%Y/%m/%d")):
                if key in records:
                    return records[key]
            record_values = records.get("records")
            if record_values is None:
                record_values = records.values()
            if isinstance(record_values, dict):
                record_values = record_values.values()
            return next(
                (
                    value
                    for value in record_values
                    if isinstance(value, dict)
                    and str(value.get("date", value.get("날짜", "")))[:10] == date_key
                ),
                None,
            )
        if isinstance(records, list):
            return next(
                (
                    value
                    for value in records
                    if isinstance(value, dict)
                    and str(value.get("date", value.get("날짜", "")))[:10] == date_key
                ),
                None,
            )
        return None

    @staticmethod
    def hasFood(selected_date: date):
        if isinstance(selected_date, datetime):
            selected_date = selected_date.date()
        if not isinstance(selected_date, date):
            return False
        record = OperationManager._getFoodRecord(selected_date)
        if not isinstance(record, dict):
            return record is not None
        meals = record.get("시간대")
        if isinstance(meals, dict):
            return any(
                isinstance(items, (list, tuple)) and items for items in meals.values()
            )
        return record is not None

    @staticmethod
    def _normalizeDate(selected_date: date | datetime):
        if isinstance(selected_date, datetime):
            return selected_date.date()
        if not isinstance(selected_date, date):
            raise TypeError("selected_date must be a date or datetime")
        return selected_date

    @staticmethod
    def _getFoods():
        foods = Data.getFoodsSnapshot()
        return foods if isinstance(foods, dict) else {}

    @staticmethod
    def getAvailableFoods():
        foods = OperationManager._getFoods()
        available = []
        for food_id, food in foods.items():
            if not isinstance(food, dict):
                continue
            if food.get("사용가능", True) is False:
                continue
            try:
                calories = float(food.get("열량", 0))
            except (TypeError, ValueError):
                calories = 0
            available.append(
                {
                    "id": food_id,
                    "name": str(food.get("이름", f"음식 {food_id}")),
                    "calories": calories,
                    "text": f"{food.get('이름', f'음식 {food_id}')} · {calories:g} kcal",
                }
            )
        return available

    @staticmethod
    def getMealItems(selected_date: date | datetime, meal: str):
        selected_date = OperationManager._normalizeDate(selected_date)
        with Data.transaction():
            record = OperationManager._getFoodRecord(selected_date)
            foods = OperationManager._getFoods()
        return OperationManager._getMealItemsFromRecord(record, foods, meal)

    @staticmethod
    def _getMealItemsFromRecord(record, foods, meal: str):
        if not isinstance(record, dict):
            return []
        meal_records = record.get("시간대", {})
        food_ids = meal_records.get(meal, []) if isinstance(meal_records, dict) else []
        items = []
        if not isinstance(food_ids, (list, tuple)):
            return items
        for index, food_id in enumerate(food_ids):
            food = foods.get(str(food_id), foods.get(food_id, {}))
            if not isinstance(food, dict):
                food = {}
            try:
                calories = float(food.get("열량", 0))
            except (TypeError, ValueError):
                calories = 0
            name = str(food.get("이름", f"알 수 없는 음식 ({food_id})"))
            items.append(
                {
                    "index": index,
                    "id": food_id,
                    "name": name,
                    "calories": calories,
                    "text": f"{name} · {calories:g} kcal",
                }
            )
        return items

    @staticmethod
    def getManagementData(selected_date: date | datetime):
        selected_date = OperationManager._normalizeDate(selected_date)
        with Data.transaction():
            record = OperationManager._getFoodRecord(selected_date)
            foods = OperationManager._getFoods()
        has_record = record is not None
        has_diet_record = OperationManager._recordHasFood(record)
        if not isinstance(record, dict):
            record = {}
        meals = {
            meal: OperationManager._getMealItemsFromRecord(record, foods, meal)
            for meal in ("아침", "점심", "저녁", "야식")
        }
        total_calories = sum(
            item["calories"] for meal_items in meals.values() for item in meal_items
        )
        return {
            "date": selected_date,
            "date_text": OperationManager.getDate(selected_date),
            "has_record": has_record,
            "has_diet_record": has_diet_record,
            "weight": record.get("체중", ""),
            "weight_pending": selected_date.isoformat()
            in OperationManager._record_manage_weight_dirty,
            "meals": meals,
            "total_calories": total_calories,
            "total_text": f"총 열량 : {total_calories:g} kcal",
            "target_calories": OperationManager.getTargetCalories(),
        }

    @staticmethod
    def getMealCardLayout():
        return [
            {
                "name": meal,
                "place": {
                    "relx": column / 2,
                    "rely": row / 2,
                    "relwidth": 0.5,
                    "relheight": 0.5,
                    "x": 3,
                    "y": 3,
                    "width": -6,
                    "height": -6,
                },
            }
            for meal, row, column in (
                ("아침", 0, 0),
                ("점심", 0, 1),
                ("저녁", 1, 0),
                ("야식", 1, 1),
            )
        ]

    @staticmethod
    def getMealReadColumnLayout():
        return [
            {
                "name": meal,
                "place": {
                    "relx": column / 4,
                    "rely": 0,
                    "relwidth": 0.25,
                    "relheight": 1,
                    "x": 2,
                    "y": 2,
                    "width": -4,
                    "height": -4,
                },
            }
            for column, meal in enumerate(("아침", "점심", "저녁", "야식"))
        ]

    @staticmethod
    def _getWritableRecord(selected_date: date):
        OperationManager.beginRecordManage(selected_date)
        return OperationManager._record_manage_drafts[selected_date.isoformat()]

    @staticmethod
    def getTargetCalories():
        Data.loadData()
        return Data.TARGET_CALORIES

    @staticmethod
    def setTargetCalories(value):
        raw_value = str(value if value is not None else "").strip()
        was_negative = False
        if not raw_value:
            calories = 0
        else:
            try:
                calories = float(raw_value)
            except (TypeError, ValueError):
                return {
                    "ok": False,
                    "message": "목표 열량에는 숫자를 기입해주세요!",
                }
            if not isfinite(calories):
                return {
                    "ok": False,
                    "message": "목표 열량에는 숫자를 기입해주세요!",
                }
            if calories < 0:
                calories = 0
                was_negative = True
            else:
                calories = int(calories) if calories.is_integer() else calories

        try:
            Data.saveTargetCalories(calories)
        except (OSError, ValueError, TypeError) as error:
            return {
                "ok": False,
                "message": f"목표 열량을 저장하지 못했습니다.\n{error}",
            }
        result = {"ok": True, "target_calories": calories}
        if was_negative:
            result["warning"] = "열량은 음수가 될 수 없습니다."
        return result

    @staticmethod
    def addFood(selected_date: date | datetime, meal: str, food_id):
        selected_date = OperationManager._normalizeDate(selected_date)
        if meal not in ("아침", "점심", "저녁", "야식"):
            return False
        foods = OperationManager._getFoods()
        food = foods.get(str(food_id), foods.get(food_id))
        if not isinstance(food, dict) or food.get("사용가능", True) is False:
            return False
        try:
            stored_id = int(food_id)
        except (TypeError, ValueError):
            stored_id = food_id
        record = OperationManager._getWritableRecord(selected_date)
        record["시간대"][meal].append(stored_id)
        OperationManager._record_manage_dirty.add(selected_date.isoformat())
        return True

    @staticmethod
    def removeFood(selected_date: date | datetime, meal: str, index: int):
        selected_date = OperationManager._normalizeDate(selected_date)
        record = OperationManager._getWritableRecord(selected_date)
        if not isinstance(record, dict):
            return False
        meal_records = record.get("시간대", {})
        if not isinstance(meal_records, dict):
            return False
        foods = meal_records.get(meal)
        if not isinstance(foods, list) or not 0 <= index < len(foods):
            return False
        foods.pop(index)
        OperationManager._record_manage_dirty.add(selected_date.isoformat())
        return True

    @staticmethod
    def setWeight(selected_date: date | datetime, weight_value: str):
        selected_date = OperationManager._normalizeDate(selected_date)
        value = str(weight_value).strip()
        if value:
            try:
                numeric_weight = float(value)
            except ValueError:
                return {"ok": False, "message": "체중을 숫자로 입력해 주세요."}
            if not isfinite(numeric_weight) or numeric_weight <= 0:
                return {"ok": False, "message": "체중은 0보다 큰 숫자여야 합니다."}
            stored_weight = (
                int(numeric_weight) if numeric_weight.is_integer() else numeric_weight
            )
        else:
            stored_weight = None
        record = OperationManager._getWritableRecord(selected_date)
        date_key = selected_date.isoformat()
        if record.get("체중") != stored_weight:
            record["체중"] = stored_weight
            OperationManager._record_manage_dirty.add(date_key)
            OperationManager._record_manage_weight_dirty.add(date_key)
        return {"ok": True, "weight": stored_weight}

    @staticmethod
    def hasDietRecord(selected_date: date | datetime):
        selected_date = OperationManager._normalizeDate(selected_date)
        record = OperationManager._getFoodRecord(selected_date)
        meals = record.get("시간대", {}) if isinstance(record, dict) else {}
        return isinstance(meals, dict) and any(
            isinstance(items, (list, tuple)) and items for items in meals.values()
        )

    @staticmethod
    def hasSavedRecord(selected_date: date | datetime):
        selected_date = OperationManager._normalizeDate(selected_date)
        records = Data.getRecordsSnapshot()
        record = (
            records.get(selected_date.isoformat())
            if isinstance(records, dict)
            else None
        )
        return OperationManager._recordHasData(record)

    @staticmethod
    def _confirmationKey(kind: str, value):
        if isinstance(value, (date, datetime)):
            value = OperationManager._normalizeDate(value).isoformat()
        return kind, str(value)

    @staticmethod
    def _beginDeleteConfirmation(kind: str, value, button_text: str):
        OperationManager._delete_confirmation_sequence += 1
        token = OperationManager._delete_confirmation_sequence
        OperationManager._delete_confirmations[
            OperationManager._confirmationKey(kind, value)
        ] = {"token": token, "remaining": 5, "button_text": button_text}
        return OperationManager._getDeleteConfirmation(kind, value)

    @staticmethod
    def _getDeleteConfirmation(kind: str, value):
        confirmation = OperationManager._delete_confirmations.get(
            OperationManager._confirmationKey(kind, value)
        )
        if confirmation is None:
            return {"active": False, "token": None, "remaining": 0, "text": "삭제"}
        return {
            "active": True,
            "token": confirmation["token"],
            "remaining": confirmation["remaining"],
            "text": f"정말로 삭제하시겠습니까? ({confirmation['remaining']})",
        }

    @staticmethod
    def _tickDeleteConfirmation(kind: str, value, token: int):
        key = OperationManager._confirmationKey(kind, value)
        confirmation = OperationManager._delete_confirmations.get(key)
        if confirmation is None or confirmation["token"] != token:
            return OperationManager._getDeleteConfirmation(kind, value)
        confirmation["remaining"] -= 1
        if confirmation["remaining"] <= 0:
            OperationManager._delete_confirmations.pop(key, None)
            return {"active": False, "token": None, "remaining": 0, "text": "삭제"}
        return OperationManager._getDeleteConfirmation(kind, value)

    @staticmethod
    def getRecordDeleteConfirmation(selected_date: date | datetime):
        return OperationManager._getDeleteConfirmation("record", selected_date)

    @staticmethod
    def beginRecordDeleteConfirmation(selected_date: date | datetime):
        if not OperationManager.hasSavedRecord(selected_date):
            return {"active": False, "token": None, "remaining": 0, "text": "삭제"}
        return OperationManager._beginDeleteConfirmation(
            "record", selected_date, "삭제"
        )

    @staticmethod
    def tickRecordDeleteConfirmation(selected_date: date | datetime, token: int):
        return OperationManager._tickDeleteConfirmation("record", selected_date, token)

    @staticmethod
    def confirmDeleteRecord(selected_date: date | datetime, token: int):
        key = OperationManager._confirmationKey("record", selected_date)
        confirmation = OperationManager._delete_confirmations.get(key)
        if confirmation is None or confirmation["token"] != token:
            return False
        OperationManager._delete_confirmations.pop(key, None)
        selected_date = OperationManager._normalizeDate(selected_date)
        record_key = selected_date.isoformat()
        with Data.transaction():
            Data.loadData(force=True)
            if not isinstance(Data.data, dict):
                return False
            record = Data.data.get(record_key)
            if not OperationManager._recordHasData(record):
                return False
            Data.data.pop(record_key)
            Data.saveRecords()
        OperationManager._record_manage_drafts.pop(record_key, None)
        OperationManager._record_manage_dirty.discard(record_key)
        OperationManager._record_manage_weight_dirty.discard(record_key)
        return True

    @staticmethod
    def beginFoodManage(selected_date: date | datetime, meal: str):
        selected_date = OperationManager._normalizeDate(selected_date)
        if meal not in ("아침", "점심", "저녁", "야식"):
            return {"ok": False, "message": "시간대가 올바르지 않습니다."}
        OperationManager._clearFoodDeleteConfirmations()
        OperationManager._food_manage_date = selected_date
        OperationManager._food_manage_meal = meal
        OperationManager._food_search_query = ""
        OperationManager._food_manage_queue = list(
            OperationManager.getMealItems(selected_date, meal)
        )
        OperationManager._food_manage_queue = [
            item["id"] for item in OperationManager._food_manage_queue
        ]
        return OperationManager.getFoodManageState()

    @staticmethod
    def _foodDetails(food_id, foods=None):
        if foods is None:
            foods = OperationManager._getFoods()
        food = foods.get(str(food_id), foods.get(food_id, {}))
        if not isinstance(food, dict):
            food = {}
        try:
            calories = float(food.get("열량", 0))
        except (TypeError, ValueError):
            calories = 0
        name = str(food.get("이름", f"알 수 없는 음식 ({food_id})"))
        return {
            "id": food_id,
            "name": name,
            "calories": calories,
            "text": f"{name} / {calories:g}(kcal)",
        }

    @staticmethod
    def getFoodManageState():
        if OperationManager._food_manage_date is None:
            return {
                "active": False,
                "title": "식단 관리",
                "query": "",
                "results": [],
                "queue": [],
            }
        query = OperationManager._food_search_query.casefold().strip()
        results = []
        foods = OperationManager._getFoods()
        for food_id, food in foods.items():
            if not isinstance(food, dict):
                continue
            if food.get("사용가능", True) is False:
                continue
            details = OperationManager._foodDetails(food_id, foods)
            if query and query not in details["name"].casefold():
                continue
            details["delete_confirmation"] = OperationManager.getFoodDeleteConfirmation(
                food_id
            )
            results.append(details)
        queue = []
        for index, food_id in enumerate(OperationManager._food_manage_queue):
            details = OperationManager._foodDetails(food_id, foods)
            details["index"] = index
            queue.append(details)
        return {
            "active": True,
            "date": OperationManager._food_manage_date,
            "meal": OperationManager._food_manage_meal,
            "query": OperationManager._food_search_query,
            "title": (
                f"{OperationManager.getDate(OperationManager._food_manage_date)} "
                f"{OperationManager._food_manage_meal} 식단"
            ),
            "results": results,
            "queue": queue,
        }

    @staticmethod
    def searchFoods(query: str):
        OperationManager._food_search_query = str(query or "")
        return OperationManager.getFoodManageState()

    @staticmethod
    def addFoodToQueue(food_id):
        foods = OperationManager._getFoods()
        food = foods.get(str(food_id), foods.get(food_id))
        if not isinstance(food, dict) or food.get("사용가능", True) is False:
            return False
        try:
            food_id = int(food_id)
        except (TypeError, ValueError):
            food_id = str(food_id)
        OperationManager._food_manage_queue.append(food_id)
        return True

    @staticmethod
    def removeFoodFromQueue(index: int):
        if not 0 <= index < len(OperationManager._food_manage_queue):
            return False
        OperationManager._food_manage_queue.pop(index)
        return True

    @staticmethod
    def commitFoodManage():
        if (
            OperationManager._food_manage_date is None
            or OperationManager._food_manage_meal is None
        ):
            return False
        record = OperationManager._getWritableRecord(OperationManager._food_manage_date)
        record["시간대"][OperationManager._food_manage_meal] = list(
            OperationManager._food_manage_queue
        )
        OperationManager._record_manage_dirty.add(
            OperationManager._food_manage_date.isoformat()
        )
        OperationManager.cancelFoodManage()
        return True

    @staticmethod
    def cancelFoodManage():
        OperationManager._clearFoodDeleteConfirmations()
        OperationManager._food_manage_date = None
        OperationManager._food_manage_meal = None
        OperationManager._food_manage_queue = []
        OperationManager._food_search_query = ""

    @staticmethod
    def _clearFoodDeleteConfirmations():
        for key in list(OperationManager._delete_confirmations):
            if key[0] == "food":
                OperationManager._delete_confirmations.pop(key, None)

    @staticmethod
    def getFoodDeleteConfirmation(food_id):
        return OperationManager._getDeleteConfirmation("food", food_id)

    @staticmethod
    def beginFoodDeleteConfirmation(food_id):
        foods = OperationManager._getFoods()
        food = foods.get(str(food_id), foods.get(food_id))
        if not isinstance(food, dict) or food.get("사용가능", True) is False:
            return {"active": False, "token": None, "remaining": 0, "text": "X"}
        OperationManager._delete_confirmation_sequence += 1
        token = OperationManager._delete_confirmation_sequence
        OperationManager._delete_confirmations[
            OperationManager._confirmationKey("food", food_id)
        ] = {"token": token, "remaining": 5, "button_text": "X"}
        confirmation = OperationManager._getDeleteConfirmation("food", food_id)
        confirmation["default_text"] = "X"
        return confirmation

    @staticmethod
    def tickFoodDeleteConfirmation(food_id, token: int):
        confirmation = OperationManager._tickDeleteConfirmation("food", food_id, token)
        if not confirmation["active"]:
            confirmation["text"] = "X"
        return confirmation

    @staticmethod
    def confirmDeleteFood(food_id, token: int):
        key = OperationManager._confirmationKey("food", food_id)
        confirmation = OperationManager._delete_confirmations.get(key)
        if confirmation is None or confirmation["token"] != token:
            return False
        OperationManager._delete_confirmations.pop(key, None)
        food_key = str(food_id)
        with Data.transaction():
            Data.loadData(force=True)
            foods = Data.foods if isinstance(Data.foods, dict) else {}
            food = foods.get(food_key, foods.get(food_id))
            if not isinstance(food, dict):
                return False
            deleted_key = next(
                (stored_key for stored_key in foods if str(stored_key) == food_key),
                None,
            )
            if deleted_key is None:
                return False
            foods.pop(deleted_key)
            records_changed = False
            if isinstance(Data.data, dict):
                for record in Data.data.values():
                    meals = record.get("시간대", {}) if isinstance(record, dict) else {}
                    if not isinstance(meals, dict):
                        continue
                    for meal_items in meals.values():
                        if isinstance(meal_items, list):
                            filtered = [
                                item for item in meal_items if str(item) != food_key
                            ]
                            if len(filtered) != len(meal_items):
                                meal_items[:] = filtered
                                records_changed = True
            for draft_key, draft in OperationManager._record_manage_drafts.items():
                meals = draft.get("시간대", {}) if isinstance(draft, dict) else {}
                if not isinstance(meals, dict):
                    continue
                for meal_items in meals.values():
                    if isinstance(meal_items, list):
                        filtered = [
                            item for item in meal_items if str(item) != food_key
                        ]
                        if len(filtered) != len(meal_items):
                            meal_items[:] = filtered
                            OperationManager._record_manage_dirty.add(draft_key)
            OperationManager._food_manage_queue = [
                queued_id
                for queued_id in OperationManager._food_manage_queue
                if str(queued_id) != food_key
            ]
            Data.foods = Data.sortFoods(foods)
            if records_changed:
                Data.data = Data.sortRecords(Data.data)
                Data.saveRecords()
            Data.saveFoods()
        return True

    @staticmethod
    def createFood(name: str, calories_value: str):
        now = time.monotonic()
        if now < OperationManager._new_food_cooldown_until:
            return {"ok": False, "message": "잠시 기다려 주세요."}
        name = str(name or "").strip()
        if not name:
            return {"ok": False, "message": "음식에는 이름이 반드시 있어야 합니다!"}
        try:
            calories = float(str(calories_value).strip())
        except (TypeError, ValueError):
            return {"ok": False, "message": "열량을 숫자로 입력해 주세요."}
        if not isfinite(calories) or calories < 0:
            return {"ok": False, "message": "열량은 0 이상의 숫자여야 합니다."}

        stored_calories = int(calories) if calories.is_integer() else calories
        with Data.transaction():
            Data.loadData(force=True)
            foods = Data.foods if isinstance(Data.foods, dict) else {}
            numeric_ids = set()
            for existing_id in foods:
                try:
                    numeric_ids.add(int(existing_id))
                except (TypeError, ValueError):
                    continue
            food_id = 1
            while food_id in numeric_ids:
                food_id += 1
            foods[str(food_id)] = {"이름": name, "열량": stored_calories}
            Data.foods = Data.sortFoods(foods)
            Data.saveFoods()
        if OperationManager._food_manage_date is not None:
            OperationManager._food_manage_queue.append(food_id)
        OperationManager._new_food_cooldown_until = now + 2.0
        return {"ok": True, "id": food_id, "message": "추가 되었습니다!"}

    @staticmethod
    def getDailyCalories(selected_date: date | datetime):
        data = OperationManager.getManagementData(selected_date)
        return data["total_calories"]

    @staticmethod
    def getDailyResult(selected_date: date | datetime):
        selected_date = OperationManager._normalizeDate(selected_date)
        data = OperationManager.getManagementData(selected_date)
        if not data["has_diet_record"]:
            return {
                "has_record": False,
                "success": None,
                "text": "해당 날짜에 등록된 식단이 없습니다.",
            }
        calories = data["total_calories"]
        target = OperationManager.getTargetCalories()
        success = calories <= target
        if success:
            result_text = f"목표 달성 성공! ({calories:g} / {target:g} kcal)"
        else:
            result_text = f"목표 달성 실패... ({calories:g} / {target:g} kcal)"
        return {
            "has_record": True,
            "success": success,
            "calories": calories,
            "target_calories": target,
            "text": result_text,
        }

    @staticmethod
    def getRecentWeightSummary(today: date | datetime | None = None):
        if today is None:
            today = datetime.now().date()
        today = OperationManager._normalizeDate(today)
        records = Data.getRecordsSnapshot()
        if not isinstance(records, dict):
            return "최근 체중 기록이 없습니다."
        measurements = []
        for days_ago in range(7, -1, -1):
            record_date = today - timedelta(days=days_ago)
            record = records.get(record_date.isoformat())
            if not isinstance(record, dict):
                continue
            try:
                weight = float(record.get("체중"))
            except (TypeError, ValueError):
                continue
            if not isfinite(weight):
                continue
            day_label = "오늘" if days_ago == 0 else f"{days_ago}일전"
            measurements.append((record_date.isoformat(), day_label, weight))
        if not measurements:
            return "최근 체중 기록이 없습니다."
        if len(measurements) == 1:
            record_date, day_label, weight = measurements[0]
            return f"{record_date} ({day_label}) / {weight:g}(Kg)"
        first_date, first_day_label, first_weight = measurements[0]
        last_date, last_day_label, last_weight = measurements[-1]
        weight_change = last_weight - first_weight
        if weight_change < 0:
            change_text = f"▼{abs(weight_change):g}(kg)▼"
        elif weight_change > 0:
            change_text = f"▲{weight_change:g}(kg)▲"
        else:
            change_text = "변화 없음 (0 kg)"
        return (
            f"{first_date} ({first_day_label}) / {first_weight:g}(Kg)\n"
            f"{last_date} ({last_day_label}) / {last_weight:g}(Kg)\n{change_text}"
        )

    @staticmethod
    def _recordHasFood(record):
        meals = record.get("시간대", {}) if isinstance(record, dict) else {}
        return isinstance(meals, dict) and any(
            isinstance(items, (list, tuple)) and items for items in meals.values()
        )

    @staticmethod
    def _recordHasData(record):
        if not isinstance(record, dict):
            return False
        weight = record.get("체중")
        return (weight is not None and str(weight).strip() != "") or (
            OperationManager._recordHasFood(record)
        )

    @staticmethod
    def getFood(selected_date: date | datetime | None = None):
        if selected_date is None:
            return "달력에서 날짜를 선택해 주세요."
        if isinstance(selected_date, datetime):
            selected_date = selected_date.date()
        if not isinstance(selected_date, date):
            raise TypeError("selected_date must be a date or datetime")

        data = OperationManager.getManagementData(selected_date)
        lines = []
        for meal, items in data["meals"].items():
            meal_text = (
                ", ".join(
                    f"{item['name']} [{item['calories']:g} kcal]" for item in items
                )
                or "-"
            )
            lines.append(f"{meal} : {meal_text}")
        weight = data["weight"] if data["weight"] is not None else "미입력"
        lines.extend(
            [
                f"체중 : {weight} Kg",
                f"총 열량 : {data['total_calories']:g} kcal",
                f"목표 열량 : {data['target_calories']:g} kcal",
            ]
        )
        if not data["has_record"]:
            lines.insert(0, "해당 날짜에 등록된 식단이 없습니다.")
        return "\n".join(lines)
