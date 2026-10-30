"""Core NLP logic for Student Feedback Sentiment and Topic Analysis.

This is an explainable, dictionary/rule-based baseline intended for a college
prototype. It is not a trained or production-ready language model.
"""
from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path
from typing import Any

TOPIC_KEYWORDS: dict[str, tuple[str, ...]] = {
    "teaching": (
        "teacher", "professor", "faculty", "lecturer", "teaching", "teach",
        "lecture", "lectures", "explain", "explains", "explained", "doubt",
        "doubts", "class", "classroom delivery", "syllabus coverage",
        "practical session", "practical sessions", "assignment", "teaching method",
    ),
    "examinations": (
        "exam", "examination", "paper", "question paper", "marks", "marking",
        "result", "results", "assessment", "internal", "viva", "evaluation",
        "timetable", "reschedule", "rescheduled", "grading", "grade",
    ),
    "infrastructure": (
        "building", "classroom", "classrooms", "bench", "benches", "fan", "fans",
        "projector", "wifi", "internet", "network", "lab", "laboratory",
        "toilet", "washroom", "water", "drinking water", "cleanliness", "clean",
        "hostel", "bus", "transport", "canteen", "equipment", "broken", "facility",
        "facilities", "electricity", "computer", "computer lab",
    ),
    "library": (
        "library", "book", "books", "journal", "journals", "reading room",
        "librarian", "borrowing", "issue books", "return books", "library hours",
    ),
    "student_support": (
        "counselling", "counseling", "scholarship", "scholarships", "financial aid",
        "student support", "administration", "office", "help desk", "portal",
        "registration", "complaint", "complaints", "response", "accessible",
        "accessibility", "placement", "career guidance", "fee", "fees", "admission",
    ),
}

TOPIC_LABELS = {
    "teaching": "Teaching & Learning",
    "examinations": "Examinations & Assessment",
    "infrastructure": "Infrastructure & Facilities",
    "library": "Library Services",
    "student_support": "Student Support & Administration",
    "other": "Other / Unclassified",
}

# Intentionally small correction dictionary. It can be expanded with local data.
SPELLING_FIXES = {
    "techer": "teacher", "teahcer": "teacher", "profeser": "professor",
    "libary": "library", "libray": "library", "infrastucture": "infrastructure",
    "examm": "exam", "exammination": "examination", "facilty": "facility",
    "facilties": "facilities", "suppport": "support", "recieve": "receive",
    "wifii": "wifi", "intenet": "internet", "studnt": "student",
    "cant": "cannot", "dont": "do not", "isnt": "is not",
    "wasnt": "was not", "didnt": "did not", "doesnt": "does not",
    "wont": "will not", "couldnt": "could not", "wouldnt": "would not",
}

POSITIVE_WORDS = {
    "good", "great", "excellent", "helpful", "clear", "clearer", "clean",
    "available", "accessible", "supportive", "friendly", "fair", "timely",
    "improved", "improving", "comfortable", "useful", "easy", "engaging",
    "convenient", "appreciate", "appreciated", "responsive", "working", "fixed",
    "well", "organized", "organised", "effective", "wonderful", "smooth", "kind",
    "understandable", "enough", "reliable", "quiet", "accurate", " prompt ".strip(),
}
NEGATIVE_WORDS = {
    "bad", "poor", "unclear", "confusing", "confused", "late", "delayed", "delay",
    "broken", "dirty", "unavailable", "inaccessible", "unhelpful", "rude", "unfair",
    "difficult", "hard", "crowded", "noisy", "slow", "waste", "wasted", "missing",
    "lack", "lacks", "lacking", "insufficient", "overcrowded", "cancelled", "canceled",
    "stressful", "disappointing", "disappointed", "problem", "problems", "issue", "issues",
    "error", "errors", "wrong", "unreliable", "uncomfortable", "terrible", "worst",
    "expensive", "ignored", "unanswered", "inconsistent", "biased", "faulty", "failure",
    "failures", "malfunctioning", "unfairly", "inconvenient", "unresponsive", "damaged",
}
NEGATORS = {
    "not", "no", "never", "cannot", "without", "neither", "hardly", "none",
    "isn't", "wasn't", "don't", "didn't", "doesn't", "won't",
}
INTENSIFIERS = {"very", "really", "extremely", "too", "so", "highly"}

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "i", "we", "they", "he", "she",
    "it", "this", "that", "is", "are", "was", "were", "be", "been", "being",
    "to", "of", "in", "on", "for", "with", "at", "by", "from", "as", "our",
    "my", "their", "there", "here", "have", "has", "had", "do", "does", "did",
    "not", "no", "very", "too", "so", "can", "could", "would", "should", "will",
    "after", "before", "when", "where", "which", "who", "what", "many", "much",
    "more", "most", "some", "all", "also", "only", "up", "down", "into", "about",
}

# Phrases/tokens useful for identifying repeated negative concerns in reports.
ISSUE_TERMS = (
    "wifi", "internet", "fan", "fans", "projector", "equipment", "washroom",
    "water", "crowded", "dirty", "broken", "slow", "late", "delayed", "missing",
    "ignored", "unfair", "confusing", "unclear", "difficult", "inconsistent",
    "unavailable", "error", "errors", "no response", "not working", "lack",
    "insufficient", "uncomfortable", "rude", "cancelled", "canceled", "overcrowded",
)


def normalize_text(text: str) -> str:
    """Lowercase, normalize contractions and correct a few common typos."""
    text = str(text or "").lower().replace("’", "'")
    contractions = {
        r"\bcan't\b": "cannot", r"\bwon't\b": "will not",
        r"\bdon't\b": "do not", r"\bdoesn't\b": "does not",
        r"\bdidn't\b": "did not", r"\bisn't\b": "is not",
        r"\bwasn't\b": "was not", r"\baren't\b": "are not",
        r"\bcouldn't\b": "could not", r"\bwouldn't\b": "would not",
    }
    for pattern, replacement in contractions.items():
        text = re.sub(pattern, replacement, text)
    for wrong, right in SPELLING_FIXES.items():
        text = re.sub(r"\b" + re.escape(wrong) + r"\b", right, text)
    text = text.replace("wi-fi", "wifi")
    text = re.sub(r"[^a-z0-9\s'-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _contains_term(text: str, term: str) -> bool:
    return re.search(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", text) is not None


def classify_topics(normalized_text: str) -> list[str]:
    """Return every matching topic, because one comment may mention many issues."""
    topics = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(_contains_term(normalized_text, keyword) for keyword in keywords):
            topics.append(topic)
    return topics or ["other"]


def classify_sentiment(normalized_text: str) -> tuple[str, int, int]:
    """Simple lexicon sentiment with a short negation window and intensity weights."""
    tokens = re.findall(r"[a-z]+(?:'[a-z]+)?", normalized_text)
    positive_score = 0
    negative_score = 0
    for index, token in enumerate(tokens):
        polarity = 1 if token in POSITIVE_WORDS else (-1 if token in NEGATIVE_WORDS else 0)
        if polarity == 0:
            continue
        # Context exceptions: "explains difficult topics clearly" is praise,
        # while "does not explain ... well" expresses a complaint.
        if token == "difficult" and "explain" in tokens and "clearly" in tokens:
            continue
        if token == "well" and "not" in tokens and "explain" in tokens:
            continue
        previous = tokens[max(0, index - 3):index]
        if any(word in NEGATORS for word in previous):
            polarity *= -1
        weight = 2 if any(word in INTENSIFIERS for word in previous) else 1
        if polarity > 0:
            positive_score += weight
        else:
            negative_score += weight

    if "not explain" in normalized_text or "does not explain" in normalized_text:
        negative_score += 1

    if positive_score and negative_score:
        label = "mixed"
    elif positive_score:
        label = "positive"
    elif negative_score:
        label = "negative"
    else:
        label = "neutral"
    return label, positive_score, negative_score


def analyze_feedback(text: str) -> dict[str, Any]:
    normalized = normalize_text(text)
    topics = classify_topics(normalized)
    sentiment, positive_score, negative_score = classify_sentiment(normalized)
    return {
        "feedback": str(text or ""),
        "normalized_feedback": normalized,
        "topics": topics,
        "topic_names": [TOPIC_LABELS[t] for t in topics],
        "sentiment": sentiment,
        "positive_score": positive_score,
        "negative_score": negative_score,
    }


def analyze_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Analyze rows from a CSV/list of dictionaries."""
    results = []
    for row in rows:
        feedback = str(row.get("feedback", "")).strip()
        if not feedback:
            continue
        result = analyze_feedback(feedback)
        result["id"] = row.get("id", len(results) + 1)
        result["expected_topics"] = [
            item.strip() for item in str(row.get("expected_topics", "")).split(";") if item.strip()
        ]
        result["expected_sentiment"] = str(row.get("expected_sentiment", "")).strip().lower()
        results.append(result)
    return results


def load_feedback_csv(file_or_path: Any) -> list[dict[str, Any]]:
    """Load a CSV path or file-like object. A 'feedback' column is required."""
    if hasattr(file_or_path, "read"):
        content = file_or_path.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8-sig")
        from io import StringIO
        handle = StringIO(content)
    else:
        handle = Path(file_or_path).open("r", encoding="utf-8-sig", newline="")
    try:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "feedback" not in reader.fieldnames:
            raise ValueError("CSV file must contain a column named 'feedback'.")
        return analyze_rows(list(reader))
    finally:
        handle.close()


def make_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Create concise institution-facing counts from analyzed comments."""
    topic_counts: Counter[str] = Counter()
    negative_topic_counts: Counter[str] = Counter()
    sentiment_counts: Counter[str] = Counter()
    issue_counts: Counter[str] = Counter()

    for row in results:
        sentiment_counts[row["sentiment"]] += 1
        for topic in row["topics"]:
            if topic != "other":
                topic_counts[topic] += 1
                if row["sentiment"] in {"negative", "mixed"}:
                    negative_topic_counts[topic] += 1
        if row["sentiment"] in {"negative", "mixed"}:
            text = row["normalized_feedback"]
            for term in ISSUE_TERMS:
                if _contains_term(text, term):
                    issue_counts[term] += 1

    return {
        "total": len(results),
        "sentiments": dict(sentiment_counts),
        "topic_counts": dict(topic_counts),
        "negative_topic_counts": dict(negative_topic_counts),
        "issue_counts": dict(issue_counts),
    }


def evaluate_results(results: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Compute metrics only when expected labels are provided in the CSV."""
    labeled = [
        row for row in results
        if row.get("expected_sentiment") and row.get("expected_topics")
    ]
    if not labeled:
        return None

    tp = fp = fn = exact = 0
    sentiment_correct = 0
    for row in labeled:
        expected = set(row["expected_topics"])
        predicted = set(row["topics"])
        tp += len(expected & predicted)
        fp += len(predicted - expected)
        fn += len(expected - predicted)
        exact += expected == predicted
        sentiment_correct += row["expected_sentiment"] == row["sentiment"]

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    accuracy = sentiment_correct / len(labeled)

    labels = sorted({row["expected_sentiment"] for row in labeled} | {row["sentiment"] for row in labeled})
    confusion = {actual: {predicted: 0 for predicted in labels} for actual in labels}
    for row in labeled:
        confusion[row["expected_sentiment"]][row["sentiment"]] += 1

    per_class = {}
    f1_values = []
    for label in labels:
        class_tp = confusion[label][label]
        class_fp = sum(confusion[actual][label] for actual in labels if actual != label)
        class_fn = sum(confusion[label][predicted] for predicted in labels if predicted != label)
        p = class_tp / (class_tp + class_fp) if class_tp + class_fp else 0.0
        r = class_tp / (class_tp + class_fn) if class_tp + class_fn else 0.0
        class_f1 = 2 * p * r / (p + r) if p + r else 0.0
        per_class[label] = {"precision": p, "recall": r, "f1": class_f1}
        f1_values.append(class_f1)

    return {
        "records": len(labeled),
        "topic_precision_micro": precision,
        "topic_recall_micro": recall,
        "topic_f1_micro": f1,
        "topic_exact_match": exact / len(labeled),
        "sentiment_accuracy": accuracy,
        "sentiment_macro_f1": sum(f1_values) / len(f1_values) if f1_values else 0.0,
        "sentiment_per_class": per_class,
        "confusion_matrix": confusion,
    }
