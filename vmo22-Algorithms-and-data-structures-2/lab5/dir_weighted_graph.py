from collections import deque

class DirectedWeightedGraph:
    def __init__(self):
        self.adj_list = {}

    def add_vertex(self, vertex):
        if vertex not in self.adj_list:
            self.adj_list[vertex] = []

    def add_edge(self, from_vertex, to_vertex, weight=1):
        if from_vertex not in self.adj_list:
            self.add_vertex(from_vertex)
        if to_vertex not in self.adj_list:
            self.add_vertex(to_vertex)
        self.adj_list[from_vertex].append((to_vertex, weight))

    def read_from_file(self, filename):
        with open(filename, 'r', encoding = 'utf8') as f:
            lines = f.read().splitlines()

        mode = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.lower() == 'вершины:' or line.lower() == 'vertices:':
                mode = 'vertices'
                continue
            elif line.lower() == 'рёбра:' or line.lower() == 'edges:':
                mode = 'edges'
                continue

            if mode == 'vertices':
                self.add_vertex(line)
            elif mode == 'edges':
                parts = line.split()
                if len(parts) >= 3:
                    from_v, to_v, weight = parts[0], parts[1], float(parts[2])
                    self.add_edge(from_v, to_v, weight)

    def write_to_file(self, filename):
        with open(filename, 'w') as f:
            f.write('Вершины:\n')
            for v in self.adj_list:
                f.write(f'{v}\n')
            f.write('Рёбра:\n')
            for from_v, edges in self.adj_list.items():
                for to_v, w in edges:
                    f.write(f'{from_v} {to_v} {w}\n')

    def outdegree(self, vertex):
        if vertex in self.adj_list:
            return len(self.adj_list[vertex])
        return 0

    def indegree(self, vertex):
        count = 0
        for from_v, edges in self.adj_list.items():
            for to_v, _ in edges:
                if to_v == vertex:
                    count += 1
        return count

    def are_adjacent(self, v1, v2):
        if v1 in self.adj_list:
            for to_v, _ in self.adj_list[v1]:
                if to_v == v2:
                    return True
        return False

    def has_loops(self):
        for v, edges in self.adj_list.items():
            for to_v, _ in edges:
                if v == to_v:
                    return True
        return False

    def has_parallel_edges(self):
        for from_v, edges in self.adj_list.items():
            seen = set()
            for to_v, _ in edges:
                if to_v in seen:
                    return True
                seen.add(to_v)
        return False

    def dfs(self, start, visited=None, result=None):
        if visited is None:
            visited = set()
        if result is None:
            result = []
        visited.add(start)
        result.append(start)
        for (neighbor, _) in self.adj_list.get(start, []):
            if neighbor not in visited:
                self.dfs(neighbor, visited, result)
        return result

    def bfs(self, start):
        visited = set()
        queue = []
        result = []

        visited.add(start)
        queue.append(start)

        while queue:
            vertex = queue.pop(0)
            result.append(vertex)
            for (neighbor, _) in self.adj_list.get(vertex, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return result

    def shortest_path_by_edges(self, start, end):
        if start not in self.adj_list or end not in self.adj_list:
            return None

        queue = deque([start])
        visited = {start}
        parent = {start: None}

        while queue:
            current = queue.popleft()
            if current == end:
                path = []
                while current is not None:
                    path.append(current)
                    current = parent[current]
                return path[::-1]  

            for (neighbor, _) in self.adj_list[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)

        return None

graph = DirectedWeightedGraph()

graph.add_edge('A', 'B', 5)
graph.add_edge('A', 'C', 3)
graph.add_edge('B', 'C', 2)
graph.add_edge('C', 'A', 4)  
graph.add_edge('C', 'D', 4)
graph.add_edge('D', 'E', 4)
graph.add_edge('B', 'E', 4)
print('Indegree of A:', graph.indegree('A'))   
print('Outdegree of A:', graph.outdegree('A'))

print('Are A and B adjacent?', graph.are_adjacent('A', 'B'))
print('Are B and A adjacent?', graph.are_adjacent('B', 'A'))  

print('Graph has loops?', graph.has_loops())  

graph.add_edge('C', 'C', 1)
print('Graph has loops after adding loop on C?', graph.has_loops())  

print('Graph has parallel edges?', graph.has_parallel_edges())  

graph.add_edge('A', 'B', 7)
print('Graph has parallel edges after adding parallel edge A->B?', graph.has_parallel_edges())

#graph.write_to_file('graph.txt')

new_graph = DirectedWeightedGraph()
#new_graph.read_from_file('graph.txt')

#print('Edges in new graph from A:', new_graph.adj_list['A'])


print("DFS from A:", graph.dfs('A'))  
print("BFS from A:", graph.bfs('A'))  

print(f'\n\nСписок смежности:\n')
for line in graph.adj_list:
    print(line, graph.adj_list[line])

path = graph.shortest_path_by_edges('A', 'E')
print("\n\nShortest path by edges from A to E:", path)
