import datetime
from enum import Enum
from typing import Union, Type, List

from table import Table
from translators import Translators


def from_list_of_dicts_with_original_type_to_list_of_objects(
    list_of_dicts_with_original_type: List[dict], translators: Translators
):
    list_of_objects = [
        translators.from_dict_of_original_types_to_object(dict_with_original_types)
        for dict_with_original_types in list_of_dicts_with_original_type
    ]

    return translators.list_like_creator_from_list_of_objects(list_of_objects)


def from_ordered_list_of_allowed_types_to_list_of_dicts_of_original_type(
    raw_list: list, list_of_field_names: List[str], table: Table
):
    list_of_dicts = [
        from_ordered_list_to_dict_with_allowed_types(
            ordered_list=ordered_list, list_of_field_names=list_of_field_names
        )
        for ordered_list in raw_list
    ]
    list_of_dicts_with_original_types = [
        from_dict_of_allowed_types_to_original_dict(some_dict, table=table)
        for some_dict in list_of_dicts
    ]

    return list_of_dicts_with_original_types


def from_ordered_list_to_dict_with_allowed_types(
    ordered_list: list, list_of_field_names: List[str]
):
    return dict(
        [
            (field_name, value)
            for field_name, value in zip(list_of_field_names, ordered_list)
        ]
    )


def dict_with_allowed_types_from_object(
    translators: Translators, table: Table, some_object
):
    dict_with_original_types = translators.from_object_to_dict_of_original_types(
        some_object
    )
    dict_with_allowed_types = from_dict_to_dict_of_allowed_types(
        dict_with_original_types, table=table
    )

    return dict_with_allowed_types


def object_from_dict_with_allowed_types(
    translators: Translators, table: Table, some_dict: dict
):
    dict_with_original_types = from_dict_of_allowed_types_to_original_dict(
        some_dict, table=table
    )
    new_object = translators.from_dict_of_original_types_to_object(
        dict_with_original_types
    )

    return new_object


def from_dict_to_dict_of_allowed_types(dict_with_original_types: dict, table: Table):
    dict_of_field_types = table.dict_of_field_types
    return dict(
        [
            (
                field_name,
                from_field_to_allowed_type(
                    value, allowed_type=dict_of_field_types.get(field_name)
                ),
            )
            for field_name, value in dict_with_original_types.items()
        ]
    )


def from_dict_of_allowed_types_to_original_dict(some_dict: dict, table: Table):
    dict_of_field_types = table.dict_of_field_types
    return dict(
        [
            (
                field_name,
                from_allowed_type_back_to_field(
                    value, original_type=dict_of_field_types.get(field_name)
                ),
            )
            for field_name, value in some_dict.items()
        ]
    )


def from_field_to_allowed_type(value, allowed_type: Type):
    if allowed_type in [int, float, str]:
        return value
    elif allowed_type in [datetime.datetime, datetime.date]:
        return date2int(value)
    elif allowed_type == bool:
        return from_bool_to_int(value)
    elif issubclass(allowed_type, Enum):
        return from_enum_to_str(value)
    else:
        raise Exception(
            "Only types allowed are int,str,Enum subclass, datetime.date, datetime.datetime and bool not %s"
            % str(allowed_type)
        )


def from_allowed_type_back_to_field(value, original_type: Type):
    if original_type == int:
        return int(value)
    elif original_type == float:
        return float(value)
    elif original_type == str:
        return str(value)
    elif original_type in [datetime.date, datetime.datetime]:
        return int2date(value)
    elif original_type == bool:
        return from_int_to_bool(value)
    elif issubclass(original_type, Enum):
        return from_str_to_enum(value, original_type)
    else:
        raise Exception(
            "Only types allowed are int,str,Enum subclass, datetime.date, datetime.datetime and bool not %s"
            % str(original_type)
        )


def from_str_to_enum(some_str, original_type: Type):
    return original_type[some_str]  ## ignore warning


def from_enum_to_str(some_enum):
    return some_enum.name


def from_bool_to_int(class_instance: bool) -> int:
    as_int = 1 if class_instance else 0
    return as_int


def from_int_to_bool(some_int: int) -> bool:
    if some_int == 1:
        return True
    elif some_int == 0:
        return False
    raise Exception("%s is not 1 or 0" % str(some_int))


def date2int(some_datetime: Union[datetime.date, datetime.datetime]) -> int:
    if type(some_datetime) is datetime.date:
        some_datetime = datetime.datetime(
            some_datetime.year,
            some_datetime.month,
            some_datetime.day,
            tzinfo=datetime.timezone.utc,
        )
    return int(some_datetime.timestamp())


def int2date(some_int: int) -> Union[datetime.date, datetime.datetime]:
    some_datetime = datetime.datetime.fromtimestamp(
        float(some_int), datetime.timezone.utc
    )
    if some_datetime.minute == 0:
        if some_datetime.hour == 0:
            return datetime.date(
                some_datetime.year, some_datetime.month, some_datetime.day
            )

    return some_datetime


def from_python_type_to_named_type(python_type: type):
    if python_type == str:
        return "STR"
    elif python_type in [int, bool, datetime.date, datetime.datetime]:
        return "INTEGER"
    elif python_type == float:
        return "REAL"
    elif issubclass(python_type, Enum):
        return "STR"
    else:
        raise Exception(
            "Only types allowed are int,str,Enum subclass, datetime.date, datetime.datetime and bool not %s"
            % str(python_type)
        )
