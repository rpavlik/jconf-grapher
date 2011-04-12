import xml.etree.cElementTree as et
import sys

links = []
definedNodes = []
usedNodes = []
filequeue = []

ns = "{http://www.vrjuggler.org/jccl/xsd/3.0/configuration}"

ignoredElements = ["input_manager",
	"display_system",
	"corba_remote_reconfig",
	"display_window" # for now, until we recurse into it to find the kb/mouse device, the user for surface projections, and proxies for simulator
	]

def sanitize(name):
	return name.replace(" ", "_").replace(".jconf", "").replace("/", "_").replace("\\", "_").replace(".", "_").replace("-", "_")

def outputNode(name, eltType = "", style = ""):
	if "proxy" in eltType:
		pass
	elif "alias" in eltType:
		style = style + "style=filled,color=lightgray,"
	elif "user" in eltType:
		style = style + "shape=egg,"
	else:
		style = style + "shape=box3d,"
	if eltType == "":
		label = name
	else:
		label = "%s\\n[%s]" % (name, eltType)
	print('%s [%slabel = "%s"];' % (sanitize(name), style, label))
def addNode(elt, style = ""):
	eltName = elt.get("name")
	eltType = elt.tag.replace(ns, "")
	definedNodes.append(sanitize(eltName))


	#print('%s [%slabel = <%s<br/><i>%s</i> >];' % (sanitize(eltName), style, eltName, eltType))
	outputNode(eltName, eltType, style)

def addLink(src, dest, label = None):
	usedNodes.extend([sanitize(src), sanitize(dest)])
	if label is None:
		links.append("%s -> %s;" % (sanitize(src), sanitize(dest)))
	else:
		links.append('%s -> %s [label = "%s"];' % (sanitize(src), sanitize(dest), label))

def handleAlias(elt):
	addLink(elt.get("name"), elt.findtext(ns + "proxy"))

def handleProxy(elt, proxyType = None):
	if proxyType is not None:
		label = proxyType
		unit = elt.findtext(ns + "unit")
		if unit is not None:
			label = "%s Unit %s" % (proxyType, unit)
		addLink(elt.get("name"), elt.findtext(ns + "device"), label)
	else:
		addLink(elt.get("name"), elt.findtext(ns + "device"))

def handleUser(elt):
	addLink(elt.get("name"), elt.findtext(ns + "head_position"), "Head Position")

def handleSimulated(elt):
	addLink(elt.get("name"), elt.findtext(ns + "keyboard_mouse_proxy"), "uses")

def processFile(filename):
	print("subgraph cluster_%s {" % sanitize(filename))

	print('label = "%s";' % filename)
	print('style = "dotted";')



	tree = et.parse(filename)
	root = tree.getroot()
	included = []

	for firstLevel in list(root):
		if firstLevel.tag == ns + "include":
			# recurse into included file
			processFile(firstLevel.text)

		elif firstLevel.tag == ns + "elements":

			for elt in list(firstLevel):
				# Some tags we ignore.
				if elt.tag in [ns + x for x in ignoredElements]:
					continue

				addNode(elt)
				if elt.tag == ns + "alias":
					handleAlias(elt)

				elif elt.tag == ns + "position_proxy":
					handleProxy(elt, "Position")

				elif elt.tag == ns + "analog_proxy":
					handleProxy(elt, "Analog")

				elif elt.tag == ns + "digital_proxy":
					handleProxy(elt, "Digital")

				elif elt.tag == ns + "keyboard_mouse_proxy":
					handleProxy(elt)

				elif elt.tag == ns + "user":
					handleUser(elt)

				elif ns + "simulated" in elt.tag:
					handleSimulated(elt)

		else:
			continue



	print("}")
	return included

def addUndefinedNodes():

	undefined = [ x for x in usedNodes if x not in definedNodes ]
	if len(undefined) > 0:
		print("subgraph cluster_undefined {")
		print('label = "Not defined in these files";')
		print('style = "dotted";')
		for node in undefined:
			outputNode(node, style = "style=dashed,")
		print("}")

def processFiles(files):

	print("digraph {")
	print('size="8.5,11"')
	print('ratio="compress"')
	for file in files:
		processFile(file)
	addUndefinedNodes()
	print( "\n".join(links))
	print("}")

if __name__ == "__main__":
	processFiles(sys.argv[1:])

