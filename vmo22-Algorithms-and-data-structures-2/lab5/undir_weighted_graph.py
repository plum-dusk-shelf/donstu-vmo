class WeightedUndirectedGraph:
    def __init__(self):
        # Словарь вершин: ключ - вершина, значение - словарь смежных вершин с весами
        self.adj = {}

    def add_vertex(self, v):
        if v not in self.adj:
            self.adj[v] = {}

    def add_edge(self, v1, v2, weight=1):
        # Добавляем вершины, если их нет
        self.add_vertex(v1)
        self.add_vertex(v2)
        # Добавляем ребро в обе стороны (неориентированный)
        self.adj[v1][v2] = weight
        self.adj[v2][v1] = weight

    def degree(self, v):
        # Степень вершины - количество смежных вершин
        if v in self.adj:
            return len(self.adj[v])
        else:
            return 0

    def are_adjacent(self, v1, v2):
        # Проверка смежности двух вершин
        return v1 in self.adj and v2 in self.adj[v1]

    def has_loops(self):
        # Проверка наличия петель (ребро из вершины в саму себя)
        for v in self.adj:
            if v in self.adj[v]:
                return True
        return False

    def has_parallel_edges(self):
        # В списке смежности параллельных ребер быть не может,
        # но если бы была другая структура, можно было бы проверять.
        # Здесь всегда False, так как словарь хранит одно ребро между двумя вершинами.
        return False

    def _dfs_cycle(self, v, visited, parent):
        visited.add(v)
        for neighbor in self.adj[v]:
            if neighbor not in visited:
                if self._dfs_cycle(neighbor, visited, v):
                    return True
            elif neighbor != parent:
                return True
        return False

    def has_cycle(self):
        # Проверка наличия циклов с помощью DFS
        visited = set()
        for v in self.adj:
            if v not in visited:
                if self._dfs_cycle(v, visited, None):
                    return True
        return False

    def read_from_file(self, filename):
        # Формат файла: каждая строка "v1 v2 weight"
        with open(filename, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 3:
                    v1, v2, w = parts[0], parts[1], float(parts[2])
                    self.add_edge(v1, v2, w)

    def write_to_file(self, filename):
        # Записываем ребра в файл, чтобы не дублировать (v1,v2) и (v2,v1),
        # выводим только v1 < v2 по лексикографическому порядку
        edges_written = set()
        with open(filename, 'w') as f:
            for v1 in self.adj:
                for v2, w in self.adj[v1].items():
                    if (v2, v1) not in edges_written:
                        f.write(f"{v1} {v2} {w}\n")
                        edges_written.add((v1, v2))

# Создаем объект графа
graph = WeightedUndirectedGraph()

# Добавляем вершины
graph.add_vertex("A")
graph.add_vertex("B")
graph.add_vertex("C")

# Добавляем ребра с весами
graph.add_edge("A", "B", 5)
graph.add_edge("B", "C", 3)
graph.add_edge("C", "A", 4)

# Проверяем степень вершины
print("Степень вершины A:", graph.degree("A"))  # Вывод: 2

# Проверяем смежность вершин
print("Вершины A и B смежны?", graph.are_adjacent("A", "B"))  # True
print("Вершины A и D смежны?", graph.are_adjacent("A", "D"))  # False

# Проверяем наличие петель
print("Есть ли петли?", graph.has_loops())  # False

# Проверяем наличие параллельных ребер
print("Есть ли параллельные ребра?", graph.has_parallel_edges())  # False

# Проверяем наличие циклов
print("Есть ли циклы?", graph.has_cycle())  # True, так как A-B-C-A образуют цикл

# Записываем граф в файл
graph.write_to_file("graph.txt")

# Создаем новый граф и читаем из файла
new_graph = WeightedUndirectedGraph()
new_graph.read_from_file("graph.txt")

# Проверяем, что граф считан корректно
print("Степень вершины B в новом графе:", new_graph.degree("B"))  # 2

