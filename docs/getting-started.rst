Getting Started
===============

Build from SPEC
---------------
Build a simple spec file and source archive using rpmbuild in a docker image.

.. code-block:: bash

	$ docker-rpmbuild build --spec <path-to-spec> --source <path-to-source> <image>

Build from SRPM
---------------
Rebuild an existing SRPM package

.. code-block:: bash

	$ docker-rpmbuild rebuild --srpm <path-to-srpm> <image>


