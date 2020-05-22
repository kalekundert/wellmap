#!/usr/bin/env python3

from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.statemachine import StringList, string2lines
from docutils.transforms import Transform
from sphinx.transforms import DoctreeReadEvent

class HiddenSection(Directive):
    required_arguments = 1
    final_argument_whitespace = True

    def run(self):
        title = self.arguments[0]
        id = title.lower().replace(' ', '-')
        name = title.lower()

        section = nodes.section('', ids=[id], names=[name])
        section += nodes.title('', title, classes=['hidden'])
        return [section]

class MakeListFromSections(Directive):
    """
    Replace all sections found at the same level as this directive with an 
    ordered list.
    """

    def run(self):
        return [make_list_from_sections()]

class SectionTransform(Transform):
    # Apply the transformation just after the doctree is read, so that the 
    # sections being converted into lists will still appear in the TOC.
    default_priority = DoctreeReadEvent.default_priority + 1

    def apply(self):
        _make_lists(self.document)

def _make_lists(node):
    if not isinstance(node, nodes.Element):
        return

    i = node.first_child_matching_class(make_list_from_sections)

    if i is not None:
        ol = nodes.enumerated_list('')
        ol += _items_from_sections(node[i+1:])

        node.children = node[:i]
        node += ol

    else:
        for child in node.children:
            _make_lists(child)

def _items_from_sections(sections):
    """
    Create a list item from each section in the given list of nodes.
    """
    items = []
    for section in sections:
        assert isinstance(section, nodes.section)
        item = nodes.list_item(); items.append(item)
        item.update_basic_atts(section)
        item += _downgrade_subsections(section)

    return items

def _downgrade_subsections(section):
    children = []

    for child in section.children[1:]:
        if not isinstance(child, nodes.section):
            children += [child]
        else:
            rubric = nodes.rubric('', child[0][0])
            rubric.update_basic_atts(child)
            children += [rubric]
            children += child.children[1:]

    return children

class make_list_from_sections(nodes.Element):
    pass

def setup(app):
    #app.add_directive('hidden-section', HiddenSection)
    app.add_directive('make-list-from-sections', MakeListFromSections)
    app.add_transform(SectionTransform)
    app.add_node(make_list_from_sections)

