import re
from .key_default_dict import KeyDefaultDict

_format_pattern = r"(\{\{([A-Za-z0-9]+):(.+?(?=\}\}))\}\})"


# TODO: Implement type support
def _build_format(format):
    resolution = {}
    subst = {}
    observed = set([])

    # Get all {{entry: regex}}
    for grp, match in enumerate(re.finditer(_format_pattern, format), start=1):
        full, key, pattern = match.group(1, 2, 3)
        if key in observed:
            raise RuntimeError("Duplicate parameter %s" % key)
        observed.add(key)
        resolution[grp] = key
        subst[full] = pattern

    # Replace {entry: regex} with (regex)
    pattern = re.compile('|'.join([re.escape(x) for x in subst.keys()]))
    # Store resolution and pattern in flywheel
    return resolution, pattern.sub(lambda x: '(%s)' % subst[x.group()], format)


_format_flywheel = KeyDefaultDict(_build_format)


def parse(format, string):
    # Fetch or build resolution and pattern from string
    resolution, pattern = _format_flywheel[format]

    # Match, retrieve and dictify; easy as $\pi$
    match = re.match(pattern, string)

    if match:
        return {k: match.group(g) for g, k in resolution.items()}
    else:
        return None
