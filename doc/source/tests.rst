Automatic tests
===============

Some test are automatised in the makefile. See the makefile for more details.

Before running any test, the test data should be setup by creating links to the data folder. This is done with ``make setup_testdata``, see :func:`pyal2.setup_testdata` for details.

- Some tests are fast like ``make testonepoint``
- Other are slower but deeper ``make testfull``.
- Some other tests are checking that the documentation in the code is accurate : ``make doctest``  (see `what is doctest ? <https://docs.python.org/2/library/doctest.html>`_ )


Again, see the :download:`makefile <\../../makefile>` for more details.

