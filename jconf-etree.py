import xml.etree.cElementTree as et

elements = {}
links = []
nodes = {}
nodecount = 0


ns = "{http://www.vrjuggler.org/jccl/xsd/3.0/configuration}"


def sanitize(name):
	return name.replace(" ", "_").replace(".jconf", "").replace("/", "_").replace("\\", "_")

def addLink(src, dest, label = None):
	if label is None:
		links.append("%s -> %s;" % (sanitize(src), sanitize(dest)))
	else:
		links.append('%s -> %s [label = "%s"];' % (sanitize(src), sanitize(dest), label))

def handleAlias(elt):
	addLink(elt.get("name"), list(elt)[0].text)
def processFile(filename):
	print("subgraph cluster_%s {" % sanitize(filename))

	print('label = "%s";' % filename)



	tree = et.parse(filename)
	root = tree.getroot()

	for firstLevel in list(root):
		if firstLevel.tag != ns + "elements":
			# This means it's an include - want to handle these eventually
			continue

		for elt in list(firstLevel):
			eltName = elt.get("name")
			print('%s [label = "%s"];' % (sanitize(eltName), eltName))
			if elt.tag == ns + "alias":
				handleAlias(elt)
			
				

	print("}")



print("digraph {")

processFile('IS900TwoWall.jconf')
print( "\n".join(links))
print("}")
