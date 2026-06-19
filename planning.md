# TakeMeter Planning

## DATA

### Community

This project studies discourse quality in Hacker News discussions about AI, large language models, and AI agents. I was interested in the types of discussions being held by the technical community. Hacker News is a good fit because it has active, text-heavy discussions around a broad set of topics from technical developments to goverment policy. Comments can range from technical analysis to firsthand experience to unsupported hot takes. 

All of these makes Hacker News comments a good fit as a discourse quality classification project.    

### Dataset 
The dataset consists of top-level Hacker News comments from high-engagement AI-related stories. 

#### Data Qualification Criteria

Candidate stories must meet all of these criteria:
- Match one of the AI-related search queries: `LLM`, `AI agents`, `OpenAI`, `Claude`, `ChatGPT`, `Cursor AI`, `coding agents`, `generative AI`, `large language models`, or `AI coding`.
- Be returned as a Hacker News story, not a comment.
- Be a high engagement story (>50 story points, >20 comments).

The labeling dataset uses "top comments" only, i.e., the first qualifying top-level comments returned in the HN Algolia item payload. Hacker News comment scores are not exposed in the API response, so the project does not attempt to filter or sort comments by individual comment points.

#### Dataset statistics
For the current 200-row shortlist:
- The script fetched 80 qualifying stories.
- It collected up to 10 qualifying top-level comments per story for the candidate pool.
- A qualifying comment must have at least 120 characters after HTML cleanup.
- The candidate pool contains 795 comments.
- The final shortlist contains 200 comments.
- The final shortlist is capped at 5 comments per story, so it covers 40 unique stories to proxy diversity of comments.

#### Dataset format
Each classifier input prepends the story title to the comment so the model and human annotator have enough context to interpret the comment:

```text
Post title: <story title>

Comment: <comment text>
```


### Labels

The classifier will use three mutually exclusive labels, listed below and then further described in this section:
1. `supported_analysis`
2. `firsthand_report`
3. `hot_takes`

#### `supported_analysis`

The comment makes a substantive claim supported by reasoning, technical detail, causal explanation, data, comparison, or concrete examples. This label applies when the comment is doing analytical work. The author may still express an opinion, but the comment gives enough reasoning or evidence that a reader can evaluate the claim.

Examples of signals:
- Explains a mechanism or tradeoff.
- Compares models, products, companies, or technical approaches using specific criteria.
- Uses concrete evidence, examples, links, benchmarks, implementation details, or causal logic.
- Makes a prediction but explains why it should happen.

Example data 1:
```
Post title: Learning to Reason with LLMs

Comment: The model performance is driven by chain of thought, but they will not be providing chain of thought responses to the user for various reasons including competitive advantage. After the release of GPT4 it became very common to fine-tune non-OpenAI models on GPT4 output. I’d say OpenAI is rightly concerned that fine-tuning on chain of thought responses from this model would allow for quicker reproduction of their results. This forces everyone else to reproduce it the hard way. It’s sad news for open weight models but an understandable decision
```

Example data 2:
```
Post title: Building a fully local LLM voice assistant to control my smart home

Comment: If Mixtral doesn't support system prompts, and you just copy in your system prompts as another ""user"" message, does that suggest that Mixtral is less resilient to prompt injection than commercial models, because it doesn't have any concept of ""trust this instruction more than this other class of instruction""?
```


#### `firsthand_report`

The comment's main support is the author's direct experience using, building, evaluating, managing, or working around AI/LLM tools. This label is used when the comment is valuable mainly because it reports lived or practical experience. The author may draw a conclusion, but the primary warrant is "I used this," "we tried this," "at my company," or "in my workflow."

Examples of signals:
- Describes personal use of an AI tool, coding assistant, model, workflow, or product.
- Describes workplace experience with AI adoption, productivity, failure, or process changes.
- Reports implementation experience, debugging experience, evaluation experience, or operational constraints.
- Gives practical lessons learned from direct use.

A comment should not be labeled `firsthand_report` merely because it says “I agree” or “this matches my experience.” It needs to describe the experience enough that the experience itself is useful evidence.

Example data 1:
```
Post title: Llamafile lets you distribute and run LLMs with a single file

Comment: Extremely cool and Justine Tunney / jart does incredible portability work [0], but I'm kind of struggling with the use-cases for this one. I make a small macOS app [1] which runs llama.cpp with a SwiftUI front-end. For the first version of the app I was obsessed with the single download -> chat flow and making 0 network connections. I bundled a model with the app and you could just download, open, and start using it. Easy! But as soon as I wanted to release a UI update to my TestFlight beta testers, I was causing them to download another 3GB. All 3 users complained :). My first change after that was decoupling the default model download and the UI so that I can ship app updates that are about 5MB. It feels like someone using this tool is going to hit the same problem pretty quick when they want to get the latest llama.cpp updates (ggerganov SHIIIIPS [2]). Maybe there are cases where that doesn't matter, would love to hear where people think this could be useful. [0]: https://justine.lol/cosmopolitan/ [1]: https://www.freechat.run [2]: https://github.com/ggerganov/llama.cpp
```

Example data 2:
```
Post title: The Era of 1-bit LLMs: ternary parameters for cost-effective computing

Comment: This is great, my employer just gave me a M1 laptop with only 16gb ram and I had to downgrade my 7B parameter local LLM’s to 3 bit quantizing, they’ve been surprisingly okay! In my personal machine at 64gb ram, I usually use 8x7B at Q5 or 70B at Q4 Its Mistral all the way down! Imagining Q1.58 that’s doing well makes me happy
```

#### `hot_takes`

The comment mainly asserts a judgment, prediction, critique, endorsement, worry, joke, or reaction without enough support to evaluate the claim. This label is used when the comment may be interesting or emotionally resonant, but it does not provide **material** evidence, reasoning, or firsthand detail. This includes venting, confident predictions, dismissive reactions, broad claims, and short argumentative moves that mostly assert rather than demonstrate.

Examples of signals:
- Makes a broad claim about AI, jobs, companies, society, or technology without support.
- Expresses strong approval, skepticism, fear, frustration, or dismissal.
- Uses rhetorical framing more than evidence.
- Makes a joke, snarky observation, or low-substance reaction.
- Cites a fact or anecdote only decoratively, without using it to build an argument.

Example data 1:
```
Post title: LLM Inevitabilism

Comment: If in 2009 you claimed that the dominance of the smartphone was inevitable, it would have been because you were using one and understood its power, not because you were reframing away our free choice for some agenda. In 2025 I don't think you can really be taking advantage of AI to do real work and still see its mass adaptation as evitable. It's coming faster and harder than any tech in history. As scary as that is we can't wish it away."
```

Example data 2:
```
Post title: DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via RL

Comment: Q: Is there a thread about DeepSeek's (apparent) progress with lots of points and lots of quality comments? (Bonus Q: If not, why not?)
```

### Decision Rules and Hard Edge Cases

The core rule is to label by the comment's primary source of support, not by topic.

- If a comment contains both analysis and opinion, label it `supported_analysis` when the provided analysis would support the claim even if the opinion framing was removed. 
- If a comment is short but makes a clear mechanism-based point, it can still be `supported_analysis`. Length is not the label criterion; the criterion is whether the comment provides valuable support.
- If a comment contains both firsthand experience and a broader claim, label it `firsthand_report` when the experience is the main reason the comment is credible. Label it `supported_analysis` when the experience is just one example inside a broader structured argument.
- If a comment is emotional or negative but grounded in specific experience, label it `firsthand_report`. If it is emotional or negative without concrete experience or reasoning, label it `hot_takes`. 
- If the comment states a conclusion confidently but gives little support, label it `hot_takes`. 
- If a comment includes technical vocabulary but does not actually explain a mechanism, tradeoff, or evidence chain, label it `hot_takes`. Technical-sounding language alone is not enough for `supported_analysis`.
- If a comment is mostly asking a question, label based on the substance around the question. A question with context, constraints, or a concrete problem may be `supported_analysis` or `firsthand_report`; a rhetorical or low-substance question is usually `hot_takes`.


Likely hard edge cases:

- **One statistic plus strong framing:** A comment that cites one benchmark but mainly uses it to dunk on a company may be `hot_takes` unless the benchmark is interpreted carefully.
- **Experience plus sweeping conclusion:** "I tried Cursor for a month and now I think junior developers are obsolete." Label `firsthand_report` if the comment describes the month of use in enough detail; label `hot_takes` if the experience is only a thin setup for the sweeping claim.
- **Technical assertion without explanation:** "RAG is dead once context windows get big enough" is `hot_takes` unless the comment explains the mechanism, cost, latency, retrieval quality, or failure modes behind the claim.
- **Enhancement suggestions** Comments that identity they identify a concrete gap, explain why it matters, or propose a specific improvement (either as a statement or question) are labeled `supported_analysis`. Low-context feature requests, praise, or unsupported “would be nice if...” comments without reasoning are labeled `hot_takes`.
- **Questions** are labeled by the substance they provide, not by the fact that they are questions. A question with concrete context, constraints, or a clearly articulated risk model can be `supported_analysis`. A question grounded in the author’s direct experience can be `firsthand_report`. A rhetorical, sarcastic, or context-light question is `hot_takes`.
- **Request for help** Requests for guidance on a commenter's personal problem that are not substantively linked to the parent posts are labeled `hot_takes`. 
- **Venting from real workplace experience:** A frustrated comment about AI adoption at work should be `firsthand_report` if it describes specific events or practices; otherwise `hot_takes`.



### Data Collection Plan

The data collection approach is intentionally simple and reproducible:

1. Use the HN Algolia search API to find AI/LLM/agent-related stories.
2. Filter stories locally by engagement and relevance.
3. Fetch the full item payload for each selected story from the HN Algolia item endpoint.
4. Extract top-level comments from each story's comment tree.
5. Clean HTML entities and tags from comment text.
6. Filter out comments under 120 characters.
7. Build a larger candidate pool than needed so the final dataset can be adjusted if label balance is poor.
8. Create a 200-comment shortlist with at most 5 comments per story.
9. Manually label the 200-comment shortlist using the three-label taxonomy above.
10. Track difficult cases in the `notes` column during annotation.

The current generated files are:

- `scripts/harvest_hn_ai_comments.py`: reproducible harvesting script.
- `data/raw/hn_ai_comments_raw.json`: raw API payloads, selected stories, and normalized comments.
- `data/processed/hn_ai_comments_candidates.csv`: 795 candidate comments.
- `data/processed/hn_ai_comments_shortlist_200.csv`: 200-comment annotation file.

If label balance is poor after initial annotation, the plan is to draw replacement or supplemental examples from the 795-row candidate pool rather than changing the taxonomy immediately. If one label still dominates after using the candidate pool, then the collection criteria may be loosened by increasing comments per story, lowering the story engagement threshold, or including second-level replies.

### Evaluation metrics

To make the assessment of fine-tuned DistilBERT model and the zero-shot Groq baseline comparable, I will evaluate them on the same held-out test set (15% of 200 = 30 samples) on the same measures. 

The measures are:

**At group level / summary metrics:**

1. Accuracy: how often does the classifier matches my manual labels?

```
Accuracy: correct predictions / all examples
```

2. Macro F1: on average, how well does the model balance precision and recall across the labels?
```
Macro F1: sum of class F1 / number of classes
```

**At per class (label) level:**

I would need to look at the disaggregated level because a model may look accurate overall while failing on the  numerically fewer classes.

1. Recall (aka Accuracy per class): of the examples that truly belong to that class, how many did the model find?
```
Recall: correct predictions for that class / number of true labels for that class
```

2. Precision: for a given class, how often does the classifier matches my manual labels out of all its predictions?
```
Precision: correct predictions / predictions for that class
```

3. F1: how well does the model balance precision and recall? 
```
2 * (precision * recall) / (precision + recall)
```

**Composite view**

I will also review a confusion matrix which shows true labels against predicted labels. This lets me identify where label boundaries are hardest for the model. 
 

### Definition of success

I'm using the hypothetical use case where the labeling is a search ranking input, e.g., `supported_analysis` comments are given a positive boost while `hot_takes` are penalized with a negative boost. A useful classifier will need to  balance precision and recall across the label.

As such, I will consider the fine-tuned model successful if:
- Overall accuracy is at least 75%
- No individual class F1 is below 0.60
- `supported_analysis` precision is at least 0.70, because boosting comments incorrectly labeled would degrade search quality
- `hot_takes` recall is at least 0.70, because missing too many unsupported takes would weaken the search result quality 
- the fine-tuned model beats the zero-shot Groq baseline by 5 percentage points on overall accuracy or macro F1


## AI Tool Plan

### Label pressure-testing

I'll use Codex to help me refine the domain and labels, in particular the worded definition that expresses the intent behind the labels.  

*What I gave the AI:* 

I prompted Codex with:
- context for a discourse classifier (background from the project page)
- initial thoughts on domain (Hacker News) and labels (`evidence_based_analysis`, `experience_report`, `hot_takes`, `other`), plus some initial concerns ("one likely issue is that people would mix personal experience and an asserted opinion in the same comment. also venting."  
- and the following question:
```
What are potential alternative classifications or even other domain/community that I
should be considering?"
```

*What it produced:* 

It produced reasoning that generally supported the  domain and the labels but specifically guided me away from `other`. 

It also produced some starter definition for the labels. 

*What I changed or overrode:* 

I accepted the recommendation to drop `other`. 

We then engaged in a collaboration we refined the definitions (we took turn making edits) and spec out the "Decision rules and Hard Edge Cases" in the planning.md document. 


### Data gathering

I'll use Codex to help me collate the unlabelled data set.

*What I gave the AI:* 

We had a discussion on:
- filters for the comments (e.g., threshold for engagements, number of top level comments to get diversity of posts).
- approach (reproducible script, oversampling of comments, and local artifacts).

This was codified into a spec in planning.md  

I then prompted Codex with the spec to create the scripts and the resulting CSV files. 

*What it produced:* 

It implemented `harvest_hn_ai_comments.py` and did some light validation of the outputs in one-shot.

*What I changed or overrode:* 

I reviewed and accepted the script and output, which matched the detailed specs.

### Annotation assistance

I had Codex sanity-check my manually applied labels, in particular on whether I consistently applied my written guidelines. 

*What I gave the AI:* 

A CSV with the 200 samples, annotated with my labels and notes, plus the labeling guidelines from planning md.

```
i've gone through the first 35 examples. there are more hot_takes than i expected. do you think i've applied the labeling guidelines consistently??
```

*What it produced:* 

It produced a list of rows where it disagreed with my labeling and it's reasnoning for why. 

```
Likely Relabel Candidates

  I would revisit these:

   Row    Current               My Lean                    Why
  ━━━━━  ━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     1    supported_analysis    hot_takes                  Smartphone analogy + AI
                                                           inevitability claim, but thin
                                                           support. Feels more asserted
                                                           than demonstrated.
```

*What I changed or overrode:* 

I took Codex's output as a collaborator's perspective and in many cases, accepted the recommendation (e.g. for row 1). 



### Failure analysis

I used Codex to help me interpret the summary metrics from the Collab cells. 

*What I gave the AI:* 

I shared the code in "Section 3: Fine-tune your model" and the specific outputs from the trainer, plus the summary metrics from Section 4's inference run and then prompted it to help me explain the results. 

```
ok, i now ran the fine-tuning on distilbert. it looked it had a much worse performance than zero-shot!

  training_args = TrainingArguments(
      output_dir="./takemeter-model",
      num_train_epochs=3,
      per_device_train_batch_size=16,
      per_device_eval_batch_size=32,
      learning_rate=2e-5,
      weight_decay=0.01,
      warmup_steps=50,
      eval_strategy="epoch",
      save_strategy="epoch",
      save_total_limit=1,
      load_best_model_at_end=True,
      metric_for_best_model="accuracy",
      logging_steps=10,
      report_to="none",
  )

  Starting fine-tuning... (5–15 minutes on T4 GPU)
   [27/27 00:59, Epoch 3/3]
  Epoch	Training Loss	Validation Loss	Accuracy
  1	No log	1.077058	0.466667
  2	1.091334	1.042261	0.500000
  3	1.066282	1.001718	0.533333
  Writing model shards: 100%
   1/1 [00:01<00:00,  1.12s/it]
  Writing model shards: 100%
   1/1 [00:05<00:00,  5.89s/it]
  Writing model shards: 100%
   1/1 [00:07<00:00,  7.31s/it]
```

*What it produced:* 

It help me diagnosed the issue that training completed before it exited warmup_steps and suggested some refinements to the hyperparameters.  

```
Yes, this is materially worse than the zero-shot baseline, but the failure mode is very
  clear:

  > The fine-tuned DistilBERT collapsed into predicting only hot_takes.

  That’s why accuracy is exactly:

  14 hot_takes in test set / 30 total = 0.467

  And why the report shows:

  supported_analysis recall = 0.00
  firsthand_report recall   = 0.00
  hot_takes recall          = 1.00

  It did not learn the task boundary. It learned the safest/commonest label.

  Most Important Issue

  Your warmup_steps=50 is probably too high for this tiny dataset.

  Training ran only 27 total steps:

  [27/27, Epoch 3/3]

  So the model spent the entire training run in warmup. It likely never reached the intended
  learning rate. That can make the model under-train badly.

  This is a strong, concrete hyperparameter explanation.
```

*What I changed or overrode:* 

THe model and I had a discussion on what the different hyperparameters meant, and what changing them would conceptually do to the training. 

I then experimented with it's suggestions, namely:
- lowering warmup_steps
- lowering per_device_train_batch_size
- increasing num_train_epochs

