#  Copyright (c) 1999 John Aycock
#  Copyright (c) 2000 by hartmut Goebel <hartmut@goebel.noris.de>
#
#  Permission is hereby granted, free of charge, to any person obtaining
#  a copy of this software and associated documentation files (the
#  "Software"), to deal in the Software without restriction, including
#  without limitation the rights to use, copy, modify, merge, publish,
#  distribute, sublicense, and/or sell copies of the Software, and to
#  permit persons to whom the Software is furnished to do so, subject to
#  the following conditions:
#  
#  The above copyright notice and this permission notice shall be
#  included in all copies or substantial portions of the Software.
#  
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#  CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# See the file 'CHANGES' for a list of changes
#
# NB. This is not a masterpiece of software, but became more like a hack.
#     Probably a complete rewrite would be sensefull. hG/2000-12-27
#

import sys, types, os
import Scanner, Walker, verify, magics

__all__ = ['decompyle_file', 'decompyle_file', 'main']

TABWIDTH=4

def _load_file(filename):
    """
    load a Python source file and compile it to byte-code

    _load_module(filename: string): code_object

    filename:	name of file containing Python source code
    		(normally a .py)
    code_object: code_object compiled from this source code

    This function does NOT write any file!
    """
    fp = open(filename, 'rb')
    source = fp.read()+'\n'
    try:
        co = compile(source, filename, 'exec')
    except SyntaxError:
        print >> sys.stderr, '>>Syntax error in', filename
        raise
    fp.close()
    return co

def _load_module(filename):
    """
    load a module without importing it
    _load_module(filename: string): code_object

    filename:	name of file containing Python byte-code object
    		(normally a .pyc)
    code_object: code_object from this file
    """
    import magics, marshal_files
    fp = open(filename, 'rb')
    magic = fp.read(4)
    try:
        version = magics.versions[magic]
        marshal = marshal_files.import_(magic=magic)
    except KeyError:
        raise ImportError, "Unknown magic number in %s" % filename
    #print version
    fp.read(4) # timestamp
    co = marshal.load(fp)
    fp.close()
    return version, co

def decompyle(version, co, out=None, showasm=0, showast=0):
    """
    diassembles a given code block 'co'
    """
    assert type(co) == types.CodeType

    # store final output stream for case of error
    __real_out = out or sys.stdout

    scanner = Scanner.getscanner(version)
    scanner.setShowAsm(showasm, out)
    tokens, customize = scanner.disassemble(co)

    #  Build AST from disassembly.
    walker = Walker.Walker(out, scanner, showast=showast)
    try:
        ast = walker.build_ast(tokens, customize)
    except Walker.ParserError, e :  # parser failed, dump disassembly
        print >>__real_out, e
        raise

    del tokens # save memory

    if not showasm and not showast:
        # add a hint for emacs
        print >> out, '# emacs-mode: -*- python-*-'

    # convert leading '__doc__ = "..." into doc string
    assert ast == 'stmts'
    if ast[0] == Walker.ASSIGN_DOC_STRING(co.co_consts[0]):
        walker.print_docstring('', co.co_consts[0])
        del ast[0]
    if ast[-1] == Walker.RETURN_NONE:
        ast.pop() # remove last node
        #todo: if empty, add 'pass'

    walker.gen_source(ast, customize)

    if not showasm and not showast:
        # add another hint for emacs
        print >> out, '# local variables:'
        print >> out, '# tab-width:', TABWIDTH


def decompyle_file(filename, outstream=None, showasm=0, showast=0):
    """
    decompile Python byte-code file (.pyc)
    """
    version, co = _load_module(filename)
    decompyle(version, co, out=outstream, showasm=showasm, showast=showast)
    co = None

#---- main -------

if sys.platform.startswith('linux') and os.uname()[2][:2] == '2.':
    def __memUsage():
        mi = open('/proc/self/stat', 'r')
        mu = mi.readline().split()[22]
	#return mu
        mi.close()
        return int(mu) / 1000000
else:
    def __memUsage():
        return ''

def main(in_base, out_base, files, outfile=None,
         showasm=0, showast=0, do_verify=0):
    """
    in_base	base directory for input files
    out_base	base directory for output files (ignored when
    files	list of filenames to be decompyles (relative to src_base)
    outfile	write output to this filename (overwrites out_base)

    For rediecting output to
    - <filename>		outfile=<filename> (out_base is ignored)
    - files below out_base	out_base=...
    - stdout			out_base=None, outfile=None
    """
    def _get_outstream(outfile):
        dir = os.path.dirname(outfile)
        failed_file = outfile + '_failed'
        if os.path.exists(failed_file): os.remove(failed_file)
        if not os.path.exists(dir):
            try:
                os.makedirs(dir)
            except:
                raise "Can't create output dir '%s'" % dir
        return open(outfile, 'w')

    of = outfile

    tot_files = okay_files = failed_files = verify_failed_files = 0

    for file in files:
        infile = os.path.join(in_base, file)
	#print >>sys.stderr, infile

        if of: # outfile was given as parameter
            outstream = _get_outstream(outfile)
        elif out_base is None:
            outstream = sys.stdout
        else:
            outfile = os.path.join(out_base, file) + '_dis'
            outstream = _get_outstream(outfile)
	#print >>sys.stderr, outfile 

        # try to decomyple the input file
        try:
            decompyle_file(infile, outstream, showasm, showast)
            tot_files += 1
        except KeyboardInterrupt:
            if outfile:
                outstream.close()
                os.remove(outfile)
            raise
        except:
	    failed_files += 1
            sys.stderr.write("### Can't decompyle  %s\n" % file)
            if outfile:
                outstream.close()
                os.rename(outfile, outfile + '_failed')
            raise
	else: # decompyle successfull
            if outfile:
                outstream.close()
            if do_verify:
                try:
                    verify.compare_code_with_srcfile(infile, outfile)
                    print "+++ okay decompyling", infile, __memUsage()
                    okay_files += 1
                except verify.VerifyCmpError, e:
		    verify_failed_files += 1
                    os.rename(outfile, outfile + '_unverified')
                    print >>sys.stderr, "### Error Verifiying", file
                    print >>sys.stderr, e
            else:
                okay_files += 1
                print "+++ okay decompyling", infile, __memUsage()
    print 'decompyled %i files: %i okay, %i failed, %i verify failed' % \
          (tot_files, okay_files, failed_files, verify_failed_files)

# local variables:
# tab-width: 4
