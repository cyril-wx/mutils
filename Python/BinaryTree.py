#! coding: utf-8


# 节点
class Node(dict):
	def __init__(self, nodeV=None, lchild=dict(), rchild=dict()):
		self.node = {nodeV: [lchild, rchild]}

# 树
class BinaryTree(object):

	root = Node()
	def __init__(self, root):
		self.root = root

	def add(self, nodeV):
		if not self.root.keys():
			self.root = {nodeV:[Node(), Node()]}
		else:
			c_node = self.root
			#while c_node.values()[0][0] and c_node.values()[0][1]:
			while c_node:
				if nodeV > c_node.keys()[0]:
					c_node = c_node.values()[0][1]
				elif nodeV < c_node.keys()[0]:
					c_node = c_node.values()[0][0]

			#print("set c_node:%s to new_node:%s" %(c_node, new_node))
			c_node.setdefault(nodeV, [Node(), Node()])

node = Node()
bt = BinaryTree(node)

print (bt.root)

bt.add(1)
print (bt.root)

bt.add(9)
print (bt.root)

bt.add(3)
print (bt.root)




