%define __jar_repack %{nil}

%global username cassandra

%define relname %{name}-%{version}-%{release}

Name:           apache-cassandra
Version:        1.0.8
Release:        1%{?dist}
Summary:        Cassandra is a highly scalable, eventually consistent, distributed, structured key-value store.

Group:          Development/Libraries
License:        Apache Software License
URL:            http://cassandra.apache.org/
Source0:        http://www.ibiblio.org/pub/mirrors/apache/%{username}/%{version}/%{name}-%{version}-src.tar.gz
Source1:        cassandra-env.sh
Source2:        cassandra.yaml
BuildRoot:      %{_tmppath}/%{relname}-root-%(%{__id_u} -n)

BuildRequires: java-devel
BuildRequires: jpackage-utils
BuildRequires: ant
BuildRequires: ant-nodeps

Conflicts:     cassandra
Obsoletes:     cassandra07

Requires:      java >= 1.6.0
Requires:      jna  >= 3.2.7
Requires:      jpackage-utils
Requires(pre): user(cassandra)
Requires(pre): group(cassandra)
Requires(pre): shadow-utils
Requires(post):   /sbin/chkconfig
Requires(preun):  /sbin/service, /sbin/chkconfig
Requires(postun): /sbin/service
Provides:      user(cassandra)
Provides:      group(cassandra)

BuildArch:      noarch

%description
Cassandra brings together the distributed systems technologies from Dynamo
and the data model from Google's BigTable. Like Dynamo, Cassandra is
eventually consistent. Like BigTable, Cassandra provides a ColumnFamily-based
data model richer than typical key/value systems.

For more information see http://cassandra.apache.org/

%prep
%setup -q -n %{name}-%{version}-src

%build
ant clean jar -Drelease=true

%install
%{__rm} -rf %{buildroot}
mkdir -p %{buildroot}%{_sysconfdir}/%{username}/
mkdir -p %{buildroot}/usr/share/%{username}
mkdir -p %{buildroot}/usr/share/%{username}/lib
mkdir -p %{buildroot}/usr/share/%{username}/default.conf
mkdir -p %{buildroot}/etc/%{username}/default.conf
mkdir -p %{buildroot}/etc/rc.d/init.d/
mkdir -p %{buildroot}/etc/security/limits.d/
mkdir -p %{buildroot}/etc/default/
mkdir -p %{buildroot}/usr/sbin
mkdir -p %{buildroot}/usr/bin
cp -p conf/* %{buildroot}/etc/%{username}/default.conf
cp -p conf/* %{buildroot}/usr/share/%{username}/default.conf
cp -p redhat/%{username} %{buildroot}/etc/rc.d/init.d/
cp -p redhat/%{username}.conf %{buildroot}/etc/security/limits.d/
cp -p redhat/default %{buildroot}/etc/default/%{username}
cp -p lib/*.jar %{buildroot}/usr/share/%{username}/lib
mv redhat/cassandra.in.sh %{buildroot}/usr/share/%{username}
rm bin/cassandra.in.sh
mv bin/cassandra %{buildroot}/usr/sbin
rm bin/*.bat 
cp -p bin/* %{buildroot}/usr/bin
# replace default config files
mv %{buildroot}/etc/%{username}/default.conf/cassandra-env.sh %{buildroot}/etc/%{username}/default.conf/cassandra-env.sh.orig
mv %{buildroot}/etc/%{username}/default.conf/cassandra.yaml %{buildroot}/etc/%{username}/default.conf/cassandra.yaml.orig
cp -p %{SOURCE1} %{buildroot}/etc/%{username}/default.conf/
cp -p %{SOURCE2} %{buildroot}/etc/%{username}/default.conf/
# Handle the case of interim SNAPHOST builds
cp build/%{name}*-%{version}.jar %{buildroot}/usr/share/%{username}/lib
mkdir -p %{buildroot}/var/lib/%{username}/commitlog
mkdir -p %{buildroot}/var/lib/%{username}/data
mkdir -p %{buildroot}/var/lib/%{username}/saved_caches
mkdir -p %{buildroot}/var/run/%{username}
mkdir -p %{buildroot}/var/log/%{username}

%clean
%{__rm} -rf %{buildroot}

%pre
getent group %{username} >/dev/null || groupadd -r %{username}
getent passwd %{username} >/dev/null || \
useradd -d /usr/share/%{username} -g %{username} -M -r %{username}
exit 0

%preun
# only delete user on removal, not upgrade
if [ "$1" = "0" ]; then
    userdel %{username}
    /sbin/service cassandra stop &>/dev/null || :
    /sbin/chkconfig --del cassandra
fi

%files
%defattr(-,root,root,0755)
%doc CHANGES.txt LICENSE.txt README.txt NEWS.txt NOTICE.txt
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_sbindir}/cassandra
%attr(755,root,root) /etc/rc.d/init.d/%{username}
%attr(755,root,root) /etc/default/%{username}
%attr(755,root,root) /etc/security/limits.d/%{username}.conf
%attr(755,%{username},%{username}) /usr/share/%{username}*
%attr(755,%{username},%{username}) %config(noreplace) /%{_sysconfdir}/%{username}
%attr(755,%{username},%{username}) %config(noreplace) /var/lib/%{username}/*
%attr(755,%{username},%{username}) /var/log/%{username}*
%attr(755,%{username},%{username}) /var/run/%{username}*
# overwritting default config files
%attr(644,%{username},%{username}) /etc/%{username}/default.conf/*

%post
/sbin/chkconfig --add cassandra
alternatives --install /etc/%{username}/conf %{username} /etc/%{username}/default.conf/ 0
exit 0

%postun
# only delete alternative on removal, not upgrade
if [ "$1" = "0" ]; then
    alternatives --remove %{username} /etc/%{username}/default.conf/
fi
exit 0

%changelog
* Tue Aug 03 2010 Nick Bailey <nicholas.bailey@rackpace.com> - 0.7.0-1
- Updated to make configuration easier and changed package name.
* Mon Jul 05 2010 Peter Halliday <phalliday@excelsiorsystems.net> - 0.6.3-1
- Initial package
