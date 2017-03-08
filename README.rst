docutils-rosetta
================

Adds partial support for markup languages that aren't rST in docutils.

The goal of this project is to provide parsing of various markup sources and the
common interfaces that transform these syntaxes into docutil nodes. There are
common patterns that every language will use, this is an effort to put all of
this into one place.

When available, this will use native modules to generate AST from source. If an
existing AST isn't available, parsing will be handed off to `Parsley`_.

.. _Parsley: http://parsley.readthedocs.io/en/latest/index.html

Markup
------

POD (Perl 4, 5)
    **Alpha quality.** Support Perl 4 and 5 POD syntax

POD (Perl 6)
    **Not started yet.** Support Perl 6 POD additions

Asciidoc
    **Candidate.** Support Asciidoc the spec

Textile
    **Candidate.** Support the Textile spec

Markdown
    **Candidate.** Bring in the Parsley grammar from ``remarkdown``

CommonMark
    **Candidate.** Make a stricter version fo the Markdown grammar
