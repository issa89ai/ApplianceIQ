# Portfolio demonstration

## A three-minute story

**Opening (20 seconds):** "ApplianceIQ is my dryer-troubleshooting prototype. I built it to understand how repair data becomes useful search results and how to evaluate those results. It retrieves source content; it does not generate repair advice with an LLM."

**Data and ranking (40 seconds):** Show the architecture and explain 100 search results, 59 wiki pages, and 18 troubleshooting guides. Explain that title plus description becomes a 384-number vector, while a separate TF-IDF index includes repair details. The final score is 80% semantic and 20% lexical similarity.

**Live phone flow (60 seconds):**

1. Keep the backend running and USB reverse configured using [setup](setup.md).
2. Enter `my dryer tumbles but does not heat`.
3. Show the general heating guide and its Electric/Gas choice.
4. Tap I'm not sure, show the identification message, then choose Electric.
5. Show source attribution and one repair-check screen without carrying out a repair.
6. Return and select Gas to demonstrate explicit guide navigation.

**Evidence (40 seconds):** Show the [evaluation table](evaluation.md). Explain why development results alone were insufficient, how harder cases exposed failures, and why cause re-ranking was rejected. Describe 100% on 12 validation examples as a small result, not perfect accuracy.

**Close (20 seconds):** "I learned that a higher similarity score is not a diagnosis, and that brand and dryer-type decisions need explicit product rules. Expanding to more appliances would require new data and evaluations."

## Recording preparation

Build and install the current app. Confirm `/health`, the phone connection, and the exact demo query before recording. Avoid showing notifications, device serials, or unrelated windows. If the app says it is showing a saved result, reconnect before presenting it as a live demonstration. No demo video has been recorded or added to this repository yet.

Suggested screenshots for a future `docs/assets/` folder: the symptom screen, dryer-type choice, and source-attributed guide. Add actual captures after reviewing them; no placeholder images are required.

## Questions to prepare for

- Why title + description for embeddings? Cause terms distracted the guide-level semantic representation in the comparison.
- Why lexical matching too? Specific tokens helped distinguish otherwise similar symptoms.
- Why three metrics? First-result usefulness, shortlist usefulness, and rank sensitivity.
- Did you train a model? No; the work is retrieval design and evaluation using a pretrained encoder.
- Why keep failed experiments? They show how decisions were tested and why attractive ideas were rejected.
- Is the app ready for general repair use? No; it is a tested, limited portfolio prototype.
