# Deamon_test

## Создание курса - пошаговое руководство

### Шаг 1. Создайте структуру директорий

```
МойКурс/
├── course.json                        # Манифест курса (обязательно)
└── content/
    ├── Lecture-1/
    │   ├── topic1.md                  # Теория (submodule)
    │   ├── task1/
    │   │   ├── task1.md               # Условие задачи
    │   │   └── tests/
    │   │       ├── 1.in               # Входные данные теста 1
    │   │       ├── 1.out              # Ожидаемый вывод теста 1
    │   │       ├── 2.in
    │   │       ├── 2.out
    │   │       ├── ...
    │   │       ├── points.txt         # (опционально) веса тестов
    │   │       └── check.exe          # (опционально) кастомный чекер
    │   └── task2/
    │       ├── task2.md
    │       └── tests/
    │           ├── 1.in
    │           └── 1.out
    ├── Lecture-2/
    │   ├── topic2.md
    │   └── ...
    └── ...
```

Все пути в `course.json` (`contentUrl`, `testsUrl`) указываются **относительно корня курса** — директории, где лежит `course.json`.

### Шаг 2. Создайте `course.json`

Минимальный рабочий пример:

```json
{
  "title": "Название моего курса",
  "modules": [
    {
      "title": "Модуль 1",
      "content": [
        {
          "type": "submodule",
          "title": "Введение",
          "contentUrl": "content/Lecture-1/topic1.md"
        },
        {
          "type": "task",
          "title": "Задача 1. Сумма чисел",
          "difficulty": "Easy",
          "contentUrl": "content/Lecture-1/task1/task1.md",
          "testsUrl": "content/Lecture-1/task1/tests",
          "time_limit": "1.0s",
          "memory_limit": "256MB",
          "max_score": 100
        }
      ]
    }
  ]
}
```

Полный список полей и их описание — в секции [Формат курса](#формат-курса) ниже.

### Шаг 3. Напишите теорию (submodule)

Файлы теории - обычный Markdown. Поддерживается:

- **LaTeX-формулы**: inline `$N! = N \times (N-1)!$`, блочные `$$...$$`
- **Блоки кода**

````markdown
# Рекурсия

Рекурсия — метод решения задач, при котором функция вызывает саму себя.

Факториал числа $N$ определяется как:

$$
N! = \begin{cases} 1, & N = 0 \\ N \times (N-1)!, & N > 0 \end{cases}
$$

```c
unsigned long long factorial(int n) {
    if (n == 0) return 1;
    return n * factorial(n - 1);
}
```


### Шаг 4. Напишите условия задач (task)

Пример структуры markdown-файла задачи:

````markdown
# Задача 1. Сумма чисел


## Условие

Даны два целых числа $a$ и $b$. Найдите их сумму.

## Формат ввода

Одна строка, содержащая два целых числа $a$ и $b$ ($-10^9 \le a, b \le 10^9$).

## Формат вывода

Одно целое число — сумма $a + b$.

## Пример

| Ввод | Вывод |
| :--- | :--- |
| `2 3` | `5` |
| `-1 1` | `0` |

````
### Шаг 5. Важные правила

**Порядок элементов в `content[]` имеет значение:**
- Элемент `"type": "submodule"` создаёт группу (раздел)
- Все последующие `"type": "task"` до следующего `submodule` попадают в эту группу
- Если задачи идут до первого `submodule`, они автоматически попадают в группу **"General"**

```
submodule "Теория"     ← создаёт группу "Теория"
  task "Задача 1"      ← входит в группу "Теория"
  task "Задача 2"      ← входит в группу "Теория"
submodule "Практика"   ← создаёт группу "Практика"
  task "Задача 3"      ← входит в группу "Практика"
```

**Что игнорируется при загрузке:**
- Файлы, начинающиеся с `.` (`.git`, `.DS_Store`)
- Файлы, начинающиеся с `__` (`__pycache__`, `__init__.py`)


### Шаг 6. Загрузите курс


1. Поместите папку курса в репозиторий
2. Создайте Pull Request
3. Добавьте лейбл `deploy`
4. Action автоматически загрузит курс на LMS


## Формат курса

Курс описывается файлом `course.json` в корне директории:

```json
{
  "title": "Базовый курс программирования",
  "description": "Курс по основам алгоритмов и структур данных",
  "address_name": "basic_programming_v1",
  "open_date": "2024-09-01T00:00:00Z",
  "close_date": "2025-01-31T23:59:59Z",
  "compilers": ["python3.7.6", "java21.0.5", "mingwc5.1.0"],
  "seminars": ["2024-09-05", "2024-09-12", "2024-09-19"],
  "allowed_users": ["student@example.com"],
  "allowed_groups": ["24214", "24215"],
  "modules": [
    {
      "title": "Модуль 1: Рекурсия",
      "open_date": "2024-01-01T00:00:00Z",
      "start_date": "2024-01-01T00:00:00Z",
      "end_date": "2024-02-01T23:59:59Z",
      "content": [
        {
          "type": "submodule",
          "title": "Теория: Основы рекурсии",
          "contentUrl": "content/Lecture-1/topic1.md"
        },
        {
          "type": "task",
          "title": "Задача 1А. Линейный поиск",
          "difficulty": "Easy",
          "contentUrl": "content/Lecture-1/task1/task1.md",
          "testsUrl": "content/Lecture-1/task1/tests",
          "time_limit": "1.0s",
          "memory_limit": "256MB",
          "max_score": 100,
          "penalties": [
            { "days_after_open": 7, "max_points": 80 },
            { "days_after_open": 14, "max_points": 50 }
          ]
        }
      ]
    }
  ]
}
```

### Описание полей

**Курс (корневой объект):**

| Поле | Тип | Обязательное | Описание |
|---|---|---|---|
| `title` | string | да | Название курса |
| `description` | string | нет | Описание курса |
| `open_date` | string | нет | Дата открытия курса (ISO 8601). До этой даты курс не виден студентам |
| `close_date` | string | нет | Дата закрытия курса (ISO 8601). После этой даты курс не виден студентам |
| `address_name` | string | нет | Адрес олимпиады в NSUTS |
| `compilers` | string[] | нет | Список доступных компиляторов |
| `seminars` | string[] | нет | Даты семинаров (формат `YYYY-MM-DD`) |
| `allowed_users` | string[] | нет | Email-адреса допущенных пользователей |
| `allowed_groups` | string[] | нет | ID учебных групп |

**Модуль (`modules[]`):**

| Поле | Тип | Обязательное | Описание |
|---|---|---|---|
| `title` | string | да | Название модуля |
| `open_date` | string | нет | Дата открытия модуля (ISO 8601). До этой даты модуль не виден студентам |
| `start_date` | string | нет | Дата начала (информационная) |
| `end_date` | string | нет | Дата закрытия модуля (ISO 8601). После этой даты модуль не виден студентам |
| `content` | object[] | да | Список элементов (задачи и подмодули) |

**Элемент контента (`content[]`):**

| Поле | Тип | Обязательное | Описание |
|---|---|---|---|
| `type` | string | да | `"task"` или `"submodule"` |
| `title` | string | да | Название элемента |
| `difficulty` | string | нет | Сложность: `Easy`, `Medium`, `Hard` |
| `contentUrl` | string | нет | Путь к файлу описания (.md) |
| `testsUrl` | string | нет | Путь к папке с тестами |
| `time_limit` | string | нет | Лимит времени (например, `"2.0s"`) |
| `memory_limit` | string | нет | Лимит памяти (например, `"256MB"`) |
| `max_score` | int | нет | Максимальный балл за задачу (по умолчанию `100`) |
| `penalties` | object[] | нет | Штрафы за просрочку (только для `type: "task"`) |
| `penalties[].days_after_open` | int | да* | Дней после `open_date` модуля |
| `penalties[].max_points` | int | да* | Максимальный балл после этого срока |
| `submissionsUrl` | string | нет | Путь к сабмитам |

### Штрафы за просрочку

Штрафы задаются **на каждой задаче** отдельно в массиве `penalties`. Дни считаются от `open_date` **модуля**, в котором находится задача.

```json
{
  "type": "task",
  "title": "Задача 1А",
  "max_score": 10,
  "penalties": [
    { "days_after_open": 7, "max_points": 8 },
    { "days_after_open": 14, "max_points": 5 }
  ]
}
```

В этом примере (при `max_score: 10`):
- До 7 дней после открытия модуля — максимум **10** баллов
- После 7 дней — максимум **8** баллов
- После 14 дней — максимум **5** баллов

**Правила:**
- `max_points` — абсолютное число баллов (не процент)
- Если у задачи нет `penalties` — штрафов нет, тьютор видит полный `max_score`
- Штрафы — **рекомендация** для тьютора, он может поставить любой балл от 0 до `max_score`

## Запуск

### Локально

```bash
pip install requests pydantic pyyaml

# Dry run (только парсинг, вывод JSON в stdout)
python -m src.runner Example --dry-run

# Загрузка на сервер
python -m src.runner Example --url https://lms.example.com --token YOUR_TOKEN
```

### Docker

```bash
docker build -t course-uploader .
docker run -v ./Example:/app/Example course-uploader Example --dry-run
```

### GitHub Action (автоматически)

1. Создайте PR с изменениями в курсе.
2. Добавьте лейбл `deploy` на PR.
3. Action автоматически загрузит курс на LMS.


## Переменные окружения

| Переменная | Описание |
|---|---|
| `LMS_API_URL` | URL эндпоинта LMS API |
| `LMS_API_TOKEN` | Bearer-токен для авторизации |
