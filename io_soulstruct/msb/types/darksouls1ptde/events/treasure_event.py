from __future__ import annotations

__all__ = [
    "BlenderMSBTreasureEvent",
]

import bpy

from soulstruct.darksouls1ptde.maps.msb import MSBTreasureEvent

from io_soulstruct.msb.properties import BlenderMSBEventSubtype, MSBTreasureEventProps
from io_soulstruct.msb.types.adapters import *
from io_soulstruct.types import SoulstructType

from .base import BaseBlenderMSBEvent_DS1


@soulstruct_adapter
class BlenderMSBTreasureEvent(BaseBlenderMSBEvent_DS1[MSBTreasureEvent, MSBTreasureEventProps]):

    SOULSTRUCT_CLASS = MSBTreasureEvent
    MSB_ENTRY_SUBTYPE = BlenderMSBEventSubtype.Treasure
    PARENT_PROP_NAME = "treasure_part"  # invasion trigger region (with Black Eye Orb)
    __slots__ = []

    SUBTYPE_FIELDS = (
        MSBReferenceFieldAdapter("treasure_part", ref_type=SoulstructType.MSB_PART),
        FieldAdapter("item_lot_1"),
        FieldAdapter("item_lot_2"),
        FieldAdapter("item_lot_3"),
        FieldAdapter("item_lot_4"),
        FieldAdapter("item_lot_5"),
        FieldAdapter("is_in_chest"),
        FieldAdapter("is_hidden"),
    )

    treasure_part: bpy.types.MeshObject | None
    item_lot_1: int
    item_lot_2: int
    item_lot_3: int
    item_lot_4: int
    item_lot_5: int
    is_in_chest: bool
    is_hidden: bool
