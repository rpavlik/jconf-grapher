import xml.etree.cElementTree as et

elements = {}
links = []
nodes = {}
nodecount = 0


ns = "{http://www.vrjuggler.org/jccl/xsd/3.0/configuration}"


def sanitize(name):
	return name.replace(" ", "_").replace(".jconf", "").replace("/", "_").replace("\\", "_")

def processFile(filename):
	print("subgraph cluster_%s {" % sanitize(filename))

	print('label = "%s";' % filename)



	tree = et.parse(filename)
	root = tree.getroot()
	print root


	for firstLevel in list(root):
		print firstLevel
		if firstLevel.tag != ns + "elements":
			continue

		for elt in list(firstLevel):
			eltName = elt.get("name")
			print('%s [label = "%s"];' % (sanitize(eltName), eltName))
			print(elt)
			print(elt.get("name"))
			#elements[elt.get("name")] = elt
			if elt.tag == ns + "alias":
				print("this is an alias")

	print("}")



	print "--------"

	elements = root.get("{http://www.vrjuggler.org/jccl/xsd/3.0/configuration}elements")
	print elements



print("digraph {")

processFile('IS900TwoWall.jconf')
print("}")
