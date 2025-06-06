import os
from pydantic import BaseModel, Field, field_serializer
import tomllib
from enum import Enum
from pathlib import Path


class _ReportStruct(BaseModel):
    """
    Patterns. Use for function get_obj_report. Only for struct. Generate custom struct report instead standart. Where %nxx: n - name of struct element,
    xx - index of struct element; %vxx: v - value of struct element, xx - index of struct element
    """
    DayProfileAction: str = "%n00: %v00 - Тариф: %v02"


class _Report(BaseModel):
    empty: str = "--"
    empty_unit: str = "??"
    scaler_format: str = "{:.3f}"
    struct: _ReportStruct = Field(default_factory=_ReportStruct)


class _Collection(BaseModel):
    path: str = "./Types/"


class _FirmwaresKey(BaseModel):
    codec: str = "ascii"
    value: str = "00000000password"


class _Firmware(BaseModel):
    key: _FirmwaresKey = Field(default_factory=_FirmwaresKey)
    man: str = Field("KPZ")
    path: Path = Field(Path("./Firmwares/firmwares.dat"))

    @field_serializer("path")
    def serialize1_path(self, path: Path) -> str:
        return str(path)


class _AmNames(BaseModel):
    """all attributes and methods names of classes"""
    # Data
    value: str = "value"
    # Register
    scaler_unit: str = "scaler unit"
    # Extended register
    status: str = "status"
    capture_time: str = "capture time"
    # Demand register
    current_average_value: str = "current average value"
    last_average_value: str = "last average value"
    start_time_current: str = "start time current"
    period: str = "period"
    number_of_periods: str = "number of periods"
    # Register activation
    mask: str = "mask"
    active_value: str = "active value"
    active_objects: str = "active objects"
    # Profile generic
    buffer: str = "buffer"
    capture_objects: str = "capture objects"
    capture_period: str = "capture period"
    sort_method: str = "sort method"
    sort_object: str = "sort object"
    entries_in_use: str = "entries in use"
    profile_entries: str = "profile entries"
    # Utility tables
    table: str = "table"
    # Register table
    table_cell_values: str = "table cell values"
    # Status mapping
    status_map: str = "status map"
    # Compact data
    compact_buffer: str = "compact buffer"
    # Association SN
    object_list: str = "object list"
    access_rights_list: str = "access rights list"
    # SAP Assignment
    sap_assignment_list: str = "sap assignment list"
    # Image transfer
    image_block_size: str = "image block size"
    image_transferred_blocks_status: str = "image transferred blocks status"
    image_first_not_transferred_block_number: str = "image first not transferred block number"
    image_transfer_enabled: str = "image transfer enabled"
    image_transfer_status: str = "image transfer status"
    # Security setup
    security_policy: str = "security policy"
    security_suite: str = "security suite"
    # Push setup
    push_object_list: str = "push object list"
    send_destination_and_method: str = "send destination and method"
    # Data protection
    protection_parameters_get: str = "protection parameters get"
    protection_parameters_set: str = "protection parameters set"
    # Function control
    function: str = "function"
    # Array manager
    array_components: str = "array components"
    # Communication port protection
    protection_mode: str = "protection mode"
    # Clock
    time: str = "time"
    time_zone: str = "time zone"
    # Script table
    scripts: str = "scripts"
    # Schedule
    entries: str = "entries"
    # Activity calendar
    calendar_name: str = "calendar name"
    season_profile: str = "season profile"
    week_profile: str = "week profile"
    # Register monitor
    thresholds: str = "thresholds"
    monitored_value: str = "monitored value"
    # Single action schedule
    executed_script: str = "executed script"
    # Disconnect control
    output_state: str = "output state"
    # Sensor manager
    sensor_values: str = "sensor values"
    # Arbitrator
    action_sets: str = "action sets"
    # Account
    payment_mode: str = "payment mode"
    account_balance: str = "account balance"
    # Credit
    current_credit_amount: str = "current credit amount"
    # Charge
    unit_charge_active: str = "unit charge active"
    # Token gateway
    token: str = "token"
    # Methods
    reset: str = "reset"
    next_period: str = "next period"
    image_transfer_initiate: str = "image transfer initiate"
    image_block_transfer: str = "image block transfer"
    image_verify: str = "image verify"
    image_activate: str = "image activate"
    security_activate: str = "security activate"
    push: str = "push"
    get_protected_attributes: str = "get protected attributes"
    set_protected_attributes: str = "set protected attributes"
    invoke_protected_method: str = "invoke protected method"
    add_element: str = "add element"
    remove_element: str = "remove element"
    adjust_to_measurement: str = "adjust to measurement"
    adjust_to_quarter: str = "adjust to quarter"
    adjust_to_minute: str = "adjust to minute"
    activate: str = "activate"
    disconnect: str = "disconnect"
    reconnect: str = "reconnect"
    credit_payment: str = "credit payment"
    debit_payment: str = "debit payment"
    set_credit: str = "set credit"
    collect_charge: str = "collect charge"
    process_token: str = "process token"


class Settings(BaseModel):
    collection: _Collection = Field(default_factory=_Collection)
    report: _Report = Field(default_factory=_Report)
    firmwares: list[_Firmware] = Field(default_factory=list)
    am_names: _AmNames = Field(default_factory=_AmNames)


if not os.path.isfile(path := ".//config.toml"):
    path = F"{os.path.dirname(__file__)}{path}"
elif os.path.isfile(path):
    with open(path, "rb") as f:
        toml_data = tomllib.load(f)
        data = toml_data.get("DLMS", {})
        print(f"Find configuration <config.toml> with path: {f}")
        settings = Settings(**data)
else:
    print("NOT FIND CONFIGURATION: <config.toml>")
    toml_data = {}
    settings = Settings()


# remove in future


def version():
    return "0.2.0"


class Language(Enum):
    ENGLISH = 'English'
    RUSSIAN = 'Russian'


__current_language = Language.RUSSIAN


def set_current_language(value: str):
    global __current_language
    __current_language = Language(value)


def get_current_language() -> Language:
    return __current_language
