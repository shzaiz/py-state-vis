from visualizer import *



# A typical program in data structure class

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class BinaryTree:
    def __init__(self):
        self.root = None

    def insert(self, value):
        if not self.root:
            self.root = TreeNode(value)
        else:
            self._insert_recursive(self.root, value)

    def _insert_recursive(self, node, value):
        
        if value < node.value:
            if node.left is None:
                node.left = TreeNode(value)
            else:
                self._insert_recursive(node.left, value)
        else:
            if node.right is None:
                node.right = TreeNode(value)
            else:
                self._insert_recursive(node.right, value)


# Trace function, call visualizer to inspect state
def trace_func(frame, event, arg):
    # avoid drawing too many states, only up to main function.
    # SURPRISE: The visualizer can visualize itself upon setting
    # valid_frames_frm to 0. (but the output will be really verbose).
    Visualizer().visualize_whole_state(valid_frames_frm=2, strict=True).write_png("test.png")
    input()
    return trace_func  


# set trace to invoke drawer function to inspect the state
sys.settrace(trace_func)

def main():
    # Create BST and insert into vals
    binary_tree = BinaryTree()
    values_to_insert = [2, 3, 1, 6, 4, 3]

    for value in values_to_insert:
        binary_tree.insert(value)

    # lst = [[0]*2]*2
    

main()


sys.settrace(None)
