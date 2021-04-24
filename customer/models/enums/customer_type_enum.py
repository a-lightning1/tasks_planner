from enum import Enum


class CustomerTypeEnum(Enum):
    INDIVIDUAL = "Individual"

CustomerCategoryChoices = [(category_type, category_type.value) for category_type in CustomerTypeEnum]