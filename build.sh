#!/bin/bash

# Exit on error
set -e

# Get the version from pyproject.toml
VERSION=$(grep -oP 'version = "\K[^"]+' pyproject.toml)
PACKAGE_NAME="shanzexpenses"
DEB_DIR="${PACKAGE_NAME}-${VERSION}"

# Clean up previous builds
rm -rf "${DEB_DIR}" build dist "${PACKAGE_NAME}.spec" "${PACKAGE_NAME}_*.deb"

# Create the package structure
mkdir -p "${DEB_DIR}/DEBIAN" \
         "${DEB_DIR}/usr/bin" \
         "${DEB_DIR}/usr/share/applications" \
         "${DEB_DIR}/usr/share/pixmaps"

# Create the control file
cat > "${DEB_DIR}/DEBIAN/control" << EOF
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Section: base
Priority: optional
Architecture: amd64
Depends: libqt5widgets5
Maintainer: Salim Ahmed <salimhabeshawi@gmail.com>
Description: A simple expense tracker application.
EOF

# Create the desktop entry file
cat > "${DEB_DIR}/usr/share/applications/${PACKAGE_NAME}.desktop" << EOF
[Desktop Entry]
Name=SHANZexpenses
Exec=/usr/bin/${PACKAGE_NAME}
Icon=/usr/share/pixmaps/shanz.png
StartupWMClass=shanzexpenses
Type=Application
Categories=Office;Finance;
EOF

# Copy the icon
cp shanz.png "${DEB_DIR}/usr/share/pixmaps/"

# Build the executable
pyinstaller --onefile --name "${PACKAGE_NAME}" --paths /home/salimhabeshawi/SHANZexpenses/.venv/lib/python3.13/site-packages main.py

# Copy the executable
cp "dist/${PACKAGE_NAME}" "${DEB_DIR}/usr/bin/"

# Build the debian package
dpkg-deb --build "${DEB_DIR}"

# Clean up
rm -rf "${DEB_DIR}" build dist "${PACKAGE_NAME}.spec"

echo "Successfully created ${PACKAGE_NAME}_${VERSION}_amd64.deb"
