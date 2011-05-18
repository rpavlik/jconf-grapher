#!/usr/bin/env python
# jconf2dot.py - parse a VR Juggler jconf file and output graphviz "dot"-format files
# Author: Ryan Pavlik

# https://github.com/rpavlik/jconf-grapher

#          Copyright Iowa State University 2011.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

import xml.etree.cElementTree as et
import sys
from find_jconf import findInSearchPath

ns = "{http://www.vrjuggler.org/jccl/xsd/3.0/configuration}"

def sanitize(name):
	"""Turn an arbitrary string into something we can use as an ID in a dot file"""
	return name.replace(" ", "_").replace(".jconf", "").replace("/", "_").replace("\\", "_").replace(".", "_").replace("-", "_")

class ConfigurationContext(object):
	ignoredElements = ["input_manager",
		"display_system",
		"corba_remote_reconfig",
		"display_window", # for now, until we recurse into it to find the kb/mouse device, the user for surface projections, and proxies for simulator
		"cluster_node", #ditto
		"cluster_manager",
		"start_barrier_plugin",
		"application_data"
		]
	def __init__(self, files):
		self.links = []
		self.definedNodes = []
		self.usedNodes = []
		self.fullPaths = []
		self.filequeue = []
		self.lines = []
		self.processFiles(files)



	def outputNode(self, name, eltType = "", style = ""):
		"""Print dot code to display a node as requested"""
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
		self.lines.append('%s [%slabel = "%s"];' % (sanitize(name), style, label))

	def addNode(self, elt, style = ""):
		"""Given an element, output the appropriate dot code for the node and mark it as 'recognized'"""
		eltName = elt.get("name")
		eltType = elt.tag.replace(ns, "")
		self.definedNodes.append(sanitize(eltName))


		#print('%s [%slabel = <%s<br/><i>%s</i> >];' % (sanitize(eltName), style, eltName, eltType))
		self.outputNode(eltName, eltType, style)

	def addLink(self, src, dest, label = None):
		"""Add a link between src and dest, with an optional label"""
		self.usedNodes.extend([sanitize(src), sanitize(dest)])
		if label is None:
			self.links.append("%s -> %s;" % (sanitize(src), sanitize(dest)))
		else:
			self.links.append('%s -> %s [label = "%s"];' % (sanitize(src), sanitize(dest), label))

	def handleAlias(self, elt):
		"""Add the link implied by an alias element."""
		self.addLink(elt.get("name"), elt.findtext(ns + "proxy"))

	def handleProxy(self, elt, proxyType = None):
		"""Add the link implied by a proxy element."""
		if proxyType is not None:
			label = proxyType
			unit = elt.findtext(ns + "unit")
			if unit is not None:
				label = "%s Unit %s" % (proxyType, unit)
			self.addLink(elt.get("name"), elt.findtext(ns + "device"), label)
		else:
			self.addLink(elt.get("name"), elt.findtext(ns + "device"))

	def handleUser(self, elt):
		"""Add the head position link implied by a user element."""
		self.addLink(elt.get("name"), elt.findtext(ns + "head_position"), "Head Position")

	def handleSimulated(self, elt):
		"""Add the kb/mouse proxy link implied by a simulated device element."""
		self.addLink(elt.get("name"), elt.findtext(ns + "keyboard_mouse_proxy"), "uses")

	def handleSimulatedRelativePosition(self, elt):
		"""Add the links implied by a simulated_relative_position element."""
		self.addLink(elt.get("name"), elt.findtext(ns + "base_frame_proxy"), "base frame")
		self.addLink(elt.get("name"), elt.findtext(ns + "relative_proxy"), "relative device")


	def processFile(self, arg):
		"""Print a cluster of nodes based on a jconf file, and process any links"""
		fullpath, directory, filename = arg
		self.fullPaths.append(fullpath)
		self.lines.append("subgraph cluster_%s {" % sanitize(filename))

		self.lines.append('label = "%s";' % filename)
		self.lines.append('style = "dotted";')

		tree = et.parse(fullpath)
		root = tree.getroot()
		included = []

		for firstLevel in list(root):
			if firstLevel.tag == ns + "include":
				# recurse into included file
				self.processFile(findInSearchPath(firstLevel.text, [directory]))

			elif firstLevel.tag == ns + "elements":

				for elt in list(firstLevel):
					# Some tags we ignore.
					if elt.tag in [ns + x for x in self.ignoredElements]:
						continue

					# Add nodes for the rest of the elements
					self.addNode(elt)

					# Some nodes contain information on relationships
					# that we want to depict in the graph.
					if elt.tag == ns + "alias":
						self.handleAlias(elt)

					elif elt.tag == ns + "position_proxy":
						self.handleProxy(elt, "Position")

					elif elt.tag == ns + "analog_proxy":
						self.handleProxy(elt, "Analog")

					elif elt.tag == ns + "digital_proxy":
						self.handleProxy(elt, "Digital")

					elif elt.tag == ns + "keyboard_mouse_proxy":
						self.handleProxy(elt)

					elif elt.tag == ns + "user":
						self.handleUser(elt)

					elif elt.tag == ns + "simulated_relative_position":
						self.handleSimulatedRelativePosition(elt)

					elif ns + "simulated" in elt.tag:
						self.handleSimulated(elt)

			else:
				continue



		self.lines.append("}")
		return included

	def addUndefinedNodes(self):
		"""Output all nodes referenced but not defined, with special formatting"""
		undefined = [ x for x in self.usedNodes if x not in self.definedNodes ]
		if len(undefined) > 0:
			self.lines.append("subgraph cluster_undefined {")
			self.lines.append('label = "Not defined in these files";')
			self.lines.append('style = "dotted";')
			for node in undefined:
				self.outputNode(node, style = "style=dashed,")
			self.lines.append("}")

	def processFiles(self, files):
		"""Process all jconf files passed, printing the complete dot output."""

		self.lines.append("digraph {")
		self.lines.append('size="8.5,11"')
		self.lines.append('ratio="compress"')
		for fn in files:
			self.processFile(findInSearchPath(fn))
		self.addUndefinedNodes()
		self.lines.append( "\n".join(self.links))
		self.lines.append("}")
		self.dotcode = "\n".join(self.lines)

if __name__ == "__main__":
	configs = ConfigurationContext(sys.argv[1:])
	print configs.dotcode

