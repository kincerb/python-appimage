# python-appimage

This project was created to facilitate the creation of an AppImage containing
a python distribution.

## Table of Contents

* [AppImage Layout / Specification](#appimage-layout-and-specification)
  + [Definitions](#definitions)
  + [Specification](#specification)
  + [Image Contents](#image-contents)
  + [AppRun File](#apprun-file)
  + [Payload Application](#payload-application)
  + [AppStream](#appstream)
  + [Update Information](#update-information)
    - [zsync](#zsync)
    - [GitHub Releases](#github-releases)
  + [Desktop Integration](#desktop-integration)
* [Creating the AppImage](#creating-the-appimage)
  + [Skeleton structure of an AppDir](#skeleton-structure-of-an-appdir)

## AppImage Layout and Specification

We're concentrating on the [Type 2 image format](https://github.com/AppImage/AppImageSpec/blob/master/draft.md#type-2-image-format),
which is the newest that I'm aware.

### Definitions

AppDir
: Application directories as described [here](http://rox.sourceforge.net/desktop/AppDirs.html)
AppImage
: File format which can be used to deploy application software to Linux-based operating systems
AppImageKit
: Reference implementation for building AppImages - [github repo](https://github.com/probonopd/AppImageKit)
.desktop file
: Desktop Entry File following the [Desktop Entry Specification](https://specifications.freedesktop.org/desktop-entry-spec/latest/)
Payload application
: Software application contained inside an AppImage
Target system(s)
: Systems where the packaged software is intended to run
zsync
: File transfer algorithm which implements efficient download of delta content

### Specification

This is not an exhaustive list, please see the link above for the full listing.

* Valid [ELF](https://en.wikipedia.org/wiki/Executable_and_Linkable_Format) executable
* Have an appended filesystem that the ELF part can mount
* When executed, mount the [AppImage](https://github.com/AppImage/AppImageSpec/blob/master/draft.md#appimage) and
execute the executable file `AppRun` contained in the root of the filesystem image
* Not rely on any specific file name extension, although `.AppImage` is recommended
  + The full naming schema recommended is `ApplicationName-$VERSION-$ARCH.AppImage`
* Should not be encapsulated in another archive/container format during download or when stored
* Work when spaces are used in its own filesystem path, file names, and in paths and filenames is uses
* May embed [update information](https://github.com/AppImage/AppImageSpec/blob/master/draft.md#update-information) in
the ELF section `.upd_info`
  + If the information in this location is not one of the known update information formats, then is should be empty
      and/or ignored
* May embed a signature in the ELF section `.sha256_sig`
  + If this exists, it **MUST** either be empty or contain a valid digital signature

### Image Contents

This section lists the contents of a filesystem image that can be created into an AppImage.
**This infers that the contents are also a valid [AppDir](https://github.com/AppImage/AppImageSpec/blob/master/draft.md#appdir)**.

* Contains a file named `AppRun` in its root directory
* Should contain a
[payload application](https://github.com/AppImage/AppImageSpec/blob/master/draft.md#payload-application)
this is executed when the AppImage is executed
* Contains exactly one `$APPNAME.desktop` file in its root directory with `$APPNAME` being the name of the payload
application
* Contains icon files in `usr/share/icons/hicolor` following the [Icon Theme Specification](https://standards.freedesktop.org/icon-theme-spec/icon-theme-spec-latest.html)
  + The icon identifier is set in the `Icon=` key of the `$APPNAME.desktop` file
  + These icon files **SHOULD** be given preference as the icon for the AppImage
  + May contain an `$APPICON.svg`, `$APPICON.svgz` or `$APPICON.png` in the root directory
  + If the icon is a PNG, should be sized one of:
    - 256x256
    - 512x512
    - 1024x1024
* Contains a `.DirIcon` file as per the [AppDir](https://github.com/AppImage/AppImageSpec/blob/master/draft.md#appdir)
specification, which should be a 256x256 PNG file

### AppRun File

* Be executable and launch the
[payload application](https://github.com/AppImage/AppImageSpec/blob/master/draft.md#payload-application)
either directly or indirectly
* Be an ELF binary or an interpreted script
  + If an ELF binary, it SHOULD have as few runtime dependencies as possible
  + If an interpreted script, it SHOULD be written in a language which an interpreter can be assumed to be available on
      every target system
* Work even when stored in a filesystem path that contains spaces
* Should pass the following through to the [payload application](https://github.com/AppImage/AppImageSpec/blob/master/draft.md#payload-application):
  + arguments
  + environment variables
* May `cd` to a directory inside the [AppImage](https://github.com/AppImage/AppImageSpec/blob/master/draft.md#appimage)
at runtime before executing the
[payload application](https://github.com/AppImage/AppImageSpec/blob/master/draft.md#payload-application),
commonly `./usr/`

### Payload Application

See the [AppRun File](#apprun-file) section on ELF binary and interpreted language guidelines.

It is **RECOMMENDED** that the
[payload application](https://github.com/AppImage/AppImageSpec/blob/master/draft.md#payload-application)
and its dependencies are located in a `$PREFIX` directory tree inside the
[AppDir](https://github.com/AppImage/AppImageSpec/blob/master/draft.md#appdir) with `$PREFIX` commonly being `./usr/`.
It's also **RECOMMENDED** that the `$PREFIX` directory tree inside the
[AppDir](https://github.com/AppImage/AppImageSpec/blob/master/draft.md#appdir) follows the
[File System Hierarchy conventions for `/usr`](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/ch04.html).

### AppStream

An AppImage should ship AppStream metadata in `/usr/share/metainfo/$ID.appdata.xml` with `$ID` being the AppStream ID.
This imformation allows the AppImage to be discoverable in application centers and/or application directory websites.

### Update Information

Update information may be embedded for exactly one transport mechanism. The two mechanisms are:

* [zsync](#zsync)
* [GitHub Releases](#github-releases)

#### zsync

The zsync transport requires a HTTP server that can hanle range requests. Its update information is in the form

```bash
zsync|https://server.domain/path/Application-latest-x86_64.AppImage.zsync
```

If an AppImage has update information embedded for this transport, then the following fields **MUST** be used;
separated by a `|`:

| Field | Type | Example | Comments |
|-------|------|---------|----------|
| Transport mechanism | String | `zsync` | zsync file and AppImage must be stored on compatible HTTP server |
| zsync file URL | String | `https://server.domain/path/Application-latest-x86_64.AppImage.zsync` | URL to `.zsync`
file (URL must not change from version to version) |

For an overview on zsync and how to create `.zsync` files, go [here](http://zsync.moria.org.uk/).

#### GitHub Releases

The GitHub Releases transport extends the zsync transport in the is uses version infromation from GitHub Releases.
Its update information is in the form:

```bash
gh-releases-zsync|kincerb|AppImages|latest|Python-*x86_64.AppImage.zsync
```

If an AppImage has update information embedded for this transport, then the following fields **MUST** be used;
separated by a `|`:

| Field | Type | Example | Comments |
|-------|------|---------|----------|
| Transport mechanism | String | `gh-releases-zsync` | zsync file and AppImage must be stored on on GitHub Releases |
| GitHub username | String | `kincerb` | Name of GH user or organization where zsync file and AppImage are stored |
| GitHub repository | String | `AppImages` | Name of GH repository in which the zsync file and AppImage are stored |
| Release name | String | `latest` | Name of release, `latest` will automatically use the latest release as determined
by the GitHub API |
| Filename | String | `Python-*x86_64.AppImage.zsync` | Filename of zsync file on GutHub, `*` is a wildcard |

### Desktop Integration

More to come, see [upstream documentation](https://github.com/AppImage/AppImageSpec/blob/master/draft.md#desktop-integration)
for more information.

## Creating the AppImage

An AppImage is created from an **AppDir**, which is the root of your package.
You treat the **AppDir** like a [chroot](https://wiki.archlinux.org/title/chroot)
in a way. Any binaries and libraries that your program can't rely upon the host
OS, must be packaged inside the **AppDir**.

### Skeleton structure of an AppDir

## Build skeleton AppDir

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
--library=/lib64/libcurses.so \
--library=/lib64/libcursesw.so \
--appdir=AppDir \
--icon-file=resources/python-logo-flattened.png \
--desktop-file=resources/net.nwie.python.desktop \
--output=appimage
```

## Links

### Documentation

* [AppImage Docs - Using the Open Build Service](https://docs.appimage.org/packaging-guide/hosted-services/opensuse-build-service.html#using-the-open-build-service)
* [AppImageKit - Reference Implementation](https://docs.appimage.org/introduction/software-overview.html#ref-appimagekit)

### Tools

* [appimage-builder - APT only](https://appimage-builder.readthedocs.io/en/latest/index.html)
* [AppImageKit GitHub](https://github.com/AppImage/AppImageKit)

