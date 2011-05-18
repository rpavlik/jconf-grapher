
import os

searchpath = []

subdirsOfShare = [ "vrjuggler-3.0",
	"vrjuggler-2.2",
	"vrjuggler"
	]

searchpath.append(os.getcwd())
# Use VJ_BASE_DIR to find additional search paths.
if "VJ_BASE_DIR" in os.environ:
	vj_base_dir = os.environ["VJ_BASE_DIR"]
	possibilities = [ os.path.join(vj_base_dir, confdir) for confdir in subdirsOfShare ]
	for fulldir in possibilities:
		if os.path.exists(fulldir):
			searchpath.append(fulldir)

class ConfigFileNotFoundError(Exception):
	def __init__(self, fn, usedpath):
		self.fn = fn
		self.usedpath = usedpath

	def __str__(self):
		return "Could not find config file %s in the search path! Searched: %s" % (self.fn, self.usedpath)

class AbsoluteConfigFileNotFound(Exception):
	def __init__(self, fn):
		self.fn = fn

	def __str__(self):
		return "Absolute path to config file specified, but %s does not exist!" % self.fn

def findInSearchPath(fn, extraSearchPaths=[]):
	"""Find a named file in the global config search path, as well as any additionally-passed optional ones."""
	# Handle absolute paths
	if os.path.isabs(fn):
		if not os.path.exists(fn):
			raise AbsoluteConfigFileNotFound(fn)
		return fn, os.path.dirname(fn), os.path.basename(fn)

	# not sure why this line is necessary...
	global searchpath

	# Create a list of paths to search this time
	paths = []
	paths.extend(searchpath)
	paths.extend(extraSearchPaths)
	for searchpath in paths:
		attempt = os.path.join(searchpath, fn)
		if os.path.exists(attempt):
			return attempt, os.path.dirname(attempt), fn

	# If we get this far we failed
	raise ConfigFileNotFoundError(fn, paths)

