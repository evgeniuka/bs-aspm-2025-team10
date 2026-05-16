export type UserRole = "trainer" | "trainee";
export type SessionStatus = "active" | "completed";
export type ParticipantStatus = "ready" | "working" | "resting" | "completed";
export type ProgramFocus = "Strength Block" | "Conditioning Circuit" | "Core Stability";

export type User = {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
};

export type Client = {
  id: number;
  name: string;
  age: number;
  fitness_level: "Beginner" | "Intermediate" | "Advanced";
  goals: string;
  active: boolean;
  last_workout_date: string | null;
  created_at: string;
};

export type ClientCheckIn = {
  id: number;
  client_id: number;
  submitted_on: string;
  energy_level: number;
  sleep_quality: number;
  soreness_level: number;
  pain_notes: string | null;
  training_goal: string | null;
  readiness_status: "ready" | "caution" | "attention";
  risk_flags: string[];
  created_at: string;
  updated_at: string;
};

export type ClientReadiness = {
  client: Client;
  check_in: ClientCheckIn | null;
  readiness_status: "ready" | "caution" | "attention" | "missing";
  risk_flags: string[];
};

export type Exercise = {
  id: number;
  name: string;
  category: string;
  equipment: string;
  difficulty: string;
  description: string;
};

export type ProgramExercise = {
  id: number;
  order_index: number;
  sets: number;
  reps: number;
  weight_kg: number;
  rest_seconds: number;
  notes: string | null;
  exercise: Exercise;
};

export type Program = {
  id: number;
  client_id: number;
  name: string;
  focus: ProgramFocus | null;
  notes: string | null;
  is_session_snapshot: boolean;
  created_at: string;
  exercises: ProgramExercise[];
};

export type TrainingGroupExercise = {
  id: number;
  order_index: number;
  sets: number;
  reps: number;
  weight_kg: number;
  rest_seconds: number;
  notes: string | null;
  exercise: Exercise;
};

export type TrainingGroup = {
  id: number;
  name: string;
  focus: ProgramFocus | null;
  notes: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
  clients: Client[];
  exercises: TrainingGroupExercise[];
};

export type SessionParticipant = {
  id: number;
  client_id: number;
  client_name: string;
  program: Program;
  current_exercise_index: number;
  current_set: number;
  status: ParticipantStatus;
  completed_exercises: number[];
  rest_time_remaining: number;
  coach_notes: string | null;
  next_focus: string | null;
  today_check_in: ClientCheckIn | null;
  sets_completed: Array<{
    program_exercise_id: number | null;
    exercise_id: number;
    exercise_name: string;
    set_number: number;
    reps_completed: number;
    weight_kg: number;
    volume_kg: number;
    created_at: string;
  }>;
};

export type TrainingSession = {
  id: number;
  status: SessionStatus;
  started_at: string;
  ended_at: string | null;
  duration_minutes: number;
  clients: SessionParticipant[];
};

export type DashboardOverview = {
  total_clients: number;
  total_programs: number;
  completed_sessions: number;
  active_session: TrainingSession | null;
  clients: Client[];
  recent_sessions: TrainingSession[];
  today_readiness: ClientReadiness[];
};

export type TrainerVolumePoint = {
  date: string;
  volume_kg: number;
  sets_completed: number;
};

export type TrainerWeeklyVolumePoint = {
  week_start: string;
  volume_kg: number;
  sets_completed: number;
  sessions: number;
};

export type TrainerFocus = {
  focus: string;
  client_sessions: number;
  sets_completed: number;
  planned_sets: number;
  volume_kg: number;
  completion_rate: number;
};

export type TrainerExerciseLoad = {
  exercise_id: number;
  exercise_name: string;
  sets_completed: number;
  volume_kg: number;
  clients: number;
};

export type TrainerReadinessStatus = {
  status: "ready" | "caution" | "attention" | "missing";
  clients: number;
};

export type TrainerAttentionClient = {
  client_id: number;
  client_name: string;
  readiness_status: "ready" | "caution" | "attention" | "missing";
  risk_flags: string[];
  completion_rate: number;
  last_workout_date: string | null;
  days_since_last_workout: number | null;
};

export type ClientLoad = {
  client_id: number;
  client_name: string;
  sessions: number;
  sets_completed: number;
  planned_sets: number;
  volume_kg: number;
  completion_rate: number;
  last_workout_date: string | null;
};

export type TrainerAnalytics = {
  total_sessions: number;
  completed_sessions: number;
  active_sessions: number;
  total_sets_completed: number;
  total_planned_sets: number;
  total_volume_kg: number;
  completion_rate: number;
  average_sets_per_session: number;
  average_session_minutes: number;
  volume_by_day: TrainerVolumePoint[];
  weekly_volume: TrainerWeeklyVolumePoint[];
  focus_mix: TrainerFocus[];
  top_exercises: TrainerExerciseLoad[];
  readiness_mix: TrainerReadinessStatus[];
  attention_clients: TrainerAttentionClient[];
  client_load: ClientLoad[];
};

export type RealtimeEvent = {
  type: "session_joined" | "set_completed" | "rest_started" | "client_status_updated" | "session_ended" | "set_undone";
  session: TrainingSession;
};

export type ClientVolumePoint = {
  session_id: number;
  date: string;
  volume_kg: number;
  sets_completed: number;
};

export type ClientAnalytics = {
  total_sessions: number;
  completed_sessions: number;
  total_sets: number;
  planned_sets: number;
  total_volume_kg: number;
  average_volume_kg: number;
  best_volume_kg: number;
  completion_rate: number;
  average_session_minutes: number;
  volume_by_session: ClientVolumePoint[];
  exercise_breakdown: Array<{
    exercise_id: number;
    exercise_name: string;
    sets_completed: number;
    volume_kg: number;
    last_logged_at: string | null;
  }>;
};

export type ClientSessionSummary = {
  session_id: number;
  status: SessionStatus;
  started_at: string;
  ended_at: string | null;
  duration_minutes: number;
  program_name: string;
  sets_completed: number;
  planned_sets: number;
  volume_kg: number;
  coach_notes: string | null;
  next_focus: string | null;
};

export type ClientDetail = {
  client: Client;
  programs: Program[];
  analytics: ClientAnalytics;
  recent_sessions: ClientSessionSummary[];
  today_check_in: ClientCheckIn | null;
};

export type ExerciseSummary = {
  exercise_id: number;
  exercise_name: string;
  sets_completed: number;
  planned_sets: number;
  reps_completed: number;
  volume_kg: number;
  sets: Array<{
    program_exercise_id: number | null;
    exercise_id: number;
    exercise_name: string;
    set_number: number;
    reps_completed: number;
    weight_kg: number;
    volume_kg: number;
    created_at: string;
  }>;
};

export type SessionClientSummary = {
  session_client_id: number;
  client_id: number;
  client_name: string;
  program_id: number;
  program_name: string;
  status: ParticipantStatus;
  sets_completed: number;
  planned_sets: number;
  volume_kg: number;
  coach_notes: string | null;
  next_focus: string | null;
  exercises: ExerciseSummary[];
};

export type SessionSummary = {
  session_id: number;
  status: SessionStatus;
  started_at: string;
  ended_at: string | null;
  duration_minutes: number;
  total_clients: number;
  total_sets_completed: number;
  total_planned_sets: number;
  total_volume_kg: number;
  clients: SessionClientSummary[];
};
