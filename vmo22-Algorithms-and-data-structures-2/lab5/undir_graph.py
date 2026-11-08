class UndirectedGraph:
    def __init__(self):
        # Используем словарь: ключ - вершина, значение - список смежных вершин
        self.adj = {}

    def add_vertex(self, v):
        if v not in self.adj:
            self.adj[v] = []

    def add_edge(self, v1, v2):
        # Добавляем вершины, если их нет
        self.add_vertex(v1)
        self.add_vertex(v2)
        # Добавляем ребро (двунаправленное)
        self.adj[v1].append(v2)
        self.adj[v2].append(v1)

    def degree(self, v):
        # Степень вершины - количество инцидентных ребер
        # Петля учитывается дважды, т.к. вершина дважды встречается в списке смежности
        if v not in self.adj:
            return 0
        return len(self.adj[v])

    def are_adjacent(self, v1, v2):
        # Проверка смежности: есть ли ребро между v1 и v2
        return v1 in self.adj and v2 in self.adj[v1]

    def has_loops(self):
        # Проверка на петли: ребро вида (v,v)
        for v in self.adj:
            if v in self.adj[v]:
                return True
        return False

    def has_parallel_edges(self):
        # Проверка на параллельные ребра: повторяющиеся соседи в списке смежности
        for v in self.adj:
            neighbors = self.adj[v]
            if len(neighbors) != len(set(neighbors)):
                return True
        return False

    def has_cycles(self):
        # Проверка на циклы с помощью DFS
        visited = set()

        def dfs(v, parent):
            visited.add(v)
            for u in self.adj[v]:
                if u not in visited:
                    if dfs(u, v):
                        return True
                elif u != parent:
                    # Найден цикл
                    return True
            return False

        for vertex in self.adj:
            if vertex not in visited:
                if dfs(vertex, None):
                    return True
        return False

    def read_from_file(self, filename):
        # Ожидается формат: число вершин n, число рёбер m,
        # затем m строк с двумя вершинами ребра
        with open(filename, 'r') as f:
            n, m = map(int, f.readline().split())
            self.adj = {}
            for _ in range(m):
                v1, v2 = f.readline().split()
                self.add_edge(v1, v2)

    def write_to_file(self, filename):
        # Записываем в файл список рёбер без дублирования (v1 < v2)
        edges = set()
        for v in self.adj:
            for u in self.adj[v]:
                if v <= u:
                    edges.add((v, u))
                else:
                    edges.add((u, v))
        with open(filename, 'w') as f:
            f.write(f"{len(self.adj)} {len(edges)}\n")
            for v1, v2 in edges:
                f.write(f"{v1} {v2}\n")


def adjacency_list_to_matrix(adj_list):
    """
    Преобразование списка смежности в матрицу смежности.
    adj_list: dict, ключ - вершина, значение - список соседей
    Возвращает: матрицу смежности в виде списка списков и список вершин в порядке индексов
    """
    vertices = sorted(adj_list.keys())
    index = {v: i for i, v in enumerate(vertices)}
    n = len(vertices)
    matrix = [[0]*n for _ in range(n)]
    
    for v, neighbors in adj_list.items():
        i = index[v]
        for u in neighbors:
            j = index[u]
            matrix[i][j] = 1
            matrix[j][i] = 1  # для неориентированного графа симметрично
    
    return matrix, vertices


def adjacency_matrix_to_list(matrix, vertices=None):
    """
    Преобразование матрицы смежности в список смежности.
    matrix: список списков (n x n)
    vertices: список вершин (если None, вершины нумеруются от 0)
    Возвращает: словарь {вершина: [соседи]}
    """
    n = len(matrix)
    if vertices is None:
        vertices = list(range(n))
    adj_list = {v: [] for v in vertices}
    
    for i in range(n):
        for j in range(n):
            if matrix[i][j] != 0:
                adj_list[vertices[i]].append(vertices[j])
    
    return adj_list

# Создаем граф
g = UndirectedGraph()

# Добавляем вершины
g.add_vertex("A")
g.add_vertex("B")
g.add_vertex("C")

# Добавляем ребра
g.add_edge("A", "B")
g.add_edge("B", "C")
g.add_edge("C", "A")  # Создаем цикл

# Проверяем степень вершины
print("Степень вершины B:", g.degree("B"))  # Выведет 2

# Проверяем смежность вершин
print("A и B смежны?", g.are_adjacent("A", "B"))  # True
print("A и C смежны?", g.are_adjacent("A", "C"))  # True
print("A и D смежны?", g.are_adjacent("A", "D"))  # False, вершина D отсутствует

# Проверяем наличие петель
print("Есть петли?", g.has_loops())  # False

# Проверяем наличие параллельных рёбер
print("Есть параллельные рёбра?", g.has_parallel_edges())  # False

# Проверяем наличие циклов
print("Есть циклы?", g.has_cycles())  # True, так как добавлено ребро C-A

# Записываем граф в файл
g.write_to_file("graph.txt")

# Создаем новый граф и читаем из файла
g2 = UndirectedGraph()
g2.read_from_file("graph.txt")

# Проверяем, что граф считан корректно
print("Степень вершины B в новом графе:", g2.degree("B"))
print("Есть циклы в новом графе?", g2.has_cycles())

matrix, verts = adjacency_list_to_matrix(g.adj)
list_ = adjacency_matrix_to_list(matrix, verts)

print(g.adj)
print(matrix)
print(list_)
