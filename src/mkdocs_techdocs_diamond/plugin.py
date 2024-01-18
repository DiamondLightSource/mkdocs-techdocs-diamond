import os
import tempfile
from copy import copy
from importlib.resources import files

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin


class TechdocsDiamond(BasePlugin):
    def __init__(self):
        self.tmp_dir_techdocs_theme = tempfile.TemporaryDirectory()

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        with open(
            os.path.join(self.tmp_dir_techdocs_theme.name, "techdocs_metadata.json"),
            "w+",
        ) as fp:
            fp.write(
                '{{ {"site_name": (config.site_name | string ), '
                '"site_description": (config.site_description | string )} | tojson }}'
            )

        default_file_path = files("mkdocs_techdocs_diamond").joinpath("config.yml")
        with default_file_path.open() as defaults_file:
            default_config: MkDocsConfig = MkDocsConfig(
                config_file_path=defaults_file.name
            )
            default_config.load_file(defaults_file)
            default_config._validate()
            default_config._post_validate()

        config.plugins.pop("techdocs-diamond")

        if config["theme"]["name"] == default_config["theme"]["name"]:
            if "features" not in config["theme"]:
                config["theme"]["features"] = []
            config["theme"]["features"].extend(default_config["theme"]["features"])
            config["theme"]["palette"] = {}
        else:
            config["theme"] = default_config["theme"]
        config["theme"].static_templates.update({"techdocs_metadata.json"})
        config["theme"].dirs.append(self.tmp_dir_techdocs_theme.name)

        for name, plugin in default_config["plugins"].items():
            config["plugins"][name] = copy(plugin)

        if "markdown_extensions" not in config:
            config["markdown_extensions"] = []
        config["markdown_extensions"].extend(default_config.markdown_extensions)

        if "mdx_configs" not in config:
            config["mdx_configs"] = []
        config["mdx_configs"].update(default_config.mdx_configs)

        config.validate()

        return config
