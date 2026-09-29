import ctypes
import json
import os
import shutil
import threading
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime
from math import isfinite
from pathlib import Path


def save(json_location, data):
    path = Path(json_location)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")


def load(json_location):
    path = Path(json_location)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


class DataManager:
    # 기본 일일 목표 섭취 열량 (kcal)
    DEFAULT_TARGET_CALORIES = 1200
    TARGET_CALORIES = DEFAULT_TARGET_CALORIES

    data = {}
    foods = {}
    _loaded = False
    _transaction_lock = threading.RLock()
    _transaction_thread_state = threading.local()
    transaction_active = False
    _data_directory = Path(__file__).resolve().parent.parent / "data"
    _backup_directory = _data_directory / "backup"
    _backup_interval_seconds = 5 * 60
    _backup_thread = None
    _backup_stop_event = threading.Event()
    source = {
        "icon": Path(__file__).resolve().parent / "source" / "Icon.ico",
        "records": _data_directory / "records.json",
        "foods": _data_directory / "foods.json",
    }

    @staticmethod
    @contextmanager
    def transaction():
        with DataManager._transaction_lock:
            depth = getattr(DataManager._transaction_thread_state, "depth", 0)
            if depth == 0:
                DataManager.transaction_active = True
            DataManager._transaction_thread_state.depth = depth + 1
            try:
                yield
            finally:
                DataManager._transaction_thread_state.depth = depth
                if depth == 0:
                    DataManager.transaction_active = False

    @staticmethod
    def loadData(force=False):
        with DataManager.transaction():
            if force or not DataManager._loaded:
                is_initial_load = not DataManager._loaded
                try:
                    if is_initial_load and any(
                        not DataManager.source[data_name].is_file()
                        for data_name in ("records", "foods")
                    ):
                        raise FileNotFoundError("Records 또는 Foods 파일이 없습니다.")
                    records_payload = load(DataManager.source["records"])
                    foods = load(DataManager.source["foods"])
                    records, target_calories, needs_migration = (
                        DataManager._unpackRecordsPayload(records_payload)
                    )
                    if not isinstance(foods, dict):
                        raise ValueError(
                            "Records 또는 Foods의 최상위 값이 딕셔너리가 아닙니다."
                        )
                    DataManager.data = DataManager.sortRecords(records)
                    DataManager.foods = DataManager.sortFoods(foods)
                    DataManager.TARGET_CALORIES = target_calories
                    if needs_migration:
                        try:
                            DataManager.saveRecords()
                        except Exception as migration_error:
                            print(
                                "Records.json 형식을 자동 변환하지 못했습니다. "
                                f"다음 저장 때 다시 적용합니다: {migration_error}"
                            )
                except Exception as error:
                    if not is_initial_load:
                        raise
                    DataManager._recoverInitialLoad(error)
                DataManager._loaded = True
            DataManager._ensureBackupScheduler()
            return DataManager.data, DataManager.foods

    @staticmethod
    def _unpackRecordsPayload(payload):
        if not isinstance(payload, dict):
            raise ValueError("Records의 최상위 값이 딕셔너리가 아닙니다.")
        if "records" not in payload:
            return payload, DataManager.DEFAULT_TARGET_CALORIES, True

        records = payload.get("records")
        target_calories = payload.get(
            "TARGET_CALORIES", DataManager.DEFAULT_TARGET_CALORIES
        )
        if not isinstance(records, dict):
            raise ValueError("Records의 records 항목이 딕셔너리가 아닙니다.")
        if (
            isinstance(target_calories, bool)
            or not isinstance(target_calories, (int, float))
            or not isfinite(float(target_calories))
        ):
            raise ValueError("TARGET_CALORIES 값이 숫자가 아닙니다.")
        return records, target_calories, False

    @staticmethod
    def _packRecordsPayload():
        return {
            "TARGET_CALORIES": DataManager.TARGET_CALORIES,
            "records": DataManager.sortRecords(DataManager.data),
        }

    @staticmethod
    def _recoverInitialLoad(load_error):
        try:
            records, foods, target_calories = DataManager._loadLatestBackup()
            DataManager.data = DataManager.sortRecords(records)
            DataManager.foods = DataManager.sortFoods(foods)
            DataManager.TARGET_CALORIES = target_calories
            try:
                DataManager.saveRecords()
                DataManager.saveFoods()
            except Exception as save_error:
                print(f"백업 복원 데이터를 저장하지 못했습니다: {save_error}")
                DataManager._initializeEmptyData()
                return
            print("가장 최근 백업 데이터로 복원했습니다.")
        except Exception as backup_error:
            print(
                "현재 데이터와 백업 데이터를 불러오지 못해 빈 데이터로 초기화합니다. "
                f"(현재 데이터: {load_error}; 백업: {backup_error})"
            )
            DataManager._initializeEmptyData()

    @staticmethod
    def _initializeEmptyData():
        DataManager.data = {}
        DataManager.foods = {}
        DataManager.TARGET_CALORIES = DataManager.DEFAULT_TARGET_CALORIES
        try:
            DataManager.saveRecords()
            DataManager.saveFoods()
        except Exception as error:
            print(f"빈 데이터 파일을 저장하지 못했습니다: {error}")

    @staticmethod
    def _loadLatestBackup():
        if not DataManager._backup_directory.is_dir():
            raise FileNotFoundError("백업 폴더가 없습니다.")
        date_directories = sorted(
            (path for path in DataManager._backup_directory.iterdir() if path.is_dir()),
            key=lambda path: path.name,
            reverse=True,
        )
        errors = []
        for date_directory in date_directories:
            time_directories = sorted(
                (path for path in date_directory.iterdir() if path.is_dir()),
                key=lambda path: path.name,
                reverse=True,
            )
            for time_directory in time_directories:
                try:
                    records_path = time_directory / DataManager.source["records"].name
                    foods_path = time_directory / DataManager.source["foods"].name
                    if not records_path.is_file() or not foods_path.is_file():
                        raise FileNotFoundError(
                            "백업 파일 한 쌍이 완성되지 않았습니다."
                        )
                    records_payload = load(records_path)
                    foods = load(foods_path)
                    records, target_calories, _ = DataManager._unpackRecordsPayload(
                        records_payload
                    )
                    if not isinstance(foods, dict):
                        raise ValueError("백업 파일의 최상위 값이 딕셔너리가 아닙니다.")
                    return records, foods, target_calories
                except Exception as error:
                    errors.append(f"{time_directory}: {error}")
        detail = "; ".join(errors) if errors else "사용 가능한 백업이 없습니다."
        raise FileNotFoundError(detail)

    @staticmethod
    def _ensureBackupScheduler():
        if (
            DataManager._backup_thread is not None
            and DataManager._backup_thread.is_alive()
        ):
            return
        DataManager._backup_stop_event.clear()
        DataManager._backup_thread = threading.Thread(
            target=DataManager._backupLoop,
            name="DataManagerBackup",
            daemon=True,
        )
        DataManager._backup_thread.start()

    @staticmethod
    def _backupLoop():
        while not DataManager._backup_stop_event.wait(
            DataManager._backup_interval_seconds
        ):
            try:
                DataManager.backupCurrentData()
            except Exception as error:
                print(f"{datetime.now():%H:%M:%S} 백업 실패: {error}")

    @staticmethod
    def _setHidden(path):
        if os.name != "nt":
            return
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        get_attributes = kernel32.GetFileAttributesW
        get_attributes.argtypes = [ctypes.c_wchar_p]
        get_attributes.restype = ctypes.c_uint32
        set_attributes = kernel32.SetFileAttributesW
        set_attributes.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32]
        set_attributes.restype = ctypes.c_int
        attributes = get_attributes(str(path))
        if attributes == 0xFFFFFFFF:
            raise ctypes.WinError(ctypes.get_last_error())
        if not attributes & 0x2 and not set_attributes(str(path), attributes | 0x2):
            raise ctypes.WinError(ctypes.get_last_error())

    @staticmethod
    def backupCurrentData():
        with DataManager.transaction():
            DataManager.loadData()
            now = datetime.now()
            date_directory = DataManager._backup_directory / now.strftime("%Y-%m-%d")
            time_directory = date_directory / now.strftime("%H-%M-%S")
            if time_directory.exists():
                time_directory = date_directory / now.strftime("%H-%M-%S-%f")
            time_directory.mkdir(parents=True, exist_ok=False)
            DataManager._setHidden(DataManager._backup_directory)
            DataManager._setHidden(date_directory)
            DataManager._setHidden(time_directory)

            for data_name in ("records", "foods"):
                source_path = DataManager.source[data_name]
                backup_path = time_directory / source_path.name
                if source_path.is_file():
                    shutil.copy2(source_path, backup_path)
                elif data_name == "records":
                    save(backup_path, DataManager._packRecordsPayload())
                else:
                    save(backup_path, DataManager.sortFoods(DataManager.foods))
                DataManager._setHidden(backup_path)

            DataManager._pruneBackups()
            print(f"{now:%H:%M:%S} 백업 완료")
            return time_directory

    @staticmethod
    def _pruneBackups(maximum_backups=12):
        if not DataManager._backup_directory.is_dir():
            return

        backups = []
        records_filename = DataManager.source["records"].name
        foods_filename = DataManager.source["foods"].name
        for date_directory in DataManager._backup_directory.iterdir():
            if not date_directory.is_dir():
                continue
            for time_directory in date_directory.iterdir():
                if time_directory.is_dir():
                    backups.append(
                        (
                            date_directory.name,
                            time_directory.name,
                            date_directory,
                            time_directory,
                            (time_directory / records_filename).is_file()
                            and (time_directory / foods_filename).is_file(),
                        )
                    )

        backups.sort(key=lambda backup: (backup[0], backup[1]), reverse=True)
        completed_backups = [backup for backup in backups if backup[4]]
        retained_backups = {
            backup[3] for backup in completed_backups[:maximum_backups]
        }
        for _, _, date_directory, time_directory, _ in backups:
            if time_directory in retained_backups:
                continue
            for backup_file in time_directory.iterdir():
                if backup_file.is_file() and backup_file.suffix.lower() == ".json":
                    backup_file.unlink()
            shutil.rmtree(time_directory)

            if date_directory.exists() and not any(
                child.is_dir() for child in date_directory.iterdir()
            ):
                shutil.rmtree(date_directory)

    @staticmethod
    def getRecordsSnapshot():
        with DataManager.transaction():
            DataManager.loadData()
            return deepcopy(DataManager.data)

    @staticmethod
    def getFoodsSnapshot():
        with DataManager.transaction():
            DataManager.loadData()
            return deepcopy(DataManager.foods)

    @staticmethod
    def sortRecords(records):
        if not isinstance(records, dict):
            return records
        return dict(sorted(records.items(), key=lambda item: str(item[0])))

    @staticmethod
    def sortFoods(foods):
        if not isinstance(foods, dict):
            return foods

        def food_id_sort_key(item):
            try:
                return (0, int(item[0]))
            except (TypeError, ValueError):
                return (1, str(item[0]))

        return dict(sorted(foods.items(), key=food_id_sort_key))

    @staticmethod
    def saveRecords():
        with DataManager.transaction():
            DataManager.data = DataManager.sortRecords(DataManager.data)
            save(DataManager.source["records"], DataManager._packRecordsPayload())

    @staticmethod
    def saveTargetCalories(target_calories):
        with DataManager.transaction():
            DataManager.loadData()
            DataManager.TARGET_CALORIES = target_calories
            DataManager.saveRecords()

    @staticmethod
    def saveFoods():
        with DataManager.transaction():
            DataManager.foods = DataManager.sortFoods(DataManager.foods)
            save(DataManager.source["foods"], DataManager.foods)
