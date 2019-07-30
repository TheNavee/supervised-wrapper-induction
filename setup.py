import setuptools

setuptools.setup(
    name="supervised_wrapper_induction",
    packages=["swi"],
    version="1.0.1",
    install_requires=[
              'python-Levenshtein',
              'BeautifulSoup4',
              'fuzzywuzzy',
              'extruct',
              'lxml',
              'soupsieve'
    ],
)
