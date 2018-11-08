import os
import jinja2


def make_html_index(converted_files, html_template, outfn='index.html',
                    relpaths=True):
    path, fn = os.path.split(html_template)
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(path),
                             autoescape=jinja2.select_autoescape(['html', 'xml']))
    templ = env.get_template(fn)

    if relpaths:
        outdir = os.path.realpath(os.path.dirname(outfn))
        converted_files = [os.path.relpath(os.path.realpath(pth), outdir)
                           for pth in converted_files]

    with open(outfn, 'w') as f:
        f.write(templ.render(notebook_html_paths=converted_files))
