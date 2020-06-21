#!/usr/bin/env python
""" Build a simple startpage using SCSS, Javascript and a Template Engine """

import argparse
import base64
import logging
from pathlib import Path
from typing import Any, Callable, Dict, Text
from urllib.parse import urlparse
from urllib.request import urlopen
from urllib.error import HTTPError

from bs4 import BeautifulSoup, NavigableString, PageElement
from jinja2 import Template
from yaml import BaseLoader, load


def prepare_domain(url: Text) -> Text:
    """ cut down an url to only keep the domain
    e.g. https://www.google.com becomes google.com
    """

    url = url.strip()
    if not url:
        raise ValueError("Empty url given")

    parsed = urlparse(url)
    if parsed.scheme == "":
        slash_loc = parsed.path.find("/")
        # splice end -> None == full string
        slash_loc = slash_loc if slash_loc != -1 else None
        return parsed.path[:slash_loc]
    else:
        return parsed.netloc


def download_favicon(domain: Text, download_path: Path = None) -> bool:
    """ Download the favicon from Googles cache service and store the result as PNG under `download_folder`.
    If the favicon is already present in the download folder, does nothing.

    Icons are downloaded to the "assets" folder. If this folder does not exist, it will be created!

    Args:
        - domain: Domain whichs icon to download
        - download_path: path to download to (defaults to the current directory)

    """

    logger = logging.getLogger()
    logger.debug("Downloading favicon...")

    # no domain given, nothing to do
    if not domain:
        logger.warning("No domain to download given!")
        return False
    # use current dir of none provided
    if not download_path:
        download_path = Path(".")
    download_path = download_path / "assets"

    # create output directories
    download_path.mkdir(parents=True, exist_ok=True)

    if (Path(download_path) / f"{domain}.png").exists():
        logger.debug(f"Domain '{domain}' exists!")
        return True
    else:
        try:
            (Path(download_path) / f"{domain}.png").write_bytes(
                urlopen("https://www.google.com/s2/favicons?domain=" + domain).read())
            logger.debug(f"Domain '{domain}' downloaded!")
        except HTTPError:
            logger.warning(f"Could not download domain: '{domain}'")
            logger.debug("", exc_info=1)
            return False
        return True


def inline_data(html_data: Text,
                asset_folder: Path,
                type_: Text,
                asset_attr: Text,
                replacement_callable: Callable[[PageElement, Path], bool],
                type_attrs: Dict[Text, Text] = None):
    """
    Embed the content of a tag (e.g. img, script, style) into the html file if
    it can be found on disk.

    Args:
        - html_data: HTML file data
        - asset_folder: Folder where the asset files (css, js, png ...) can be found
        - type_: tag to find (e.g. "img", "link", "script")
        - asset_attr: attribute of the tag that holds the path info (e.g. src in img tags)
        - replacement_callable: callable that does the actual replacement
        - type_attrs: additional attributes that identify the tags to replace (e.g. rel="stylesheet" for link tags)

    Returns:
        - HTML file data with replaced values
    """

    logger = logging.getLogger()
    logger.info(f"Embedding {type_} content into HTML...")

    if not asset_folder:
        raise ValueError("Asset Folder not given!")
    if not type_attrs:
        type_attrs = {}

    soup = BeautifulSoup(html_data, features="html.parser")

    nodes = soup.findAll(type_, type_attrs)
    for node in nodes:
        node_path = asset_folder / node[asset_attr]
        if not node_path.exists():
            logger.debug(f"Skipping file '{node_path}' as it does not exist on disk!")
            continue
        replacement_callable(node, node_path)
        logger.debug(f"Embedded '{node_path}'!")
    return str(soup)


def _inline_css(style_tag: PageElement, style_file: Path) -> bool:
    """ replacement callable to replace stylesheets for inline_data """

    style_content = NavigableString(style_file.read_text())

    new_style_tag = BeautifulSoup(features="html.parser").new_tag("style")
    new_style_tag.insert(0, style_content)
    new_style_tag["type"] = "text/css"

    style_tag.replaceWith(new_style_tag)


def _inline_script(script_tag: PageElement, script_file: Path) -> bool:
    """ replacement callable to replace scripts for inline_data """

    script_content = NavigableString(script_file.read_text())

    new_script_tag = BeautifulSoup(features="html.parser").new_tag("script")
    new_script_tag.insert(0, script_content)
    new_script_tag["type"] = "text/javascript"

    script_tag.replaceWith(new_script_tag)


def _inline_image(image_tag: PageElement, image_file: Path) -> bool:
    """ replacement callable to replace img tags for inline_data """

    image_content = "data:image/png;base64," + base64.b64encode(image_file.read_bytes()).decode("utf-8")
    image_content = NavigableString(image_content)

    image_tag["src"] = image_content


def load_config(config_file: Path) -> Dict[Text, Any]:
    """ load the config from file (yml formatted) and return a dict """

    data = load(config_file.read_text(), Loader=BaseLoader)
    if not data:
        raise TypeError("Empty config file")
    return data


def load_template(template_file: Path) -> Template:
    """ load a Jinja2 template from file and return it """

    return Template(template_file.read_text())


def render_template(template: Template,
                    data: Dict[Text, Any],
                    one_file: bool = False,
                    asset_folder: Path = None) -> Text:
    """ Render template to a string.

    Args:
        - template: Jinja2 Template to use
        - data: Config data to be replaced when rendering the template
        - one_file: If all the assets should be embedded into the final HTML file
        - asset_folder: Folder where the assets can be found (Defaults to "./dist/")

    Returns:
        - Finalized HTML file data
    """

    logger = logging.getLogger()
    logger.info("Rendering template...")

    template_str = template.render(data)

    if one_file:
        if not asset_folder:
            asset_folder = Path("dist/")

        template_str = inline_data(template_str,
                                   asset_folder,
                                   "link",
                                   "href",
                                   _inline_css,
                                   type_attrs={"rel": "stylesheet"})
        template_str = inline_data(template_str, asset_folder, "script", "src", _inline_script)
        template_str = inline_data(template_str, asset_folder, "img", "src", _inline_image)

    return template_str


def write_template(html_data: Text, filename: Text, output_path: Path, overwrite: bool = False):
    """ Output the template data (html string) to file. """

    logger = logging.getLogger()
    logger.info("Writing data...")

    if not html_data:
        raise TypeError("No HTML data given")
    if not filename:
        raise TypeError("No filename given!")
    if not output_path:
        logger.warning("No output path given. Setting to current directory!")
        output_path = Path(".")

    # create output directories
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / filename
    if output_file.exists() and not overwrite:
        raise FileExistsError(output_file.resolve())

    output_file.write_text(html_data)


def main():
    parser = argparse.ArgumentParser(description="Generate the Startpage HTML and CSS.")
    parser.add_argument("config", type=Path, help="Path to the config file")
    parser.add_argument("template", type=Path, help="Path to the template file")
    parser.add_argument("-v", "--verbose", required=False, action="store_true", help="More verbose output")
    parser.add_argument("-o",
                        "--output-path",
                        required=False,
                        type=Path,
                        default=Path("./dist"),
                        help="Path to output the finished Startpage files to. Defaults to './dist'.")
    parser.add_argument("-1",
                        "--one-file",
                        required=False,
                        default=False,
                        action="store_true",
                        help="Include all files into one big HTML file. Fonts are not included right now.")
    parser.add_argument("-f",
                        "--force-overwrite",
                        action="store_true",
                        default=False,
                        required=False,
                        help="When present, overwrites any existing file under 'output_path'")
    parser.add_argument("-s",
                        "--source-path",
                        required=False,
                        type=Path,
                        default=Path("./dist"),
                        help="Path where all the resource files are stored (css, js, img etc.). Defaults to './dist'.")

    args = parser.parse_args()

    logger = logging.getLogger()

    if args.verbose:
        logger.info("Verbose output enabled")
        logging.basicConfig(level=logging.DEBUG, force=True)
    if args.force_overwrite:
        logger.info("Overwriting output files is enabled")
    if not args.config.is_file():
        raise FileNotFoundError("Config file does not exist or is a directory.")
    if not args.template.is_file():
        raise FileNotFoundError("Template file does not exist or is a directory.")
    if not args.source_path.is_dir():
        raise FileNotFoundError("Source path is not a folder or does not exist!")

    config = load_config(args.config)
    logger.debug(config)

    for card in config["card"]:
        for link in card["link"]:
            domain = prepare_domain(link["link"])
            # download the favicon and add a new config entry 'link'
            if download_favicon(domain, download_path=args.output_path):
                link["icon"] = f"{domain}.png"
            else:
                link["icon"] = "_default.png"

    template = load_template(args.template)

    template_html = render_template(template, config, args.one_file, args.source_path)

    write_template(template_html, "index.html", args.output_path, overwrite=args.force_overwrite)


if __name__ == "__main__":
    logging.basicConfig(format="{asctime} - {levelname:<8} : {message}",
                        style="{",
                        datefmt="%H:%M:%S",
                        level=logging.INFO)
    main()
