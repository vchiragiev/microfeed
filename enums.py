from enum import Enum


class ActionEnum(Enum):
    # Order Add
    A = 1
    # Order Modify
    M = 2
    # Order Remove
    X = 3
    # Trade Message
    T = 4


class SideEnum(Enum):
    # Sell
    S = 1
    # Buy
    B = 2


class ErrorEnum(Enum):
    # corrupted messages
    CorruptedMessage = 1
    # duplicated order ids (duplicate adds)
    DuplicateOrder = 2
    # trades with no corresponding order
    TradeWithNoOrder = 3
    # removes with no corresponding order
    RemoveWithNoOrder = 4
    # best sell order price at or below best buy order price but no trades occur
    MissingTrade = 5
    # negative, missing, or out-of-bounds prices, quantities, order ids
    InvalidValue = 6
