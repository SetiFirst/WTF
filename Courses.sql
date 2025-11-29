-- TYPES OF COURSES
CREATE TABLE types_of_courses (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(40) NOT NULL UNIQUE
);

-- COURSES
CREATE TABLE courses (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(40) NOT NULL,
    description     TEXT NOT NULL DEFAULT '',
    create_date     DATE NOT NULL DEFAULT CURRENT_DATE,
    type_course_id  INT NOT NULL,
    author_id       INT NOT NULL,   -- FK на users (уже существует)
    is_archive      BOOLEAN NOT NULL DEFAULT FALSE,
    is_private      BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_course_type
        FOREIGN KEY (type_course_id) REFERENCES types_of_courses(id)
            ON DELETE RESTRICT
    -- author_id связывать тут не буду, потому что твоей таблицы users нет в этой схеме
);

-------------------------------------------------
-- MODULES (Новый уровень структуры курсов)
-------------------------------------------------
CREATE TABLE course_modules (
    id              SERIAL PRIMARY KEY,
    course_id       INT NOT NULL,
    name            VARCHAR(80) NOT NULL,
    description     TEXT DEFAULT '',
    position_index  INT NOT NULL CHECK (position_index > 0),

    CONSTRAINT fk_module_course
        FOREIGN KEY (course_id) REFERENCES courses(id)
            ON DELETE CASCADE,

    CONSTRAINT uq_module_position
        UNIQUE (course_id, position_index)
);

-------------------------------------------------
-- LESSON TYPES
-------------------------------------------------
CREATE TABLE lesson_type (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(40) NOT NULL UNIQUE
);

-------------------------------------------------
-- LESSONS
-- Теперь уроки принадлежат МОДУЛЯМ, а не напрямую курсу.
-------------------------------------------------
CREATE TABLE lessons (
    id              SERIAL PRIMARY KEY,
    module_id       INT NOT NULL,
    name            VARCHAR(60) NOT NULL,
    difficulty      INT NOT NULL DEFAULT 0 CHECK (difficulty >= 0 AND difficulty <= 10),
    weight          INT NOT NULL CHECK (weight > 0),
    lesson_type_id  INT NOT NULL,
    position_index  INT NOT NULL CHECK (position_index > 0),

    CONSTRAINT fk_lesson_module
        FOREIGN KEY (module_id) REFERENCES course_modules(id)
            ON DELETE CASCADE,

    CONSTRAINT fk_lesson_type
        FOREIGN KEY (lesson_type_id) REFERENCES lesson_type(id)
            ON DELETE RESTRICT,

    CONSTRAINT uq_lesson_position
        UNIQUE (module_id, position_index)
);

-------------------------------------------------
-- ANSWERS
-------------------------------------------------
CREATE TABLE answers (
    id          SERIAL PRIMARY KEY,
    lesson_id   INT NOT NULL,
    name        VARCHAR(100) NOT NULL,
    is_correct  BOOLEAN NOT NULL,

    CONSTRAINT fk_answer_lesson
        FOREIGN KEY (lesson_id) REFERENCES lessons(id)
            ON DELETE CASCADE
);
