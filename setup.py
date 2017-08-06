from setuptools import setup, find_packages
setup(
    name="GEMEditor",
    version="0.0.7",
    packages=find_packages(),
    install_requires=['cobra',
                      'escher',
                      'PyQt5',
                      'lxml',
                      'networkx',
                      'numpy',
                      'sqlalchemy'],
    description="A graphical editor for the reconstruction, annotation and testing of genome-scale models",
    url="https://github.com/JuBra/GEMEditor",
    author="Julian Brandl",
    author_email="jubra@bio.dtu.dk",
    license="GPL",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.5',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
        ],
    keywords="metabolism biology",
    platforms="GNU/Linux, Mac OS X >= 10.7, Microsoft Windows >= 7",
    include_package_data=True
)