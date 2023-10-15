# Maintainer: gardenapple <mailbox@appl.garden>
# Contributor: Andrew Clunis <andrew@orospakr.ca>
# Contributor: Ben R <thebenj88@gmail.com>
# Contributor: Loïc Bidoux <loic.bidoux@owndata.org>

pkgname=vrms-arch-git
_pkgname=vrms-arch
pkgver=2.0.1.r3.g79316e8
pkgrel=1
pkgdesc="Virtual Richard M. Stallman for Arch Linux (gardenapple's fork)"
arch=('any')
url="https://github.com/gardenappl/${_pkgname}"
license=('custom:BSD3')
makedepends=('git' 'python-build' 'python-installer' 'python-wheel')
depends=('python' 'pyalpm')
source=("git+https://github.com/gardenappl/${_pkgname}.git")
sha256sums=('SKIP')

pkgver() {
	git describe --long --tags | sed -E 's/([^-]*-g)/r\1/;s/-/./g;s/v*//'
}

build() {
	cd ..
	python -m build --wheel --no-isolation
}

package() {
	cd ..
	python -m installer --destdir="$pkgdir" dist/*.whl
	install -Dm 644 LICENSE.md "${pkgdir}/usr/share/licenses/${_pkgname}/LICENSE"
}

