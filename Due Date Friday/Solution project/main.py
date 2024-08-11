class QueryNode:
    def __init__(self, operation, children=None):
        self.operation = operation
        self.children = children if children else []

    def __repr__(self, level=0):
        ret = "\t" * level + repr(self.operation) + "\n"
        for child in self.children:
            ret += child.__repr__(level + 1)
        return ret

class SQLQueryOptimizer:
    def __init__(self, query):
        self.query = query
        self.canonical_tree = None
        self.optimized_tree = None

    def build_initial_tree(self):
        # Hardcoding the initial tree structure for the example query
        product_filter = QueryNode("σ(x.price > 100)", [QueryNode("Product")])
        customer_filter = QueryNode("σ(z.city = 'Seattle')", [QueryNode("Customer")])
        join_purchase_customer = QueryNode("⨝(y.cid = z.cid)", [QueryNode("Purchase"), customer_filter])
        join_product_purchase = QueryNode("⨝(x.pid = y.pid)", [product_filter, join_purchase_customer])
        projection = QueryNode("π(x.name, y.name)", [join_product_purchase])
        self.canonical_tree = QueryNode("δ(DISTINCT)", [projection])

    def apply_heuristics(self, node):
        # Example heuristic: pushing selections down
        if node.operation.startswith("⨝"):
            left_child, right_child = node.children
            if isinstance(left_child, QueryNode) and isinstance(right_child, QueryNode):
                left_child = self.apply_heuristics(left_child)
                right_child = self.apply_heuristics(right_child)
                return QueryNode(node.operation, [left_child, right_child])
        elif node.operation.startswith("π") or node.operation.startswith("δ"):
            child = node.children[0]
            optimized_child = self.apply_heuristics(child)
            return QueryNode(node.operation, [optimized_child])
        else:
            return node

    def optimize(self):
        self.optimized_tree = self.apply_heuristics(self.canonical_tree)

    def tree_to_sql(self, node):
        if node.operation.startswith("σ"):
            return f"SELECT * FROM {node.children[0].operation} WHERE {node.operation[2:]}"
        elif node.operation.startswith("π"):
            return f"SELECT {node.operation[2:]} FROM ({self.tree_to_sql(node.children[0])})"
        elif node.operation.startswith("⨝"):
            return f"SELECT * FROM {node.children[0].operation} JOIN {node.children[1].operation} ON {node.operation[2:]}"
        elif node.operation.startswith("δ"):
            return f"SELECT DISTINCT {node.children[0].operation} FROM ({self.tree_to_sql(node.children[0])})"
        else:
            return node.operation

    def output_results(self):
        print("Initial Canonical Query Tree:")
        print(self.canonical_tree)
        print("\nOptimized Query Tree:")
        print(self.optimized_tree)
        print("\nRefined SQL Query:")
        print(self.tree_to_sql(self.optimized_tree))


if __name__ == "__main__":
    query = "SELECT DISTINCT x.name, y.name FROM Product x, Purchase y, Customer z WHERE x.pid = y.pid AND y.cid = z.cid AND x.price > 100 AND z.city = 'Seattle'"
    optimizer = SQLQueryOptimizer(query)
    optimizer.build_initial_tree()
    optimizer.optimize()
    optimizer.output_results()
