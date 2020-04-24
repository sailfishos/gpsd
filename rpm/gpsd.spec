Name:           gpsd
Version:        3.19
Release:        0
Summary:        Service daemon for mediating access to a GPS
License:        BSD-3-Clause
Url:            http://www.catb.org/gpsd/
Source0:        %{name}-%{version}.tar.gz
Source1:        gpsd.service
BuildRequires:  chrpath
BuildRequires:  fdupes
BuildRequires:  libcap-devel
BuildRequires:  ncurses-devel
BuildRequires:  pkgconfig
BuildRequires:  scons
BuildRequires:  dbus-devel dbus-glib-devel
BuildRequires:  pkgconfig(libusb-1.0)
BuildRequires:  pkgconfig(udev)
Requires:       udev

%description
gpsd is a service daemon that mediates access to a GPS sensor connected
to the host computer by serial or USB interface, making its data on the
location/course/velocity of the sensor available to be queried on TCP
port 2947 of the host computer.  With gpsd, multiple GPS client
applications (such as navigational and wardriving software) can share
access to a GPS without contention or loss of data.  Also, gpsd
responds to queries with a format that is substantially easier to parse
than NMEA 0183.  A client library is provided for applications.

After installing this RPM, gpsd will automatically connect to USB GPSes
when they are plugged in and requires no configuration.  For serial
GPSes, you will need to start gpsd by hand.  Once connected, the daemon
automatically discovers the correct baudrate, stop bits, and protocol.
The daemon will be quiescent when there are no clients asking for
location information, and copes gracefully when the GPS is unplugged
and replugged.

%package -n libgps
Summary:        Shared library for GPS applications

%description -n libgps
This package provides the shared library for gpsd and other GPS aware
applications.

%package -n libgps-devel
Summary:        Shared library for GPS applications development files
Requires:       libgps = %{version}

%description -n libgps-devel
This package provides the development files for gpsd and other GPS aware
applications.

%package clients
Summary:        Clients for gpsd

%description clients
gpsdmon is a simple test client for gpsd. It displays current
GPS position/time/velocity information and (for GPSes that
support the feature) the locations of accessible satellites.

%prep
%autosetup -n %{name}-%{version}/upstream

%build
scons %{_smp_mflags}          	\
    prefix=/                  	\
    bindir=%{_bindir}         	\
    includedir=%{_includedir} 	\
    libdir=%{_libdir}         	\
    sbindir=%{_sbindir}       	\
    mandir=%{_mandir}         	\
    docdir=%{_docdir}         	\
    dbus_export=yes            	\
    systemd=yes 		\
    debug=yes 			\
    leapfetch=no 		\
    pkgconfigdir=%{_libdir}/pkgconfig

# Fix python interpreter path.
sed -e "s,#!/usr/bin/\(python[23]\?\|env \+python[23]\?\),#!/usr/bin/python3,g" -i \
    gegps gpscat gpsfake xgps xgpsspeed gpsprof gps/*.py ubxtool zerk

%install
rm -rf $RPM_BUILD_ROOT
export DESTDIR=$RPM_BUILD_ROOT
scons install

mkdir -p %{buildroot}/lib/systemd/system/multi-user.target.wants/

install -D -m 644 %{SOURCE1} %{buildroot}/lib/systemd/system/gpsd.service
ln -s ../gpsd.service %{buildroot}/lib/systemd/system/multi-user.target.wants/gpsd.service

%post -n libgps -p /sbin/ldconfig
%postun -n libgps -p /sbin/ldconfig

%post
%systemd_post gpsd.service gpsd.socket

%preun
%systemd_preun gpsd.service gpsd.socket

%postun
# Don't restart the service
%systemd_postun gpsd.service gpsd.socket

%files
/lib/systemd/system/gpsd.service
/lib/systemd/system/multi-user.target.wants/gpsd.service
%{_sbindir}/gpsd
%{_sbindir}/gpsdctl

%files -n libgps
%{_libdir}/libgps.so.*

%files -n libgps-devel
%{_includedir}/gps.h
%{_includedir}/libgpsmm.h
%{_libdir}/libgps.so
%{_libdir}/pkgconfig/libgps.pc

%files clients
%{_bindir}/gpsdecode
%{_bindir}/cgps
%{_bindir}/gegps
%{_bindir}/ubxtool
%{_bindir}/zerk
%{_bindir}/gpsfake
%{_bindir}/gpscat
%{_bindir}/gpsprof
%{_bindir}/gps2udp
%{_bindir}/gpsctl
%{_bindir}/gpsmon
%{_bindir}/gpspipe
%{_bindir}/gpsrinex
%{_bindir}/gpxlogger
%{_bindir}/lcdgps
%{_bindir}/ntpshmmon
%{_bindir}/ppscheck
