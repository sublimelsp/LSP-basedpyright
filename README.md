# LSP-basedpyright

Python support for Sublime's LSP plugin provided through [DetachHead/basedpyright](https://github.com/DetachHead/basedpyright),
which basically includes all [Pyright][ms-marketplace-pyright] features and some exclusive [Pylance][ms-marketplace-pylance] features such as semantic highlighting and inlay hints.

## Installation

1. Install [LSP](https://packagecontrol.io/packages/LSP) and [LSP-basedpyright](https://packagecontrol.io/packages/LSP-basedpyright) via Package Control.
2. (Optional but recommended) Install the [LSP-file-watcher-chokidar](https://github.com/sublimelsp/LSP-file-watcher-chokidar) via Package Control to enable functionality to notify the server about new files.
3. Restart Sublime.
4. (Optional) Configure basedpyright for your `virtualenv`.

> The [Node.js](https://nodejs.org) is required by this server. If `node` is not in your `$PATH`, this package will suggest to install a local Node.js runtime automatically. If you instead decide to use `node` that is already installed on your system, make sure that it's at least a version 14.

## Configuration

> **TIP**: It's recommended to additionally install the `LSP-json` package which provides validation and auto-complete for `LSP-basedpyright` settings and the `pyrightconfig.json` configuration file.

Here are some ways to configure the package and the language server.

- From `Preferences > Package Settings > LSP > Servers > LSP-basedpyright`
- From the command palette `Preferences: LSP-basedpyright Settings`
- Project-specific configuration
  From the command palette run `Project: Edit Project` and add your settings in:

  ```js
  {
     "settings": {
        "LSP": {
           "LSP-basedpyright": {
              "settings": {
                 // Put your settings here
              }
           }
        }
     }
  }
  ```

- Various options can only be configured through a `pyrightconfig.json` configuration file (check [basedpyright configuration](https://github.com/microsoft/basedpyright/blob/main/docs/configuration.md) for more info)

### Provided Command Palette commands

| Command | Description |
|---------|-------------|
| `LSP-basedpyright: Create Basedpyright Configuration File` | Creates a `pyrightconfig.json` file in the root of the project with basic options. Opens the configuration file if it already exists. |

### Virtual environments

The plugin attempts to resolve the virtual environment automatically from well-known environment variables and workspace files.
This behavior can be disabled by explicitly setting the python interpreter in the `python.pythonPath` setting.

If you want to overwrite the virtual environment, the `pyrightconfig.json` file must be present at the root of your project.

This configuration file, at a minimum, should define where your Python virtualenvs are located, as well as the name of the one to use for your project:

```json
{
    "venvPath": "/path/to/virtualenvs/",
    "venv": "myenv"
}
```

For example, if you have created a virtual environment inside the directory `.venv` within the project directory then you would use:

```json
{
    "venvPath": ".",
    "venv": ".venv"
}
```

Note that the `venv` option is only supported in the `pyrightconfig.json` file. The `venvPath` option can also be specified in your .sublime-project, in case you don't want to hard-code a system-specific path in a shared project.

[ms-marketplace-pyright]: https://marketplace.visualstudio.com/items?itemName=ms-pyright.pyright
[ms-marketplace-pylance]: https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance
