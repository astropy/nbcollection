import os
import jinja2
import collections


def make_html_index(converted_files, html_template, outfn='index.html',
                    relpaths=True):
    """
    Generates an html index page for a set of notebooks

    Parameters
    ----------
    converted_files : list
        The list of paths to the notebooks
    html_template : str
        A path to the template file to be used for generating the index. The
        template should be in jinja2 format and have a loop over
        ``notebook_html_paths`` to populate with the links
    outfn : str or None
        the output file name, or None to not write the file
    relpaths : bool
        If True, the paths are all passed in as relative paths with respect to
        ``outfn`` if given or the current directory (if ``outfn`` is None)

    Returns
    -------
    content : str
        The content of the index file
    """
    if not converted_files:
        return None

    path, fn = os.path.split(html_template)
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(path),
                             autoescape=jinja2.select_autoescape(['html', 'xml']))
    templ = env.get_template(fn)

    if relpaths:
        outdir = os.path.realpath(os.path.dirname(outfn) if outfn else os.path.curdir)

        if isinstance(converted_files[0], str):
            converted_file_paths = [os.path.relpath(os.path.realpath(page), outdir)
                               for page in converted_files]
            converted_file_dicts = [dict(output_file_path=os.path.relpath(os.path.realpath(page), outdir), name=page, title=page)
                               for page in converted_files]
        else:
            converted_file_paths = [os.path.relpath(os.path.realpath(page['output_file_path']), outdir)
                               for page in converted_files]
            converted_file_dicts = [dict(output_file_path=os.path.relpath(os.path.realpath(page['output_file_path']), outdir), name=page['name'], title=page['title'])
                               for page in converted_files]
    else:
        if isinstance(converted_files[0], str):
            converted_file_paths = converted_files
            converted_file_dictss = [dict(output_file_path=page, name=page, title=page)
                               for page in converted_files]
        else:
            converted_file_paths = [x['output_file_path'] for x in converted_files]
            converted_file_dicts = [converted_files]

    # sorts notebooks into "groups" of their parent directories
    result = collections.defaultdict(list)
    for d in converted_file_dicts:
        result[d['output_file_path'].split("/")[1]].append(d)
        converted_file_dicts = list(result.values())

    content = templ.render(notebook_html_paths=converted_file_paths, page_groups=converted_file_dicts)
    if outfn:
        with open(outfn, 'w') as f:
            f.write(content)

    return content
