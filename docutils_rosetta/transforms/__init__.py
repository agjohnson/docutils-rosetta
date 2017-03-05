import parsley
from docutils.utils import new_document
from docutils import nodes


class DefaultTransform(object):

    grammar = None

    def __init__(self, *args, **kwargs):
        self.grammar = parsley.makeGrammar(self.grammar, {'transform': self})
        self.document = kwargs.pop('document', new_document('<string>'))

    def parse(self, source):
        return self.grammar(source)

    def parse_file(self, path):
        return self.parse(codecs.open(path, encoding='utf-8').read())

    def visit(self, node_type, **kwargs):
        try:
            fn = getattr(self, 'visit_{0}'.format(node_type))
        except AttributeError:
            node = self.default_visit(node_type, **kwargs)
        else:
            node = fn(**kwargs)
        if isinstance(node, nodes.Node):
            pass
        return node

    def default_visit(self, node_type, **kwargs):
        # print 'MISSING NODE:', node_type, kwargs
        return dict(node_type=node_type, **kwargs)
