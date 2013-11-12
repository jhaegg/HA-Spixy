import re

_format_pattern = "(\{\{([A-Za-z0-9]+):(.*)\}\})"

def parse(format, string):
	# Get all {{entry: regex}}
	res = {}
	subst = {}
	for grp, match in enumerate(re.finditer(_format_pattern, format), start=1):
		full, key, pattern = match.group(1, 2, 3)
		res[grp] = key
		subst[full] = pattern

	# Replace {entry: regex} with (regex)
	pattern = re.compile('|'.join([re.escape(x) for x in subst.keys()]))
	repl = pattern.sub(lambda x: '(%s)' % subst[x.group()], format)

	# Match, retrieve and dictify; easy as $\pi$
	match = re.match(repl, string)

	if match:
		return {k: match.group(g) for g, k in res.items()}
	else:
		return {}
