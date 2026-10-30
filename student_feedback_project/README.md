# Student Feedback Sentiment and Topic Analysis

**Group 1 | Unit 5 - CEP 1 | Problem Statement A**

A beginner-friendly NLP project that reads student feedback comments, identifies the topic(s), predicts the overall sentiment, finds repeated concern words, and prepares a summary for university decision-makers.

## 1. What this project does

The university may receive comments such as:

> The teacher explains topics clearly, but the classroom projector is broken.

The program processes this comment and may return:

- **Topics:** Teaching & Learning; Infrastructure & Facilities
- **Sentiment:** Mixed
- **Reason:** It found positive wording (`clearly`) and negative wording (`broken`).

One comment can belong to more than one topic.

## 2. Project files

| File/folder | Purpose |
|---|---|
| `app.py` | Main dashboard that opens in a web browser on your computer |
| `nlp_engine.py` | Main NLP logic: cleaning, topic detection, sentiment detection and summary calculations |
| `student_feedback_analyzer.py` | Command-line version for a quick demonstration |
| `data/sample_feedback.csv` | 30 sample comments with expected labels for evaluation |
| `tests/test_nlp_engine.py` | Small automatic tests for the main NLP functions |
| `assets/` | Architecture, workflow, algorithm and result diagrams |
| `requirements.txt` | Python libraries needed for the dashboard |
| `run_windows.bat` | Windows shortcut to install requirements and start the dashboard |
| `run_cli_demo.bat` | Windows shortcut to run the command-line demonstration |

The Word technical report is also included in this ZIP for convenience.

## 3. Requirements

- Windows 10/11, Linux, or macOS
- Python 3.10 or later (Python 3.11 or 3.12 is a safe choice for a student setup)
- Internet connection for the first installation of Streamlit and Pandas
- A modern browser such as Chrome or Edge

## 4. Run the project on Windows

### Option A: Start the dashboard (recommended for project demonstration)

1. Download and extract `Student_Feedback_Analysis_Project.zip`.
2. Open the extracted folder.
3. Make sure Python is installed. In Command Prompt, check with `py --version`.
4. Double-click **`run_windows.bat`**.
5. The script installs the required libraries and starts the application.
6. A local web address appears in Command Prompt, usually `http://localhost:8501`. Open it in Chrome or Edge if it does not open automatically.
7. Choose **Analyze one comment** to test one comment, or **Analyze a CSV** to process many comments.

### Option B: Run the command-line demo (no extra libraries needed)

1. Open the extracted project folder.
2. Click the folder address bar, type `cmd`, and press Enter.
3. Run:

```bash
py student_feedback_analyzer.py --demo
```

To analyze one comment:

```bash
py student_feedback_analyzer.py --text "The library is clean but the Wi-Fi is not working."
```

To analyze your own CSV:

```bash
py student_feedback_analyzer.py --csv "C:\path\to\your_feedback.csv"
```

## 5. CSV format for your own feedback

Your CSV must have a column named **`feedback`**. For example:

```csv
id,feedback
1,"The teacher explains concepts clearly."
2,"The library is crowded and Wi-Fi is slow."
3,"The exam result portal is not working."
```

For evaluation, you can add optional columns `expected_topics` and `expected_sentiment`. Topic labels must use these codes, separated by semicolons when there is more than one:

- `teaching`
- `examinations`
- `infrastructure`
- `library`
- `student_support`

Sentiment labels: `positive`, `negative`, `neutral`, or `mixed`.

## 6. How the NLP works (easy explanation)

1. **Input:** The user enters a comment or uploads a CSV file.
2. **Preprocessing:** The program makes the text lowercase, fixes a small list of common spelling mistakes, and expands short forms such as `don't` to `do not`.
3. **Topic classification:** It checks topic-specific words. For example, `teacher`, `lecture`, and `professor` point to Teaching; `exam`, `marks`, and `result` point to Examinations.
4. **Sentiment classification:** It checks positive words (such as `helpful`, `good`, `clear`) and negative words (such as `broken`, `slow`, `unfair`).
5. **Negation handling:** It checks nearby words such as `not` and `never`. For example, `not helpful` should be treated as negative, not positive.
6. **Recurring issue analysis:** It counts concern words in comments predicted as negative or mixed.
7. **Output:** It displays topic and sentiment results, charts, a short summary, and a downloadable CSV.

## 7. Test the code

Open Command Prompt in the project folder and run:

```bash
py -m unittest discover -s tests -v
```

The tests check spelling correction, multiple topics in one comment, negation, neutral text, and loading the sample dataset.

## 8. Evaluation and honest reporting

The bundled data contains **30 synthetic demonstration comments**, not real university feedback. The application calculates topic precision, topic recall, topic F1, exact topic-set match, sentiment accuracy, class-wise sentiment scores, and a confusion matrix when expected labels are provided.

The sample comments were deliberately written around the dictionary, so high scores on this small set are only a demonstration/reproducibility check. They do not show how well the system will work on new real student comments. For a meaningful evaluation, collect consented and anonymized feedback, have multiple people label a representative sample, split it into training/development/test sets, and evaluate on comments not used to create the rules.

## 9. Limitations

- This is a keyword/lexicon rule-based NLP baseline, not a deep-learning or transformer model.
- It may misunderstand sarcasm, complicated sentences, misspellings not in the correction list, and regional languages.
- The negation rule checks only a short nearby word window; it cannot understand every sentence structure.
- Recurring concerns are based on a predefined word list and require a human to review original comments.
- The program supports decision-making; it must not automatically judge individual teachers or students.
- Avoid uploading names, phone numbers, roll numbers, medical details, or other personal information.

## 10. Future improvements

- Build a real labelled university feedback dataset.
- Compare this baseline with TF-IDF + Logistic Regression or a transformer-based sentiment model.
- Add Marathi/Hindi support after collecting and validating language-specific data.
- Add date/department filters and a secure administrator login.
- Add human review and a correction option so predictions can be improved.

---

**Important:** This project is an educational prototype. Review the results manually before making institutional decisions.
