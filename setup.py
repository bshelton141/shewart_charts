import setuptools

setuptools.setup(
name="shewhart",
version="0.1.1",
author="Brandon Shelton",
author_email="brandon.michael.shelton@gmail.com",
description="Shewart Module",
url="https://github.com/bshelton141/shewhart_charts",
packages=setuptools.find_packages(),
classifiers=[
"Programming Language :: Python :: 3",
"License :: OSI Approved :: MIT License",
"Operating System :: OS Independent",
],
include_package_data=True,
package_data = {'': ['data/*.csv', 'data/*.xlsx']},
python_requires='>=3.6',
)
