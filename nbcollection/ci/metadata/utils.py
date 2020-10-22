from nbcollection.ci.datatypes import BuildJob

def reset_notebook_execution(job: BuildJob) -> None:
    # https://gist.github.com/autodrive/cb05134b68205e4b94335dd67fe16023#file-ipynb_remove_output-py-L30
    import pdb; pdb.set_trace()
    pass
