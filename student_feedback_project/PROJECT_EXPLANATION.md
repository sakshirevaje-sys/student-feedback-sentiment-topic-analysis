# Project Explanation in Very Easy Words

## Project name
**Student Feedback Sentiment and Topic Analysis**

## 1. What problem are we solving?

Students write feedback about their college. For example, they may write about teachers, exams, classrooms, the library, or college office services. A university may receive hundreds of comments. Reading every comment one by one takes time.

Our project reads those comments and helps organize them automatically.

## 2. What does the project give as output?

For every comment, it gives two main answers:

- **Topic:** What is the student talking about? Teaching, examination, infrastructure, library, or student support.
- **Sentiment:** Is the comment positive, negative, neutral, or mixed?

It also counts common problems and creates a small summary for college administrators.

### Example

Input comment:

`The teacher explains topics clearly, but the classroom projector is broken.`

Expected type of output:

- Topic 1: Teaching & Learning
- Topic 2: Infrastructure & Facilities
- Sentiment: Mixed

Why mixed? The words `clearly` and `broken` indicate both positive and negative opinions.

## 3. How does it work?

Think of it as a small assistant that reads each feedback comment and sorts it.

**Step 1: Student feedback**

The user types one comment or uploads a CSV Excel-like file containing many comments.

**Step 2: Cleaning the sentence**

The program makes letters lowercase and corrects a few common typing mistakes. For example, `libary` is corrected to `library`. It also changes short forms like `don't` to `do not`.

**Step 3: Finding the topic**

The program checks important words. Examples:

| Words found | Topic assigned |
|---|---|
| teacher, professor, lecture | Teaching & Learning |
| exam, marks, result | Examinations & Assessment |
| classroom, fan, Wi-Fi, lab | Infrastructure & Facilities |
| books, library, librarian | Library Services |
| scholarship, fees, help desk, portal | Student Support & Administration |

A sentence can have two or more topics. For example, a sentence about a teacher and an exam can be assigned to both Teaching and Examinations.

**Step 4: Finding sentiment**

The program checks positive and negative words.

| Sentiment | Meaning | Example |
|---|---|---|
| Positive | Student is happy or satisfied | The teacher is helpful. |
| Negative | Student is unhappy or reports a problem | The projector is broken. |
| Neutral | The sentence gives information without a clear opinion | The library opens at 9 AM. |
| Mixed | The sentence contains both positive and negative opinions | The library is clean but crowded. |

The program also checks nearby words like `not`. This helps with sentences such as `The teacher is not helpful`.

**Step 5: Finding repeated problems**

After analyzing all comments, the program counts repeated concern words such as slow, broken, crowded, missing, or unavailable. It also counts how many comments mention each topic.

**Step 6: Showing the result**

The dashboard displays the total comments, sentiment chart, topic chart, recurring concern terms, and a table of predictions. The result can be downloaded as a CSV file.

## 4. Which technology is used?

- **Python:** Main programming language. It runs the analysis logic.
- **NLP (Natural Language Processing):** The method used to process and understand written feedback.
- **Streamlit:** Creates the simple dashboard that opens in a web browser.
- **Pandas:** Helps read and display feedback rows from CSV files.
- **CSV:** Stores sample feedback in table form.

## 5. Is this a trained machine-learning model?

No. This first working version is a **rule-based NLP prototype**. It uses word dictionaries, spelling corrections, and simple rules. It is easier to understand and demonstrate, but it does not learn from examples like a trained machine-learning model.

For a more advanced version, the college can collect many real comments, label them, and compare machine-learning methods such as TF-IDF with Logistic Regression. That advanced model is not included in this ZIP.

## 6. How to demonstrate it to the teacher

1. Start the dashboard with `run_windows.bat`.
2. Open the **Analyze one comment** tab.
3. Enter: `The teacher is helpful, but the exam paper is confusing.`
4. Click **Analyze comment**. Show that it detects Teaching and Examinations and gives Mixed sentiment.
5. Open **Analyze a CSV**.
6. Keep **Use the sample demonstration dataset** selected.
7. Show the sentiment chart, topic chart, recurring concerns, and comment table.
8. Point out the download button that saves the analysis as a CSV file.
9. Explain that administrators should read the original feedback before taking action.

## 7. What are the limitations?

- It may not understand sarcasm, jokes, or complicated sentences.
- It corrects only the spelling mistakes added to its small correction list.
- It may make mistakes when a word has different meanings in different sentences.
- This version is designed mainly for English comments.
- The sample data is made for demonstration, not collected from actual students.
- It should help administrators, not make final decisions automatically.

## 8. Simple viva questions and answers

**Q1. What is the aim of this project?**

To automatically group student feedback by topic and sentiment and identify repeated concerns.

**Q2. What is NLP?**

NLP means Natural Language Processing. It is a field of computing that helps computers process human language, such as written sentences.

**Q3. What is sentiment analysis?**

It identifies whether a sentence expresses a positive, negative, neutral, or mixed opinion.

**Q4. What is topic classification?**

It identifies the subject of the feedback, such as teaching, examination, infrastructure, library, or student support.

**Q5. Why can one comment have multiple topics?**

Because one sentence may discuss more than one college facility or service.

**Q6. How do you handle spelling mistakes?**

The program uses a small dictionary of common spelling corrections before classification.

**Q7. How do you handle negation?**

It checks words such as `not`, `no`, and `never` near sentiment words. This is a simple rule, so it cannot understand every sentence perfectly.

**Q8. Which algorithm is used?**

This prototype uses keyword-based multi-label topic classification and lexicon-based sentiment classification with a short negation rule. It does not train a machine-learning model.

**Q9. What is a CSV file?**

CSV means Comma-Separated Values. It stores table data in a simple text file that can be opened in Excel.

**Q10. What can be improved in the future?**

Use a larger real labelled dataset, compare machine-learning models, add Marathi and Hindi language support, and add a secure administrator dashboard.
