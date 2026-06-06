class Node:
    def __init__(self, val = 0, left = None, right = None):
        self.left = left
        self.right = right
        self.val = val

def solution(root: Node) -> Node:
    """
    Transforms a binary tree according to the illustrated rule by manipulating its nodes.

    Parameters:
        root (Node): The root node of the input binary tree.

    Returns:
        Node: The root node of the transformed binary tree.
    """
    if root is None:
        return None
    left_val = solution(root.left)
    right_val = solution(root.right)
    # return true only if one of the left or right child is not None
    if left_val or right_val:
        if left_val is None or right_val is None:
            root.val = -root.val

    return root 
