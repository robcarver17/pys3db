from typing import List, Union

from base_filter import Filter
from filters import AND
from misc_components import SqlStr
from table import Table


class ListOfFilters(List[Filter]):
    def get_sql(self):
        sql_all_fitters = SqlStr("")
        for filter in self:
            sql_all_fitters.add(filter.get_sql())

        return sql_all_fitters


no_filters = ListOfFilters([])


def get_sql_from_raw_list_of_filters(
    list_of_filters: Union[Filter, List[Filter], ListOfFilters], table: Table
):
    if type(list_of_filters) is ListOfFilters:
        pass
    elif type(list_of_filters) is list:
        list_of_filters = ListOfFilters(list_of_filters)
    elif issubclass(type(list_of_filters), Filter):
        ## assume filter
        list_of_filters = ListOfFilters([list_of_filters])

    if len(list_of_filters) == 0:
        return SqlStr("")

    processed_list_of_filters = get_list_of_filters_from_raw_list(
        list_of_filters, table=table
    )
    sql_for_all_filters = processed_list_of_filters.get_sql()
    sql_for_all_filters.prefix_string("WHERE ")

    return sql_for_all_filters


def get_list_of_filters_from_raw_list(list_of_filters: ListOfFilters, table: Table):
    expanded_list_of_filters = get_expanded_list_of_filters_from_raw_list(
        list_of_filters
    )
    filters_with_values_translated = replace_values_with_translated_values(
        expanded_list_of_filters, table=table
    )
    filters_with_ands_included = add_implicit_ands_to_list_of_filters(
        filters_with_values_translated
    )

    return filters_with_ands_included


def get_expanded_list_of_filters_from_raw_list(list_of_filters: ListOfFilters):
    expanded_list_of_filters = []
    for filter in list_of_filters:
        expanded_list_of_filters += filter.expand_to_list()

    return ListOfFilters(expanded_list_of_filters)


def add_implicit_ands_to_list_of_filters(expanded_list_of_filters: ListOfFilters):
    filters_with_ands_included = []
    for idx, filter in enumerate(expanded_list_of_filters):
        filters_with_ands_included.append(filter)
        if filter.is_action_filter:
            continue
        final_filter = idx == len(expanded_list_of_filters) - 1
        if final_filter:
            break
        next_filter = expanded_list_of_filters[idx + 1]
        if not next_filter.is_action_filter:
            filters_with_ands_included.append(AND)

    return ListOfFilters(filters_with_ands_included)


def replace_values_with_translated_values(
    filters_with_ands_included: ListOfFilters, table: Table
):
    [
        filter.replace_values_with_allowed_types(table=table)
        for filter in filters_with_ands_included
    ]
    return filters_with_ands_included
