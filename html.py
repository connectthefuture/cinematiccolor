import subprocess
from bs4 import BeautifulSoup, Comment, NavigableString

BOOTSTRAP_STYLESHEET_TEMPLATE = ('<link rel="stylesheet" type="text/css" '
                                 'href="assets/css/bootstrap.min.css"/>')

JQUERY_JAVSCRIPT_TEMPLATE = ('<script src="assets/js/jquery.min.js">'
                             '</script>')
POPPER_JAVSCRIPT_TEMPLATE = ('<script src="assets/js/popper.min.js">'
                             '</script>')
BOOTSTRAP_JAVSCRIPT_TEMPLATE = ('<script src="assets/js/bootstrap.min.js">'
                                '</script>')

NAVBAR_TEMPLATE = """
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


def extract_navigation(path):
    with open(path) as html_file:
        html = BeautifulSoup(html_file, 'lxml')
        toc = html.body.find('ul', **{'class_': 'TofC'})

    navigation = BeautifulSoup(NAVBAR_TEMPLATE, 'html.parser').find('nav')
    navigation_ul = navigation.find('ul')
    for toc_li_child in toc.find_all('li', recursive=False):
        toc_li_child_a = toc_li_child.find('a')
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
        navigation_ul.append(navigation_li)

    return navigation


def process_html(path, navigation):
    with open(path) as html_file:
        html = BeautifulSoup(html_file, 'lxml')

        # TODO: Removing comments.
        for child in html.descendants:
            if isinstance(child, Comment):
                child.extract()

        # Removing the first "latex2html" navigation panel.
        html.body.find('div', **{'class_': 'navigation'}).extract()

        # Cleaning up the second "latex2html" navigation panel.
        # navigation = html.body.find('div', **{'class_': 'navigation'})

        # children_to_extract = []
        # for child in navigation.descendants:
        #     if child is None:
        #         continue

        #     if child.name == 'br':
        #         break

        #     children_to_extract.append(child)

        # for child in reversed(children_to_extract):
        #     child.extract()

        # Appending "Bootstrap" stylesheet.
        html.head.append(
            BeautifulSoup(BOOTSTRAP_STYLESHEET_TEMPLATE, 'html.parser'))

        # Appending the navigation bar.
        html.body.insert(0, navigation)

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
