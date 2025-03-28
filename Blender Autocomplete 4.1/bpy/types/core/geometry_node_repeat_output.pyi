import typing
import collections.abc
import mathutils
from .repeat_item import RepeatItem
from .struct import Struct
from .bpy_struct import bpy_struct
from .node_internal_socket_template import NodeInternalSocketTemplate
from .node import Node
from .node_geometry_repeat_output_items import NodeGeometryRepeatOutputItems
from .geometry_node import GeometryNode
from .node_internal import NodeInternal

GenericType1 = typing.TypeVar("GenericType1")
GenericType2 = typing.TypeVar("GenericType2")


class GeometryNodeRepeatOutput(GeometryNode, NodeInternal, Node, bpy_struct):
    active_index: int | None
    """ Index of the active item

    :type: int | None
    """

    active_item: RepeatItem | None
    """ Index of the active item

    :type: RepeatItem | None
    """

    inspection_index: int
    """ Iteration index that is used by inspection features like the viewer node or socket inspection

    :type: int
    """

    repeat_items: NodeGeometryRepeatOutputItems
    """ 

    :type: NodeGeometryRepeatOutputItems
    """

    @classmethod
    def is_registered_node_type(cls) -> bool:
        """True if a registered node type

        :return: Result
        :rtype: bool
        """
        ...

    @classmethod
    def input_template(cls, index: int | None) -> NodeInternalSocketTemplate:
        """Input socket template

        :param index: Index
        :type index: int | None
        :return: result
        :rtype: NodeInternalSocketTemplate
        """
        ...

    @classmethod
    def output_template(cls, index: int | None) -> NodeInternalSocketTemplate:
        """Output socket template

        :param index: Index
        :type index: int | None
        :return: result
        :rtype: NodeInternalSocketTemplate
        """
        ...

    @classmethod
    def bl_rna_get_subclass(cls, id: str | None, default=None) -> Struct:
        """

        :param id: The RNA type identifier.
        :type id: str | None
        :param default:
        :return: The RNA type or default when not found.
        :rtype: Struct
        """
        ...

    @classmethod
    def bl_rna_get_subclass_py(cls, id: str | None, default=None) -> typing.Any:
        """

        :param id: The RNA type identifier.
        :type id: str | None
        :param default:
        :return: The class or default when not found.
        :rtype: typing.Any
        """
        ...
