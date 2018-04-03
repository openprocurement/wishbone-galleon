import setuptools


VERSION = '1.0.0a1.dev1'
DESCRIPTION = """
Wishbone Encode modules to use galleon transforms
"""
CLASSIFIERS = [
    'Development Status :: 2 - Pre-Alpha',
    'Programming Language :: Python',
    # 'Programming Language :: Python :: 2',
    # 'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
]
INSTALL_REQUIRES = [
    'setuptools',
    'wishbone',
    'galleon',
    'pyyaml'
]
TEST_REQUIRES = [
    'pytest',
    'pytest-cov'
]
EXTRA = {
    "test": TEST_REQUIRES
}
ENTRY_POINTS = {
    'wishbone.module.process': [
        'galleon = wishbonegalleon:GalleonModule'
    ]
}

setuptools.setup(
    name="wishbonegalleon",
    version=VERSION,
    url="-",

    author="yshalenyk",
    author_email="yshalenyk@quintagroup.com",

    description=DESCRIPTION,
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=INSTALL_REQUIRES,
    test_requires=TEST_REQUIRES,
    extras_require=EXTRA,
    setup_requires=['pytest-runner'],

    entry_points=ENTRY_POINTS,
    classifiers=CLASSIFIERS
)
