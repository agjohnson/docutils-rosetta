from docutils import parsers, nodes
from docutils.parsers.rst import states

import codecs

from . import DefaultTransform


grammar = """\

char_space = ' ' | '\t'
char_normal = ~(char_space | crlf) anything
char_command = '='

sp = char_space+ -> ' '
space = char_space+ -> ' '
crlf = ('\n' | '\r' '\n'?)
    -> transform.visit('text', children=[' '])
blank_line = char_space* crlf

inline_roles = (
    inline_code | inline_emphasis | inline_bold | inline_filename | inline_link
)
inline_code = "C<" <inline_role_text+>:text ">"
    -> transform.visit('inline_code', text=text)
inline_emphasis = "I<" <inline_role_text+>:text ">"
    -> transform.visit('inline_emphasis', text=text)
inline_bold = "B<" <inline_role_text+>:text ">"
    -> transform.visit('inline_bold', text=text)
inline_filename = "F<" <inline_role_text+>:text ">"
    -> transform.visit('inline_filename', text=text)
inline_link = "L<" <inline_role_text+>:link ">"
    -> transform.visit('inline_link', link=link)
inline_role_text = ~">" anything

inline_text = (~inline_roles text)+:children
    -> transform.visit('text', children=children)

inline = (inline_roles | inline_text)
inlines = inline+:inlines -> transform.visit('inlines', children=inlines)

text = <char_normal | sp>

heading_directive = char_command "head" <digit+>:level sp argument_lines:children
    -> transform.visit('heading', level=int(level), children=children)
item_directive = char_command "item" sp argument_lines:children -> children
over_directive = char_command "over" (sp digit* | crlf)
back_directive = char_command "back"

begin_directive = char_command 'begin' sp <text*>:format crlf
end_directive = char_command 'end' (sp <text*>) (crlf | end)
begin_rst_directive = char_command 'begin' sp 'rst' crlf
end_rst_directive = char_command 'end' (sp 'rst')? (crlf | end)

title_directive = char_command 'TITLE' sp argument_lines:children
    -> transform.visit('heading', level=1, children=children)
subtitle_directive = char_command 'SUBTITLE' sp argument_lines:children
    -> transform.visit('heading', level=2, children=children)

argument_line = inlines:children (crlf | end):crlf
    -> transform.visit('argument_line', children=children, crlf=crlf)
argument_lines = argument_line+:children ~~(blank_line | end)
    -> transform.visit('argument_lines', children=children)

begin_rst_block_line = ~end_rst_directive anything:children
begin_rst_block = begin_rst_directive begin_rst_block_line*:children end_rst_directive
    -> transform.visit('begin', children=children)

paragraph_lines = inline+:children (crlf | end) -> children
paragraph = paragraph_lines+:children (blank_line | end)
    -> transform.visit('paragraph', children=children)

block = blank_line* paragraph

bullet_list_item = item_directive:children
    -> transform.visit('bullet_list_item', children=children)
bullet_list_block = ~over_directive bullet_list_item:children blank_line* -> children
bullet_list = blank_line* over_directive bullet_list_block*:children back_directive
    -> transform.visit('bullet_list', children=children)

naked_list = bullet_list_block+:children
    -> transform.visit('bullet_list', children=children)

section_block = blank_line*
    ~(title_directive | subtitle_directive | heading_directive | end_directive)
    (bullet_list | naked_list | code_block | paragraph):children
    -> children
section = blank_line*
    (title_directive | subtitle_directive | heading_directive):title
    section_block*:children
    -> transform.visit('section', title=title, children=children)

code_block_line = crlf* ' '+ text*:children (crlf | end) -> children
code_block = blank_line* code_block_line+:children (blank_line | end)
    -> transform.visit('code', children=children)

document_block = (
    begin_rst_block
    | begin_directive
    | end_directive
    | section
    | bullet_list
    | naked_list
    | code_block
    | block
)

document = document_block*:children blank_line*
    -> transform.visit('document', children=children)

"""


class PODTransform(DefaultTransform):

    grammar = grammar

    def __init__(self, *args, **kwargs):
        self.rst_statemachine = kwargs.pop('rst_statemachine', None)
        super(PODTransform, self).__init__(*args, **kwargs)
        self.sections = {}
        self.current_section_level = 0

    def visit_text(self, children):
        return nodes.Text(''.join(children), ''.join(children))

    def visit_inline_code(self, text):
        node = nodes.literal()
        node.append(nodes.Text(text, text))
        return node

    def visit_inline_emphasis(self, text):
        node = nodes.emphasis()
        node.append(nodes.Text(text, text))
        return node

    def visit_inline_bold(self, text):
        node = nodes.strong()
        node.append(nodes.Text(text, text))
        return node

    def visit_inline_link(self, link):
        node = nodes.reference()
        node['refuri'] = link
        return node

    def visit_inlines(self, children):
        return children

    # Directives
    def visit_argument_line(self, children, crlf):
        if isinstance(crlf, str):
            children.append(nodes.Text(' ', ' '))
        return children

    def visit_argument_lines(self, children):
        return [item for sublist in children for item in sublist]

    def visit_heading(self, level, children):
        title = nodes.title()
        title.document = self.document
        title['level'] = level
        title.extend(children)
        return title

    def visit_section(self, title, children):
        section = nodes.section()
        section.document = self.document
        section['ids'] = ['foo']
        section.append(title)
        section.extend(children)

        level = title['level']
        if level > self.current_section_level:
            self.current_section_level = level
            self.sections[level] = section

        return section

    def visit_paragraph(self, children):
        node = nodes.paragraph()
        node.document = self.document
        node.extend([c for line in children for c in line])
        return node

    def visit_bullet_list(self, children):
        node = nodes.bullet_list()
        node.extend(children)
        return node

    def visit_bullet_list_item(self, children):
        node = nodes.list_item()
        node.document = self.document
        node.append(self.visit_paragraph([children]))
        return node

    def visit_item(self, children):
        node = nodes.list_item()

    def visit_code(self, children):
        node = nodes.literal_block()
        node.extend(
            nodes.Text(text, text) for text in
            map(lambda n: ''.join(n + ['\n']), children)
        )
        return node

    def visit_begin(self, format, children):
        return children

#    def visit_begin(self, children):
#        content = ''.join(children)
#        node = nodes.section()
#        node.document = self.document
#        node.settings = self.document.settings
#        node.reporter = self.document.reporter
#        node.note_source = self.document.note_source
#        node['source'] = self.document['source']
#        if self.rst_statemachine:
#            self.rst_statemachine.run(
#                content,
#                node,
#                match_titles=False
#            )
#        else:
#            text = nodes.Text(children, children)
#            node.children.append(nodes.literal_block(text))
#        return node

    def visit_document(self, children):
        self.document.extend([c for c in children])
        self.fix_sections()
        return self.document

    # Other
    def fix_sections(self):
        """Walk through document and push around sections

        This is too complex for this parser, as docutils expects sections to be
        nested to show hierarchy.
        """
        sections = [self.document]
        for node in self.document.traverse(nodes.section):
            current_level = len(sections) - 1
            title = node.next_node(nodes.title)

            try:
                level = title.get('level', 1)
                if level != current_level and level > 0:
                    current_level = level
                sections = sections[0:current_level]
                sections.append(node)

                node.parent.remove(node)
                sections[level - 1].append(node)
            except AttributeError:
                pass
