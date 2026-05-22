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
### Шаг 5. Назначьте преподавателей курса (опционально)

Если преподавателям курса нужна возможность проверять работы, выставлять оценки и писать комментарии — перечислите их email'ы в поле `teachers` в `course.json`:

```json
{
  "title": "Мой курс",
  "teachers": [
    "prof@g.nsu.ru",
    "assistant@g.nsu.ru"
  ],
  "modules": [...]
}
```

**Как это работает:**

1. При импорте курса для каждого email создаётся `course_enrollments` с ролью `teacher` **только на этот конкретный курс**.
2. Преподаватель получает доступ к вкладке "Проверка" исключительно в указанных курсах. На других курсах он остаётся обычным студентом (или не имеет доступа вовсе).
3. Глобальная системная роль `teacher` **не выдаётся** — вся модель доступа идёт через per-course enrollment.
4. Если преподаватель ещё никогда не логинился в LMS — не страшно. При импорте создаётся placeholder, а при первом логине через NSUID все права автоматически перекидываются на реального пользователя. Никаких действий от администратора не требуется.

**Обновление списка преподавателей:**

- `"teachers": ["a@x", "b@x"]` — заменяет текущий список на указанный (тех, кого нет в новом списке, убирают из преподавателей курса).
- `"teachers": []` — убирает всех преподавателей курса.
- Отсутствие поля `teachers` — ничего не меняет (существующие преподаватели остаются).

### Шаг 6. Важные правила

**Порядок элементов в `content[]` имеет значение:**
- Элемент `"type": "submodule"` создаёт группу (раздел)
- Все последующие `"type": "task"` до следующего `submodule` попадают в эту группу
- Если задачи идут до первого `submodule`, они остаются задачами уровня модуля и **не** заворачиваются в синтетический раздел

```
task "Разминка"        ← остаётся задачей уровня модуля
submodule "Теория"     ← создаёт группу "Теория"
  task "Задача 1"      ← входит в группу "Теория"
  task "Задача 2"      ← входит в группу "Теория"
submodule "Практика"   ← создаёт группу "Практика"
  task "Задача 3"      ← входит в группу "Практика"
```

**Что игнорируется при загрузке:**
- Файлы, начинающиеся с `.` (`.git`, `.DS_Store`)
- Файлы, начинающиеся с `__` (`__pycache__`, `__init__.py`)


### Шаг 7. Загрузите курс


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
  "teachers": ["prof@g.nsu.ru", "assistant@g.nsu.ru"],
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
| `compilers` | string[] | нет | Список доступных компиляторов (см. [Доступные компиляторы](#доступные-компиляторы)) |
| `seminars` | string[] | нет | Даты семинаров (формат `YYYY-MM-DD`) |
| `allowed_users` | string[] | нет | Email-адреса допущенных студентов |
| `allowed_groups` | string[] | нет | Номера учебных групп НГУ (берутся из JWT NSUID `/NSU/StudentGroups/<номер>`). Все студенты этих групп автоматически зачисляются на курс как `student`. |
| `teachers` | string[] | нет | Email-адреса преподавателей курса. При импорте каждый email получает `course_enrollments.role=teacher` только на этот курс. Глобальной роли `teacher` не выдаётся — права на проверку работ, выставление оценок и комментарии действуют **строго в пределах этого курса**. Если teacher ещё не логинился в LMS, создаётся placeholder — при первом логине через NSUID placeholder автоматически заменяется на реального пользователя с сохранением всех enrollments. Поддерживается семантика обновления: `"teachers": [...]` — заменить список целиком, `"teachers": []` — убрать всех преподавателей курса, отсутствие поля — не трогать существующих. |

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
| `tasks` | object[] | нет | Вложенные задачи для explicit `type: "submodule"` при группировке |
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

## Доступные компиляторы

В поле `compilers` нужно указывать **id** компилятора из таблицы ниже. Список актуален для `fresh.nsuts.ru`.

### C / C++

| ID | Название |
|---|---|
| `gcc9.3.0` | GCC 9.3.0 (Ubuntu 20 LTS) |
| `gpp9.3.0` | G++ 9.3.0 (Ubuntu 20 LTS) |
| `clanglinux` | Clang 10.0.0 (Ubuntu 20 LTS) |
| `clangpplinux` | Clang++ 10.0.0 (Ubuntu 20 LTS) |
| `mingw8.1c` | MinGW64 C 8.1 |
| `mingw8.1cpp` | MinGW64 C++ 8.1 |
| `mingw11.2c` | MinGW C 11.2 |
| `mingw11.2cpp` | MinGW C++ 11.2 |
| `mingwc5.1.0` | C (TDM-GCC 5.1.0) (testing) |
| `mingw5.1.0` | C++ (TDM-GCC 5.1.0) |
| `tdmgcc_c10.3.0` | TDM-GCC C 10.3.0 |
| `tdmgcc_cpp10.3.0` | TDM-GCC C++ 10.3.0 |
| `vc2019` | Visual C 2019 |
| `vcc2019` | Visual C++ 2019 |
| `vc2015` | Visual C 2015 |
| `vcc2015` | Visual C++ 2015 |
| `vcc2013` | Visual C++ 2013 |
| `vcc2010` | Visual C++ 2010 |
| `vcc2005` | Visual C++ 2005 |

### Java

| ID | Название |
|---|---|
| `java12.0.2` | Java 12.0.2 |
| `java11.0.2` | OpenJDK 11.0.2 |
| `java8.60` | Java 1.8.0_60 (64bit) |
| `java8u101x64` | Java 8u121 (64bit) |
| `java8u101x32` | Java 8u121 (32bit) |
| `java7.25` | Java 1.7.0_25 (64bit) |

### Python

| ID | Название |
|---|---|
| `python3.7.6` | Python 3.7.6 |
| `python3.6` | Python 3.6 |
| `python3.5` | Python 3.5 |
| `python2.7` | Python 2.7 |
| `python3.6linux` | Python 3.4 (Linux) |

### Pascal

| ID | Название |
|---|---|
| `pabcnet3.7.1` | PascalABC.NET 3.7.1 |
| `pabcnet3.2.4` | PascalABC.NET 3.4.2 |
| `fpas3.0.0` | Free Pascal 3.0.0 |
| `fpas2.6.4` | Free Pascal 2.6.4 |
| `fpas2.6` | Free Pascal 2.6.0 |
| `fpc` | Free Pascal 2.4.0 (Ubuntu 10.04 LTS) |

### C# / Kotlin / Lua

| ID | Название |
|---|---|
| `vc-sharp6` | Visual C# 2015 |
| `vc-sharp5` | Visual C# 2013 |
| `kotlinc` | Kotlin 1.4.10 |
| `lua` | Lua 5.1.5 |
| `luajit` | Lua JIT 2.0.2 |

### Прочие

| ID | Название |
|---|---|
| `nolang` | Текст (без компиляции) |
| `customfile` | Custom File |
| `dockertecharena` | Docker TechArena (Ubuntu 20 LTS) |
| `dvdrental_sql` | PostgresSQL (DvdRental Database) |
| `wares_sql` | SQLite (Wares Database) |

> **Рек��мендуемые для курсов C:** `mingw8.1c`, `gcc9.3.0`, `clanglinux`
>
> **Рекомендуемые для курсов C++:** `mingw8.1cpp`, `gpp9.3.0`, `clangpplinux`
>
> **Получить актуальный список:** `GET /api/jury/tour_settings/compilers/info` (требует авторизацию и контекст тура в NSUTS)

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
