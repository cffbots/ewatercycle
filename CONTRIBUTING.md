# Contributing guidelines

We welcome any kind of contributions to our software, from simple
comment or question to a full fledged [pull
request](https://help.github.com/articles/about-pull-requests/). Please
read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

A contribution can be one of the following cases:

1. you have a question;
2. you think you may have found a bug (including unexpected behavior);
3. you want to make some kind of change to the code base (e.g. to fix a
    bug, to add a new feature, to update documentation).
4. you want to make a release

The sections below outline the steps in each case.

## You have a question

1. use the search functionality
    [here](https://github.com/eWaterCycle/ewatercycle/issues) to see if
    someone already filed the same issue;
2. if your issue search did not yield any relevant results, make a new
    issue;
3. apply the \"Question\" label; apply other labels when relevant.

## You think you may have found a bug

1. use the search functionality
    [here](https://github.com/eWaterCycle/ewatercycle/issues) to see if
    someone already filed the same issue;
2. if your issue search did not yield any relevant results, make a new
    issue, making sure to provide enough information to the rest of the
    community to understand the cause and context of the problem.
    Depending on the issue, you may want to include: - the [SHA
    hashcode](https://help.github.com/articles/autolinked-references-and-urls/#commit-shas)
    of the commit that is causing your problem; - some identifying
    information (name and version number) for dependencies you\'re
    using; - information about the operating system;
3. apply relevant labels to the newly created issue.

## You want to make some kind of change to the code base

1. (**important**) announce your plan to the rest of the community
    *before you start working*. This announcement should be in the form
    of a (new) issue;
2. (**important**) wait until some kind of consensus is reached about
    your idea being a good idea;
3. if needed, fork the repository to your own Github profile and create
    your own feature branch off of the latest main commit. While working
    on your feature branch, make sure to stay up to date with the main
    branch by pulling in changes, possibly from the \'upstream\'
    repository (follow the instructions
    [here](https://help.github.com/articles/configuring-a-remote-for-a-fork/)
    and [here](https://help.github.com/articles/syncing-a-fork/));
4. install the package in editable mode and its dependencies with
    `pip3 install -e .[dev]`;
4. make sure pre commit hook is installed by running `pre-commit install`, causes linting and formatting to be applied during commit;
5. make sure the existing tests still work by running `pytest`;
6. make sure the existing documentation can still by generated without
    warnings by running `cd docs && make html`. [Pandoc](https://pandoc.org/) is required to generate docs, it can be installed with ``conda install -c conda-forge pandoc`` ;
7. add your own tests (if necessary);
8. update or expand the documentation; Please add [Google Style Python
    docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).
9. [push](http://rogerdudler.github.io/git-guide/) your feature branch
    to (your fork of) the ewatercycle repository on GitHub;
10. create the pull request, e.g. following the instructions
    [here](https://help.github.com/articles/creating-a-pull-request/).

In case you feel like you\'ve made a valuable contribution, but you
don\'t know how to write or run tests for it, or how to generate the
documentation: don\'t let this discourage you from making the pull
request; we can help you! Just go ahead and submit the pull request, but
keep in mind that you might be asked to append additional commits to
your pull request.

## You want to make a release

This section is for maintainers of the package.

1. Checkout ``HEAD`` of ``main`` branch with ``git checkout main`` and ``git pull``.
2. Determine what new version (major, minor or patch) to use. Package uses `semantic versioning <https://semver.org>`_.
3. Run ``bump2version <major|minor|patch>`` to update version in package files.
4. Update CHANGELOG.md with changes between current and new version.
5. Make sure pre-commit hooks are green for all files by running ``pre-commit run --all-files``.
6. Commit & push changes to GitHub.
7. Wait for [GitHub
    actions](https://github.com/eWaterCycle/ewatercycle/actions?query=branch%3Amain+)
    to be completed and green.

8. Create a [GitHub release](https://github.com/eWaterCycle/ewatercycle/releases/new)

    - Use version as title and tag version.
    - As description use intro text from README.md (to give context to
        Zenodo record) and changes from CHANGELOG.md

9. Create a PyPI release.

    1. Create distribution archives with `python3 -m build`.
    2. Upload archives to PyPI with `twine upload dist/*` (use your
        personal PyPI account).

10. Verify

    1. Has [new Zenodo
        record](https://zenodo.org/search?page=1&size=20&q=ewatercycle)
        been created?
    2. Has [stable
        ReadTheDocs](https://ewatercycle.readthedocs.io/en/stable/) been
        updated?
    3. Can new version be installed with pip using
        `pip3 install ewatercycle==<new version>`?

11. Celebrate
