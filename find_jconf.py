
import os

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


	# Create a list of paths to search this time
	paths = []
	paths.extend(jconfSearchPath)
	paths.extend(extraSearchPaths)
	for searchpath in paths:
		attempt = os.path.join(searchpath, fn)
		if os.path.exists(attempt):
			return attempt, os.path.dirname(attempt), fn

	# If we get this far we failed
	raise ConfigFileNotFoundError(fn, paths)

def __createSearchPath():
	mypath = []

	# Search current directory
	mypath.append(os.getcwd())

	# Search in JCCL_CFG_PATH and VJ_CFG_PATH
	if "JCCL_CFG_PATH" in os.environ:
		mypath.extend([path for path in os.environ["JCCL_CFG_PATH"].split(os.pathsep) if not path == ""])
	if "VJ_CFG_PATH" in os.environ:
		mypath.extend([path for path in os.environ["VJ_CFG_PATH"].split(os.pathsep) if not path == ""])

	# Search relative to $VJ_DATA_DIR/data/configFiles, if set
	if "VJ_DATA_DIR" in os.environ:
		possibility = os.path.join(os.environ["VJ_DATA_DIR"], "data/configFiles")
		if os.path.exists(possibility):
			mypath.append(possibility)

	# Use VJ_BASE_DIR (defaulting to /usr) to find additional search paths.
	vj_base_dir = "/usr"
	if "VJ_BASE_DIR" in os.environ:
		vj_base_dir = os.environ["VJ_BASE_DIR"]

	subdirsOfShare = [ "vrjuggler-3.0",
		"vrjuggler-2.2",
		"vrjuggler"
		]

	possibilities = [ os.path.join(vj_base_dir, "share", confdir, "data/configFiles") for confdir in subdirsOfShare ]
	for fulldir in possibilities:
		if os.path.exists(fulldir):
			mypath.append(fulldir)

	return [ os.path.normcase(os.path.normpath(eachDir)) for eachDir in mypath ]
jconfSearchPath = __createSearchPath()
