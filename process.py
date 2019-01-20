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
    'ENCODING', 'NAVBAR_TEMPLATE', 'NAVBAR_DROPDOWN_LI_TEMPLATE',
    'NAVBAR_DROPDOWN_A_TEMPLATE', 'NAVBAR_DROPDOWN_DIV_TEMPLATE',
    'NAVBAR_DROPDOWN_ITEM_TEMPLATE', 'NAVBAR_A_TEMPLATE', 'SUBTITLE_TEMPLATE',
    'AUTHORS_TEMPLATE', 'parse_toc', 'build_navigation', 'process_title',
    'process_html', 'process_index'
]

codecs.register_error('strict', codecs.ignore_errors)

ENCODING = 'utf-8'

NAVBAR_TEMPLATE = """
<!-- Navbar -->
<nav class="navbar navbar-expand-md navbar-light bg-light">
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
        <form class="form-inline my-3 my-md-0">
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

SUBTITLE_TEMPLATE = '<h2 class="sub-title">{text}</h2>'

AUTHORS_TEMPLATE = '<p class="pt-3">{text}</p>'


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
        with codecs.open(html_path, encoding=ENCODING) as html_file:
            content = html_file.read()

        with codecs.open(html_path, 'w', encoding=ENCODING) as html_file:
            for pattern, replacement in patterns:
                content = content.replace(pattern, replacement)

            html_file.write(content)

        os.rename(
            os.path.join(root_directory, source_file),
            os.path.join(root_directory, target_file))


def build_navigation(toc):
    """
    Builds the *HTML* navigation using given table of content.

    Parameters
    ----------
    toc : OrderedDict
        Table of content used to build the *HTML* navigation.

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


def process_title(path):
    """
    Processes the title *div* of the *HTML* file at given path.

    Parameters
    ----------
    path : unicode
        Path of the *HTML* file to process.

    Returns
    -------
    bool
        Definition success.
    """

    with codecs.open(path, encoding=ENCODING) as html_file:
        html = BeautifulSoup(html_file, 'html5lib')

        # Extracting "page-tile" section to make it a "body" top-level element.
        section = html.body.find('section', **{'class_': 'page-title'})
        section.extract()
        html.body.insert(0, section)

        container = section.find(
            'div', **{'class_': 'container-fluid text-center py-3'})

        # Creating the sub-title.
        h1 = section.find('h1')
        h1.find('br').extract()
        h2 = BeautifulSoup(
            SUBTITLE_TEMPLATE.format(
                **{'text': list(h1.children)[-1].extract().string}),
            'html.parser').find('h2')
        container.append(h2)

        # Formatting "author" div.
        div = section.find('div', **{'class_': 'author'}).extract()
        for br in div.find_all('br'):
            br.extract()

        authors = []
        for child in div.children:
            author = child.string.strip()

            if author:
                authors.append(author)

            child.extract()

        container.append(
            BeautifulSoup(
                AUTHORS_TEMPLATE.format(**{'text': '; '.join(authors)}),
                'html.parser').find('p'))

        # Removing unused "<br>" tag.
        list(section.find_all('br'))[-1].extract()

    with codecs.open(path, 'w', encoding=ENCODING) as html_file:
        html_file.write(unicode(html))

    return True


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

    with codecs.open(path, encoding=ENCODING) as html_file:
        html = BeautifulSoup(html_file, 'html5lib')

        # Removing comments.
        comments = html.find_all(text=lambda text: isinstance(text, Comment))
        for comment in comments:
            comment.extract()

        # Removing empty "<p>" tags of class "indent" of "noindent".
        p_i = html.body.find_all('p', **{'class_': ['indent', 'noindent']})
        for p in p_i:
            extract = True
            for child in p.children:
                if not isinstance(child, NavigableString) and child is not None:
                    extract = False
                    break
                else:
                    if len(child.string.strip()) != 0:
                        extract = False
                        break

            if extract:
                p.extract()

        # Cleanup "<pre>" tags of class "listings".
        pre_l = html.body.find_all('pre', **{'class_': 'listings'})
        for pre in pre_l:
            # Removing the surounding "<br>" tags.
            pre.find('br').extract()
            pre.find_all('br')[-1].extract()
            for child in pre.children:
                if isinstance(child, NavigableString):
                    if len(child.string.strip()) == 0:
                        child.extract()

        # Removing first breadcrumbs.
        breadcrumbs = html.body.find('div', **{'class_': 'crosslinks'})
        if breadcrumbs is not None:
            breadcrumbs.extract()

        # Inserting the navigation bar.
        html.body.insert(0, navigation)

    with codecs.open(path, 'w', encoding=ENCODING) as html_file:
        html_file.write(unicode(html))

    return True


def process_index(path):
    """
    Process the index *HTML* file at given path.

    Parameters
    ----------
    path : unicode
        Path of the *HTML* file to process.

    Returns
    -------
    bool
        Definition success.
    """

    with codecs.open(path, encoding=ENCODING) as html_file:
        html = BeautifulSoup(html_file, 'html5lib')

        # Removing the navigation bar.
        html.body.find('nav').extract()

        # Removing side columns.
        for div in html.body.find_all('div', **{'class_': 'col-md-2'}):
            div.extract()

        # Updating central column class.
        html.body.find('div', **{'class_': 'col-md-8'})['class'] = 'col-xl-12'

    with codecs.open(path, 'w', encoding=ENCODING) as html_file:
        html_file.write(unicode(html))

    return True
