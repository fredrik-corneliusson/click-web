=======================
Contribution guidelines
=======================


Running tests
=============

Install development dependencies::

   pip install -e .[dev]

Running tests and code linting::

  ./check

Creating a release
==================

* Checkout the ``master`` branch.
* Pull the latest changes from ``origin``.
* Increment the version number (in setup.py).
* If needed update the ``AUTHORS.rst`` file with new contributors.
* Run ./check.sh to verify that all unittests and code checks pass.
* Commit everything and make sure the working tree is clean.
* Push everything to github::

     git push origin master

* Build release::

    python setup.py sdist bdist_wheel

* Tag the release::

    git tag -a "v$(python setup.py --version)" -m "$(python setup.py --name) release version $(python setup.py --version)"

* Push everything to github::

    git push --tags origin master

* Publish on test.pypi::

    twine upload --repository-url https://test.pypi.org/legacy/ dist/* -u fredrik-corneliusson -p 'some_secret_password'

* Verify release looks ok at `test.pypi <https://test.pypi.org/search/?q=click-web>`_

* Install package from test.pypi in a clean virtual env and verify that it works::

    pip install --extra-index-url https://test.pypi.org/simple/ click-web --upgrade

* Deploy release to production pypi::

    twine upload dist/* -u fredrik-corneliusson -p 'some_secret_password'

* Verify release on `production pypi <https://pypi.org/search/?q=click-web>`_::

    pip install click-web --upgrade

