%global sb_commit d8887bc8ce14a47d5b9d45f6697f05d53e43fe9a
%global sb_cert surface.cer
%global sb_password surface
%global sb_cert_dir /usr/share/surface-secureboot

Name:       surface-secureboot
Version:    20211103
Release:    1%{?dist}
Summary:    The secureboot certificate for linux-surface

License:    proprietary
BuildArch:  noarch
URL:        https://github.com/linux-surface/linux-surface
Source:     %{url}/raw/%{sb_commit}/pkg/keys/%{sb_cert}

Requires:   mokutil

%description
This package installs the secureboot certificate that is used to sign the
kernel from the linux-surface kernel package. When you reboot for the first
time, it will ask you to enroll the MOK certificate. Please check if the key
is correct, and then confirm the import by entering "%{sb_password}".

%prep
%setup -q -c -T

%install
rm -rf %{buildroot}
install -dm 755 %{buildroot}%{sb_cert_dir}
install -pm 644 %{SOURCE0} %{buildroot}%{sb_cert_dir}

%pre

# Upgrading
if [ "$1" = "2" ]; then
	cp %{sb_cert_dir}/%{sb_cert} %{sb_cert_dir}/%{sb_cert}.bak
fi

%post

# First installation
if [ ! -f "%{sb_cert_dir}/%{sb_cert}.bak" ]; then
	echo ""
	echo "The secure-boot certificate has been installed to:"
	echo ""
	echo "    %{sb_cert_dir}/%{sb_cert}"
	echo ""
	echo "It will now be automatically enrolled for you and guarded with the password:"
	echo ""
	echo "    %{sb_password}"
	echo ""

	HASHFILE=$(mktemp)
	mokutil --generate-hash=%{sb_password} > $HASHFILE
	mokutil --hash-file $HASHFILE --import %{sb_cert_dir}/%{sb_cert}

	echo "To finish the enrollment process you need to reboot, where you will then be"
	echo "asked to enroll the certificate. During the import, you will be prompted for"
	echo "the password mentioned above. Please make sure that you are indeed adding"
	echo "the right key and confirm by entering '%{sb_password}'."
	echo ""
	echo "Note that you can always manage your secure-boot keys, including the one"
	echo "just enrolled, from inside Linux via the 'mokutil' tool."
	echo ""
elif ! cmp --silent %{sb_cert_dir}/%{sb_cert} %{sb_cert_dir}/%{sb_cert}.bak; then
	echo ""
	echo "Updating secure boot certificate. The old key will be revoked and a new key"
	echo "will be installed. You will need to reboot your system, where you will then"
	echo "be asked to delete the old and import the new key. In both cases, make sure"
	echo "this is the right key and confirm with the password '%{sb_password}'."
	echo ""

	HASHFILE=$(mktemp)
	mokutil --generate-hash=%{sb_password} > $HASHFILE
	mokutil --hash-file $HASHFILE --delete %{sb_cert_dir}/%{sb_cert}.bak
	mokutil --hash-file $HASHFILE --import %{sb_cert_dir}/%{sb_cert}
	rm -f %{sb_cert_dir}/%{sb_cert}.bak
else
	rm -f %{sb_cert_dir}/%{sb_cert}.bak
fi

%preun

# Last version is being removed
if [ "$1" = "0" ]; then
	echo ""
	echo "The following secure-boot certificate will be uninstalled and revoked from:"
	echo "your system"
	echo ""
	echo "	%{sb_cert_dir}/%{sb_cert}"
	echo ""

	HASHFILE=$(mktemp)
	mokutil --generate-hash=%{sb_password} > $HASHFILE
	mokutil --hash-file $HASHFILE --delete %{sb_cert_dir}/%{sb_cert}

	echo "The key will be revoked on the next start of your system. You will then"
	echo "again asked for the password. Enter '%{sb_password}' to confirm."
	echo ""
	echo "Kernels signed with the corresponding private key will still not be allowed"
	echo "to boot after this. Note that you can always manage your secure-boot keys"
	echo "via the 'mokutil' tool. Please refer to 'man mokutil' for more information."
	echo ""
fi


%files
%{sb_cert_dir}/%{sb_cert}

%changelog
* Wed Nov 03 2021 Dorian Stoll <dorian.stoll@tmsp.io> - 20211103-1
- Bump release to build for Fedora 35

* Fri Mar 19 2021 Dorian Stoll <dorian.stoll@tmsp.io> - 20210319-1
- Bump release to build for Fedora 34

* Tue Sep 29 2020 Dorian Stoll <dorian.stoll@tmsp.io> - 20200929-1
- Bump release to build for Fedora 33

* Thu Apr 02 2020 Dorian Stoll <dorian.stoll@tmsp.io> 20200402-1
- Bump package version to align across distributions

* Tue Mar 31 2020 Dorian Stoll <dorian.stoll@tmsp.io> 20200202-2
- Bump pkgrel

* Sun Feb 02 2020 Dorian Stoll <dorian.stoll@tmsp.io>
- Initial version
