from dataclasses import dataclass
from typing import List, Union

no_ordering = object()


@dataclass  # ORDER BY Country ASC, CustomerName DESC
class OrderBy:
    field_name: str
    desc: bool = False


def create_order_by_sql(
    sort_by_field_list: Union[str, List[Union[OrderBy, str]]] = no_ordering
):
    if sort_by_field_list is no_ordering:
        return SqlStr("")
    if type(sort_by_field_list) == str:
        sort_by_field_list = [sort_by_field_list]
    sort_by_field_list_of_str = [
        order_by_element(order_by) for order_by in sort_by_field_list
    ]
    sort_by_field_list_as_single_str = ", ".join(sort_by_field_list_of_str)

    return SqlStr("ORDER BY %s" % sort_by_field_list_as_single_str)


def order_by_element(order_by: Union[OrderBy, str]):
    if type(order_by) == str:
        field_name = order_by
        desc_str = ""
    else:
        field_name = order_by.field_name
        desc_str = " DESC" if order_by.desc else " ASC"
    return "%s%s" % (field_name, desc_str)


@dataclass
class SqlStr:
    str: str = ""
    list_of_arguments: tuple = ()

    def add(self, sql_str: "SqlStr"):
        self.str = self.str + " " + sql_str.str
        self.list_of_arguments = self.list_of_arguments + sql_str.list_of_arguments

    def prefix_string(self, prefix: str):
        self.str = "%s %s" % (prefix, self.str)


class NonExistentTable(Exception):
    pass


class DuplicateRecords(Exception):
    pass


class NoMatchingDataFound(Exception):
    pass
