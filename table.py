from typing import List, Dict, Type
from dataclasses import fields as dataclass_fields


class Table:
    def __init__(
        self,
        table_name: str,
        list_of_field_names: List[str],
        list_of_field_types: List[Type],
        index_on_field_names: List[str] = None,
        unique_index: bool = True,
    ):
        self._table_name = table_name
        self._unique_index = unique_index
        self._list_of_field_names = list_of_field_names
        if index_on_field_names is None:
            index_on_field_names = []

        dict_of_field_types = dict(
            [
                (field_name, allowed_type)
                for field_name, allowed_type in zip(
                    list_of_field_names, list_of_field_types
                )
            ]
        )
        self._index_on_field_names = index_on_field_names
        self._list_of_field_types = list_of_field_types
        self._dict_of_field_types = dict_of_field_types

    @property
    def index_name(self):
        return "INDEX_%s" % self.table_name

    @property
    def unique_index(self):
        return self._unique_index

    @property
    def table_name(self):
        return self._table_name

    @property
    def list_of_field_names(self):
        return self._list_of_field_names

    @property
    def index_on_field_names(self):
        return self._index_on_field_names

    @property
    def list_of_field_types(self):
        return self._list_of_field_types

    @property
    def dict_of_field_types(self) -> Dict[str, Type]:
        return self._dict_of_field_types


def create_table_for_conforming_dict(
    conforming_dict: dict,
    table_name: str,
    index_on_field_names: List[str] = None,
    unique_index: bool = True,
):
    list_of_field_names = list(conforming_dict.keys())
    list_of_field_types = [type(x) for x in conforming_dict.values()]

    return Table(
        table_name=table_name,
        index_on_field_names=index_on_field_names,
        unique_index=unique_index,
        list_of_field_names=list_of_field_names,
        list_of_field_types=list_of_field_types,
    )


def create_table_for_conforming_dataclass(
    conforming_dataclass,
    table_name: str,
    index_on_field_names: List[str] = None,
    unique_index: bool = True,
):
    fields_in_class = dataclass_fields(conforming_dataclass)
    list_of_field_names = [field.name for field in fields_in_class]
    list_of_field_types = [field.type for field in fields_in_class]

    return Table(
        table_name=table_name,
        index_on_field_names=index_on_field_names,
        unique_index=unique_index,
        list_of_field_names=list_of_field_names,
        list_of_field_types=list_of_field_types,
    )


class FactoryForManagingDataClasses:
    def __init__(self, conforming_dataclass):
        self.conforming_dataclass = conforming_dataclass

    def from_dict_of_original_types_to_object_for_conforming_dataclass(
        self, dict_of_original_types: dict
    ):
        return self.conforming_dataclass(**dict_of_original_types)
