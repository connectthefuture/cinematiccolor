# -*- coding: utf-8 -*-
"""
HTML - Processing
=================
"""

import subprocess
from bs4 import BeautifulSoup, Comment, NavigableString

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
    'NAVBAR_A_TEMPLATE', 'CONTENT_TEMPLATE', 'FOOTER_TEMPLATE',
    'extract_navigation', 'process_html'
]

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


def extract_navigation(path, ignored_chapters=None):
    """
    Extracts and generate the *HTML* navigation using given reference path.

    Parameters
    ----------
    path : unicode
        Path to parse to extract the *HTML* navigation.
    ignored_chapters : array_like, optional
        Chapters to ignore in the reference path.

    Returns
    -------
    BeautifulSoup
        *HTML* navigation.
    """

    with open(path) as html_file:
        html = BeautifulSoup(html_file, 'lxml')
        toc = html.body.find('ul', **{'class_': 'ChildLinks'})

    navigation = BeautifulSoup(NAVBAR_TEMPLATE, 'html.parser').find('nav')
    navigation_ul = navigation.find('ul')
    for toc_li_child in toc.find_all('li', recursive=False):
        toc_li_child_a = toc_li_child.find('a')

        if toc_li_child_a.text in ignored_chapters:
            continue

        navigation_li = BeautifulSoup(NAVBAR_DROPDOWN_LI_TEMPLATE,
                                      'html.parser').find('li')
        aria = toc_li_child_a['href']
        aria = aria.rsplit('.', 1)[0].lower().replace('_', '-')
        navigation_a = BeautifulSoup(
            NAVBAR_DROPDOWN_A_TEMPLATE.format(
                **{
                    'href': toc_li_child_a['href'],
                    'id': aria,
                    'text': toc_li_child_a.string
                }), 'html.parser')
        navigation_li.append(navigation_a)
        navigation_div = BeautifulSoup(
            NAVBAR_DROPDOWN_DIV_TEMPLATE.format(**{'aria': aria}),
            'html.parser').find('div')

        for toc_ul_child in toc_li_child.find_all('ul', recursive=False):
            for li_grand_child in toc_ul_child.find_all('li', recursive=False):
                li_grand_child_a = li_grand_child.find('a')
                navigation_item_a = BeautifulSoup(
                    NAVBAR_DROPDOWN_ITEM_TEMPLATE.format(
                        **{
                            'href': li_grand_child_a['href'],
                            'text': li_grand_child_a.string
                        }), 'html.parser')
                navigation_div.append(navigation_item_a)

        navigation_li.append(navigation_div)

        # Changing non-dropdowns into links.
        if navigation_div.find('a') is None:
            navigation_div.extract()
            navigation_li_a = navigation_li.find('a')
            navigation_li_a.extract()
            navigation_li.append(
                BeautifulSoup(
                    NAVBAR_A_TEMPLATE.format(
                        **{
                            'href': navigation_li_a['href'],
                            'text': navigation_li_a.string
                        }), 'html.parser'))
            navigation_li['class_'] = 'nav-item'

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

        # Removing "latex2html" stylesheet.
        html.find('link').extract()

        # Appending "Bootstrap" stylesheet.
        html.head.append(
            BeautifulSoup(BOOTSTRAP_STYLESHEET_TEMPLATE, 'html.parser'))

        # Appending "Custom" stylesheet.
        html.head.append(
            BeautifulSoup(CUSTOM_STYLESHEET_TEMPLATE, 'html.parser'))

        # Cleaning up the second "latex2html" navigation panel.
        navigation_panel = html.body.find('div', **{'class_': 'navigation'})
        children_to_extract = []
        for child in navigation_panel.descendants:
            if child is None:
                continue

            if child.name == 'br':
                break

            children_to_extract.append(child)

        for child in reversed(children_to_extract):
            child.extract()

        # Update "Subsections" "strong" name to "Contents".
        # for strong in html.body.find_all('strong'):
        #     if 'id' in strong.parent.attrs:
        #         if strong.parent.attrs['id'] == 'CHILD_LINKS':
        #             strong.string = 'Contents'
        #             break

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