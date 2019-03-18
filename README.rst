Cinematic Color
===============

**A VES Technology Committee White Paper**

..  image:: https://raw.githubusercontent.com/ves-tech/cinematiccolor/master/latex/assets/images/cinematic-color-jumbotron.jpg

This repository contains the source of the current
`Cinematic Color <https://cinematiccolor.org>`_ website and associated publication.

The initial **Cinematic Color** repository as it was authored and published by
`Jeremy Selan <https://github.com/jeremyselan>`_ is available at the
`v2012 <https://github.com/ves-tech/cinematiccolor/releases/tag/v2012>`_ tag.
The associated website content is available at the related
`v2012-website <https://github.com/ves-tech/cinematiccolor/releases/tag/v2012-website>`_
tag.

Installation
------------

The *HTML* website and the *PDF* document are built using
`LaTeX <https://www.latex-project.org/>`_. The *HTML* website build specifically
relies on `TeX4ht <https://tug.org/applications/tex4ht/mn.html>`_.

The build process is executed by `Invoke <http://www.pyinvoke.org/>`_ and only
requires a few commands to build both the *HTML* website and the *PDF* document.

.. note:: The build process only works on *Linux* and *macOs* currently.

It is possible to edit the *LaTeX* source with any editor, and generate the
*PDF* document with it.

Primary Dependencies
^^^^^^^^^^^^^^^^^^^^

**Cinematic Color** requires various dependencies in order to build:

-   `Beautiful Soup 4 <https://www.crummy.com/software/BeautifulSoup/>`_
-   `biblib <https://github.com/aclements/biblib/>`_
-   `html5lib <https://pypi.org/project/html5lib/>`_
-   `Inkscape <https://inkscape.org/>`_
-   `Invoke <http://www.pyinvoke.org/>`_
-   `LaTeX <https://www.latex-project.org/>`_ (`MacTeX <http://www.tug.org/mactex/>`_ on *macOs*).
-   `Python 3.6 <https://www.python.org/download/releases/>`_
-   `Tidy <http://www.html-tidy.org/>`_

Secondary Dependencies
^^^^^^^^^^^^^^^^^^^^^^

-   `ghp-import <https://github.com/davisp/ghp-import/>`_
-   `Pylint <https://www.pylint.org/>`_
-   `Yapf <https://github.com/google/yapf/>`_

macOs
^^^^^

Assuming `Homebrew <https://brew.sh/>`_ is installed::

    brew install tidy-html5
    brew tap caskroom/cask
    brew cask install mactex
    brew cask install inkscape

The *LaTeX* distribution needs to be updated, preparing a coffee might be a
good idea because it is long::

    sudo tlmgr update --self
    sudo tlmgr update --all

`Anaconda <https://www.continuum.io/downloads>`_ from *Continuum Analytics*
is the Python distribution used by the authors, it is recommended to create a
dedicated environment::

    conda create -y -n cinematic-color-2 python=3.6
    source activate cinematic-color-2
    conda install -y beautifulsoup4 html5lib invoke pylint yapf
    pip install ghp-import git+https://github.com/aclements/biblib.git

.. note:: *Inkscape 0.92* command line usage on *macOs* requires passing images
    with an absolute path which breaks portability of the project.
    A `Inkscape wrapper <https://github.com/ves-tech/cinematiccolor/blob/master/utilities/inkscape>`_
    exists in the `utilities` directory, this wrapper must be added to
    **$PATH** and takes precedence on *Inkscape* binary.

Build
-----

With the dependencies installed, the *PDF* document is built as follows::

    invoke build-pdf

The *HTML* website is built as follows::

    invoke build-html

The repository can be cleaned as follows::

    invoke clean

It is possible to chain multiple commands as follows::

    invoke clean build-pdf build-html

Cleaning and building all the targets, i.e. *PDF* and *HTML* website, is done
as follows::

    invoke build-all

Overleaf
^^^^^^^^

`Overleaf <https://www.overleaf.com/>`_ can be used to edit the *LaTeX* source:

-   *Fork* the `Cinematic Color <https://github.com/ves-tech/cinematiccolor/>`_
    repository.
-   Create a new project in *Overleaf*, use the *Import from Github* option and
    choose the newly created *Fork*.
-   Perform your edits and push them to the *Fork* using the *Overleaf* menu
    *Sync --> Github* option.
-   Once the edits are pushed to the *Fork*,
    `create a Pull Request <https://help.github.com/en/articles/creating-a-pull-request>`_.
-   The *Fork* can be kept in sync with the *Cinematic Color* repository by
    following this `Github guide <https://help.github.com/en/articles/syncing-a-fork>`_.

Visual Studio Code and LaTeX Workshop
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`Visual Studio Code <https://code.visualstudio.com/>`_ can be used along with
the `LaTeX Workshop <https://github.com/James-Yu/LaTeX-Workshop>`_ extension to
edit the *LaTeX* source. The following settings are recommended:

.. code:: json

    "latex-workshop.chktex.enabled": true,
    "latex-workshop.latex.recipes": [{
        "name": "pdflatex ➞ biber ➞ pdflatex × 2",
        "tools": [
            "pdflatex",
            "biber",
            "pdflatex",
            "pdflatex"
        ]
    }],
    "latex-workshop.latex.tools": [{
            "name": "pdflatex",
            "command": "pdflatex",
            "args": [
                "--shell-escape",
                "-synctex=1",
                "-interaction=nonstopmode",
                "-file-line-error",
                "%DOC%"
            ],
            "env": {}
        },
        {
            "args": [
                "%DOCFILE%"
            ],
            "command": "biber",
            "env": {},
            "name": "biber"
        }
    ]

License
-------

**Cinematic Color** has currently no license thus you are currently not free
to use it even though it is distributed on `Github <https://github.com/>`_!

About
-----

| **Cinematic Color** by Cinematic Color Authors - 2012-2019
| Copyright © 2012-2019 - Colour Developers - `ves-tech-color@googlegroups.com <ves-tech-color@googlegroups.com>`_
| `https://github.com/ves-tech/cinematiccolor <https://github.com/ves-tech/cinematiccolor>`_
