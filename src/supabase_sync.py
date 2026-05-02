"""
Module kết nối và đồng bộ dữ liệu từ SQL Server lên Supabase.
"""

import os
from typing import Any, Dict, List

from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

COURSE_NAME_TO_CODE = {
    "Nhập Môn Lập Trình": "NMLT",
    "Kĩ Thuật Lập Trình": "KTLT",
    "Cấu trúc Dữ Liệu và Giải Thuật": "CTDL",
    "Lập Trình Hướng Đối Tượng": "OOP",
    "NMLT": "NMLT",
    "KTLT": "KTLT",
    "CTDL": "CTDL",
    "OOP": "OOP",
}


def _create_supabase_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Thiếu SUPABASE_URL hoặc SUPABASE_KEY trong file .env")

    from supabase import create_client

    return create_client(SUPABASE_URL, SUPABASE_KEY)


def _chunked(items: List[Any], size: int = 500):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _to_students_rows(students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for student in students:
        rows.append(
            {
                "student_id": int(student.get("student_id", 0)),
                "name": student.get("name", ""),
                "class": student.get("class") or student.get("csv_data", {}).get("class", ""),
                "khoa": student.get("Khoa") or student.get("khoa", "Khoa Công Nghệ Thông Tin"),
                "sex": student.get("sex") or student.get("csv_data", {}).get("sex") or "Không rõ",
            }
        )
    return rows


def _to_csv_rows(students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for student in students:
        csv_data = student.get("csv_data", {})
        rows.append(
            {
                "student_id": int(student.get("student_id", 0)),
                "midterm_score": float(csv_data.get("midterm_score", 0) or 0),
                "final_score": float(csv_data.get("final_score", 0) or 0),
                "homework_score": float(csv_data.get("homework_score", 0) or 0),
                "total_score": float(csv_data.get("total_score", 0) or 0),
                "attendance_rate": float(csv_data.get("attendance_rate", 0) or 0),
                "assignment_completion": float(csv_data.get("assignment_completion", 0) or 0),
                "study_hours_per_week": int(float(csv_data.get("study_hours_per_week", 0) or 0)),
                "participation_score": int(float(csv_data.get("participation_score", 0) or 0)),
                "late_submissions": int(float(csv_data.get("late_submissions", 0) or 0)),
                "lms_usage_hours": int(float(csv_data.get("lms_usage_hours", 0) or 0)),
                "response_quality": int(float(csv_data.get("response_quality", 0) or 0)),
                "behavior_score_100": int(float(csv_data.get("behavior_score_100", 0) or 0)),
            }
        )
    return rows


def _to_course_rows(students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for student in students:
        sid = int(student.get("student_id", 0))
        courses = student.get("courses", {})
        for course_name, course_data in courses.items():
            course_code = COURSE_NAME_TO_CODE.get(course_name, str(course_name).strip())
            rows.append(
                {
                    "student_id": sid,
                    "course_code": course_code,
                    "score": float(course_data.get("score", 0) or 0),
                    "time_minutes": int(float(course_data.get("time_minutes", 0) or 0)),
                    "midterm_score": float(course_data.get("midterm_score", 0) or 0),
                    "final_score": float(course_data.get("final_score", 0) or 0),
                    "homework_score": float(course_data.get("homework_score", 0) or 0),
                }
            )
    return rows


def _to_classification_rows(classifications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for row in classifications:
        reasons = row.get("anomaly_reasons")
        if reasons is None:
            reason = row.get("anomaly_reason")
            if reason:
                reasons = [reason]
            else:
                reasons = []

        rows.append(
            {
                "student_id": int(row.get("student_id", 0)),
                "kmeans_prediction": row.get("kmeans_prediction", ""),
                "knn_prediction": row.get("knn_prediction", ""),
                "final_level": row.get("final_level", ""),
                "normalization_method": row.get("normalization_method", "minmax"),
                "anomaly_detected": bool(row.get("anomaly_detected", False)),
                "anomaly_reasons": reasons,
            }
        )
    return rows


def _to_integrated_rows(integrated_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for row in integrated_results:
        components = row.get("components", {})
        exercise_data = row.get("exercise_data", {})
        rows.append(
            {
                "student_id": int(row.get("student_id", 0)),
                "original_score": float(row.get("original_score", 0) or 0),
                "integrated_score": float(row.get("integrated_score", 0) or 0),
                "score_difference": float(row.get("score_difference", 0) or 0),
                "classification": row.get("classification", ""),
                "exercise_avg": float(components.get("exercise_avg", 0) or 0),
                "midterm_avg": float(components.get("midterm", 0) or 0),
                "final_avg": float(components.get("final", 0) or 0),
                "total_exercises": int(float(exercise_data.get("total_exercises", 0) or 0)),
            }
        )
    return rows


def sync_all_to_supabase(
    students: List[Dict[str, Any]],
    classifications: List[Dict[str, Any]] = None,
    integrated_results: List[Dict[str, Any]] = None,
) -> Dict[str, int]:
    """Đồng bộ dữ liệu từ SQL Server lên Supabase."""
    if not students:
        return {
            "students": 0,
            "student_csv_data": 0,
            "course_scores": 0,
            "classifications": 0,
            "integrated_scores": 0,
        }

    supabase = _create_supabase_client()

    student_rows = _to_students_rows(students)
    csv_rows = _to_csv_rows(students)
    course_rows = _to_course_rows(students)
    classification_rows = _to_classification_rows(classifications or [])
    integrated_rows = _to_integrated_rows(integrated_results or [])

    student_ids = [r["student_id"] for r in student_rows]

    for chunk in _chunked(student_rows):
        supabase.table("students").upsert(chunk, on_conflict="student_id").execute()

    for chunk in _chunked(csv_rows):
        supabase.table("student_csv_data").upsert(chunk, on_conflict="student_id").execute()

    for ids in _chunked(student_ids):
        supabase.table("course_scores").delete().in_("student_id", ids).execute()
    for chunk in _chunked(course_rows):
        supabase.table("course_scores").insert(chunk).execute()

    if classification_rows:
        for ids in _chunked(student_ids):
            supabase.table("classifications").delete().in_("student_id", ids).execute()
        for chunk in _chunked(classification_rows):
            supabase.table("classifications").insert(chunk).execute()

    if integrated_rows:
        for chunk in _chunked(integrated_rows):
            supabase.table("integrated_scores").upsert(chunk, on_conflict="student_id").execute()

    return {
        "students": len(student_rows),
        "student_csv_data": len(csv_rows),
        "course_scores": len(course_rows),
        "classifications": len(classification_rows),
        "integrated_scores": len(integrated_rows),
    }
