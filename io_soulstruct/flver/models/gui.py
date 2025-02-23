from __future__ import annotations

__all__ = [
    "FLVERPropsPanel",
    "FLVERDummyPropsPanel",
    "FLVERImportPanel",
    "FLVERExportPanel",
]

import bpy
from io_soulstruct.general.gui import map_stem_box
from soulstruct.base.models import FLVERVersion
from .import_operators import *
from .export_operators import *
from .types import BlenderFLVER, BlenderFLVERDummy


class FLVERPropsPanel(bpy.types.Panel):
    """Draw a Panel in the Object properties window exposing the appropriate FLVER fields for active object."""
    bl_label = "FLVER Properties"
    bl_idname = "OBJECT_PT_flver"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context) -> bool:
        if not context.active_object:
            return False
        return BlenderFLVER.is_obj_type(context.active_object)

    def draw(self, context):
        bl_flver = BlenderFLVER.from_armature_or_mesh(context.active_object)
        prop_names = bl_flver.type_properties.__annotations__
        if bl_flver.version == "DEFAULT":
            pass  # show all properties
        elif FLVERVersion[bl_flver.version].is_flver0():
            prop_names = [prop for prop in prop_names if not prop.startswith("f2_")]
        else:
            prop_names = [prop for prop in prop_names if not prop.startswith("f0_")]
        for prop in prop_names:
            self.layout.prop(bl_flver.type_properties, prop)


class FLVERDummyPropsPanel(bpy.types.Panel):
    """Draw a Panel in the Object properties window exposing the appropriate FLVER Dummy fields for active object."""
    bl_label = "FLVER Dummy Properties"
    bl_idname = "OBJECT_PT_flver_dummy"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context) -> bool:
        return BlenderFLVERDummy.is_obj_type(context.active_object)

    def draw(self, context):
        bl_dummy = BlenderFLVERDummy.from_active_object(context)
        props = bl_dummy.type_properties
        for prop in props.__annotations__:
            self.layout.prop(props, prop)


class FLVERImportPanel(bpy.types.Panel):
    """Panel for Soulstruct FLVER operators."""
    bl_label = "FLVER Import"
    bl_idname = "SCENE_PT_flver_import"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FLVER"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.soulstruct_settings

        map_stem_box(layout, settings)

        # NOTE: FLVER import settings are exposed within each individual operator (all use browser pop-ups).

        layout.label(text="Import from Game/Project:")
        layout.operator(ImportMapPieceFLVER.bl_idname)
        layout.operator(ImportCharacterFLVER.bl_idname)
        if settings.is_game("ELDEN_RING"):
            layout.operator(ImportAssetFLVER.bl_idname)
        else:
            layout.operator(ImportObjectFLVER.bl_idname)
        layout.operator(ImportEquipmentFLVER.bl_idname)

        layout.label(text="Generic Import:")
        layout.operator(ImportFLVER.bl_idname, text="Import Any FLVER")


class FLVERExportPanel(bpy.types.Panel):
    """Panel for Soulstruct FLVER operators."""
    bl_label = "FLVER Export"
    bl_idname = "SCENE_PT_flver_export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FLVER"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        settings = context.scene.soulstruct_settings

        header, panel = layout.panel("FLVER Export Settings", default_closed=True)
        header.label(text="FLVER Export Settings")
        if panel:
            export_settings = context.scene.flver_export_settings
            panel.prop(settings, "detect_map_from_collection")
            panel.prop(export_settings, "export_textures")
            panel.prop(export_settings, "allow_missing_textures")
            panel.prop(export_settings, "allow_unknown_texture_types")
            panel.prop(export_settings, "create_lod_face_sets")
            panel.prop(export_settings, "base_edit_bone_length")
            panel.prop(export_settings, "normal_tangent_dot_max")

        if not context.selected_objects:
            layout.label(text="Select some FLVER models.")
            layout.label(text="MSB Parts cannot be selected.")
            return

        for obj in context.selected_objects:
            if not BlenderFLVER.is_obj_type(obj):
                layout.label(text="Select some FLVER models.")
                layout.label(text="MSB Parts cannot be selected.")
                return

        map_stem_box(layout, settings)

        if settings.can_auto_export:
            map_stem = settings.get_active_object_detected_map(context)
            if not map_stem:
                layout.label(text="To Map: <NO MAP>")
            else:
                map_stem = settings.get_oldest_map_stem_version(map_stem)
                layout.label(text=f"To Map: {map_stem}")
            layout.operator(ExportMapPieceFLVERs.bl_idname)
            layout.label(text="Game Models:")
            layout.operator(ExportCharacterFLVER.bl_idname)
            layout.operator(ExportObjectFLVER.bl_idname)
            layout.operator(ExportEquipmentFLVER.bl_idname)
        else:
            layout.label(text="No export directory set.")

        layout.label(text="Generic Export:")
        layout.operator(ExportLooseFLVER.bl_idname, text="Export Loose FLVER")
        layout.operator(ExportFLVERIntoBinder.bl_idname)
