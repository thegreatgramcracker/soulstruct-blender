from __future__ import annotations

__all__ = [
    "ANY_NVM_NAME_RE",
    "STANDARD_NVM_STEM_RE",
    "NVMBND_NAME_RE",
    "NAVMESH_FLAG_COLORS",
    "NAVMESH_MULTIPLE_FLAG_COLOR",
    "set_face_material",
    "get_navmesh_material",
]

import re

import bpy

from soulstruct.base.events.enums import NavmeshFlag

from io_soulstruct.utilities.materials import hsv_color, create_basic_material

ANY_NVM_NAME_RE = re.compile(r"^(?P<stem>.*)\.nvm(?P<dcx>\.dcx)?$")
STANDARD_NVM_STEM_RE = re.compile(r"^n(\d{4})B(?P<B>\d)A(?P<A>\d{2})$")  # no extensions
NVMBND_NAME_RE = re.compile(r"^.*?\.nvmbnd(\.dcx)?$")


# In descending priority order. All flags can be inspected in custom properties.
NAVMESH_FLAG_COLORS = {
    "Disable": hsv_color(0.0, 0.0, 0.1),  # DARK GREY
    "Degenerate": hsv_color(0.0, 0.0, 0.1),  # DARK GREY
    "Obstacle": hsv_color(0.064, 0.9, 0.2),  # DARK ORANGE
    "BlockExit": hsv_color(0.3, 0.9, 1.0),  # LIGHT GREEN
    "Hole": hsv_color(0.066, 0.9, 0.5),  # ORANGE
    "Ladder": hsv_color(0.15, 0.9, 0.5),  # YELLOW
    "ClosedDoor": hsv_color(0.66, 0.9, 0.25),  # DARK BLUE
    "Exit": hsv_color(0.33, 0.9, 0.15),  # DARK GREEN
    "Door": hsv_color(0.66, 0.9, 0.75),  # LIGHT BLUE
    "InsideWall": hsv_color(0.4, 0.9, 0.3),  # TURQUOISE
    "Edge": hsv_color(0.066, 0.9, 0.5),  # ORANGE
    "FloorBeneathWall": hsv_color(0.0, 0.8, 0.8),  # LIGHT RED
    "LandingPoint": hsv_color(0.4, 0.9, 0.7),  # LIGHT TURQUOISE
    "LargeSpace": hsv_color(0.7, 0.9, 0.7),  # PURPLE
    "Event": hsv_color(0.5, 0.9, 0.5),  # CYAN
    "Wall": hsv_color(0.0, 0.8, 0.1),  # DARK RED
    "Default": hsv_color(0.8, 0.9, 0.5),  # MAGENTA
}
NAVMESH_MULTIPLE_FLAG_COLOR = hsv_color(0.0, 0.0, 1.0)  # WHITE
NAVMESH_UNKNOWN_FLAG_COLOR = hsv_color(0.0, 0.0, 0.25)  # GREY


def set_face_material(bl_mesh, bl_face, face_flags: int):
    """Set face materials according to their `NVMTriangle` flags.

    Searches for existing materials on the mesh with names like "Navmesh Flag <flag_name>", and creates them with
    simple diffuse colors if they don't exist in the Blender session yet.

    NOTE: `bl_face` can be from a `Mesh` or `BMesh`. Both have `material_index`.
    """

    # Color face according to its single `flag` if present.
    try:
        flag = NavmeshFlag(face_flags)
        material_name = f"Navmesh Flag {flag.name}"
    except ValueError:  # multiple flags
        flag = None
        material_name = "Navmesh Flag <Multiple>"

    material_index = bl_mesh.materials.find(material_name)
    if material_index >= 0:
        bl_face.material_index = material_index
        return bl_mesh.materials[material_name]

    bl_material = get_navmesh_material(flag)

    # Add material to this mesh and this face.
    bl_face.material_index = len(bl_mesh.materials)
    bl_mesh.materials.append(bl_material)
    return bl_material


def get_navmesh_material(flag: int | NavmeshFlag) -> bpy.types.Material:
    """Try to get existing material for navmesh `flag` from Blender, or create it."""

    try:
        navmesh_flag = NavmeshFlag(flag)
        material_name = f"Navmesh Flag {navmesh_flag.name}"
    except ValueError:  # multiple flags
        navmesh_flag = None
        material_name = "Navmesh Flag <Multiple>"

    try:
        bl_material = bpy.data.materials[material_name]
    except KeyError:
        # Create new material with color from dictionary.
        if navmesh_flag is None:
            color = NAVMESH_MULTIPLE_FLAG_COLOR
        else:
            try:
                color = NAVMESH_FLAG_COLORS[navmesh_flag.name]
            except (ValueError, KeyError):
                # Unspecified flag color.
                color = NAVMESH_UNKNOWN_FLAG_COLOR
        bl_material = create_basic_material(material_name, color, wireframe_pixel_width=2)

        # Set viewport display diffuse color.
        try:
            bl_material.diffuse_color = bl_material.node_tree.nodes["Diffuse BSDF"].inputs["Color"].default_value
        except (AttributeError, KeyError):
            pass  # ignore

    return bl_material
