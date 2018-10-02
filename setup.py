# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""


import re
import sys
import collections
from pathlib import Path
import subprocess
from setuptools import setup, find_packages
import setuptools.command.build_py

project_name = "visual_image_splitter"
script_file = "{project_name}/{project_name}.py".format(project_name=project_name)
description = "Setuptools setup.py for visual_image_splitter."

with open("README.rst", "r", encoding="utf-8") as f:
    long_description = f.read()


MetaData = collections.namedtuple(
    "MetaData", [
        "version", "author", "author_email", "maintainer", "maintainer_email", "home_page"
    ]
)


def extract_metadata() -> MetaData:
    source_file_path = Path(__file__).parent / "visual_image_splitter" / "visual_image_splitter.py"
    with open(source_file_path, "r") as data_source_file:
        source = data_source_file.read()
    if not source:
        print("Cannot read Visual Image Splitter source file containing required information. Unreadable: {}".format(
            source_file_path))
        sys.exit(1)

    def search_for(pattern: str) -> str:
        return re.search(
            r"""^{}\s*=\s*('(.*)'|"(.*)")""".format(pattern),  # Search for assignments: VAR = 'VALUE' or VAR = "VALUE"
            source,
            re.M
        ).group(1)[1:-1]  # Cut off outer quotation marks

    return MetaData(
        version=search_for("VERSION"),
        author=search_for("AUTHOR"),
        author_email=search_for("AUTHOR_EMAIL"),
        maintainer=search_for("MAINTAINER"),
        maintainer_email=search_for("MAINTAINER_EMAIL"),
        home_page=search_for("HOME_PAGE")
    )


class BuildWithQtResources(setuptools.command.build_py.build_py):
    """Try to build the Qt resources file for visual_image_splitter."""
    def run(self):
        if not self.dry_run:  # Obey the --dry-run switch
            source_root = Path(__file__).resolve().parent / "visual_image_splitter"
            build_root = Path(self.build_lib).resolve() / "visual_image_splitter"
            resources_file = source_root / "resources" / "resources.qrc"
            compiled_qt_resources = self._compile_resource_file(resources_file)
            target_directory = build_root / "ui"
            self.mkpath(str(target_directory))
            with open(target_directory / "compiled_resources.py", "w") as compiled_qt_resources_file:
                compiled_qt_resources_file.write(compiled_qt_resources)
        super(BuildWithQtResources, self).run()

    @staticmethod
    def _compile_resource_file(resource_file: Path) -> str:
        command = ("pyrcc5", str(resource_file))
        compiled = subprocess.check_output(command, universal_newlines=True)  # type: str
        return compiled


meta_data = extract_metadata()

setup(
    name=project_name,
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    # add required packages to install_requires list
    # This causes pip to download and install a copy from PyPi, instead of using the already installed version
    # install_requires=["PyQt5"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pyhamcrest"],
    test_suite="pytest",
    entry_points={
        "gui_scripts": [
            "{project_name} = {project_name}.{project_name}:main".format(project_name=project_name)
        ]
    },
    version=meta_data.version,
    description=description,
    long_description=long_description,
    python_requires=">=3.6",
    author=meta_data.author,
    author_email=meta_data.author_email,
    maintainer=meta_data.maintainer,
    maintainer_email=meta_data.maintainer_email,
    url=meta_data.home_page,
    cmdclass={'build_py': BuildWithQtResources},
    license="GPLv3",
    # list of classifiers: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Environment :: X11 Applications :: Qt',
        'Environment :: Win32 (MS Windows)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion'
    ],
)
