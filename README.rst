============================
Supervised Wrapper Induction
============================

SWI is a library for extracting structured data from HTML pages. The difference with other
XPath based libraries is that it builds itself the selectors needed. It was inspired by scrapely. Given
some example web page(s) and the data to be extracted, SWI constructs a wrapper to extract
information on all similar pages.


Installation
============

Install SWI with pip::

    pip install supervised_wrapper_induction


Build Locally
=============

SWI works in Python 3.3+.

To build::

    python setup.py sdist


Requirements
============

SWI uses:

- BeautifulSoup4
- fuzzywuzzy
- python-Levenshtein
- extruct
- python-lxml
- soupsieve


Usage (API)
===========

You can use SWI to build very capable scrapers.

What follows is a quick example that you can run in a python shell.

Start by importing and instantiating the Extractor class::

    >>> from swi import Extractor
    >>> extractor = Extractor()

Then, proceed to train the Extractor by adding some page and the data you expect
to scrape from there (note that all keys and values in the data you pass must
be strings).::

    >>> import requests
    >>> url1 = "https://pypi.org/project/pip/19.2.1/"
    >>> response = requests.get(url1)
    >>> train_set_1 = {"name":"pip 19.2.1",
		"maintainers":["cjerdonek", "dstufft"],
		"maintainers_profile_pictures":[
		"https://warehouse-camo.cmh1.psfhosted.org/697af4520c5134f9d47c5647352f0a1a83bac949/68747470733a2f2f7365637572652e67726176617461722e636f6d2f6176617461722f39623531336565376363343030633962373337346634363937613165363961643f73697a653d3530",
		"https://warehouse-camo.cmh1.psfhosted.org/6d0424bff7dd2ff3855b621bf1470d578040d430/68747470733a2f2f7365637572652e67726176617461722e636f6d2f6176617461722f65626631333233363262363232343233656435626163613239383839313162383f73697a653d3530"]}
	>>> extractor.add_train_page(response.content, train_set_1)

Finally, you can scrape any other similar page::

    >>> extractor.predict(response.content)
    {'name': 'pip 19.2.1', 'maintainers': ['cjerdonek', 'dstufft', 'pf_moore', 'pradyunsg'], 'maintainers_profile_pictures': ['https://warehouse-camo.cmh1.psfhosted.org/697af4520c5134f9d47c5647352f0a1a83bac949/68747470733a2f2f7365637572652e67726176617461722e636f6d2f6176617461722f39623531336565376363343030633962373337346634363937613165363961643f73697a653d3530', 'https://warehouse-camo.cmh1.psfhosted.org/6d0424bff7dd2ff3855b621bf1470d578040d430/68747470733a2f2f7365637572652e67726176617461722e636f6d2f6176617461722f65626631333233363262363232343233656435626163613239383839313162383f73697a653d3530', 'https://warehouse-camo.cmh1.psfhosted.org/1d0deb041bb7e8edce368279a37546324366eced/68747470733a2f2f7365637572652e67726176617461722e636f6d2f6176617461722f64393935623436326139386665613431326566613739643137626133373837613f73697a653d3530', 'https://warehouse-camo.cmh1.psfhosted.org/f15785f37e0e3fb85805ffd0760ea2f7ad35cba0/68747470733a2f2f7365637572652e67726176617461722e636f6d2f6176617461722f64333733306664646430333536643334366666636437653466376137616261643f73697a653d3530']}
    >>> url2 = "https://pypi.org/project/Django/2.2.3"
    >>> response2 = requests.get(url2)
    >>> extractor.predict(response2.content)
    {'name': 'Django 2.2.3', 'maintainers': ['apollo13', 'carltongibson', 'felixx', 'jacobian', 'Tim.Graham', 'ubernostrum'], 'maintainers_profile_pictures': ['https://warehouse-camo.cmh1.psfhosted.org/04bfcf7860c8fffd7f686950c3cdcb81d8c61e45/68747470733a2f2f7365637572652e67726176617461722e636f6d2f6176617461722f31646339636564326637323165346266636239396534356135306231383366323f73697a653d3530', 'https://warehouse-camo.cmh1.psfhosted.org/d9cf326b5aeb544a49654e29530691c03bdef3ec/68747470733a2f2f7365637572652e67726176617461722e636f6d2f6176617461722f64646564323130636631623537326636663832303836393562326663366562333f73697a653d3530', 'https://warehouse-camo.cmh1.psfhosted.org/183c060dbdfbe42fe63df08f08badca85dca3bb9/68747470733a2f2f7365637572652e67726176617461722e636f6d2f6176617461722f36643037376136613161663037386435346631613231353535366537643436333f73697a653d3530', 'https://warehouse-camo.cmh1.psfhosted.org/e524204ccab58fe3ec3ca04af176f6dbeaa50c3b/68747470733a2f2f7365637572652e67726176617461722e636f6d2f6176617461722f32663534363338333263636237363863636234613163613336303763323765663f73697a653d3530', 'https://warehouse-camo.cmh1.psfhosted.org/a9e53e05771e61c8079939fe5a6553cd2eb19679/68747470733a2f2f7365637572652e67726176617461722e636f6d2f6176617461722f66613137303737373237336361376232333562646465376438306539663861363f73697a653d3530', 'https://warehouse-camo.cmh1.psfhosted.org/095e1b32c90de718c30ab173b05be0cec0bb6ca4/68747470733a2f2f7365637572652e67726176617461722e636f6d2f6176617461722f31303835333466363564386432643764653639393539373363316634393838393f73697a653d3530']}

In the train set you can either give a single value or a list of values. If you want to find a list of items, you don't have to
give them all during the training, you need to give at least two values and the extractor should find the rest of them. See example above with "maintainers" field.


Testing
=======

For testing we use pytest::

	pytest

