USE database;
CREATE TABLE courses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code TEXT NOT NULL,
  name TEXT NOT NULL,
  instructor_name TEXT NOT NULL,
  date DATE NOT NULL,
  status TEXT NOT NULL,
  instructor_email TEXT NOT NULL UNIQUE
);
