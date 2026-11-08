from collections import deque, defaultdict

class DirectedGraph:
    def __init__(self):
        self.graph = defaultdict(list)  # adjacency list representation

    def add_vertex(self, v):
        if v not in self.graph:
            self.graph[v] = []

    def add_edge(self, from_v, to_v):
        if from_v in self.graph and to_v in self.graph:
            self.graph[from_v].append(to_v)

    def read_from_file(self, filename):
        self.graph.clear()
        with open(filename, 'r') as f:
            # Expect file format: each line "from to"
            for line in f:
                from_v, to_v = line.strip().split()
                self.add_vertex(from_v)
                self.add_vertex(to_v)
                self.add_edge(from_v, to_v)

    def write_to_file(self, filename):
        with open(filename, 'w') as f:
            for from_v, to_list in self.graph.items():
                for to_v in to_list:
                    f.write(f"{from_v} {to_v}\n")

    def dfs(self, start):
        visited = set()
        result = []

        def _dfs(v):
            visited.add(v)
            result.append(v)
            for neighbor in self.graph[v]:
                if neighbor not in visited:
                    _dfs(neighbor)

        if start in self.graph:
            _dfs(start)
        return result

    def bfs(self, start):
        visited = set()
        queue = deque([start])
        result = []
        visited.add(start)

        while queue:
            v = queue.popleft()
            result.append(v)
            for neighbor in self.graph[v]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return result

    def in_degree(self, v):
        # Count how many edges come into v
        count = 0
        for from_v, to_list in self.graph.items():
            if v in to_list:
                count += to_list.count(v)
        return count

    def out_degree(self, v):
        # Count how many edges go out from v
        if v in self.graph:
            return len(self.graph[v])
        return 0

    def are_adjacent(self, v1, v2):
        # Check if there is an edge from v1 to v2
        return v2 in self.graph.get(v1, [])

    def has_loops(self):
        # Check if any vertex has an edge to itself
        for v, to_list in self.graph.items():
            if v in to_list:
                return True
        return False

    def has_parallel_edges(self):
        # Check if any vertex has duplicate edges to the same vertex
        for v, to_list in self.graph.items():
            seen = set()
            for to_v in to_list:
                if to_v in seen:
                    return True
                seen.add(to_v)
        return False

    def has_cycle(self):
        # Detect cycle using DFS with coloring method:
        # 0 = unvisited, 1 = visiting, 2 = visited
        color = {v: 0 for v in self.graph}

        def dfs_cycle(v):
            color[v] = 1  # visiting
            for neighbor in self.graph[v]:
                if color[neighbor] == 0:
                    if dfs_cycle(neighbor):
                        return True
                elif color[neighbor] == 1:
                    return True  # found cycle
            color[v] = 2  # visited
            return False

        for vertex in self.graph:
            if color[vertex] == 0:
                if dfs_cycle(vertex):
                    return True
        return False

# Создание графа и добавление вершин и рёбер
g = DirectedGraph()
for vertex in ["A", "B", "C", "D"]:
    g.add_vertex(vertex)

g.add_edge("A", "B")
g.add_edge("A", "C")
g.add_edge("B", "D")
g.add_edge("C", "D")

# Обходы графа
print("DFS from A:", g.dfs("A"))  # Пример вывода: ['A', 'B', 'D', 'C']
print("BFS from A:", g.bfs("A"))  # Пример вывода: ['A', 'B', 'C', 'D']

# Полустепени захода и исхода
print("In-degree of D:", g.in_degree("D"))    # 2 (из B и C)
print("Out-degree of A:", g.out_degree("A"))  # 2 (в B и C)

# Проверка смежности
print("Are A and B adjacent?", g.are_adjacent("A", "B"))  # True
print("Are B and A adjacent?", g.are_adjacent("B", "A"))  # False

# Проверка наличия петель и параллельных рёбер
print("Has loops?", g.has_loops())               # False
print("Has parallel edges?", g.has_parallel_edges())  # False

# Проверка наличия циклов
print("Has cycle?", g.has_cycle())  # False

# Запись графа в файл и чтение из файла
g.write_to_file("graph.txt")
g2 = DirectedGraph()
g2.read_from_file("graph.txt")
print("Graph read from file DFS from A:", g2.dfs("A"))

