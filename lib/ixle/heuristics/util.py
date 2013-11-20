""" ixle.heuristics.util
"""
def _generic(item, r_list):
    # NOTE: assumes file_magic already ready already
    if item.file_magic:
        for x in item.file_magic:
            for y in r_list:
                if y.match(x):
                    return True
