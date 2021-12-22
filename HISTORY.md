This is the code for a Python decompiler for Python versions 1.5 to 2.4. It is the ancestor of a number of other decompilers.

The below is an annotated history from talking to participants involved, and from my reading of the code and sources cited.

In 1998, John Aycock first wrote a grammar parser in Python, eventually called SPARK, that was usable inside a Python program. This
code was described in the [7th International Python Conference](http://legacy.python.org/workshops/1998-11/proceedings/papers/aycock-little/aycock-little.html). That
paper doesn't talk about decompilation, nor did John have that in mind at that time. It does mention that a full parser for Python (rather than the simple languages in the paper) was being considered, but never came about.

[This](http://pages.cpsc.ucalgary.ca/~aycock/spark/content.html#contributors) contains a of people acknowledged in developing SPARK. What's amazing about this code is that it is reasonably fast and has survived up to Python 3 with relatively little change. This work was done in conjunction with his Ph.D Thesis. This was finished around 2001. In working on his thesis, John realized SPARK could be used to deparse Python bytecode. In the fall of 1999, he started writing the Python program, "decompyle", to do this.

To help with control structure deparsing the instruction sequence was augmented with pseudo instruction `COME_FROM`. This code introduced another clever idea: using table-driven semantics routines, using
format specifiers.

The last mention of a release of SPARK from John is around 2002. As released, although the Earley Algorithm parser was in good shape, this code was woefully lacking as serious Python deparser.

In the fall of 2000, Hartmut Goebel [took over maintaining the code](https://groups.google.com/forum/#!searchin/comp.lang.python/hartmut$20goebel/comp.lang.python/35s3mp4-nuY/UZALti6ujnQJ). The
first subsequent public release announcement that I can find is ["decompyle - A byte-code-decompiler version 2.2 beta 1"](https://mail.python.org/pipermail/python-announce-list/2002-February/001272.html).

From the CHANGES file found in [the tarball for that release](http://old-releases.ubuntu.com/ubuntu/pool/universe/d/decompyle2.2/decompyle2.2_2.2beta1.orig.tar.gz) (and also listed in this repository in CHANGES),
it appears that Hartmut did most of the work to get this code to be able to decompile the full Python language. He added precedence to the table specifiers, support for multiple versions of Python, the pretty-printing of docstrings, lists, and hashes. He also wrote test and verification routines of deparsed bytecode, and used this in an extensive set of tests that he also wrote. He says he could verify against the
entire Python library. However I have subsequently found small and relatively obscure bugs in the decompilation code.

decompyle2.2 was packaged for Debian (sarge) by [Ben Burton around 2002](https://packages.qa.debian.org/d/decompyle.html). As
it worked on Python 2.2 only long after Python 2.3 and 2.4 were in widespread use, it was removed.

As far as I know, this code has never been in PyPI or the previous incarnation, the Python Cheese shop.

[Crazy Compilers](http://www.crazy-compilers.com/decompyle/) offered (offers?) a byte-code decompiler service for versions of Python up to 2.6. As someone who worked in compilers, it is tough to make a living by
working on compilers. (For example, based on [John Aycock's recent papers](http://pages.cpsc.ucalgary.ca/~aycock/) it doesn't look like he's done anything compiler-wise since SPARK). So I hope people will use the crazy-compilers service. I wish them the success that his good work deserves.

Dan Pascu did a bit of work from late 2004 to early 2006 to get this code to handle first Python 2.3 and then 2.4 bytecodes. Because of jump optimization introduced in the CPython bytecode compiler at that
time, various `JUMP` instructions were classified to assist parsing. For example, due to the way that code generation and line number table work, jump instructions to an earlier offset must be looping jumps,
such as those found in a `continue` statement; `COME FROM` instructions were reintroduced.  See [RELEASE-2.4-CHANGELOG.txt](https://github.com/rocky/python-uncompyle6/blob/master/DECOMPYLE-2.4-CHANGELOG.txt)
for more details here. There wasn't a public release of RELEASE-2.4 and bytecodes other than Python 2.4 weren't supported. Dan says the Python 2.3 version could verify the entire Python library. But given subsequent bugs found like simply recognizing complex-number constants in bytecode, decompilation wasn't perfect.

NB. If you find mistakes, want corrections, or want your name added (or removed), please contact me.
