# python-appimage

This project was created to facilitate the creation of an AppImage containing
a python distribution.

It ships with a custom module `appimage_venv` to facilitate the use of virtual environments.

## virtual environments

We copy a custom module called `appimage_venv` into the *stdlib* directory so it can be used in the same way as the
`venv` module. In fact, what `appimage_venv` does is wrap the creation process, calling `venv` and then laying down
some new configuration files to support the AppImage python.

```bash
python3.10.0.AppImage -m appimage_venv --prompt appimage ./venv
```
