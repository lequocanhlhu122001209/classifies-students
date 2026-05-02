-- Add integrated_scores table for Supabase sync

create table if not exists public.integrated_scores (
  student_id integer primary key references public.students(student_id) on delete cascade,
  original_score double precision default 0,
  integrated_score double precision default 0,
  score_difference double precision default 0,
  classification varchar(30),
  exercise_avg double precision default 0,
  midterm_avg double precision default 0,
  final_avg double precision default 0,
  total_exercises integer default 0
);
