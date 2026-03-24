# Графы и обходы

## Основные понятия

**Граф** — это математическая структура, состоящая из множества вершин (узлов) и множества рёбер (связей между вершинами).

### Типы графов

1. **Ориентированный граф** — рёбра имеют направление
2. **Неориентированный граф** — рёбра не имеют направления
3. **Взвешенный граф** — рёбрам присвоены веса (стоимости)

### Способы представления

- **Матрица смежности** — двумерный массив `A[n][n]`, где `A[i][j] = 1`, если есть ребро из `i` в `j`
- **Список смежности** — массив списков, где `adj[i]` содержит всех соседей вершины `i`

## Обход в глубину (DFS)

```python
def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    for neighbor in graph[start]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
    return visited
```

Сложность: **O(V + E)**, где V — вершины, E — рёбра.

## Обход в ширину (BFS)

```python
from collections import deque

def bfs(graph, start):
    visited = {start}
    queue = deque([start])
    while queue:
        vertex = queue.popleft()
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return visited
```

Сложность: **O(V + E)**.
