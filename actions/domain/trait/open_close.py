from enum import Enum

from actions.domain.trait.base import BaseTrait


class OpenCloseCommands(Enum):
    OpenClose = "action.devices.commands.OpenClose"
    OpenCloseRelative = "action.devices.commands.OpenCloseRelative"


class OpenClose(BaseTrait):
    def open_close(self, open_percent, open_direction=None):
        if "openDirection" in self.attributes:
            if open_direction is not None:
                if open_direction not in self.attributes["openDirection"]:
                    raise
                for state in self.states["openState"]:
                    if state["openDirection"] == open_direction:
                        state["openPercent"] = open_percent
                        break
                else:
                    self.states["openState"].apppen({
                        "openDirection": open_direction,
                        "openPercent": open_percent
                    })
            else:
                for state in self.states["openState"]:
                    state["openPercent"] = open_percent
        else:
            self.states["openPercent"] = open_percent

    def open_close_relative(self, open_relative_percent, open_direction=None):
        if "openDirection" in self.attributes:
            if open_direction is not None:
                if open_direction not in self.attributes["openDirection"]:
                    raise
                for state in self.states["openState"]:
                    if state["openDirection"] == open_direction:
                        state["openPercent"] *= 1 + open_relative_percent / 100
                        if state["openPercent"] > 100:
                            state["openPercent"] = 100
                        break
            else:
                for state in self.states["openState"]:
                    state["openPercent"] *= 1 + open_relative_percent / 100
                    if state["openPercent"] > 100:
                        state["openPercent"] = 100
        else:
            self.states["openPercent"] *= 1 + open_relative_percent / 100
            if self.states["openPercent"] > 100:
                self.states["openPercent"] = 100
