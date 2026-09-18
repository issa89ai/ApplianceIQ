\# Hybrid Semantic and Lexical Retrieval Experiment



\## Goal



Improve dryer-guide ranking when a technician uses specific technical words that semantic retrieval alone may under-weight.



Examples include:



\- `burning rubber`

\- `electric dryer`

\- `drum does not move`



\## Starting point



The production retriever uses:



\- `all-MiniLM-L6-v2` sentence-transformer embeddings;

\- symptom-focused guide text: title plus description;

\- cosine similarity across 18 dryer troubleshooting guides.



This semantic approach handles paraphrases well, but an earlier held-out challenge set showed 67% Top-1 accuracy.



\## First hypothesis: semantic cause re-ranking



The first experiment retrieved the best five symptom-matched guides, then used detailed repair-cause text to re-rank those candidates.



Result: reject the method.



Increasing cause-text influence reduced development Top-1 accuracy from 100% to 95%, then 90% and 85%, while the held-out challenge Top-1 score remained 67%.



Detailed cause text contains useful repair evidence, but it also contains broad overlapping language such as smells, fumes, heat, motors, and belts. It is better used after guide selection as technician-facing repair information.



\## Second hypothesis: hybrid retrieval



The second experiment combines:



\- semantic similarity: similarity of sentence meaning;

\- lexical TF-IDF similarity: exact important-word overlap.



The lexical index uses guide titles, descriptions, branches, cause titles, and detailed cause text.



The final score is:



```text

final score =

&#x20; (1 - lexical weight) × semantic score

&#x20; + lexical weight × lexical score





\## Production Integration Verification



The validated hybrid method was integrated into `backend/main.py`.



At backend startup, ApplianceIQ now:



1\. Loads the existing symptom-focused sentence-transformer embeddings.

2\. Builds a TF-IDF lexical index from guide titles, descriptions, branch titles, cause titles, and cause text.

3\. Calculates the final ranking score as:



```text

80% semantic similarity + 20% lexical TF-IDF similarity

