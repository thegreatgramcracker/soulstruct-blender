"""Import MSB Object entries."""
from __future__ import annotations

__all__ = [
    "ImportMSBObject",
    "ImportAllMSBObjects",
]

import time
import traceback
import typing as tp

import bpy

from soulstruct.containers import Binder

from io_soulstruct.exceptions import *
from io_soulstruct.utilities import *
from io_soulstruct.flver.textures.import_textures import TextureImportManager
from io_soulstruct.flver.model_import import FLVERImporter, FLVERImportSettings
from io_soulstruct.flver.utilities import get_flvers_from_binder
from .core import *

if tp.TYPE_CHECKING:
    from io_soulstruct.general import SoulstructSettings
    from io_soulstruct.type_checking import MSB_OBJECT_TYPING


def import_object_model(
    operator: LoggingOperator, context, settings: SoulstructSettings, model_name: str
) -> tuple[bpy.types.ArmatureObject | None, bpy.types.MeshObject]:
    """Import the model of the given name into a collection in the current scene."""

    flver_import_settings = context.scene.flver_import_settings  # type: FLVERImportSettings
    chrbnd_path = settings.get_import_file_path(f"obj/{model_name}.objbnd")

    operator.info(f"Importing object FLVER from: {chrbnd_path.name}")

    texture_manager = TextureImportManager(settings) if flver_import_settings.import_textures else None

    objbnd = Binder.from_path(chrbnd_path)
    binder_flvers = get_flvers_from_binder(objbnd, chrbnd_path, allow_multiple=False)
    if texture_manager:
        texture_manager.find_flver_textures(chrbnd_path, objbnd)
    flver = binder_flvers[0]

    importer = FLVERImporter(
        operator,
        context,
        settings,
        texture_import_manager=texture_manager,
        collection=get_collection("Object Models", context.scene.collection, hide_viewport=True),
    )

    try:
        return importer.import_flver(flver, name=model_name)
    except Exception as ex:
        # Delete any objects created prior to exception.
        importer.abort_import()
        traceback.print_exc()  # for inspection in Blender console
        raise FLVERImportError(f"Cannot import FLVER from OBJBND: {chrbnd_path.name}. Error: {ex}")


def get_object_model(
    operator: LoggingOperator, context, settings: SoulstructSettings, model_name: str
) -> tuple[bpy.types.ArmatureObject, bpy.types.MeshObject]:
    """Find or create actual Blender model armature/mesh data."""
    try:
        return find_flver_model("Object", model_name)
    except MissingModelError:
        t = time.perf_counter()
        armature, mesh = import_object_model(operator, context, settings, model_name)
        operator.info(f"Imported Object FLVER Model '{model_name}' in {time.perf_counter() - t:.3f} seconds.")
        return armature, mesh


class BaseImportMSBObject(BaseImportMSBPart):

    PART_TYPE_NAME = "Object"
    PART_TYPE_NAME_PLURAL = "Objects"
    MSB_LIST_NAME = "objects"

    def _create_part_instance(
        self,
        context,
        settings: SoulstructSettings,
        map_stem: str,
        part: MSB_OBJECT_TYPING,
        collection: bpy.types.Collection,
    ) -> bpy.types.Object:
        armature, mesh = get_object_model(self, context, settings, part.model.name)  # NOT map-specific
        part_armature, part_mesh = create_flver_model_instance(context, armature, mesh, part.name, collection)
        msb_entry_to_obj_transform(part, part_armature)
        part_armature["Draw Parent Name"] = part.draw_parent.name if part.draw_parent else ""
        return part_armature  # return armature to center view on

class ImportMSBObject(BaseImportMSBObject):
    """Import ALL MSB Object parts and their transforms. Will probably take a long time!"""
    bl_idname = "import_scene.msb_object_part"
    bl_label = "Import Object Part"
    bl_description = "Import FLVER model and MSB transform of selected MSB Object part"

    GAME_ENUM_NAME = "object_part"

    def execute(self, context):
        return self.import_enum_part(context)


class ImportAllMSBObjects(BaseImportMSBObject):
    """Import ALL MSB Object parts and their transforms. Will probably take a long time!"""
    bl_idname = "import_scene.all_msb_object_parts"
    bl_label = "Import All Object Parts"
    bl_description = ("Import FLVER model and MSB transform of every MSB Object part. Very slow, especially when "
                      "textures are imported (see console output for progress)")

    GAME_ENUM_NAME = None

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        return self.import_all_parts(context)
