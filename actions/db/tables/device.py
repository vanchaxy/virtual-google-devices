from copy import deepcopy

from sqlalchemy import ARRAY, JSON, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from actions.db.tables import Base
from actions.domain import DeviceType
from actions.domain.trait import (TraitType, get_class_by_trait,
                                  get_trait_by_command)


class Device(Base):
    __tablename__ = "device"

    id = Column(Integer, primary_key=True)
    type = Column(Enum(DeviceType))
    traits = Column(ARRAY(Enum(TraitType)))
    name = Column(String(255))
    nicknames = Column(ARRAY(String(255)))
    attributes = Column(MutableDict.as_mutable(JSONB))
    states = Column(MutableDict.as_mutable(JSONB))

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", foreign_keys=[user_id])

    def serialize_info(self):
        serialized = {
            "id": self.id,
            "type": self.type.value,
            "traits": [t.value for t in self.traits],
            "name": {
                "name": self.name,
                "nicknames": self.nicknames,
            },
            "willReportState": False,
            "attributes": {}
        }
        for attribute in self.attributes.values():
            serialized["attributes"].update(attribute)
        return serialized

    def serialize_status(self):
        serialized = {
            "on": True,
            "online": True,
            "status": "SUCCESS",
        }
        for state in self.states.values():
            serialized.update(state)
        return serialized

    def serialize(self):
        serialized = self.serialize_info()
        serialized["status"] = self.serialize_status()
        return serialized

    def execute_command(self, command, params):
        trait_enum = get_trait_by_command(command)
        if trait_enum not in self.traits:
            raise

        trait_class = get_class_by_trait(trait_enum)
        attributes = self.attributes.get(trait_enum.value, {})
        states = self.states.get(trait_enum.value, {})

        trait = trait_class(attributes, states)

        self.states[trait_enum.value] = trait.process_command(command, params)
