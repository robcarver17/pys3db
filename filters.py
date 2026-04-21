from base_filter import (
    Filter,
    _abc_is_between_or_not_between,
    _abc_is_in_or_not_in,
    _abc_with_lower_bound,
    _abc_with_upper_bound,
    And,
    Or,
)
from misc_components import SqlStr

### Here is a list of possible filters
### All can be used as one instance or as a dict


class is_equal(Filter):
    """
    is_equal('name','bob')
    is_equal(dict(name='bob', age=23))
    """

    @property
    def equal_to(self):
        assert self.is_expanded
        return self.values_as_list[0]

    def get_sql(self):
        return SqlStr("%s=?" % self.field_name, (self.equal_to,))


class is_not_equal(Filter):
    """
    is_not_equal('name','sue')
    is_not_equal(dict(name='sue', age=25))
    """

    @property
    def not_equal_to(self):
        assert self.is_expanded
        return self.values_as_list[0]

    def get_sql(self):
        return SqlStr("%s<>?" % self.field_name, (self.not_equal_to,))


class is_between(_abc_is_between_or_not_between):
    """
    is_between('age',23, 30)
    is_between(dict(age=[25,30], weight=[60,80]))
    """

    def get_sql(self):
        return SqlStr(
            "%s BETWEEN ? AND ?" % self.field_name, (self.lower_bound, self.upper_bound)
        )


class is_not_between(_abc_is_between_or_not_between):
    """
    is_not_between('age',23, 30)
    is_not_between(dict(age=[25,30], weight=[60,80]))
    """

    def get_sql(self):
        return SqlStr(
            "%s NOT BETWEEN ? AND ?" % self.field_name,
            (self.lower_bound, self.upper_bound),
        )


class is_in(_abc_is_in_or_not_in):
    """
    is_in('name',['bob','sue'])
    is_in(dict(name=['bob','sue'], age=[21,22])
    """

    def get_sql(self):
        values_as_list = self.list_of_values_to_check  ## is itself a list
        list_of_question_marks = ["?"] * len(values_as_list)
        list_of_question_marks = ",".join(list_of_question_marks)

        return SqlStr(
            "%s IN (%s)" % (self.field_name, list_of_question_marks),
            tuple(values_as_list),
        )


class is_not_in(_abc_is_in_or_not_in):
    """
    is_not_in('name',['bob','sue'])
    is_not_in(dict(name=['bob','sue'], age=[21,22])
    """

    def get_sql(self):
        values_as_list = self.list_of_values_to_check  ## is itself a list
        list_of_question_marks = ["?"] * len(values_as_list)
        list_of_question_marks = ",".join(list_of_question_marks)

        return SqlStr(
            "%s NOT IN (%s)" % (self.field_name, list_of_question_marks),
            tuple(values_as_list),
        )


class is_greater_than(_abc_with_lower_bound):
    """
    is_greater_than('age',18)
    is_greater_than(dict(age=18, weight=50))
    """

    def get_sql(self):
        return SqlStr("%s>?" % self.field_name, (self.lower_bound,))


class is_not_greater_than(_abc_with_lower_bound):
    """
    is_not_greater_than('age',18)
    is_not_greater_than(dict(age=18, weight=50))
    """

    def get_sql(self):
        return SqlStr("NOT %s>?" % self.field_name, (self.lower_bound,))


class is_less_than(_abc_with_upper_bound):  # dict(age=20)
    """
    is_less_than('age',60)
    is_less_than(dict(age=60, weight=80))
    """

    def get_sql(self):
        return SqlStr("%s<?" % self.field_name, (self.upper_bound,))


class is_not_less_than(_abc_with_upper_bound):
    """
    is_not_less_than('age',60)
    is_not_less_than(dict(age=60, weight=80))
    """

    def get_sql(self):
        return SqlStr("NOT %s<?" % self.field_name, (self.upper_bound,))


class is_like(Filter):
    """
    is_like('name','bob')
    is_like(dict(name='bob', colour='blue'))
    """

    @property
    def like(self):
        assert self.is_expanded
        return self.values_as_list[0]

    def get_sql(self):
        return SqlStr("%s LIKE ?" % self.field_name, (self.like,))


class is_not_like(Filter):
    """
    is_not_like('name','bob')
    is_not_like(dict(name='bob', colour='blue'))
    """

    @property
    def not_like(self):
        assert self.is_expanded
        return self.values_as_list[0]

    def get_sql(self):
        return SqlStr("%s NOT LIKE ?" % self.field_name, (self.not_like,))


### logic 'filters'
AND = And(None)
OR = Or(None)
