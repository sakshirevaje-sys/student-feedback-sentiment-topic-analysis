from __future__ import annotations

from collections import Counter
from pathlib import Path
import io

import pandas as pd
import streamlit as st

from nlp_engine import (
    TOPIC_LABELS,
    analyze_feedback,
    evaluate_results,
    load_feedback_csv,
    make_summary,
)

BASE_DIR = Path(__file__).resolve().parent
SAMPLE_CSV = BASE_DIR / "data" / "sample_feedback.csv"

st.set_page_config(
    page_title="Student Feedback Analyzer",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 Student Feedback Sentiment & Topic Analysis")
st.caption("An explainable NLP prototype that groups student comments by topic and sentiment.")

with st.sidebar:
    st.header("About this project")
    st.write("This prototype helps a university review feedback about teaching, exams, infrastructure, library services, and student support.")
    st.info("The current version uses keyword dictionaries, spelling corrections, and simple negation rules. It is an academic baseline, not a trained AI model.")
    st.markdown("**Topics detected**")
    for label in TOPIC_LABELS.values():
        if label != "Other / Unclassified":
            st.write(f"• {label}")
    st.markdown("---")
    st.caption("Use anonymous feedback. Do not upload names, phone numbers, roll numbers, or other personal information.")


def make_result_frame(results: list[dict]) -> pd.DataFrame:
    rows = []
    for item in results:
        rows.append({
            "ID": item.get("id", ""),
            "Feedback": item["feedback"],
            "Predicted topics": "; ".join(item["topic_names"]),
            "Sentiment": item["sentiment"].title(),
            "Normalized text": item["normalized_feedback"],
        })
    return pd.DataFrame(rows)


def show_dashboard(results: list[dict], title: str = "Analysis results") -> None:
    if not results:
        st.warning("No feedback comments were found. Add a comment or upload a CSV file.")
        return
    summary = make_summary(results)
    sentiment_counts = summary["sentiments"]
    negative_or_mixed = sentiment_counts.get("negative", 0) + sentiment_counts.get("mixed", 0)

    st.subheader(title)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Feedback comments", summary["total"])
    m2.metric("Positive", sentiment_counts.get("positive", 0))
    m3.metric("Negative", sentiment_counts.get("negative", 0))
    m4.metric("Negative or mixed", negative_or_mixed)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Sentiment distribution**")
        sent_df = pd.DataFrame(
            [{"Sentiment": key.title(), "Number of comments": value} for key, value in sentiment_counts.items()]
        )
        if not sent_df.empty:
            st.bar_chart(sent_df.set_index("Sentiment"))
    with col2:
        st.markdown("**Most discussed topics**")
        topic_rows = [
            {"Topic": TOPIC_LABELS[key], "Mentions": value}
            for key, value in summary["topic_counts"].items()
        ]
        topic_df = pd.DataFrame(topic_rows)
        if not topic_df.empty:
            st.bar_chart(topic_df.set_index("Topic"))
        else:
            st.write("No known topic was detected in these comments.")

    st.markdown("**Recurring concerns in negative or mixed comments**")
    issue_rows = sorted(summary["issue_counts"].items(), key=lambda pair: (-pair[1], pair[0]))[:8]
    if issue_rows:
        issue_df = pd.DataFrame(issue_rows, columns=["Concern keyword", "Mentions"])
        st.dataframe(issue_df, use_container_width=True, hide_index=True)
    else:
        st.write("No predefined concern keyword was detected. Review the comments manually.")

    # Short, transparent decision-support summary.
    top_topics = sorted(summary["topic_counts"].items(), key=lambda pair: (-pair[1], pair[0]))[:3]
    st.markdown("**Institutional summary**")
    if top_topics:
        topic_sentence = ", ".join(f"{TOPIC_LABELS[t]} ({n})" for t, n in top_topics)
    else:
        topic_sentence = "no specific topic was detected"
    st.write(
        f"The system analyzed {summary['total']} comments. It labeled {negative_or_mixed} comments "
        f"as negative or mixed. The most frequently discussed areas were {topic_sentence}. "
        "Administrators should read the original comments and verify these patterns before taking action."
    )

    st.markdown("**Comment-level predictions**")
    result_df = make_result_frame(results)
    st.dataframe(result_df[["ID", "Feedback", "Predicted topics", "Sentiment"]], use_container_width=True, hide_index=True)

    csv_bytes = result_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Download analysis as CSV",
        data=csv_bytes,
        file_name="student_feedback_analysis.csv",
        mime="text/csv",
    )

    metrics = evaluate_results(results)
    if metrics:
        st.markdown("**Evaluation metrics**")
        st.caption("These are calculated only when the uploaded CSV includes expected_topics and expected_sentiment labels.")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Topic precision", f"{metrics['topic_precision_micro']:.1%}")
        c2.metric("Topic recall", f"{metrics['topic_recall_micro']:.1%}")
        c3.metric("Topic F1", f"{metrics['topic_f1_micro']:.1%}")
        c4.metric("Sentiment accuracy", f"{metrics['sentiment_accuracy']:.1%}")
        cm = metrics["confusion_matrix"]
        labels = sorted(cm)
        cm_df = pd.DataFrame([[cm[a][p] for p in labels] for a in labels], index=labels, columns=labels)
        cm_df.index.name = "Actual \\ Predicted"
        st.markdown("**Sentiment confusion matrix**")
        st.dataframe(cm_df, use_container_width=True)
        st.warning("The bundled sample is synthetic and curated. These scores are a demonstration check, not proof of real-world accuracy.")


tab_single, tab_batch, tab_guide = st.tabs(["Analyze one comment", "Analyze a CSV", "How it works"])

with tab_single:
    st.subheader("Enter student feedback")
    comment = st.text_area(
        "Feedback comment",
        placeholder="Example: The library is clean, but the Wi-Fi is not working.",
        height=120,
    )
    if st.button("Analyze comment", type="primary"):
        if not comment.strip():
            st.error("Please enter a feedback comment first.")
        else:
            result = analyze_feedback(comment)
            left, right = st.columns(2)
            left.metric("Predicted sentiment", result["sentiment"].title())
            right.metric("Number of topics", len(result["topics"]))
            st.write("**Topics:** " + ", ".join(result["topic_names"]))
            st.write("**Cleaned text:** " + result["normalized_feedback"])
            st.write(f"Positive evidence score: {result['positive_score']} | Negative evidence score: {result['negative_score']}")
            st.caption("Scores are counts from a small word list, not probabilities or confidence scores.")
            st.json({"sentiment": result["sentiment"], "topics": result["topics"]})

with tab_batch:
    st.subheader("Upload multiple feedback comments")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"], help="Your CSV must contain a column named feedback.")
    use_sample = st.checkbox("Use the sample demonstration dataset", value=uploaded_file is None)
    if uploaded_file is not None:
        try:
            batch_results = load_feedback_csv(uploaded_file)
        except Exception as error:
            st.error(f"Could not read this CSV: {error}")
            batch_results = []
    elif use_sample:
        batch_results = load_feedback_csv(SAMPLE_CSV)
    else:
        batch_results = []

    if batch_results:
        show_dashboard(batch_results, "Batch analysis dashboard")
    elif uploaded_file is None and not use_sample:
        st.info("Upload a CSV file or select the sample dataset to see the dashboard.")

with tab_guide:
    st.subheader("How this project works")
    st.markdown("""
1. **Input:** A student types feedback or the administrator uploads a CSV file.
2. **Text cleaning:** The program converts text to lowercase, fixes a few common spelling mistakes, and expands common short forms such as `don't`.
3. **Topic detection:** It searches for words linked with teaching, examinations, infrastructure, library, and student support. One comment may receive more than one topic.
4. **Sentiment detection:** It checks positive and negative word lists. A small negation rule tries to understand phrases such as `not helpful`.
5. **Recurring concerns:** It counts common issue words in negative or mixed comments.
6. **Output:** The dashboard shows charts, comment-level results, a short summary, and a downloadable CSV.

**Important:** This first version is an explainable rule-based NLP baseline. It does not learn from a large training dataset. Sarcasm, complex grammar, regional languages, and unfamiliar spelling may cause mistakes. A real deployment needs manually labelled university data and human review.
    """)
    architecture = BASE_DIR / "assets" / "architecture.png"
    workflow = BASE_DIR / "assets" / "workflow.png"
    algorithm = BASE_DIR / "assets" / "algorithm_flowchart.png"
    if architecture.exists():
        st.image(str(architecture), caption="System architecture")
    if workflow.exists():
        st.image(str(workflow), caption="System workflow")
    if algorithm.exists():
        st.image(str(algorithm), caption="Analysis algorithm flowchart")
