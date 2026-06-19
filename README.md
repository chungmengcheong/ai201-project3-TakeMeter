# TakeMeter

TakeMeter is a discourse-quality classifier for Hacker News comments about AI, LLMs, and agents. The project compares two approaches on the same held-out test set: a zero-shot Groq baseline using `llama-3.3-70b-versatile`, and a fine-tuned `distilbert-base-uncased` classifier trained on a manually labeled dataset.

My two primary lessons from the project are that:

1. The model can learn some coarse discourse signals to distinguish between `supported_analysis`, `firsthand_report`, and `hot_takes`. However the most challenging hard edge case is deciding whether a comment has enough support to count as analysis (and therefore `supported_analysis`) when the surface style looks like a hot take: short, rhetorical, snarky, question-shaped, or framed as a recommendation.
2. The choice of hyperparameters can materially affect the fine-tuned model's performance. The default settings in the Collab notebook had set `warmup_steps` to be greater than the total number of actual training steps, which resulted in the model under-learning during training 


## Data and Labels

### Data Source

The dataset comes from Hacker News discussions about AI, large language models, and agents. I chose Hacker News because it is active, text-heavy, and has a real distinction between substantive analysis, firsthand technical experience, and unsupported takes. That made it a better fit for a discourse-quality labeling project than a simple topic or sentiment classifier.

Candidate stories were collected through the HN Algolia API. A story qualified if it:

- matched one of the AI-related search queries: `LLM`, `AI agents`, `OpenAI`, `Claude`, `ChatGPT`, `Cursor AI`, `coding agents`, `generative AI`, `large language models`, or `AI coding`;
- was returned as a story, not a comment;
- had more than 50 story points and more than 20 comments.

The labeling dataset uses top-level comments only. For each story, I used the first qualifying top-level comments returned in the HN Algolia item payload. HN comment scores are not exposed in the API response, so I did not try to sort comments by individual comment points. Each classifier input prepends the story title to the comment text to give both the human labeler and the model more context:

```text
Post title: <story title>

Comment: <comment text>
```

### Data Collection Approach

I used a reproducible harvesting script rather than manual copy-paste. The script:

1. searches HN Algolia for AI/LLM/agent-related stories;
2. filters stories locally by engagement and relevance;
3. fetches the full item payload for each selected story;
4. extracts top-level comments;
5. strips HTML and normalizes whitespace;
6. filters out comments under 120 characters;
7. builds a larger candidate pool than needed;
8. creates a 200-comment shortlist capped at 5 comments per story.

The script fetched 80 qualifying stories, collected 795 candidate comments, and produced a 200-comment labeling file covering 40 unique stories. The final labeled dataset is [data/processed/hn_ai_comments_200_labelled.csv](data/processed/hn_ai_comments_200_labelled.csv).

### Labels

I used three mutually exclusive labels:

| Label | Definition |
|-|-|
| `supported_analysis` | The comment makes a substantive claim supported by reasoning, technical detail, causal explanation, data, comparison, or concrete examples. |
| `firsthand_report` | The comment's main support is the author's direct experience using, building, evaluating, managing, or working around AI/LLM tools. |
| `hot_takes` | The comment mainly asserts a judgment, prediction, critique, endorsement, worry, joke, or reaction without enough support to evaluate the claim. |

The core labeling rule was to label by the comment's primary source of support, not by topic. A comment could still be `supported_analysis` if it had an opinionated tone, as long as the reasoning would support the claim even if the framing were removed. A comment could be `firsthand_report` only if it described the experience enough for the experience itself to function as evidence. Comments with technical vocabulary but little actual reasoning stayed `hot_takes`.

Some edge cases mattered a lot:

- Enhancement suggestions were labeled `supported_analysis` when they identified a concrete gap, explained why it mattered, or proposed a specific improvement.
- Questions were labeled by substance, not form. A question with concrete context or a clearly articulated risk model could be `supported_analysis`; a rhetorical or low-context question was `hot_takes`.
- First-person language was not enough for `firsthand_report`. A comment saying "this matches my experience" without describing the experience was not treated as a report.

### Label Examples and Difficult Cases

`supported_analysis`
| Clear example | Difficult case |
|-|-|
| **Post title:** Learning to Reason with LLMs<br><br>**Comment:** The model performance is driven by chain of thought, but they will not be providing chain of thought responses to the user for various reasons including competitive advantage. After the release of GPT4 it became very common to fine-tune non-OpenAI models on GPT4 output. I’d say OpenAI is rightly concerned that fine-tuning on chain of thought responses from this model would allow for quicker reproduction of their results. This forces everyone else to reproduce it the hard way. It’s sad news for open weight models but an understandable decision. | **Post title:** Asking 60 LLMs a set of 20 questions<br><br>**Comment:** You should add what version of the model you are testing For example you mention Jon Durbin Airoboros L2 70B But is it 1.4? 2.0? 2.1? Etc.<br><br>**Decision:** labeled `supported_analysis` because this is a concrete methodology critique, even though it is short. |

 `firsthand_report` 
| Clear example | Difficult case |
|-|-|
| **Post title:** Llamafile lets you distribute and run LLMs with a single file<br><br>**Comment:** Extremely cool and Justine Tunney / jart does incredible portability work [0], but I'm kind of struggling with the use-cases for this one. I make a small macOS app [1] which runs llama.cpp with a SwiftUI front-end. For the first version of the app I was obsessed with the single download -> chat flow and making 0 network connections. I bundled a model with the app and you could just download, open, and start using it. Easy! But as soon as I wanted to release a UI update to my TestFlight beta testers, I was causing them to download another 3GB. All 3 users complained :). My first change after that was decoupling the default model download and the UI so that I can ship app updates that are about 5MB. | **Post title:** I genuinely don't understand why some people are still bullish about LLMs<br><br>**Comment:** We've had the opposite experience, especially with o3-mini using Deep Research for market research & topic deep-dive tasks. The sources that are pulled have never been 404 for us, and typically have been highly relevant to the search prompt. It's been a huge time-saver. We are just scratching the surface of how good these LLMs will become at research tasks.<br><br>**Decision:** labeled `firsthand_report` because the main support is direct reported use, despite the broad final claim. |


`hot_takes` 
| Clear example | Difficult case |
|-|-|
| **Post title:** LLM Inevitabilism<br><br>**Comment:** If in 2009 you claimed that the dominance of the smartphone was inevitable, it would have been because you were using one and understood its power, not because you were reframing away our free choice for some agenda. In 2025 I don't think you can really be taking advantage of AI to do real work and still see its mass adaptation as evitable. It's coming faster and harder than any tech in history. As scary as that is we can't wish it away. | **Post title:** A small number of samples can poison LLMs of any size<br><br>**Comment:** I don't think this can scale to really large models (300B+ params), especially once you add a little bit of RL for "common sense"/adversarial scenarios.<br><br>**Decision:** labeled `hot_takes` because the technical vocabulary is not backed by an explanation of mechanism. |

### Final label distribution:

| Label | Count | Share |
|-|-:|-:|
| `hot_takes` | 95 | 47.5% |
| `supported_analysis` | 78 | 39.0% |
| `firsthand_report` | 27 | 13.5% |
| **Total** | **200** | **100.0%** |

The `firsthand_report` class ended up thinner than I wanted. I kept it because it was a real discourse category in the data, but I expected its evaluation metrics to be noisy.

## Classification Approach

### Zero-Shot Baseline: Groq

The baseline used Groq's `llama-3.3-70b-versatile` model with a zero-shot classification prompt. The prompt defined the three labels, gave one example for each label, and instructed the model to return only the label name. I used temperature `0` and parsed the model's response against the valid label strings.

The baseline was run only on the held-out test set, not on the training or validation examples. All 30 test examples produced parseable responses.

### Fine-Tuned DistilBERT

The fine-tuned model used `distilbert-base-uncased`. Training ran in Google Colab using Hugging Face `transformers`, `datasets`, and the course starter notebook. The notebook split the 200 labeled examples into train, validation, and test sets using a 70/15/15 stratified split.

Split distribution:

| Split | Total | `hot_takes` | `supported_analysis` | `firsthand_report` |
|-|-:|-:|-:|-:|
| Train | 140 | 66 | 55 | 19 |
| Validation | 30 | 15 | 11 | 4 |
| Test | 30 | 14 | 12 | 4 |



## Evaluation

### Test Setup

Both models were evaluated on the same 30-example held-out test set. I report overall accuracy plus per-class precision, recall, and F1. Accuracy gives the simple overall hit rate, but the per-class metrics matter because the labels are not evenly distributed and a model could look acceptable overall while failing one discourse category.

Headline comparison:

| Model | Accuracy |
|-|-:|
| Zero-shot baseline (Groq) | 0.567 |
| Fine-tuned DistilBERT | 0.633 |

Fine-tuning improved overall accuracy by 0.067, or 6.7 percentage points.

### Groq Baseline Performance

```text
Baseline accuracy: 0.567  (evaluated on 30/30 parseable responses)

                    precision    recall  f1-score   support

supported_analysis       0.50      0.25      0.33        12
  firsthand_report       0.50      1.00      0.67         4
         hot_takes       0.62      0.71      0.67        14

          accuracy                           0.57        30
         macro avg       0.54      0.65      0.56        30
      weighted avg       0.56      0.57      0.53        30
```

The zero-shot baseline performed meaningfully above random guessing for a three-class task, but it struggled with `supported_analysis`. Its recall on `supported_analysis` was only 0.25, meaning it found only 3 of 12 true analysis examples. This suggests that even a strong general LLM had trouble applying my exact boundary between supported analysis and hot takes.

The baseline did better on `hot_takes` and `firsthand_report`, but the `firsthand_report` result should be interpreted cautiously. The test set contained only 4 firsthand examples, so one error would move recall by 25 percentage points.

### Fine-Tuned DistilBERT: First Run

The first run performed worse than the zero-shot baseline:

```text
Fine-tuned model accuracy: 0.467

                    precision    recall  f1-score   support

supported_analysis       0.00      0.00      0.00        12
  firsthand_report       0.00      0.00      0.00         4
         hot_takes       0.47      1.00      0.64        14

          accuracy                           0.47        30
         macro avg       0.16      0.33      0.21        30
      weighted avg       0.22      0.47      0.30        30
```

The model collapsed into predicting only `hot_takes`. This was an instructive failure. With 140 training examples, batch size 16, and 3 epochs, the model had only about 27 update steps. Since `warmup_steps` was set to 50, the model never reached the intended learning rate. It spent the entire run in warmup and did not meaningfully learn the task.

### Fine-Tuned DistilBERT: Second Run

For the second run, I changed the training setup to create more learning steps. With 140 training examples, batch size 8, and 8 epochs, the model had about 144 update steps. I kept the learning rate and weight decay fixed so the main changes were more update opportunities and no oversized warmup period.

```python
num_train_epochs = 8
per_device_train_batch_size = 8
per_device_eval_batch_size = 32
learning_rate = 2e-5
weight_decay = 0.01
warmup_steps = 0
```

The second run improved substantially:

```text
Fine-tuned model accuracy: 0.633

                    precision    recall  f1-score   support

supported_analysis       0.80      0.33      0.47        12
  firsthand_report       0.60      0.75      0.67         4
         hot_takes       0.60      0.86      0.71        14

          accuracy                           0.63        30
         macro avg       0.67      0.65      0.61        30
      weighted avg       0.68      0.63      0.61        30
```

Compared with the zero-shot baseline, the fine-tuned model improved overall accuracy, weighted F1, `supported_analysis` precision, and `hot_takes` recall. There was material improvement, but the model still struggled to find `supported_analysis` examples, with recall of only 0.33.

### Diagnosis

**Confusion matrix:**

| True \ Predicted label | `supported_analysis` | `firsthand_report` | `hot_takes` |
|-|-:|-:|-:|
| `supported_analysis` | 4 | 1 | 7 |
| `firsthand_report` | 0 | 3 | 1 |
| `hot_takes` | 1 | 1 | 12 |

The confusion matrix showed that the main issue was recall for `supported_analysis`. The model had strong `supported_analysis` precision at 0.80, so when it predicted analysis it was usually right. But it was conservative and missed many comments that I labeled as analysis. Of 12 true `supported_analysis` examples, only 4 were correctly predicted. Seven were misclassified as `hot_takes`.

My interpretation is that DistilBERT relied heavily on surface style. It learned a blunt version of `hot_takes`: comments that were rhetorical, terse, sarcastic, question-shaped, recommendation-like, or casual often got classified as `hot_takes`. That hurt `supported_analysis` because my labeling rules treated some compact comments, enhancement suggestions, resource recommendations, and concrete counterexamples as substantive analysis when they contributed evidence, critique, or useful context regardless of the rhetoric.

Three examples (full text in the appendix) illustrate the pattern:

- Example #4: A comment saying "You should add what version of the model..." was labeled `supported_analysis` because it made a concrete methodology critique. The model predicted `hot_takes`, likely because the comment was short and imperative.
- Example #7: A comment giving a GPT-4 counterexample to a benchmark result was labeled `supported_analysis` because it provided evidence against the reported result. The model predicted `hot_takes`, likely because the comment was compact and quote-heavy.
- Example #8: A comment listing missing programming languages was labeled `supported_analysis` because it identified a concrete coverage gap. The model predicted `hot_takes`, likely because the repetitive "No X. No Y." style looked like a rant.

There were also boundary errors in the other direction. Example #11 was a true `hot_takes` comment that mentioned "300B+ params," "RL," and "adversarial scenarios." The model predicted `supported_analysis`, likely because technical vocabulary made the comment look more analytical than it was.

Overall, the model learned some of the task, but not the deeper labeling rule. It learned that hot takes often have a certain style. It did not reliably learn that support can be compact, informal, or embedded inside a question or suggestion.

Put differently: the model captured the stylistic shape of unsupported takes better than it captured my intended concept of evidentiary support.

### Success Against Planning Criteria

In `planning.md`, I defined success using a hypothetical search-ranking use case where `supported_analysis` comments would receive a positive boost and `hot_takes` would be penalized. Against those criteria:

| Planning criterion | Result | Met? | Notes |
|-|-:|-|-|
| Overall accuracy at least 75% | 63.3% | No | Better than baseline, but below the planned usefulness threshold. |
| No individual class F1 below 0.60 | lowest F1 = 0.47 for `supported_analysis` | No | `supported_analysis` remained the weakest class. |
| `supported_analysis` precision at least 0.70 | 0.80 | Yes | When the model predicted `supported_analysis`, it was usually right. |
| `hot_takes` recall at least 0.70 | 0.86 | Yes | The model caught most unsupported or reactive comments. |
| Beat Groq baseline by at least 5 percentage points on accuracy or macro F1 | +6.7 accuracy points; +5 macro-F1 points | Yes | Improvement was real but modest and not robust across every class. |

The fine-tuned model met the baseline-improvement and search-ranking precision/recall sub-goals, but it did not meet the full "good enough for deployment" threshold. It is analytically useful, but not reliable enough for an actual ranking system.

## AI Usage

I used AI tools in three specific places.

First, I used Codex to pressure-test the project domain and label taxonomy. My initial label ideas included an `other` bucket and broader labels like `analysis`, `experience_report`, and `hot_takes`. Codex pushed me away from `other` because it would weaken the taxonomy and make the model learn a vague catch-all class. I accepted that recommendation and refined the labels into `supported_analysis`, `firsthand_report`, and `hot_takes`.

Second, I used Codex to help create the data-harvesting script. I specified the community, search queries, story engagement thresholds, top-level comment rule, minimum comment length, and the requirement to save both raw API output and a 200-row CSV. Codex wrote `scripts/harvest_hn_ai_comments.py`, and I reviewed the output shape before using the CSV for manual labeling.

Third, I used Codex during analysis to reason through the training results. In particular, Codex helped identify why the first fine-tuning run collapsed to `hot_takes`: the run had about 27 total update steps, while `warmup_steps=50`, so the model never left warmup. I then changed the hyperparameters and reran the model.

I did not use AI to label the dataset. The 200 labels in `data/processed/hn_ai_comments_200_labelled.csv` were manually assigned.

## Spec Reflection

The planning document helped most by forcing the label boundaries to be explicit before training. The rule that mattered most was labeling by the primary source of support, not by topic or tone. I did find myself refining the decision rules and hard edge cases as I went through the data set. Without those rules, I would have labeled many comments inconsistently, especially comments that mixed opinion, technical vocabulary, and evidence.

The implementation diverged from the original plan because `firsthand_report` ended up thinner than expected. I considered adding more examples from the candidate pool, but decided to keep the dataset as-is because the imbalance was still within the rubric limits and reflected the actual distribution in the shortlisted comments. 

The final result was useful, but not deployable. Fine-tuning improved accuracy over the zero-shot baseline, but the model still struggled with the central boundary between `supported_analysis` and `hot_takes`.

## Appendix: Wrong Predictions

Wrong predictions: 11 / 30

### #1

```text
Post title: Replacing my best friends with an LLM trained on 500k group chat messages

Comment: Highly recommend the TV show Black Mirror, which has an episode called "Be Right Back" where a character talks to her dead husband using an AI trained model in an app type setup. Very interesting discussion piece on the real world impact and repercussions of these types of systems
True:      supported_analysis
Predicted: hot_takes  (confidence: 1.00)
```

### #2

```text
Post title: I genuinely don't understand why some people are still bullish about LLMs

Comment: My experience (almost exclusively Claude), has just been so different that I don't know what to say. Some of the examples are the kinds of things I explicitly wouldn't expect LLMs to be particularly good at so I wouldn't use them for, and others, she says that it just doesn't work for her, and that experience is just so different than mine that I don't know how to respond. I think that there are two kinds of people who use AI: people who are looking for the ways in which AIs fail (of which there are still many) and people who are looking for the ways in which AIs succeed (of which there are also many). A lot of what I do is relatively simple one off scripting. Code that doesn't need to deal with edge cases, won't be widely deployed, and whose outputs are very quickly and easily verifiable. LLMs are almost perfect for this. It's generally faster than me looking up syntax/documentation, when it's wrong it's easy to tell and correct. Look for the ways that AI works, and it can be a powerful tool. Try and figure out where it still fails, and you will see nothing but hype and hot air. Not every use case is like this, but there are many. -edit- Also, when she says "none of my students has ever invented references that just don't exist"...all I can say is "press X to doubt"
True:      supported_analysis
Predicted: firsthand_report  (confidence: 0.99)
```

### #3

```text
Post title: Building LLMs from the Ground Up: A 3-Hour Coding Workshop

Comment: This is excellent. Thanks for sharing. It's always good to go back to the fundamentals. There's another resource that is also quite good: https://jaykmody.com/blog/gpt-from-scratch/
True:      supported_analysis
Predicted: hot_takes  (confidence: 1.00)
```

### #4

```text
Post title: Asking 60 LLMs a set of 20 questions

Comment: You should add what version of the model you are testing For example you mention Jon Durbin Airoboros L2 70B But is it 1.4? 2.0? 2.1? Etc.
True:      supported_analysis
Predicted: hot_takes  (confidence: 0.77)
```

### #5

```text
Post title: Building LLMs from the Ground Up: A 3-Hour Coding Workshop

Comment: Excuse my ignorance, is this different from Andrej Karpathy https://www.youtube.com/watch?v=kCc8FmEb1nY Anyway I will watch it tonight before bed. Thank you for sharing.
True:      supported_analysis
Predicted: hot_takes  (confidence: 1.00)
```

### #6

```text
Post title: Why LLMs can't really build software

Comment: > We don't just keep adding more words to our context window, because it would drive us mad. That, and we also don't only focus on the textual description of a problem when we encounter a problem. We don't see the debugger output and go "how do I make this bad output go away?!?". Oh, I am getting an authentication error. Well, meaybe I should just delete the token check for that code path...problem solved?! No. Problem very much not-solved. In fact, problem very much very bigger big problem now, and [Grug][1] find himself reaching for club again. Software engineers are able to step back, think about the whole thing, and determine the root cause of a problem. I am getting an auth error...ok, what happens when the token is verified...oh, look, the problem is not the authentication at all...in fact there is no error! The test was simply bad and tried to call a higher privilege function as a lower privilege user. So, test needs to be fixed. And also, even though it isn't per-se an error, the response for that function should maybe differentiate between "401 because you didn't authenticate" and "401 because your privileges are too low". [1]: https://grugbrain.dev
True:      hot_takes
Predicted: firsthand_report  (confidence: 0.97)
```

### #7

```text
Post title: Asking 60 LLMs a set of 20 questions

Comment: > Sally (a girl) has 3 brothers. Each brother has 2 sisters. How many sisters does Sally have? The site reports every LLM as getting this wrong. But GPT4 seems to get it right for me: > Sally has 3 brothers. Since each brother has 2 sisters and Sally is one of those sisters, the other sister is the second sister for each brother. So, Sally has 1 sister.
True:      supported_analysis
Predicted: hot_takes  (confidence: 1.00)
```

### #8

```text
Post title: Replit's new Code LLM: Open Source, 77% smaller than Codex, trained in 1 week

Comment: No Clojure. No Julia. No Haskell. No Racket. No Scheme. No Common Lisp. No OCaml. And, as much as I despise Microsoft, No C#. No F#. No Swift. No Objective-C. No Perl. No Datalog. A glaringly lacking choice of languages.
True:      supported_analysis
Predicted: hot_takes  (confidence: 0.85)
```

### #9

```text
Post title: Implementing a ChatGPT-like LLM from scratch, step by step

Comment: How does this compare to the karpathy video [0]? I'm trying to get into LLMs and am trying to figure out what the best resource to get that level of understanding would be. [0] https://www.youtube.com/watch?v=kCc8FmEb1nY
True:      supported_analysis
Predicted: hot_takes  (confidence: 1.00)
```

### #10

```text
Post title: I genuinely don't understand why some people are still bullish about LLMs

Comment: We've had the opposite experience, especially with o3-mini using Deep Research for market research & topic deep-dive tasks. The sources that are pulled have never been 404 for us, and typically have been highly relevant to the search prompt. It's been a huge time-saver. We are just scratching the surface of how good these LLMs will become at research tasks.
True:      firsthand_report
Predicted: hot_takes  (confidence: 1.00)
```

### #11

```text
Post title: A small number of samples can poison LLMs of any size

Comment: I don't think this can scale to really large models (300B+ params), especially once you add a little bit of RL for "common sense"/adversarial scenarios.
True:      hot_takes
Predicted: supported_analysis  (confidence: 0.99)
```
