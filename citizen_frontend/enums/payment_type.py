from enum import StrEnum


class PaymentType(StrEnum):
    NONE = "none"
    FIXED_FEE = "fixed"
    VARIABLE_FEE = "variable"
