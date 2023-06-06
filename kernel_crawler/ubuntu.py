from . import deb
from . import repo
from .debian import fixup_deb_arch
import re

class UbuntuMirror(repo.Distro):
    def __init__(self, arch):
        arch = fixup_deb_arch(arch)
        mirrors = [
            deb.DebMirror('http://mirrors.edge.kernel.org/ubuntu/', arch),
            deb.DebMirror('http://security.ubuntu.com/ubuntu/', arch),
            deb.DebMirror('http://ports.ubuntu.com/ubuntu-ports/', arch),
        ]
        super(UbuntuMirror, self).__init__(mirrors, arch)

    def to_driverkit_config(self, release, deps):
        dk_configs = {}
        krel, kver = release.split("/")
        for dep in deps:
            if 'headers' in dep:

                # set a default flavor
                flavor = 'generic'
                # capture the flavor from the string after 'linux-' in the url subdir
                # example: http://security.ubuntu.com/ubuntu/pool/main/l/linux-oracle/linux-headers-4.15.0-1087-oracle_4.15.0-1087.95_amd64.deb
                flavor_capture = re.search(r"^.*l/linux-(.+)/.*$", dep)

                # if capture was successful, set the flavor
                if flavor_capture is not None:
                    flavor = flavor_capture.group(1)  # set flavor to the first capture group

                target = 'ubuntu'
                release = f'{krel}-{flavor}'  # add flavor to release

                val = dk_configs.get(target)
                if val is None:
                    headers = [dep]
                    dk_configs[target] = repo.DriverKitConfig(release, target, headers, kver)
                else:
                    # If already existent, just add the new url to the list of headers
                    val.headers.append(dep)
                    dk_configs[target] = val
        return dk_configs.values()
