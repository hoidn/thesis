import re
from collections import namedtuple
import pdb

Reference = namedtuple("Reference", ["number", "text"])

class Reference:
    def __init__(self, txt):
        m = re.match(r'\{\[\}(\d)\{\]\}(.*)', txt)
        self.num = int(m.groups()[0])
        self.text = m.groups()[1]

    def getbib(self):
        import subprocess
        proc = subprocess.Popen(["python", "scholar.py", "-c", "1", "--phrase", self.text, "--citation", "bt"], stdout=subprocess.PIPE)
        out = proc.communicate()[0]
        return out.upper()

    def getbibname(self):
        return refname(self.getbib())

def refname(bibentry):
    """
    Extract the citation name.
    """
    pat = r'\@[0-9a-zA-Z]+\{([0-9a-zA-Z]+).*\}'
    return re.match(pat, bibentry.replace('\n', ' ')).groups()[0]

def strip_latex_commands(str):
    pat = r"\\[a-z]+\{(.*?)\}"
    return re.sub(pat, r'\1', str)

def get_references(fname, strip = True):
    with open(fname, 'r') as f:
        lines = f.readlines()
    newlines = ['']
    for l in lines:
        if l == '\n':
            newlines.append('')
        else:
            new = l.replace('\n', ' ')
            newlines[-1] += new
    isref = lambda l: re.match(r'\{\[\}\d\{\]\}', l)
    references = list(map(lambda l: Reference(strip_latex_commands(l)),
        filter(isref, newlines)))
    rest = list(filter(lambda l: not isref(l), lines))
    return references, ' '.join(rest)

def update_citations(fname):
    references, rest = get_references(fname)
    reflookup = {ref.num: ref.getbibname() for ref in references}
    for ref in references:
        rest = re.sub(r'\{\[\}%d\{\]\}' % ref.num, r'\cite{%s}' % reflookup[ref.num], rest)
    #isref = lambda l: re.match(r'\{\[\}\d\{\]\}', l)
    return rest
