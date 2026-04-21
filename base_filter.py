from misc_components import SqlStr
from table import Table
from translate import from_field_to_allowed_type


class Filter:
    def __init__(self, *args):
        if len(args) == 1:
            if type(args[0]) == dict:
                self._values_as_dict = args[0]
                self._values_as_list = None
                self._field_name = None
                self._action_filter = False
            else:
                raise Exception("Need to pass at least keyword and one value, or dict")
        else:
            field_name = args[0]
            values = args[1:]
            self._values_as_list = values
            self._field_name = field_name
            self._values_as_dict = None
            self._action_filter = False

    def __repr__(self):
        if self.is_not_expanded:
            return "%s %s" % (str(type(self)), self.values_as_dict)
        else:
            return "%s %s %s" % (
                str(type(self)),
                self.field_name,
                str(self.values_as_list),
            )

    def get_sql(self):
        raise NotImplemented

    def replace_values_with_allowed_types(self, table: Table):
        assert self.is_expanded
        field_name = self.field_name
        values_as_list = self.values_as_list
        allowed_type = table.dict_of_field_types[field_name]
        new_list = [
            from_field_to_allowed_type(value=value, allowed_type=allowed_type)
            for value in values_as_list
        ]
        self.replace_values_as_list(new_list)

    def expand_to_list(self):
        if self.is_not_expanded:
            return self._expand_dict_of_filters()
        else:
            return [self]

    def _expand_dict_of_filters(self):
        class_of_filter = type(self)
        return [
            class_of_filter(key, filter_value)
            for key, filter_value in self.values_as_dict.items()
        ]

    @property
    def field_name(self):
        assert self.is_expanded
        return self._field_name

    @property
    def values_as_list(self):
        return self._values_as_list

    def replace_values_as_list(self, new_values: list):
        assert self.is_expanded
        self._values_as_list = new_values

    @property
    def is_expanded(self):
        return self.values_as_dict is None

    @property
    def is_not_expanded(self):
        return self.values_as_list is None

    @property
    def values_as_dict(self) -> dict:
        return self._values_as_dict

    @property
    def is_action_filter(self):
        return self._action_filter


class _abc_is_between_or_not_between(Filter):
    def _expand_dict_of_filters(self):
        class_of_filter = type(self)
        return [
            class_of_filter(key, filter_values[0], filter_values[1])
            for key, filter_values in self.values_as_dict.items()
        ]

    @property
    def lower_bound(self):
        assert self.is_expanded
        return self.values_as_list[0]

    @property
    def upper_bound(self):
        assert self.is_expanded
        return self.values_as_list[1]


class _abc_is_in_or_not_in(Filter):
    @property
    def list_of_values_to_check(self):
        assert self.is_expanded
        return self.values_as_list[0]

    def replace_values_with_allowed_types(self, table: Table):
        field_name = self.field_name
        values_as_list = self.list_of_values_to_check  ## is itself a list
        allowed_type = table.dict_of_field_types[field_name]
        new_list = [
            from_field_to_allowed_type(value=value, allowed_type=allowed_type)
            for value in values_as_list
        ]
        self.replace_values_as_list([new_list])


class _abc_with_lower_bound(Filter):
    @property
    def lower_bound(self):
        assert self.is_expanded
        return self.values_as_list[0]


class _abc_with_upper_bound(Filter):
    @property
    def upper_bound(self):
        assert self.is_expanded
        return self.values_as_list[0]


class _abc_ActionFilter(Filter):
    def __init__(self, action):  ## ignore complier method
        self._values_as_list = [""]
        self._field_name = action
        self._values_as_dict = None
        self._action_filter = True

    def expand_to_list(self):
        return [self]

    def replace_values_with_allowed_types(self, table: Table):
        pass

    def replace_values_as_list(self, new_values: list):
        raise NotImplemented


class And(_abc_ActionFilter):
    @property
    def field_name(self):
        return "And"

    def get_sql(self):
        return SqlStr("AND")


class Or(_abc_ActionFilter):
    @property
    def field_name(self):
        return "OR"

    def get_sql(self):
        return SqlStr("OR")
