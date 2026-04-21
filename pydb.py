from db_connection import DbConnectionSql3
from from_list_of_filters_to_sql import ListOfFilters, no_filters
from base_filter import Filter
from misc_components import *
from sql_changes import (
    create_table_creation_sql,
    create_index_creation_sql,
    create_insertion_sql,
    create_update_sql,
    create_sql_delete,
)
from sql_reading import (
    all_fields,
    create_select_sql,
    create_sql_get_first_field_only_in_raw_form,
    create_distinct_select_sql,
    create_minimum_value_sql,
    create_maximum_value_sql,
)
from table import Table
from translate import (
    dict_with_allowed_types_from_object,
    from_allowed_type_back_to_field,
    from_list_of_dicts_with_original_type_to_list_of_objects,
    from_ordered_list_of_allowed_types_to_list_of_dicts_of_original_type,
    from_dict_to_dict_of_allowed_types,
)
from translators import Translators


class PyDb(object):
    def __init__(
        self, db_connection: DbConnectionSql3, table: Table, translators: Translators
    ):
        self._db_connection = db_connection
        self._table = table
        self._translators = translators

    ## Table management
    def create_table(self):
        if not self.table_does_not_exist():
            print("Table already exists")
            return

        table_creation_sql = create_table_creation_sql(self.table)
        index_creation_sql = create_index_creation_sql(self.table)
        try:
            self.execute_sql_write(table_creation_sql)
            self.execute_sql_write(index_creation_sql)
            self.sql_commit()
        except Exception as e1:
            raise Exception(
                "Error %s creating %s table" % (str(e1), self.table.table_name)
            )
        finally:
            self.close()

    def table_does_not_exist(self) -> bool:
        return self.db_connection.table_does_not_exist(self.table.table_name)

    def drop_table(self, drop_non_empty_table: bool = False):
        if not self.is_table_empty():
            if drop_non_empty_table:
                pass
            else:
                raise Exception("Can't drop non empty table - delete data first")

        self.db_connection.drop_table(self.table.table_name, are_you_sure_bool=True)

    def is_table_empty(self):
        records = self.get_count_of_matching_records()
        return records == 0

    ## Changes
    def add_item(self, new_object):
        ## DOES NOT CHECK FOR UNIQUENESS
        self.write_list_of_objects([new_object])

    def write_list_of_objects(self, list_of_objects):
        try:
            if self.table_does_not_exist():
                self.create_table()

            for some_object in list_of_objects:
                self.write_element_in_list_without_checks_or_commit(some_object)

            self.sql_commit()

        except Exception as e1:
            raise Exception(
                "error %s when writing %s table" % (str(e1), self.table.table_name)
            )
        finally:
            self.close()

    def write_element_in_list_without_checks_or_commit(self, some_object):
        dict_with_allowed_types = dict_with_allowed_types_from_object(
            some_object=some_object, table=self.table, translators=self.translators
        )
        insert_sql = create_insertion_sql(dict_with_allowed_types, table=self.table)
        self.execute_sql_write(insert_sql)

    def update_item(
        self,
        update_dict_with_original_types: dict,
        list_of_filters: Union[Filter, List[Filter], ListOfFilters],
    ):
        ## DOES NOT CHECK FOR UNIQUENESS
        try:
            if self.table_does_not_exist():
                raise NonExistentTable("Can't update if table does not exist")

            dict_with_allowed_types_updated_fields_only = (
                from_dict_to_dict_of_allowed_types(
                    dict_with_original_types=update_dict_with_original_types,
                    table=self.table,
                )
            )
            update_sql = create_update_sql(
                dict_with_allowed_types_updated_fields_only=dict_with_allowed_types_updated_fields_only,
                list_of_filters=list_of_filters,
                table=self.table,
            )
            self.execute_sql_write(update_sql)
            self.sql_commit()
        except Exception as e1:
            raise Exception(
                "error %s when updating %s table with %s"
                % (str(e1), self.table.table_name, str(update_dict_with_original_types))
            )
        finally:
            self.close()

    def delete_items(self, list_of_filters: Union[Filter, List[Filter], ListOfFilters]):
        try:
            if self.table_does_not_exist():
                raise NonExistentTable("Can't delete if table does not exist")

            delete_sql = create_sql_delete(
                table=self.table, list_of_filters=list_of_filters
            )
            self.execute_sql_write(delete_sql)
            self.sql_commit()
        except Exception as e1:
            raise Exception(
                "error %s when deleting from %s table with %s"
                % (str(e1), self.table.table_name, str(list_of_filters))
            )
        finally:
            self.close()

    ## selection
    def max_or_min_of_selected_field(
        self,
        field_name: str,
        list_of_filters: Union[Filter, List[Filter], ListOfFilters] = no_filters,
        get_minimum: bool = False,
    ):
        if get_minimum:
            select_sql = create_minimum_value_sql(
                field_name=field_name, table=self.table, list_of_filters=list_of_filters
            )

        else:
            select_sql = create_maximum_value_sql(
                field_name=field_name, table=self.table, list_of_filters=list_of_filters
            )

        try:
            raw_list = self.execute_sql_read(select_sql)
        except Exception as e1:
            raise Exception(
                "Error %s reading table %s " % (str(e1), self.table.table_name)
            )
        finally:
            self.close()

        if len(raw_list) == 0:
            raise NoMatchingDataFound(
                "Can't find min or max, no records match filter %s"
                % str(list_of_filters)
            )

        original_type = self.table.dict_of_field_types.get(field_name)
        value = raw_list[0][0]
        value_in_original_type = from_allowed_type_back_to_field(
            value=value, original_type=original_type
        )

        return value_in_original_type

    def read_distinct_list_of_selected_field_values(
        self,
        field_name: str,
        list_of_filters: Union[Filter, List[Filter], ListOfFilters] = no_filters,
    ):
        try:
            select_sql = create_distinct_select_sql(
                table=self.table, field_name=field_name, list_of_filters=list_of_filters
            )
            raw_list = self.execute_sql_read(select_sql)
        except Exception as e1:
            raise Exception(
                "Error %s reading table %s " % (str(e1), self.table.table_name)
            )
        finally:
            self.close()

        original_type = self.table.dict_of_field_types.get(field_name)
        list_of_values = [
            from_allowed_type_back_to_field(
                value=raw_item[0], original_type=original_type
            )
            for raw_item in raw_list
        ]

        return list_of_values

    def get_unique_matching_object(
        self, list_of_filters: Union[Filter, List[Filter], ListOfFilters]
    ):
        list_of_objects = self.read_list_of_objects(list_of_filters)
        if len(list_of_objects) == 0:
            raise NoMatchingDataFound
        elif len(list_of_objects) > 1:
            raise DuplicateRecords
        else:
            return list_of_objects[0]

    def read_list_of_objects(
        self,
        list_of_filters: Union[Filter, List[Filter], ListOfFilters] = no_filters,
        sort_by_field_list: Union[str, List[Union[OrderBy, str]]] = no_ordering,
    ):
        list_of_dicts_with_original_type = self.read_list_of_dicts(
            list_of_field_names=all_fields,
            list_of_filters=list_of_filters,
            sort_by_field_list=sort_by_field_list,
        )

        return from_list_of_dicts_with_original_type_to_list_of_objects(
            list_of_dicts_with_original_type=list_of_dicts_with_original_type,
            translators=self.translators,
        )

    def read_list_of_dicts(
        self,
        list_of_field_names: List[str] = all_fields,
        list_of_filters: Union[Filter, List[Filter], ListOfFilters] = no_filters,
        sort_by_field_list: Union[str, List[Union[OrderBy, str]]] = no_ordering,
    ) -> List[dict]:
        if list_of_field_names is all_fields:
            list_of_field_names = self.table.list_of_field_names
        try:
            select_sql = create_select_sql(
                table=self.table,
                list_of_field_names=list_of_field_names,
                list_of_filters=list_of_filters,
                sort_by_field_list=sort_by_field_list,
            )
            raw_list = self.execute_sql_read(select_sql)
        except Exception as e1:
            raise Exception(
                "Error %s reading table %s " % (str(e1), self.table.table_name)
            )
        finally:
            self.close()

        list_of_dicts_with_original_type = (
            from_ordered_list_of_allowed_types_to_list_of_dicts_of_original_type(
                raw_list=raw_list,
                list_of_field_names=list_of_field_names,
                table=self.table,
            )
        )
        return list_of_dicts_with_original_type

    def does_unique_matching_item_exist(
        self, list_of_filters: Union[Filter, List[Filter], ListOfFilters] = no_filters
    ):
        records_matching = self.get_count_of_matching_records(list_of_filters)

        if records_matching == 0:
            return False
        elif records_matching == 1:
            return True
        else:
            raise DuplicateRecords("more than one matching %s found" % list_of_filters)

    def does_matching_item_exist(
        self, list_of_filters: Union[Filter, List[Filter], ListOfFilters] = no_filters
    ):
        records_matching = self.get_count_of_matching_records(list_of_filters)

        if records_matching == 0:
            return False
        else:
            return True

    def get_count_of_matching_records(
        self, list_of_filters: Union[Filter, List[Filter], ListOfFilters] = no_filters
    ):
        try:
            select_sql = create_sql_get_first_field_only_in_raw_form(
                table=self.table, list_of_filters=list_of_filters
            )
            raw_list = self.execute_sql_read(select_sql)
        except Exception as e1:
            raise Exception(
                "Error %s reading table %s " % (str(e1), self.table.table_name)
            )
        finally:
            self.close()

        return len(raw_list)

    def close(self):
        self.db_connection.close()

    def execute_sql_read(self, sql: SqlStr) -> List[List]:
        raw_list = self.db_connection.execute_sql_read(sql)

        return raw_list

    def execute_sql_write(self, sql: SqlStr):
        self.db_connection.execute_sql_write(sql)

    def sql_commit(self):
        self.db_connection.sql_commit()

    @property
    def table(self):
        return self._table

    @property
    def db_connection(self):
        return self._db_connection

    @property
    def translators(self):
        return self._translators
