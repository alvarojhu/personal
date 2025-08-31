import streamlit as st

st.title("Sample Feedback Rubric")

st.markdown("""
Each story will be evaluated on **three dimensions**: *Rule Adherence*, *Creative Quality*, and *Enjoyability*.

---

## 1. Rule Adherence (20 points)
✅ Stories must meet the group’s structural rules.

- **Effective Use of Word Count (10 pts)**
  - 10 = The story fully develops its ideas and content within the given word count; no sections feel unnecessary or underdeveloped.
  - 7 = Mostly effective, with minor areas that feel padded or thin.
  - 4 = Story feels too thin, rushed, or overstuffed for the word limit.

- **Category Words (10 pts)**
  (Object, Setting, Action, Emotion)
  - 10 = All four used *organically*.
  - 7 = All four used, but one feels shoehorned.
  - 4 = Missing or poorly integrated use of one category.
  - 0 = Multiple categories missing/unnatural.

---

## 2. Creative Quality (60 points)
🎨 Evaluates storytelling craft.

- **Originality & Creativity (20 pts)**
  - 20 = Fresh, unique premise or perspective.
  - 15 = Familiar but with inventive twists.
  - 10 = Predictable or derivative.

- **Character & Emotion (20 pts)**
  - 20 = Characters feel real; emotions resonate strongly.
  - 15 = Characters present but somewhat underdeveloped.
  - 10 = Flat or ineffective.

- **Language, Style & Flow (20 pts)**
  - 20 = Writing style (sparse, lyrical, experimental, etc.) is clear, consistent, and well-suited to the story. Sentences and transitions flow smoothly, making the story engaging and readable.
  - 15 = Style works overall but has uneven moments (occasional clunky word choice, awkward transitions, or mismatched tone).
  - 10 = Style feels unfocused, unclear, or disrupts reader engagement.

---

## 3. Enjoyability (20 points)
⭐ Does the story *land* with readers?

- **Engagement (10 pts)**
  - 10 = Grabs attention and holds it throughout.
  - 7 = Engaging in parts but drags occasionally.
  - 4 = Difficult to stay invested.

- **Overall Impact (10 pts)**
  - 10 = Leaves a strong impression (memorable, thought-provoking, or entertaining).
  - 7 = Pleasant but not particularly lasting.
  - 4 = Forgettable or confusing.

---

## Scoring Scale
- **90–100**: Excellent — meets rules, highly creative, and enjoyable.
- **75–89**: Strong — solid story, enjoyable, some polish needed.
- **60–74**: Adequate — fulfills rules but weaker in craft or engagement.
- **<60**: Needs Work — didn’t meet rules or lacked impact.
""")
