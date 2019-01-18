# -*- coding: utf-8 -*-
"""
HTML - Processing
=================
"""

import codecs
import os
import re
import subprocess
from bs4 import BeautifulSoup, Comment, NavigableString
from collections import OrderedDict

__author__ = 'Cinematic Color Authors'
__copyright__ = 'Copyright (C) 2019 - Cinematic Color Authors'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Cinematic Color Authors'
__email__ = 'ves-tech-color@googlegroups.com'
__status__ = 'Production'

__all__ = [
    'BOOTSTRAP_STYLESHEET_TEMPLATE', 'CUSTOM_STYLESHEET_TEMPLATE',
    'JQUERY_JAVSCRIPT_TEMPLATE', 'POPPER_JAVSCRIPT_TEMPLATE',
    'BOOTSTRAP_JAVSCRIPT_TEMPLATE', 'NAVBAR_TEMPLATE',
    'NAVBAR_DROPDOWN_LI_TEMPLATE', 'NAVBAR_DROPDOWN_A_TEMPLATE',
    'NAVBAR_DROPDOWN_DIV_TEMPLATE', 'NAVBAR_DROPDOWN_ITEM_TEMPLATE',
    'NAVBAR_A_TEMPLATE', 'CONTENT_TEMPLATE', 'FOOTER_TEMPLATE', 'parse_toc',
    'build_navigation', 'process_html'
]

codecs.register_error('strict', codecs.ignore_errors)

BOOTSTRAP_STYLESHEET_TEMPLATE = ('<link rel="stylesheet" type="text/css" '
                                 'href="assets/css/bootstrap.min.css"/>')
CUSTOM_STYLESHEET_TEMPLATE = ('<link rel="stylesheet" type="text/css" '
                              'href="assets/css/custom.css"/>')

JQUERY_JAVSCRIPT_TEMPLATE = ('<script src="assets/js/jquery.min.js">'
                             '</script>')
POPPER_JAVSCRIPT_TEMPLATE = ('<script src="assets/js/popper.min.js">'
                             '</script>')
BOOTSTRAP_JAVSCRIPT_TEMPLATE = ('<script src="assets/js/bootstrap.min.js">'
                                '</script>')

NAVBAR_TEMPLATE = """
<!-- Navbar -->
<nav class="navbar navbar-expand-md navbar-dark bg-dark">
    <a class="navbar-brand" href="#">Cinematic Color 2</a>
    <button
        class="navbar-toggler"
        type="button"
        data-toggle="collapse"
        data-target="#navbarSupportedContent"
        aria-controls="navbarSupportedContent"
        aria-expanded="false"
        aria-label="Toggle navigation"
    >
        <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbar">
        <ul class="navbar-nav mr-auto"></ul>
        <form class="form-inline my-2 my-md-0">
            <input class="form-control" type="text" placeholder="Search" />
        </form>
    </div>
</nav>
"""

NAVBAR_ITEM_LI_TEMPLATE = '<li class="nav-item"></li>'
NAVBAR_DROPDOWN_LI_TEMPLATE = '<li class="nav-item dropdown"></li>'
NAVBAR_DROPDOWN_A_TEMPLATE = ('<a class="nav-link dropdown-toggle" '
                              'href="{href}" '
                              'id="{id}" '
                              'role="button" '
                              'data-toggle="dropdown" '
                              'aria-haspopup="true" '
                              'aria-expanded="false">{text}</a>')
NAVBAR_DROPDOWN_DIV_TEMPLATE = ('<div class="dropdown-menu" '
                                'aria-labelledby="{aria}"></div>')
NAVBAR_DROPDOWN_ITEM_TEMPLATE = ('<a class="dropdown-item" '
                                 'href="{href}">{text}</a>')
NAVBAR_A_TEMPLATE = '<a class="nav-link" href="{href}">{text}</a>'

CONTENT_TEMPLATE = """
<!-- Content -->
<div class="container-fluid">
    <div class="row">
        <div class="col-md-12 px-3 py-3">
        </div>
    </div>
</div>
"""

FOOTER_TEMPLATE = """
<!-- Footer -->
<footer class="page-footer font-small">
    <div class="footer-copyright text-center py-3">
        Copyright © 2019 – Cinematic Color Authors –
        <a href="mailto:ves-tech-color@googlegroups.com">
            ves-tech-color@googlegroups.com</a
        >
    </div>
</footer>
"""


def _sanitize_filename(filename):
    """
    Sanitizes given filename.

    Paramters
    ---------
    filename : unicode
        Filename to sanitize.

    Returns
    -------
    unicode
        Sanitized filename.
    """

    return re.sub('\s+', ' ', re.sub("[\s,\\(\\)-\\.']+", ' ',
                                     filename)).strip()


def parse_toc(path):
    """
    Parses the table of content at given path.

    Parameters
    ----------
    path : unicode
        Path to parse the table of content.

    Returns
    -------
    OrderedDefaultDict
        Parsed table of content.
    """

    pattern = re.compile("{\\\\numberline {[\\d\\.]+}([\\w\\s,\\(\\)-\\.']+)}|"
                         "{([\\w\\s,\\(\\)-\\.']+)}")

    toc = OrderedDict()
    with open(path, 'r') as toc_file:
        chapter = None
        for line in toc_file.readlines():
            if line.startswith('\contentsline {chapter}'):
                search = re.search(pattern,
                                   line.replace('\contentsline {chapter}', ''))
                chapter = [
                    group for group in search.groups() if group is not None
                ][0]

                toc[chapter] = []

            if chapter is None:
                continue

            if line.startswith('\contentsline {section}'):
                search = re.search(pattern,
                                   line.replace('\contentsline {section}', ''))
                section = [
                    group for group in search.groups() if group is not None
                ][0]

                toc[chapter].append(section)

    return toc


def conform_filenames(toc, root_directory, extra_patterns=None):
    """
    Conforms the *HTML* filenames in given root directory and according to
    given table of content.

    Parameters
    ----------
    toc : unicode
        Table of content.
    root_directory : unicode
        Directory to conform the *HTML* filenames.
    extra_patterns : array_like, optional
        Extra patterns to search and replace for.
    """

    def _reference_path(filename):
        """
        Returns the reference *HTML* path of given filename.
        """

        return os.path.join(root_directory, '{0}.html'.format(
            filename.replace(' ', '')))

    patterns = extra_patterns[:]
    for chapter, sections in toc.items():
        chapter_base = _sanitize_filename(chapter)
        chapter_path = _reference_path(chapter_base)

        assert os.path.exists(chapter_path), (
            'Expected "{0}" chapter file was not found!'.format(chapter_path))

        patterns.append((os.path.basename(chapter_path), '{0}.html'.format(
            chapter_base.replace(' ', '-').lower())))

        for section in sections:
            section_base = _sanitize_filename(section)
            section_path = _reference_path(section_base)

            assert os.path.exists(section_path), (
                'Expected "{0}" section file was not found!'.format(
                    section_path))

            patterns.append((os.path.basename(section_path), '{0}.html'.format(
                section_base.replace(' ', '-').lower())))

    for source_file, target_file in patterns:
        print('Replacing "{0}" file patterns.'.format(source_file))

        html_path = os.path.join(root_directory, source_file)
        with codecs.open(html_path, encoding='utf-8') as html_file:
            content = html_file.read()

        with codecs.open(html_path, 'w', encoding='utf-8') as html_file:
            for pattern, replacement in patterns:
                content = content.replace(pattern, replacement)

            html_file.write(content)

        os.rename(
            os.path.join(root_directory, source_file),
            os.path.join(root_directory, target_file))


def build_navigation(toc, ignored_chapters=None):
    """
    Builds the *HTML* navigation using given table of content.

    Parameters
    ----------
    toc : OrderedDict
        Table of content used to build the *HTML* navigation.
    ignored_chapters : array_like, optional
        Chapters to ignore in the reference path.

    Returns
    -------
    BeautifulSoup
        *HTML* navigation.
    """

    def _reference_path(filename):
        """
        Returns the reference *HTML* path of given filename.
        """

        return '{0}.html'.format(
            _sanitize_filename(filename).replace(' ', '-').lower())

    navigation = BeautifulSoup(NAVBAR_TEMPLATE, 'html.parser').find('nav')
    navigation_ul = navigation.find('ul')
    for chapter, sections in toc.items():
        if chapter in ignored_chapters:
            continue

        chapter_href = _reference_path(chapter)

        if len(sections) != 0:
            navigation_li = BeautifulSoup(NAVBAR_DROPDOWN_LI_TEMPLATE,
                                          'html.parser').find('li')
            aria = os.path.splitext(chapter_href)[0]
            navigation_a = BeautifulSoup(
                NAVBAR_DROPDOWN_A_TEMPLATE.format(**{
                    'href': chapter_href,
                    'id': aria,
                    'text': chapter,
                }), 'html.parser')
            navigation_li.append(navigation_a)
            navigation_div = BeautifulSoup(
                NAVBAR_DROPDOWN_DIV_TEMPLATE.format(**{'aria': aria}),
                'html.parser').find('div')

            for section in sections:
                section_href = _reference_path(section)

                section_a = BeautifulSoup(
                    NAVBAR_DROPDOWN_ITEM_TEMPLATE.format(**{
                        'href': section_href,
                        'text': section,
                    }), 'html.parser')
                navigation_div.append(section_a)
                navigation_li.append(navigation_div)
        else:
            navigation_li = BeautifulSoup(NAVBAR_ITEM_LI_TEMPLATE,
                                          'html.parser').find('li')
            navigation_li.append(
                BeautifulSoup(
                    NAVBAR_A_TEMPLATE.format(**{
                        'href': chapter_href,
                        'text': chapter
                    }), 'html.parser'))

        navigation_ul.append(navigation_li)

    return navigation


def process_html(path, navigation):
    """
    Process the *HTML* file at given path.

    Parameters
    ----------
    path : unicode
        Path of the *HTML* file to process.
    navigation : BeautifulSoup
        *HTML* navigation.

    Returns
    -------
    bool
        Definition success.
    """

    with open(path) as html_file:
        html = BeautifulSoup(html_file, 'lxml')

        # Removing comments.
        comments = html.findAll(text=lambda text: isinstance(text, Comment))
        for comment in comments:
            comment.extract()

        # Removing initial css file.
        html.head.find('link').extract()

        # Removing first breadcrumbs.
        breadcrumbs = html.body.find('div', **{'class_': 'crosslinks'})
        if breadcrumbs is not None:
            breadcrumbs.extract()

        # Appending "Bootstrap" stylesheet.
        html.head.append(
            BeautifulSoup(BOOTSTRAP_STYLESHEET_TEMPLATE, 'html.parser'))

        # Appending "Custom" stylesheet.
        html.head.append(
            BeautifulSoup(CUSTOM_STYLESHEET_TEMPLATE, 'html.parser'))

        # Wrapping "body" contents.
        body_children = list(html.body.children)
        html.body.clear()
        container = BeautifulSoup(CONTENT_TEMPLATE, 'html.parser')
        column = container.find('div', **{'class_': 'col-md-12'})
        for child in body_children:
            column.append(child)
        html.body.append(container)

        # Inserting the navigation bar.
        html.body.insert(0, navigation)

        # Appending "Footer".
        html.body.append(BeautifulSoup(FOOTER_TEMPLATE, 'html.parser'))

        # Appending "JQuery" javascript.
        html.body.append(
            BeautifulSoup(JQUERY_JAVSCRIPT_TEMPLATE, 'html.parser'))

        # Appending "Popper" javascript.
        html.body.append(
            BeautifulSoup(POPPER_JAVSCRIPT_TEMPLATE, 'html.parser'))

        # Appending "Bootstrap" javascript.
        html.body.append(
            BeautifulSoup(BOOTSTRAP_JAVSCRIPT_TEMPLATE, 'html.parser'))

    with open(path, 'w') as html_file:
        html_file.write(html.prettify(encoding='utf8', formatter='xhtml'))

    return True
