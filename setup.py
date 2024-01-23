import setuptools


setuptools.setup(
    long_description_content_type="text/markdown",
    url="https://github.com/youserj/DlmsSPODES",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License"
    ],
    entry_points={
        'console_scripts': [
            'parser=src.DlmsSPODES.setting:version'
        ]
    },
)
