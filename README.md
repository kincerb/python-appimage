# python-appimage

This project was created to facilitate the creation of an AppImage containing
a python distribution.

## Table of Contents

- [Creating the AppImage](#creating-the-appimage)
  - [Skeleton structure of an AppDir](#skeleton-structure-of-an-appdir)

## Creating the AppImage

An AppImage is created from an **AppDir**, which is the root of your package.
You treat the **AppDir** like a [chroot](https://wiki.archlinux.org/title/chroot)
in a way. Any binaries and libraries that your program can't rely upon the host
OS, must be packaged inside the **AppDir**.

### Skeleton structure of an AppDir

```bash
mkdir -p AppDir/{src,usr}
```

### Compile newer libraries for openssl and sqlite if needed (optional)

Extract the source code into the `AppDir/src` directory. When using `cmake`,
you ***must*** use the `DESTDIR` variable to set where you want
the libraries installed.

### sqlite

```bash
cd AppDir/src
wget https://www.sqlite.org/2021/sqlite-autoconf-3350100.tar.gz
tar -xzf sqlite-autoconf-3350100.tar.gz 
cd sqlite-autoconf-3350100
./configure --prefix=/usr/local/sqlite3
make -j$(nproc)
# sqlite doesn't support relative paths
make install DESTDIR=/home/kincerb/AppDir/
# not sure if this is needed, but install says to run this
libtool --finish ../../usr/local/sqlite3
```

### openssl

```bash
cd AppDir/src
wget https://artfiles.org/openssl.org/source/openssl-1.1.1k.tar.gz
tar -xzf openssl-1.1.1k.tar.gz 
cd openssl-1.1.1k
./config no-shared -fPIC --prefix=/usr/local/ssl --openssldir=/usr/local/ssl
make -j$(nproc)
make install DESTDIR=../../
```

:stop_sign: Be sure to make all the libraries readable by everyone or else
linking python against them will fail.

```bash
find AppDir/usr/local -type d -exec chmod o+rx {} \;
find AppDir/usr/local -type f -exec chmod o+r {} \;
```

## Compile and install desired python version into AppDir

You can use the tags created for each release to build the specific version
of python you want to ship.

### install build dependencies

```bash
sudo yum -y install yum-utils
sudo yum-builddep python3
```

### clone source code repo and checkout the tagged release

```bash
cd AppDir/src
git clone https://github.com/python/cpython.git
cd cpython
```

There are a lot of tags, so you may want to use the `-l` flag with `git tag` to
list by a pattern.

```bash
git tag -l v3.9*
```

Let's build *v3.9.6*.

```bash
git checkout v3.9.6
```

### set environment variables to control library search paths (if needed)

```bash
export LDFLAGS="-Wl,-rpath=../../usr/local/sqlite3/lib,-rpath=../../usr/local/ssl/lib"
export CPPFLAGS="-I../../usr/local/sqlite3/include -I../../usr/local/ssl/include"
```

You can also specify these variables along with the `configure` script,
but that gets very unwieldy.

```bash
./configure --with-pydebug LDFLAGS="-Wl,-rpath=../../usr/local/ssl/lib"
```

### configure and compile python with cmake

```bash
./configure --with-pydebug --enable-loadable-sqlite-extensions --with-openssl=../../usr/local/ssl
make -j$(nproc)
make install DESTDIR=../../
```

## Add required files for building an AppImage

AppImage is very much geared to desktop applications, but supports CLI
based applications as well. At the very least, you need these files to
create your AppImage.

| File | Description |
|------|-------------|
| [AppRun](./resources/AppRun) | Bootstraps environment and runs desired executable. |
| [desktop entry](./resources/io.nucoder.python.desktop) | Desktop file to create Application entry. |
| [python-logo-flattened.png](./resources/python-logo-flattened.png) | Icon to use for Application entry. |

## Get latest linuxdeploy AppImage

```bash
wget https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
chmod a+x linuxdeploy-x86_64.AppImage
```

## Building the AppImage

```bash
ARCH=x86_64 linuxdeploy-x86_64.AppImage \
--library=/lib64/libreadline.so \
--library=/lib64/libhistory.so \
--appdir=AppDir \
--icon-file=resources/python-logo-flattened.png \
--desktop-file=resources/net.nwie.python.desktop \
--output=appimage
```

## Links

### Documentation

- [AppImage Docs - Using the Open Build Service](https://docs.appimage.org/packaging-guide/hosted-services/opensuse-build-service.html#using-the-open-build-service)
- [AppImageKit - Reference Implementation](https://docs.appimage.org/introduction/software-overview.html#ref-appimagekit)

### Tools

- [appimage-builder - APT only](https://appimage-builder.readthedocs.io/en/latest/index.html)
- [AppImageKit GitHub](https://github.com/AppImage/AppImageKit)
