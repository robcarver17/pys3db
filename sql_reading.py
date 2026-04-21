from typing import List, Union


from from_list_of_filters_to_sql import (
    ListOfFilters,
    get_sql_from_raw_list_of_filters,
    no_filters,
)
from base_filter import Filter
from misc_components import no_ordering, create_order_by_sql, SqlStr, OrderBy
from table import Table


def create_sql_get_first_field_only_in_raw_form(
    table: Table,
    list_of_filters: Union[Filter, List[Filter], ListOfFilters] = no_filters,
):  ## handy for quick does this exist
    random_first_field_name = table.list_of_field_names[0]
    where_clause = get_sql_from_raw_list_of_filters(
        list_of_filters=list_of_filters, table=table
    )
    initial_sql = SqlStr(
        "SELECT %s from %s" % (random_first_field_name, table.table_name)
    )
    initial_sql.add(where_clause)
    return initial_sql


def create_distinct_select_sql(
    field_name: str,
    table: Table,
    list_of_filters: Union[Filter, List[Filter], ListOfFilters] = no_filters,
):
    where_clause = get_sql_from_raw_list_of_filters(
        list_of_filters=list_of_filters, table=table
    )
    initial_sql = SqlStr("SELECT DISTINCT %s from %s" % (field_name, table.table_name))
    initial_sql.add(where_clause)
    return initial_sql


def create_maximum_value_sql(
    field_name: str,
    table: Table,
    list_of_filters: Union[Filter, List[Filter], ListOfFilters] = no_filters,
):
    where_clause = get_sql_from_raw_list_of_filters(
        list_of_filters=list_of_filters, table=table
    )
    initial_sql = SqlStr("SELECT MAX(%s) from %s" % (field_name, table.table_name))
    initial_sql.add(where_clause)
    return initial_sql


def create_minimum_value_sql(
    field_name: str,
    table: Table,
    list_of_filters: Union[Filter, List[Filter], ListOfFilters] = no_filters,
):
    where_clause = get_sql_from_raw_list_of_filters(
        list_of_filters=list_of_filters, table=table
    )
    initial_sql = SqlStr("SELECT MIN(%s) from %s" % (field_name, table.table_name))
    initial_sql.add(where_clause)
    return initial_sql


all_fields = object()


def create_select_sql(
    table: Table,
    list_of_field_names: List[str],
    list_of_filters: Union[Filter, List[Filter], ListOfFilters] = no_filters,
    sort_by_field_list: Union[str, List[Union[OrderBy, str]]] = no_ordering,
):
    order_by = create_order_by_sql(sort_by_field_list=sort_by_field_list)
    where_clause = get_sql_from_raw_list_of_filters(
        list_of_filters=list_of_filters, table=table
    )
    select_sql = create_start_of_select(
        table=table, list_of_field_names=list_of_field_names
    )
    where_clause.add(order_by)
    select_sql.add(where_clause)
    return select_sql


def create_start_of_select(table: Table, list_of_field_names: List[str]):
    list_of_field_names_as_str = ", ".join(list_of_field_names)

    return SqlStr("SELECT %s from %s" % (list_of_field_names_as_str, table.table_name))
