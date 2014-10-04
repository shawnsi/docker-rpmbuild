docker-rpmbuild's documentation
===============================

Builds RPMs inside a docker container. A :doc:`Dockerfile </dockerfile>` and
build context are dynamically generated to construct the RPM development
environment. Then ``rpmbuild -ba`` is executed and the RPM results are extracted.

Site Documentation
==================

.. toctree::
   :maxdepth: 2
    
   installation
   getting-started
   run-arguments
   configuration-files
   dockerfile
