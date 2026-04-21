from dataclasses import dataclass
import datetime
from enum import Enum
from typing import List

from misc_components import OrderBy
from filters import *

from pydb import PyDb
from misc_components import DuplicateRecords, NoMatchingDataFound
from db_connection import DbConnectionSql3
from table import (
    create_table_for_conforming_dataclass,
    create_table_for_conforming_dict,
)
from translators import (
    translator_for_conforming_dict,
    get_translator_for_conforming_dataclass,
)

dbc = DbConnectionSql3("temp.sql")

### Example with conforming dict - only these types are allowed
Colour = Enum("colour", ["red", "green", "blue"])

car_a = dict(
    name="ford",
    price=2000.5,
    quantity=50,
    when_issued=datetime.date(2025, 1, 1),
    when_sold=datetime.datetime(2026, 1, 1, 12, 4),
    available=False,
    colour=Colour.red,
)  ## we need one example of the dict we're going to use

translators = translator_for_conforming_dict
table = create_table_for_conforming_dict(
    conforming_dict=car_a,
    table_name="cars",
    index_on_field_names=["name", "available"],
    unique_index=True,
)  ## indexing is optional

db = PyDb(db_connection=dbc, table=table, translators=translators)
db.add_item(car_a)  ## recreates table
db.read_list_of_objects()

## Example with conforming dataclass


@dataclass
class Car:
    name: str
    price: float
    quantity: int
    when_issued: datetime.date
    when_sold: datetime.datetime
    available: bool
    colour: Colour = Colour.red  ## any enum allowed


class ListOfCars(List[Car]):  ## It's entirely optional to use these
    pass


def from_list_to_list_of_cars(some_list: List[Car]):
    return ListOfCars(some_list)


translators = get_translator_for_conforming_dataclass(
    Car, list_like_creator_from_list_of_objects=from_list_to_list_of_cars
)

table = create_table_for_conforming_dataclass(
    conforming_dataclass=Car,
    table_name="cars",
    index_on_field_names=["name", "available"],
    unique_index=True,
)  ## indexing is optional

db = PyDb(db_connection=dbc, table=table, translators=translators)

### Note we can create custom translators as well for any kind of object, as long as we can create a dict with conforming types

## Let's do stuff

try:
    db.drop_table(drop_non_empty_table=True)
except:
    print("Table did not exist no need to drop")

car_a = Car(
    "ford",
    2000.5,
    50,
    when_issued=datetime.date(2025, 1, 1),
    when_sold=datetime.datetime(2026, 1, 1, 12, 4),
    available=False,
)
car_b = Car(
    "ford",
    2100.5,
    50,
    when_issued=datetime.date(2024, 1, 1),
    when_sold=datetime.datetime(2025, 1, 1, 1, 12),
    available=False,
)
car_c = Car(
    "ford",
    2200.54,
    50,
    when_issued=datetime.date(2025, 1, 1),
    when_sold=datetime.datetime(2026, 1, 1, 14, 5),
    available=True,
    colour=Colour.green,
)
car_d = Car(
    "mustang",
    200,
    10,
    when_issued=datetime.date(2023, 1, 1),
    when_sold=datetime.datetime(2022, 1, 1, 7, 30),
    available=True,
    colour=Colour.blue,
)

car_e = Car(
    "audi",
    230.56,
    10,
    when_issued=datetime.date(2023, 1, 1),
    when_sold=datetime.datetime(2022, 1, 1, 12, 4),
    available=True,
    colour=Colour.green,
)
car_f = Car(
    "vw",
    2840.56,
    150,
    when_issued=datetime.date(2000, 1, 1),
    when_sold=datetime.datetime(2012, 1, 1, 19, 34),
    available=False,
)


db.add_item(car_a)  ## recreates table
try:
    db.add_item(car_a)  ## fails not unique
except:
    print("expected to fail")

db.add_item(car_c)  ## works
db.write_list_of_objects(ListOfCars([car_d, car_e, car_f]))  ## can actually be any list
db.get_count_of_matching_records()  ## 5

db.read_list_of_objects()  ## get everything
db.read_list_of_objects(sort_by_field_list="name")  ## defaults to ascending
db.read_list_of_objects(sort_by_field_list=["name"])  ## also fine
db.read_list_of_objects(
    sort_by_field_list=[OrderBy("name", desc=False)]
)  ## not required as defaults to ascending, but hey
db.read_list_of_objects(
    sort_by_field_list=[OrderBy("name", desc=True), "price"]
)  ## multiple items are fine, don't need to wrap ascending just put field name

## filters, see filters.py for more
db.read_list_of_objects(list_of_filters=is_equal("name", "ford"))
db.read_list_of_objects(
    list_of_filters=[is_equal("name", "ford"), is_equal("available", True)]
)  ## can chain in a list
db.read_list_of_objects(
    list_of_filters=is_equal(dict(name="ford", available=True))
)  ## can chain examples of the same filter in a dict
db.read_list_of_objects(
    list_of_filters=[is_equal("name", "ford"), AND, is_greater_than("price", 2200)]
)  # AND is redundant here since they are inserted automatically, can include for clarity
db.read_list_of_objects(
    list_of_filters=[is_equal("name", "ford"), OR, is_equal("name", "vw")]
)  ## .. but OR is not

# filter and sort
db.read_list_of_objects(
    list_of_filters=[is_in("name", ["ford", "vw"])], sort_by_field_list="name"
)

## filters can also be used here
db.does_matching_item_exist(
    list_of_filters=[is_greater_than("when_issued", datetime.date(2027, 1, 1))]
)

## and here if we don't want a proper list of objects, just one or more selected fields. These values will be returned in one of the allowed types only
db.read_list_of_dicts(
    list_of_field_names=["name", "quantity", "available", "colour"],
    sort_by_field_list="name",
)

try:
    db.does_unique_matching_item_exist([is_equal("name", "ford")])
except DuplicateRecords:
    print("expected to fail")

db.does_unique_matching_item_exist([is_equal("name", "vw")])

try:
    db.get_unique_matching_object([is_equal("name", "ford")])
except DuplicateRecords:
    print("expected to fail")

try:
    db.get_unique_matching_object([is_equal("name", "car mc car face")])
except NoMatchingDataFound:
    print("expected to fail")

db.get_unique_matching_object([is_equal("name", "vw")])

db.get_count_of_matching_records([is_equal("available", True)])

db.max_or_min_of_selected_field("price", get_minimum=True)

db.read_distinct_list_of_selected_field_values(
    "name", list_of_filters=is_equal("available", True)
)  ## auto sorts

db.delete_items(is_equal("name", "ford"))
db.read_distinct_list_of_selected_field_values("name")

db.update_item(
    update_dict_with_original_types=dict(price=3000),
    list_of_filters=is_equal("name", "vw"),
)
db.drop_table(drop_non_empty_table=True)
