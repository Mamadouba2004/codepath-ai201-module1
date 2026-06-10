# Document Sources

**Domain:** Student course reviews at the University of Waterloo — what courses are
actually like (difficulty, workload, grading schemes, whether they're worth taking),
as told by students who took them.

**Provenance:** All reviews were written by University of Waterloo students on
[UWFlow](https://uwflow.com), the student-run course review site. The raw data comes
from the publicly available UWaterloo Course Reviews dataset (Kaggle), mirrored on
GitHub at [jpbower14/uwaterloo_data](https://github.com/jpbower14/uwaterloo_data)
(`course_data_clean.csv`, 14,838 review rows across 1,974 courses). Twelve courses
with the most written reviews were selected for subject variety, and each course's
reviews were exported to one plain-text document.

| # | File | Course | Reviews | Original review page |
|---|------|--------|---------|----------------------|
| 1 | `uwflow_math135_reviews.txt` | MATH 135: Algebra for Honours Mathematics | 253 | https://uwflow.com/course/math135 |
| 2 | `uwflow_econ101_reviews.txt` | ECON 101: Introduction to Microeconomics | 214 | https://uwflow.com/course/econ101 |
| 3 | `uwflow_math137_reviews.txt` | MATH 137: Calculus 1 for Honours Mathematics | 171 | https://uwflow.com/course/math137 |
| 4 | `uwflow_cs135_reviews.txt` | CS 135: Designing Functional Programs | 146 | https://uwflow.com/course/cs135 |
| 5 | `uwflow_engl109_reviews.txt` | ENGL 109: Introduction to Academic Writing | 135 | https://uwflow.com/course/engl109 |
| 6 | `uwflow_stat230_reviews.txt` | STAT 230: Probability | 131 | https://uwflow.com/course/stat230 |
| 7 | `uwflow_pd1_reviews.txt` | PD 1: Career Fundamentals | 127 | https://uwflow.com/course/pd1 |
| 8 | `uwflow_spcom223_reviews.txt` | SPCOM 223: Public Speaking | 124 | https://uwflow.com/course/spcom223 |
| 9 | `uwflow_math239_reviews.txt` | MATH 239: Introduction to Combinatorics | 122 | https://uwflow.com/course/math239 |
| 10 | `uwflow_chem120_reviews.txt` | CHEM 120: General Chemistry 1 | 116 | https://uwflow.com/course/chem120 |
| 11 | `uwflow_cs246_reviews.txt` | CS 246: Object-Oriented Software Development | 112 | https://uwflow.com/course/cs246 |
| 12 | `uwflow_cs240_reviews.txt` | CS 240: Data Structures and Data Management | 87 | https://uwflow.com/course/cs240 |

**Document format:** Each file starts with a 3-line header (course code/title, source,
aggregate rating stats), followed by the course's written reviews. Each review is
labeled `Review N (student liked/disliked the course):` followed by the review text.
