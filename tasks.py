# -*- coding: utf-8 -*-
"""
Invoke - Tasks
==============
"""

from __future__ import print_function, unicode_literals

import biblib.bib
import glob
import os
import re
import subprocess
from invoke import task
from invoke.exceptions import Failure
from itertools import chain
from textwrap import TextWrapper

import process

__author__ = 'Cinematic Color Authors'
__copyright__ = 'Copyright (C) 2019 - Cinematic Color Authors'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Cinematic Color Authors'
__email__ = 'ves-tech-color@googlegroups.com'
__status__ = 'Production'

__all__ = [
    'UTILITIES_DIRECTORY', 'INDEX_DOCUMENT_NAME', 'ROOT_DOCUMENT_NAME',
    'TYPESETTING_DOCUMENT_NAME', 'BIBLIOGRAPHY_NAME', 'LATEX_SOURCE_DIRECTORY',
    'ASSETS_DIRECTORY', 'JERI_DIRECTORY', 'PDF_BUILD_DIRECTORY',
    'HTML_BUILD_DIRECTORY', 'HTML_RELEASE_DIRECTORY', 'TIDY_HTML',
    'message_box', 'clean', 'format', 'serve', 'build_pdf', 'build_html',
    'build_all', 'gh_deploy'
]

UTILITIES_DIRECTORY = 'utilities'

INDEX_DOCUMENT_NAME = 'index.tex'

ROOT_DOCUMENT_NAME = 'cinematic-color.tex'

TYPESETTING_DOCUMENT_NAME = 'typesetting.tex'

BIBLIOGRAPHY_NAME = 'bibliography.bib'

LATEX_SOURCE_DIRECTORY = 'latex'

ASSETS_DIRECTORY = 'assets'

JERI_DIRECTORY = os.sep.join([ASSETS_DIRECTORY, 'js', 'jeri'])

PDF_BUILD_DIRECTORY = os.sep.join(['build', 'pdf'])

HTML_BUILD_DIRECTORY = os.sep.join(['build', 'html'])

HTML_RELEASE_DIRECTORY = 'cinematic-color'

TIDY_HTML = [
    'tidy', '-q', '-i', '-utf8', '-asxhtml', '-m', '--custom-tags',
    'blocklevel', '--drop-empty-elements', 'no'
]


def message_box(message, width=79, padding=3, print_callable=print):
    """
    Prints a message inside a box.

    Parameters
    ----------
    message : unicode
        Message to print.
    width : int, optional
        Message box width.
    padding : unicode, optional
        Padding on each sides of the message.
    print_callable : callable, optional
        Callable used to print the message box.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> message = ('Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
    ...     'sed do eiusmod tempor incididunt ut labore et dolore magna '
    ...     'aliqua.')
    >>> message_box(message, width=75)
    ===========================================================================
    *                                                                         *
    *   Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do       *
    *   eiusmod tempor incididunt ut labore et dolore magna aliqua.           *
    *                                                                         *
    ===========================================================================
    True
    >>> message_box(message, width=60)
    ============================================================
    *                                                          *
    *   Lorem ipsum dolor sit amet, consectetur adipiscing     *
    *   elit, sed do eiusmod tempor incididunt ut labore et    *
    *   dolore magna aliqua.                                   *
    *                                                          *
    ============================================================
    True
    >>> message_box(message, width=75, padding=16)
    ===========================================================================
    *                                                                         *
    *                Lorem ipsum dolor sit amet, consectetur                  *
    *                adipiscing elit, sed do eiusmod tempor                   *
    *                incididunt ut labore et dolore magna                     *
    *                aliqua.                                                  *
    *                                                                         *
    ===========================================================================
    True
    """

    ideal_width = width - padding * 2 - 2

    def inner(text):
        """
        Formats and pads inner text for the message box.
        """

        return '*{0}{1}{2}{0}*'.format(
            ' ' * padding, text, (' ' * (width - len(text) - padding * 2 - 2)))

    print_callable('=' * width)
    print_callable(inner(''))

    wrapper = TextWrapper(
        width=ideal_width, break_long_words=False, replace_whitespace=False)

    lines = [wrapper.wrap(line) for line in message.split("\n")]
    lines = [' ' if len(line) == 0 else line for line in lines]
    for line in chain(*lines):
        print_callable(inner(line.expandtabs()))

    print_callable(inner(''))
    print_callable('=' * width)

    return True


@task
def clean(ctx, bytecode=False):
    """
    Cleans the project.

    Parameters
    ----------
    bytecode : bool, optional
        Whether to clean the bytecode files, e.g. *.pyc* files.

    Returns
    -------
    bool
        Task success.
    """

    message_box('Cleaning project...')

    patterns = [
        PDF_BUILD_DIRECTORY, HTML_BUILD_DIRECTORY,
        '{0}/*'.format(HTML_RELEASE_DIRECTORY), '**/.DS_Store'
    ]

    if bytecode:
        patterns.append('**/*.pyc')
        patterns.append('**/*.pyo')

    for pattern in patterns:
        ctx.run("rm -rf {}".format(pattern))


@task
def format(ctx):
    """
    Converts unicode characters to ASCII and cleanup the *BIB* file.

    Parameters
    ----------
    ctx : invoke.context.Context
        Context.

    Returns
    -------
    bool
        Task success.
    """

    message_box('Converting unicode characters to ASCII...')
    with ctx.cd(UTILITIES_DIRECTORY):
        ctx.run('./unicode_to_ascii.py')

    message_box('Cleaning up "BIB" file...')
    with ctx.cd(LATEX_SOURCE_DIRECTORY):
        bibtex_path = os.path.join(LATEX_SOURCE_DIRECTORY, BIBLIOGRAPHY_NAME)
        with open(bibtex_path) as bibtex_file:
            bibtex = biblib.bib.Parser().parse(
                bibtex_file.read()).get_entries()

        for entry in bibtex.values():
            try:
                del entry['file']
            except KeyError:
                pass
            for key, value in entry.items():
                entry[key] = re.sub('(?<!\\\\)\\&', '\\&', value)

        with open(bibtex_path, 'w') as bibtex_file:
            for entry in bibtex.values():
                bibtex_file.write(entry.to_bib())
                bibtex_file.write('\n')


@task
def serve(ctx, port=8900):
    """
    Serves the *HTML* website on given port.

    Parameters
    ----------
    ctx : invoke.context.Context
        Context.
    port : int, optional
        Port to start the *Python* server at.

    Returns
    -------
    bool
        Task success.
    """

    message_box('Serving "HTML" website...')
    with ctx.cd(HTML_RELEASE_DIRECTORY):
        ctx.run('python3 -m http.server {0};'.format(port))


@task(format)
def build_pdf(ctx):
    """
    Builds the *PDF*.

    Parameters
    ----------
    ctx : invoke.context.Context
        Context.

    Returns
    -------
    bool
        Task success.
    """

    message_box('Building "PDF"...')

    ctx.run('mkdir -p {0}'.format(PDF_BUILD_DIRECTORY))
    ctx.run('cp -r {0}/* {1}'.format(LATEX_SOURCE_DIRECTORY,
                                     PDF_BUILD_DIRECTORY))
    ctx.run('cp -r {0} {1}'.format(ASSETS_DIRECTORY, PDF_BUILD_DIRECTORY))

    with ctx.cd(PDF_BUILD_DIRECTORY):
        ctx.run(
            'pdflatex --shell-escape -interaction=nonstopmode {0}'.format(
                ROOT_DOCUMENT_NAME),
            warn=True)
        ctx.run(
            'biber {0}'.format(ROOT_DOCUMENT_NAME.replace('tex', 'bcf')),
            warn=True)
        ctx.run(
            'pdflatex --shell-escape -interaction=nonstopmode {0}'.format(
                ROOT_DOCUMENT_NAME),
            warn=True)
        ctx.run(
            'pdflatex --shell-escape -interaction=nonstopmode {0}'.format(
                ROOT_DOCUMENT_NAME),
            warn=True)


@task(format)
def build_html(ctx, process_html=True):
    """
    Builds the *HTML* website.

    Parameters
    ----------
    ctx : invoke.context.Context
        Context.
    process_html : bool
        Whether to process the *HTML* files.

    Returns
    -------
    bool
        Task success.
    """

    message_box('Building "HTML" website...')

    ctx.run('mkdir -p {0}'.format(HTML_BUILD_DIRECTORY))
    ctx.run('cp -r {0}/* {1}'.format(LATEX_SOURCE_DIRECTORY,
                                     HTML_BUILD_DIRECTORY))

    ctx.run('cp -r {0} {1}'.format(ASSETS_DIRECTORY, HTML_BUILD_DIRECTORY))

    with ctx.cd(HTML_BUILD_DIRECTORY):
        # ".toc" and ".bbl" file generation.
        ctx.run(
            'pdflatex --shell-escape -interaction=nonstopmode {0}'.format(
                ROOT_DOCUMENT_NAME),
            warn=True)
        ctx.run(
            'biber {0}'.format(ROOT_DOCUMENT_NAME.replace('tex', 'bcf')),
            warn=True)
        # "TeX4Ht" invokation.
        ctx.run(
            'make4ht -ul -c {0} {1} '
            '"" '
            '"" '
            '"" '
            '"-interaction=nonstopmode"'.format(
                ROOT_DOCUMENT_NAME.replace('tex', 'cfg'), ROOT_DOCUMENT_NAME),
            warn=True)
        ctx.run(
            'make4ht -ul -c {0} {1} '
            '"" '
            '"" '
            '"" '
            '"-interaction=nonstopmode"'.format(
                ROOT_DOCUMENT_NAME.replace('tex', 'cfg'), INDEX_DOCUMENT_NAME),
            warn=True)

    ctx.run('mkdir -p {0}'.format(HTML_RELEASE_DIRECTORY))

    ctx.run('cp -r {0}/*.html {1}'.format(HTML_BUILD_DIRECTORY,
                                          HTML_RELEASE_DIRECTORY))
    ctx.run('cp -r {0}/*.css {1}'.format(HTML_BUILD_DIRECTORY,
                                         HTML_RELEASE_DIRECTORY))
    ctx.run('cp -r {0} {1}'.format(ASSETS_DIRECTORY, HTML_RELEASE_DIRECTORY))
    ctx.run('cp -r {0}/* {1}'.format(JERI_DIRECTORY, HTML_RELEASE_DIRECTORY))

    if process_html:
        message_box('Processing "HTML"...')

        toc_file = os.path.join(HTML_BUILD_DIRECTORY,
                                ROOT_DOCUMENT_NAME.replace('tex', 'toc'))
        toc = process.parse_toc(toc_file)

        typesetting_sections = process.parse_sections(
            os.path.join(HTML_BUILD_DIRECTORY, TYPESETTING_DOCUMENT_NAME))
        typesetting_filenames = [('{0}.html'.format(section.replace(' ', '')),
                                  '{0}.html'.format(sanitized))
                                 for section, sanitized in typesetting_sections
                                 ]

        process.conform_filenames(
            toc, HTML_RELEASE_DIRECTORY,
            [('cinematic-color.html', 'cinematic-color.html'),
             ('contentsname.html', 'contents.html'),
             ('bibname.html', 'bibliography.html')] + typesetting_filenames)

        toc.update({'Bibliography': []})

        navigation = process.build_navigation(toc)

        html_file = os.path.join(HTML_RELEASE_DIRECTORY,
                                 ROOT_DOCUMENT_NAME).replace('tex', 'html')
        print('Processing "{0}" file...'.format(html_file))
        process.process_title(html_file)

        for html_file in glob.glob(
                os.path.join(HTML_RELEASE_DIRECTORY, '*.html')):
            print('Processing "{0}" file...'.format(html_file))

            process.process_html(html_file, navigation)
            subprocess.call(TIDY_HTML + [html_file])

        html_file = os.path.join(HTML_RELEASE_DIRECTORY,
                                 INDEX_DOCUMENT_NAME).replace('tex', 'html')
        print('Processing "{0}" file...'.format(html_file))
        process.process_title(html_file)
        process.process_index(html_file)
        subprocess.call(TIDY_HTML + [html_file])

    for document_name in (ROOT_DOCUMENT_NAME, INDEX_DOCUMENT_NAME):
        css_file = os.path.join(HTML_RELEASE_DIRECTORY, document_name).replace(
            'tex', 'css')
        print('Processing "{0}" file...'.format(css_file))
        process.process_css(css_file)

    # Stand-in process.
    with ctx.cd(HTML_RELEASE_DIRECTORY):
        ctx.run('mv {0} {1}'.format(
            INDEX_DOCUMENT_NAME.replace('tex', 'html'),
            'no-{0}'.format(INDEX_DOCUMENT_NAME)).replace('tex', 'html'))
        ctx.run('cp -r ../stand-in/* .')


@task(clean, build_pdf, build_html)
def build_all(ctx):
    """
    Cleans and builds all the targets, i.e. *PDF* and *HTML* website.

    Parameters
    ----------
    ctx : invoke.context.Context
        Context.

    Returns
    -------
    bool
        Task success.
    """

    message_box('Building all targets...')


@task(clean, build_html)
def gh_deploy(ctx):
    """
    Deploys the *HTML* website to *Github Pages*.

    Parameters
    ----------
    ctx : invoke.context.Context
        Context.

    Returns
    -------
    bool
        Task success.
    """

    message_box('Deploying "HTML" website to "Github Pages"...')

    result = ctx.run('git rev-parse HEAD', hide='both')
    sha = result.stdout.strip().split('\n')[0]
    ctx.run('ghp-import '
            '-c "cinematiccolor.org" '
            '-m "Deploy {0} with \"ghp-import\"." '
            '-p {1}'.format(sha, HTML_RELEASE_DIRECTORY))
