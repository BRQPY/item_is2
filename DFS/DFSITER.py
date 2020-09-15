def dfs_iterative(graph, start_vertex):
    visited = set()
    traversal = []
    stack = [start_vertex]
    n =0

    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.add(vertex)
            traversal.append(vertex)
            stack.extend(reversed(graph[vertex]))
        else:
            n = n+1
            print("Se ha detectado un ciclo")
            return (traversal)
    print("No existen ciclos")
    return traversal

test_graph = {



    'A' : [],
    'B' : ['C'],
    'C' : ['A'],
    'D' : [],
    'S': []

}

print(dfs_iterative(test_graph, 'A'))

