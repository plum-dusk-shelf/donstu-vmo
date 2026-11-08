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

    def greedy_coloring(self):
        """
        Жадный алгоритм раскраски вершин графа.
        Возвращает словарь: вершина -> цвет (целое число, начиная с 1).
        """
        color = {}
        for vertex in self.adj_list:
            # Находим цвета соседей
            neighbor_colors = set()
            for (neighbor, _) in self.adj_list[vertex]:
                if neighbor in color:
                    neighbor_colors.add(color[neighbor])
            # Также учитываем вершины, у которых есть ребра в эту вершину (обратные ребра)
            for u, edges in self.adj_list.items():
                for (v, _) in edges:
                    if v == vertex and u in color:
                        neighbor_colors.add(color[u])
            # Назначаем минимально возможный цвет
            c = 1
            while c in neighbor_colors:
                c += 1
            color[vertex] = c
        return color


graph = DirectedWeightedGraph()
graph.add_edge('A', 'B', 5)
graph.add_edge('A', 'C', 3)
graph.add_edge('B', 'C', 2)
graph.add_edge('C', 'D', 4)
graph.add_edge('D', 'A', 1)  # добавим ребро для цикла

print(graph.adj_list)

coloring = graph.greedy_coloring()
print("Vertex coloring:")
for vertex, col in coloring.items():
    print(f"Vertex {vertex}: Color {col}")

