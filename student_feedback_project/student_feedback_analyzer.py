"""Command-line entry point for quick demonstration without Streamlit."""
from __future__ import annotations
import argparse
from pathlib import Path
from collections import Counter
from nlp_engine import analyze_feedback, load_feedback_csv, make_summary, evaluate_results, TOPIC_LABELS


def print_report(rows: list[dict]) -> None:
    summary = make_summary(rows)
    print("\nSTUDENT FEEDBACK ANALYSIS REPORT")
    print("=" * 68)
    print(f"Feedback records analyzed: {summary['total']}")
    print("\nSentiment distribution:")
    for sentiment in ("positive", "neutral", "negative", "mixed"):
        print(f"  {sentiment.title():10s}: {summary['sentiments'].get(sentiment, 0)}")
    print("\nTopic frequency and negative/mixed mentions:")
    for topic, count in sorted(summary["topic_counts"].items(), key=lambda item: -item[1]):
        print(f"  {TOPIC_LABELS[topic]:36s} {count:3d} mentions | negative/mixed: {summary['negative_topic_counts'].get(topic, 0)}")
    print("\nRecurring concern terms:")
    for word, count in sorted(summary["issue_counts"].items(), key=lambda item: -item[1])[:8]:
        print(f"  {word:20s}: {count}")
    print("\nIndividual predictions:")
    for index, row in enumerate(rows, 1):
        print(f"{index:02d}. [{row['sentiment'].upper():8s}] [{', '.join(row['topic_names'])}] {row['feedback']}")
    metrics = evaluate_results(rows)
    if metrics:
        print("\nEVALUATION ON LABELLED SAMPLE DATA")
        print(f"  Topic micro precision: {metrics['topic_precision_micro']:.3f}")
        print(f"  Topic micro recall:    {metrics['topic_recall_micro']:.3f}")
        print(f"  Topic micro F1:        {metrics['topic_f1_micro']:.3f}")
        print(f"  Topic exact match:     {metrics['topic_exact_match']:.3f}")
        print(f"  Sentiment accuracy:    {metrics['sentiment_accuracy']:.3f}")
        print(f"  Sentiment macro F1:    {metrics['sentiment_macro_f1']:.3f}")
        print("  Reminder: sample comments are synthetic and curated, not real student data.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Student feedback topic and sentiment analyzer")
    parser.add_argument("--demo", action="store_true", help="Analyze the bundled sample dataset")
    parser.add_argument("--csv", type=Path, help="Analyze a CSV with a 'feedback' column")
    parser.add_argument("--text", help="Analyze one comment")
    args = parser.parse_args()
    base = Path(__file__).resolve().parent
    if args.text is not None:
        result = analyze_feedback(args.text)
        print("Cleaned text:", result["normalized_feedback"])
        print("Topics:", ", ".join(result["topic_names"]))
        print("Sentiment:", result["sentiment"])
        print("Positive score:", result["positive_score"])
        print("Negative score:", result["negative_score"])
    elif args.csv:
        print_report(load_feedback_csv(args.csv))
    elif args.demo:
        print_report(load_feedback_csv(base / "data" / "sample_feedback.csv"))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
