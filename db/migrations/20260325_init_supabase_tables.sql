-- Init tables required for SQL Server -> Supabase sync

create table if not exists public.students (
  student_id integer primary key,
  name varchar(100),
  class varchar(20),
  khoa varchar(100),
  sex varchar(10)
);

create table if not exists public.student_csv_data (
  student_id integer primary key references public.students(student_id) on delete cascade,
  midterm_score double precision default 0,
  final_score double precision default 0,
  homework_score double precision default 0,
  total_score double precision default 0,
  attendance_rate double precision default 0,
  assignment_completion double precision default 0,
  study_hours_per_week integer default 0,
  participation_score integer default 0,
  late_submissions integer default 0,
  lms_usage_hours integer default 0,
  response_quality integer default 0,
  behavior_score_100 integer default 0
);

create table if not exists public.course_scores (
  id bigserial primary key,
  student_id integer references public.students(student_id) on delete cascade,
  course_code varchar(10),
  score double precision default 0,
  time_minutes integer default 0,
  midterm_score double precision default 0,
  final_score double precision default 0,
  homework_score double precision default 0
);

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

create table if not exists public.classifications (
  student_id integer primary key references public.students(student_id) on delete cascade,
  kmeans_prediction varchar(50),
  knn_prediction varchar(50),
  final_level varchar(50),
  normalization_method varchar(20),
  anomaly_detected boolean default false,
  anomaly_reasons jsonb default '[]'::jsonb
);

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
