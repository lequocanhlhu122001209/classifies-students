-- Migration: add unique constraints and expand skill_code length
-- Run this on your Supabase/Postgres instance (psql or SQL Editor in Supabase)

-- 1) Expand skill_code to varchar(50) to avoid truncation
ALTER TABLE public.skill_evaluations
  ALTER COLUMN skill_code TYPE varchar(50);

-- 2) Ensure UNIQUE(student_id, course_code, skill_code) exists
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'skill_evaluations_student_course_skill_key'
  ) THEN
    ALTER TABLE public.skill_evaluations
      ADD CONSTRAINT skill_evaluations_student_course_skill_key UNIQUE (student_id, course_code, skill_code);
  END IF;
END
$$;

-- 3) Add composite unique on course_scores (student_id, course_code)
-- Ensure course_code column exists and has appropriate type
ALTER TABLE public.course_scores
  ALTER COLUMN course_code TYPE varchar(10);

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'course_scores_student_course_key'
  ) THEN
    ALTER TABLE public.course_scores
      ADD CONSTRAINT course_scores_student_course_key UNIQUE (student_id, course_code);
  END IF;
END
$$;

-- 4) Add helpful indexes if missing
CREATE INDEX IF NOT EXISTS idx_course_scores_student_course ON public.course_scores(student_id, course_code);
CREATE INDEX IF NOT EXISTS idx_skill_evaluations_student_course_skill ON public.skill_evaluations(student_id, course_code, skill_code);

-- NOTE:
-- - Review existing NULL/empty course_code values before adding unique constraints in environments
--   where course_code may be missing. Postgres allows multiple NULLs in UNIQUE columns.
-- - Run this migration from Supabase SQL editor or via `psql` connected to your Supabase Postgres.
