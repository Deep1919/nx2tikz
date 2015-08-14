"""Export NetworkX graphs to TikZ graphs with automatic layout."""
import argparse
import subprocess
from networkx import is_directed, Graph


def dumps_tikz(g, preamble=True, layout='layered', use_label=True):
    if layout not in {'layered', 'spring'}:
        raise ValueError('Unknown layout: {s}'.format(s=layout))
    s = ''
    for n, d in g.nodes_iter(data=True):
        # label
        label = g.node[n].get('label', '')
        label = 'as={' + label + '}' if label else ''
        # geometry
        color = d.get('color', '')
        fill = d.get('fill', '')
        shape = d.get('shape', '')
        # style
        style = ', '.join(filter(None, [label, color, fill, shape]))
        style = '[' + style + ']' if style else ''
        # pack them
        s += str(n) + style + ';\n'
    s += '\n'
    if is_directed(g):
        line = ' -> '
    else:
        line = ' -- '
    for u, v, d in g.edges_iter(data=True):
        if use_label:
            label = d.get('label', '')
            color = d.get('color', '')
        else:
            label = str(d)
            color = ''
        if label:
            label = '"' + label + '"\' above'
        loop = 'loop' if u is v else ''
        style = ', '.join(filter(None, [label, color, loop]))
        style = ' [' + style + '] ' if style else ''
        s += str(u) + line + style + str(v) + ';\n'
    tikzpicture = (
        r'\begin{tikzpicture}' '\n'
        '\graph[' + layout + ' layout, sibling distance=5.0cm,'
        # 'edge quotes mid,'
        'edges={nodes={sloped, inner sep=10pt}},'
        'nodes={circle,draw}]{\n' +
        s +
        '};\n'
        '\end{tikzpicture}\n')
    if not preamble:
        return tikzpicture
    if layout == 'layered':
        layout_lib = 'layered'
    elif layout == 'spring':
        layout_lib = 'force'
    else:
        raise ValueError('Unknown which library includes the layout: ' +
                         str(layout))
    document = (
        '\documentclass{minimal}\n'
        '\usepackage{amsmath}\n'
        '\n'
        '\usepackage{tikz}\n'
        '\usetikzlibrary{graphs,graphs.standard,graphdrawing,quotes,shapes}\n'
        '\usegdlibrary{' + layout_lib + '}\n'
        '\n'
        r'\begin{document}' '\n'
        '\n' +
        tikzpicture +
        '\end{document}\n')
    return document


def dump_tikz(g, fname):
    """Write TikZ picture as TeX file."""
    s = dumps_tikz(g)
    with open(fname, 'w') as f:
        f.write(s)



def dump_pdf(g, fname, use_label=True):
    opt = ['lualatex', '--jobname', fname]
    p = subprocess.Popen(opt, stdin=subprocess.PIPE)
    p.stdin.write(s)
    p.stdin.close()
    p.wait()

if __name__ == '__main__':
    g = Graph()
    # nodes
    g.add_node(1, label='$a$', color='yellow', shape='ellipse')
    g.add_node(2, label='$b$', color='blue', fill='orange', shape='circle')
    g.add_node(3, label='$c$', shape='rectangle')
    g.add_node(4, label='$E=mc^2$')
    g.add_node(5, label=r'$\begin{bmatrix} x_1\\ x_2\\ x_3\end{bmatrix}$')
    # edges
    g.add_edge(1, 2, label='$\{p\}$')
    g.add_edge(1, 3, label='$\{a,b\}$', color='purple')
    g.add_edge(3, 4, label=r'$\begin{matrix} x=1\\ y=2\\ z=10 \end{matrix}$')
    g.add_edge(4, 5)
    g.add_edge(5, 4, color='red')
    g.add_edge(2, 2, color='blue')
    g.add_edge(4, 1)
    desc = 'Convert a NetworkX graph to TikZ.'
    parser = argparse.ArgumentParser(prog='nx2tikz', description=desc)
    parser.add_argument('--format', '-f', help='output format',
                        choices={'pdf', 'tikz'}, default='pdf')
    opts = parser.parse_args()
    if opts.format == 'pdf':
        write_pdf(g, 'hehe')
    elif opts.format == 'tikz':
        s = dumps_tikz(g)
        print(s)
    else:
        raise Exception('Unknow output format: {f}'.format(f=opts.format))
