# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""


import re
from setuptools import setup, find_packages

project_name = "visual_image_splitter"
script_file = "{project_name}/{project_name}.py".format(project_name=project_name)
description = "Setuptools setup.py for visual_image_splitter."

with open(script_file, "r", encoding="utf-8") as opened_script_file:
    version = re.search(
        r"""^__version__\s*=\s*"(.*)"\s*""",
        opened_script_file.read(),
        re.M
        ).group(1)


with open("README.rst", "r", encoding="utf-8") as f:
    long_description = f.read()


setup(
    name=project_name,
    packages=find_packages(),
    # add required packages to install_requires list
    install_requires=["PyQt5"],
    test_requires=["pyhamcrest"],
    entry_points={
        "console_scripts": [
            "{project_name} = {project_name}.{project_name}:main".format(project_name=project_name)
        ]
    },
    version=version,
    description=description,
    long_description=long_description,
    author="Thomas Hess",
    author_email="thomas.hess@udo.edu",
    url="http://Project.url.here",
    license="GPLv3",
    # list of classifiers: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Environment :: Console',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
