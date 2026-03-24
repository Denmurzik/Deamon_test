# Условные операторы и циклы

## 1. Условный оператор if

Позволяет выполнять код в зависимости от условия.

```c
if (x > 0) {
    printf("Positive\n");
} else if (x == 0) {
    printf("Zero\n");
} else {
    printf("Negative\n");
}
```

```python
if x > 0:
    print("Positive")
elif x == 0:
    print("Zero")
else:
    print("Negative")
```

## 2. Операторы сравнения

| Оператор | Значение |
|----------|----------|
| `==` | Равно |
| `!=` | Не равно |
| `<`, `>` | Меньше, больше |
| `<=`, `>=` | Меньше или равно, больше или равно |

## 3. Логические операторы

- `&&` (C) / `and` (Python) — логическое И
- `||` (C) / `or` (Python) — логическое ИЛИ
- `!` (C) / `not` (Python) — логическое НЕ

## 4. Цикл for

```c
for (int i = 0; i < n; i++) {
    printf("%d ", i);
}
```

```python
for i in range(n):
    print(i, end=" ")
```

## 5. Цикл while

```c
int i = n;
while (i > 0) {
    printf("%d ", i % 10);
    i /= 10;
}
```

```python
i = n
while i > 0:
    print(i % 10, end=" ")
    i //= 10
```

## 6. Вложенные циклы

Циклы можно вкладывать друг в друга. Сложность вложенного цикла — $O(N \times M)$.

```c
for (int i = 1; i <= n; i++) {
    for (int j = 1; j <= m; j++) {
        printf("%d ", i * j);
    }
    printf("\n");
}
```
