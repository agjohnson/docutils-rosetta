import parsley

from docutils import parsers
from docutils.parsers.rst import states

from ..transforms.pod import PODTransform


class PodParser(parsers.Parser):

    supported = ('pod', 'pod6')

    def parse(self, inputstring, document):
        self.setup_parse(inputstring, document)

        rst_statemachine = states.RSTStateMachine(
              state_classes=states.state_classes,
              initial_state='Body',
              debug=document.reporter.debug_flag
        )

        self.transform = PODTransform(rst_statemachine=rst_statemachine,
                                      document=self.document)
        self.transform.document = document

        self.document = self.transform.parse(inputstring + '\n').document()

        self.finish_parse()


def setup(app):
    app._additional_source_parsers['.pod'] = PodParser
