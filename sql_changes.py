from typing import Union, List

from from_list_of_filters_to_sql import ListOfFilters, get_sql_from_raw_list_of_filters
from base_filter import Filter
from misc_components import SqlStr
from table import Table
from translate import from_python_type_to_named_type


def create_table_creation_sql(table: Table):
    fields_and_types = [
        "%s %s" % (field_name, from_python_type_to_named_type(field_type))
        for field_name, field_type in zip(
            table.list_of_field_names, table.list_of_field_types
        )
    ]
    fields_and_types_as_single_str = ", ".join(fields_and_types)

    return SqlStr(
        "CREATE TABLE %s (%s)" % (table.table_name, fields_and_types_as_single_str)
    )


def create_index_creation_sql(table: Table):
    list_of_index_names = table.index_on_field_names
    if len(list_of_index_names) == 0:
        return ""
    list_of_index_names_as_single_str = ", ".join(list_of_index_names)
    unique_str = "UNIQUE " if table.unique_index else ""

    return SqlStr(
        "CREATE %s INDEX %s ON %s (%s)"
        % (
            unique_str,
            table.index_name,
            table.table_name,
            list_of_index_names_as_single_str,
        )
    )


def create_insertion_sql(dict_with_allowed_types: dict, table: Table):
    ### Need to be translated into correct type
    list_of_field_names = table.list_of_field_names
    list_of_values_as_tuple = tuple(
        [dict_with_allowed_types.get(field_name) for field_name in list_of_field_names]
    )
    field_names_as_single_str = ", ".join(list_of_field_names)
    how_many_questions = ", ".join(["?"] * len(list_of_field_names))
    insert_sql = "INSERT INTO %s ( %s) VALUES ( %s)" % (
        table.table_name,
        field_names_as_single_str,
        how_many_questions,
    )

    return SqlStr(insert_sql, list_of_values_as_tuple)


def create_update_sql(
    dict_with_allowed_types_updated_fields_only: dict,
    table: Table,
    list_of_filters: Union[Filter, List[Filter], ListOfFilters],
):
    where_clause = get_sql_from_raw_list_of_filters(
        list_of_filters=list_of_filters, table=table
    )
    update_sql = create_start_of_update(
        dict_with_allowed_types_updated_fields_only, table=table
    )
    update_sql.add(where_clause)
    return update_sql


def create_start_of_update(
    dict_with_allowed_types_updated_fields_only: dict, table: Table
):
    update_field_names = list(dict_with_allowed_types_updated_fields_only.keys())
    update_set_fields_as_str = ["SET %s=?" % key for key in update_field_names]
    update_set_fields_as_single_str = ", ".join(update_set_fields_as_str)

    update_values_as_tuple = tuple(dict_with_allowed_types_updated_fields_only.values())

    return SqlStr(
        "UPDATE %s %s" % (table.table_name, update_set_fields_as_single_str),
        update_values_as_tuple,
    )


def create_sql_delete(
    table: Table, list_of_filters: Union[Filter, List[Filter], ListOfFilters]
):
    where_clause = get_sql_from_raw_list_of_filters(
        list_of_filters=list_of_filters, table=table
    )
    initial_sql = SqlStr("DELETE FROM %s" % table.table_name)
    initial_sql.add(where_clause)
    return initial_sql
