# Maze-Router

## Setting up dev environment


### Making the pre-commit hook executable

Make sure the pre-commit hook is executable by the system
[Check why a pre-commit hook is needed](#pre-commit)

```bash
chmod +x ./.git/hooks/pre-commit
```
> or the equivalent to your system

### Python Virtual Environment
Use python `Python3.10` and above

#### Set up a virtual environemnt for Python at the root of the project
```bash
python -m venv ./venv
```

>[!IMPORTANT]
> Do not rename your venv,
> If you really really need to rename it, add it to the `.gitignore` template

---

#### Source the virtual env to your shell:

**For POSIX complaint Shells:**

to check your current Shell
```bash
echo $0
```
The output will be your shell

Now source your shell according to the required activate script,
refer to [Python Docs on venv](https://docs.python.org/3/library/venv.html) if you cant source your shell.

For bash OR zsh
```bash
source ./venv/bin/activate
```

At the project root install project requirements:
```bash
pip install -r requirements.txt
```

### Visualizer Setup
Currently `vispy` does not query on correct OpenGL version when wayland, nvidia and certain Qt versions are invovled
see [issue 2640 on vispy](https://github.com/vispy/vispy/issues/2640)

**if** you encounter any problems run the visualizer on an xorg session, **or** set the following environment variable:
```bash
export QT_QPA_PLATFORM=xcb
```

---
## Installing or Removing Libraries **(Important)**

Any Libraries you add or remove from the project must be reflected in the `requirements.txt` to avoid errors so we standardize installation of libraries to automatically reflect in `requirements.txt`

To **install** a library use:
```bash
pip install library_to_install && rm requirements.txt && pip freeze > requirements.txt
```

To **remove** a library use:
```bash
pip uninstall library_to_install && rn requirements.txt && pip freeze > requirements.txt
```

To update the `requirements.txt` at any time use:
```bash
rm requirements.txt && python -m pip freeze > requirements.txt
```

Or the equivalent functionality of above commands according to your shell/environment

<a name="pre-commit">
</a>

>[!WARNING]
> Not updating your `requirements.txt` will abort the commit:
> This is done by the pre-commit hook in `.git/hooks/pre-commit`
