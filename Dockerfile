FROM centos
MAINTAINER Shawn Siefkas <shawn@siefk.as>

RUN yum -y localinstall http://mirror.rit.edu/epel/6/x86_64/epel-release-6-8.noarch.rpm
RUN yum -y install rpmdevtools yum-utils
RUN rpmdev-setuptree

ADD python-docker-rpmbuild.spec /rpmbuild/SPECS/
RUN chown root:root /rpmbuild/SPECS/python-docker-rpmbuild.spec
RUN yum-builddep -y /rpmbuild/SPECS/python-docker-rpmbuild.spec
ADD . /tmp/sources
RUN chown -R root:root /tmp/sources
RUN tar -C /tmp/sources -czvf /rpmbuild/SOURCES/python-docker-rpmbuild-0.0.1.tar.gz --exclude .git .
