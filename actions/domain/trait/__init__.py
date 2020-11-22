from enum import Enum

from actions.domain.trait.open_close import OpenClose, OpenCloseCommands

__all__ = ["TraitType", "get_class_by_trait", "get_trait_by_command", ]


class TraitType(Enum):
    OpenClose = "action.devices.traits.OpenClose"


def get_class_by_trait(trait):
    return _TRAIT_TO_CLASS[trait]


def get_trait_by_command(command):
    return _COMMAND_TO_TRAIT[command]


_TRAIT_TO_CLASS = {
    TraitType.OpenClose: OpenClose,
}

_COMMAND_TO_TRAIT = {
    OpenCloseCommands.OpenClose.value: TraitType.OpenClose,
    OpenCloseCommands.OpenCloseRelative.value: TraitType.OpenClose,
}
