-- Add skill_evaluations table for Supabase sync

create table if not exists public.skill_evaluations (
  id bigserial primary key,
  student_id integer references public.students(student_id) on delete cascade,
  course_code varchar(10),
  skill_code varchar(20),
  score double precision default 0,
  level varchar(20),
  passed boolean default false,
  unique(student_id, course_code, skill_code)
);

create index if not exists idx_skill_evaluations_student on public.skill_evaluations(student_id);
create index if not exists idx_skill_evaluations_course on public.skill_evaluations(course_code);
