import xml.etree.cElementTree as et

links = []
definedNodes = []
usedNodes = []
filequeue = []

ns = "{http://www.vrjuggler.org/jccl/xsd/3.0/configuration}"

ignoredElements = ["input_manager", "display_system"]

def sanitize(name):
	return name.replace(" ", "_").replace(".jconf", "").replace("/", "_").replace("\\", "_")

def addNode(elt):
	eltName = elt.get("name")
	eltType = elt.tag.replace(ns, "")
	definedNodes.append(sanitize(eltName))
	style = ""
	if "proxy" in elt.tag:
		pass
	elif "alias" in elt.tag:
		pass
	else:
		style = style + "shape=box,"

	#print('%s [%slabel = <%s<br/><i>%s</i> >];' % (sanitize(eltName), style, eltName, eltType))
	print('%s [%slabel = "%s\\n[%s]"];' % (sanitize(eltName), style, eltName, eltType))

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



	tree = et.parse(filename)
	root = tree.getroot()

	for firstLevel in list(root):
		if firstLevel.tag == ns + "include":
			filequeue.push(firstLevel.text)
			# todo add an edge indicating the include relationship
			#links.append("

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
					handleProxy(elt, "Keyboard/Mouse")

				elif elt.tag == ns + "user":
					handleUser(elt)

				elif ns + "simulated" in elt.tag:
					handleSimulated(elt)

		else:
			continue



	print("}")

def addUndefinedNodes():

	undefined = [ '%s [label="%s",style=dotted];' % (sanitize(x), x)
		for x in usedNodes if x not in definedNodes ]
	if len(undefined) > 0:
		print("subgraph cluster_undefined {")

		print('label = "Not defined in these files";')
		print("\n".join(undefined))
		print("}")

def processFiles(files):

	print("digraph {")
	#print('page="8.5,11"')
	filequeue = files
	while len(filequeue) > 0:
		current = filequeue.pop()
		processFile(current)
	addUndefinedNodes()
	print( "\n".join(links))
	print("}")

processFiles(['IS900TwoWall.jconf'])

