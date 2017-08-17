import re
from collections import namedtuple
import pdb

bib_pattern = r'\{\[\}(\d+)\{\]\}'
Reference = namedtuple("Reference", ["number", "text"])

def memoize(f):
    cache = {}
    def newf(*args):
        if args not in cache:
            cache[args] = f(*args)
        return cache[args]
    return newf

@memoize
def getbib(text):
    import subprocess
    proc = subprocess.Popen(["python", "scholar.py", "-c", "1", "--phrase", text, "--citation", "bt"], stdout=subprocess.PIPE)
    out = proc.communicate()[0]
    return out.upper().strip('\n')

class Reference:
    def __init__(self, txt):
        m = re.match(r'\{\[\}(\d+)\{\]\}(.*)', txt)
        self.num = int(m.groups()[0])
        self.text = m.groups()[1]

    def getbib(self):
        return getbib(self.text)

    def getbibname(self):
        return refname(self.getbib())

def refname(bibentry):
    """
    Extract the citation name.
    """
    if not bibentry:
        return ''
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
    isref = lambda l: re.match(r'\{\[\}\d+\{\]\}', l)
    references = list(map(lambda l: Reference(strip_latex_commands(l)),
        filter(isref, newlines)))
    rest = list(filter(lambda l: not isref(l), lines))
    return references, ' '.join(rest)

def parse_citation(citation):
    pat_body = r'\{\[\}(.+)\{\]\}'
    body = re.match(pat_body, citation).groups()[0]

    pat_range = r'((\d+)\-?(\d+)?)\,?(.*)?'
    ranges = []
    while re.match(pat_range, body):
        both, start, end, body = re.match(pat_range, body).groups()
        ranges.append((start, end))
    rangesets = set()
    for start, end in ranges:
        if end is not None:
            rangesets |= set(list(range(int(start), int(end) + 1)))
        else:
            rangesets |= set([int(start)])
    return rangesets

def segment_citations(fname):
    """
    yield, in alternation, sets of cited reference numbers and intervening text segments.
    """
    # TODO we've assumed no more than one citation instance per line.
    with open(fname, 'r') as f:
        lines = f.readlines()
    pat_citation = r'(.+)(\{\[\}(?:.+)?\{\]\})(.*)'
    pairs = [] 
    suffix = ''
    for l in lines:
        if re.match(pat_citation, l):
            prefix, cite, next_suffix = re.match(pat_citation, l).groups()
            prefix = suffix + prefix
            suffix = next_suffix + '\n'
            pairs.append((prefix, cite))
        else:
            suffix += l
    return pairs, suffix
    
def update_citations(fname):
    references, rest = get_references(fname)
    reflookup = {ref.num: ref.getbibname() for ref in references}
    output = ''
    pairs, rest = segment_citations(fname)
    for prefix, cite in pairs:
        output += prefix
        refnums = parse_citation(cite)
        refnames = filter(lambda name: name, [reflookup[num] for num in sorted(refnums)])
        print(refnames)
        print(reflookup)
        if any(refnames):
            output += (r'\cite{%s}' % ', '.join(refnames))
    output += rest
    return output
