from dataclasses import fields as dataclass_fields, dataclass
from typing import Callable

#### default to make lists, can be much fancier if desired


def default_list_like_creator_from_list_of_objects(some_list: list):
    return some_list


### This is the core object we need, can customise
### Translate between original objects of any kind, and dict of 'original types'
## these types must be conforming, eg: int, float, bool, str, datetime.date, datetime.datetime, or inherit from Enum


@dataclass
class Translators:
    from_object_to_dict_of_original_types: Callable
    from_dict_of_original_types_to_object: Callable
    list_like_creator_from_list_of_objects: Callable = (
        default_list_like_creator_from_list_of_objects
    )


### Simplest case is when the original object is just a dict which also conforms in types, then we need do nothing:


def default_from_object_to_dict_of_original_types_for_conforming_dict(
    conforming_dict: dict,
):
    ## a conforming dict has only the allowed types: dict, str, bool, int, float, datetime.date, datetime.datetime, Enum subclass
    return conforming_dict


def default_from_dict_of_original_types_to_conforming_dict(
    dict_of_original_types: dict,
):
    ## a conforming dict has only the allowed types: dict, str, bool, int, float, datetime.date, datetime.datetime, Enum subclass
    return dict_of_original_types


translator_for_conforming_dict = Translators(
    default_from_object_to_dict_of_original_types_for_conforming_dict,
    default_from_object_to_dict_of_original_types_for_conforming_dict,
)

## Next simplest case we provide a default for is a 'conforming' dataclass where again all the types


def from_object_to_dict_of_original_types_for_conforming_dataclass(
    conforming_dataclass_instance,
):
    type_of_class = type(conforming_dataclass_instance)
    fields_in_class = dataclass_fields(type_of_class)
    output_dict = {}
    for field in fields_in_class:
        output_dict[field.name] = getattr(conforming_dataclass_instance, field.name)

    return output_dict


class FactoryForManagingDataClasses:
    def __init__(self, conforming_dataclass):
        self.conforming_dataclass = conforming_dataclass

    def from_dict_of_original_types_to_object_for_conforming_dataclass(
        self, dict_of_original_types: dict
    ):
        return self.conforming_dataclass(**dict_of_original_types)


def from_dict_of_original_types_to_object_for_conforming_dataclass(
    conforming_dataclass_instance,
):
    type_of_class = type(conforming_dataclass_instance)
    fields_in_class = dataclass_fields(type_of_class)
    output_dict = {}
    for field in fields_in_class:
        output_dict[field.name] = getattr(conforming_dataclass_instance, field.name)

    return output_dict


def get_translator_for_conforming_dataclass(
    conforming_dataclass,
    list_like_creator_from_list_of_objects: Callable = default_list_like_creator_from_list_of_objects,
):
    factory = FactoryForManagingDataClasses(conforming_dataclass)
    from_dict_of_original_types_to_object_for_conforming_dataclass = (
        factory.from_dict_of_original_types_to_object_for_conforming_dataclass
    )
    return Translators(
        from_object_to_dict_of_original_types=from_object_to_dict_of_original_types_for_conforming_dataclass,
        from_dict_of_original_types_to_object=from_dict_of_original_types_to_object_for_conforming_dataclass,
        list_like_creator_from_list_of_objects=list_like_creator_from_list_of_objects,
    )
