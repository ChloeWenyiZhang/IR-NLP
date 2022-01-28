class Node:
    def __init__(self, order):
        self.keys = []
        self.children = []
        self.leaf = True
        self._t = order

    def split(self, parent, payload):
        new_node = self.__class__(self._t)

        mid_point = self.size // 2
        split_value = self.keys[mid_point]
        parent.add_key(split_value)

        # Add keys and children to appropriate nodes
        new_node.children = self.children[mid_point + 1:]
        self.children = self.children[:mid_point + 1]
        new_node.keys = self.keys[mid_point + 1:]
        self.keys = self.keys[:mid_point]

        # If the new_node has children, set it as internal node
        if len(new_node.children) > 0:
            new_node.leaf = False

        parent.children = parent.add_child(new_node)
        if payload < split_value:
            return self
        else:
            return new_node

    @property
    def _is_full(self):
        return self.size == 2 * self._t - 1

    @property
    def size(self):
        return len(self.keys)

    def add_key(self, value):
        """Add a key to a node. The node will have room for the key by definition."""
        self.keys.append(value)
        self.keys.sort()

    def add_child(self, new_node):
        """
        Add a child to a node. This will sort the node's children, allowing for children
        to be ordered even after middle nodes are split.
        returns: an order list of child nodes
        """
        i = len(self.children) - 1
        while i >= 0 and self.children[i].keys[0] > new_node.keys[0]:
            i -= 1
        return self.children[:i + 1] + [new_node] + self.children[i + 1:]


class BTree:
    def __init__(self, t):
        """
        Create the B-tree. t is the order of the tree. Tree has no keys when created.
        This implementation allows duplicate key values, although that hasn't been checked
        strenuously.
        """
        self._t = t
        if self._t <= 1:
            raise ValueError("B-Tree must have a degree of 2 or more.")
        self.root = Node(t)

    def insert(self, payload):
        """Insert a new key of value payload into the B-Tree."""
        node = self.root
        # Root is handled explicitly since it requires creating 2 new nodes instead of the usual one.
        if node._is_full:
            new_root = Node(self._t)
            new_root.children.append(self.root)
            new_root.leaf = False
            # node is being set to the node containing the ranges we want for payload insertion.
            node = node.split(new_root, payload)
            self.root = new_root
        while not node.leaf:
            i = node.size - 1
            while i > 0 and payload < node.keys[i]:
                i -= 1
            if payload > node.keys[i]:
                i += 1

            next = node.children[i]
            if next._is_full:
                node = next.split(node, payload)
            else:
                node = next
        # Since we split all full nodes on the way down, we can simply insert the payload in the leaf.
        node.add_key(payload)

    def search(self, value, node=None):
        """Return True if the B-Tree contains a key that matches the value."""
        if node is None:
            node = self.root
        if value in node.keys:
            return True
        elif node.leaf:
            # If we are in a leaf, there is no more to check.
            return False
        else:
            i = 0
            while i < node.size and value > node.keys[i]:
                i += 1
            return self.search(value, node.children[i])

    def print_order(self):
        """Print an level-order representation."""
        this_level = [self.root]
        store_size = 0
        while this_level:
            next_level = []
            output = ""
            for node in this_level:
                if node.children:
                    store_size += 8 * len(node.children)
                    next_level.extend(node.children)
                for key in node.keys:
                    store_size += len(key)
                output += str(node.keys) + " "
            # print(output)
            this_level = next_level
        return store_size

    def get_suffix(self, prefix, node=None):
        if node is None:
            node = self.root
        if node.leaf:
            return []
        else:
            prefix_len = len(prefix)
            for i in range(node.size):
                if prefix == node.keys[i][:prefix_len]:
                    result_list = self.get_match(prefix, node, i)
                    return result_list
                elif prefix < node.keys[i][:prefix_len]:
                    return self.get_suffix(prefix, node.children[i])
            if prefix > node.keys[node.size - 1][:prefix_len]:
                return self.get_suffix(prefix, node.children[node.size])

    def get_match(self, prefix, node, match_pos):
        match_list = []
        match_list.append(node.keys[match_pos])
        prefix_len = len(prefix)
        if len(node.children) > match_pos:
            left_node = node.children[match_pos]
            if left_node is not None:
                last_match = left_node.size
                for i in range(left_node.size):
                    i = left_node.size - i - 1
                    if prefix == left_node.keys[i][:prefix_len]:
                        last_match = i
                        submatch_list = self.get_match(prefix, left_node, i)
                        match_list.extend(submatch_list)
                if len(left_node.children) > last_match:
                    submatch_list = self.check_right(prefix, left_node.children[last_match])
                    match_list.extend(submatch_list)
        if len(node.children) > match_pos + 1:
            right_node = node.children[match_pos + 1]
            if right_node is not None:
                last_match = 0
                for i in range(right_node.size):
                    if prefix == right_node.keys[i][:prefix_len]:
                        last_match = i
                        submatch_list = self.get_match(prefix, right_node, i)
                        match_list.extend(submatch_list)
                if len(right_node.children) > last_match:
                    submatch_list = self.check_left(prefix, right_node.children[last_match])
                    match_list.extend(submatch_list)
        return match_list

    def check_right(self, prefix, node):
        prefix_len = len(prefix)
        match_cnt = 0
        match_list = []
        for i in range(node.size):
            if prefix == node.keys[i][:prefix_len]:
                match_cnt += 1
                submatch_list = self.get_match(prefix, node, i)
                match_list.extend(submatch_list)
        if match_cnt == 0 and len(node.children) > node.size:
            submatch_list = self.check_right(prefix, node.children[node.size])
            match_list.extend(submatch_list)
        return match_list

    def check_left(self, prefix, node):
        prefix_len = len(prefix)
        match_cnt = 0
        match_list = []
        for i in range(node.size):
            if prefix == node.keys[i][:prefix_len]:
                match_cnt += 1
                submatch_list = self.get_match(prefix, node, i)
                match_list.extend(submatch_list)
        if match_cnt == 0 and len(node.children) > 0:
            submatch_list = self.check_left(prefix, node.children[0])
            match_list.extend(submatch_list)
        return match_list

