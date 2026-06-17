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
- The final shortlist is capped at 5 comments per story, so it covers 40 unique stories.

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

The comment makes a substantive claim supported by reasoning, technical detail, causal explanation, data, comparison, or concrete examples. 

Use this label when the comment is doing analytical work. The author may still express an opinion, but the comment gives enough reasoning or evidence that a reader can evaluate the claim.

Examples of signals:
- Explains a mechanism or tradeoff.
- Compares models, products, companies, or technical approaches using specific criteria.
- Uses concrete evidence, examples, links, benchmarks, implementation details, or causal logic.
- Makes a prediction but explains why it should happen.

Example data 1:
```

```

Example data 2:
```

```



#### `firsthand_report`

The comment's main support is the author's direct experience using, building, evaluating, managing, or working around AI/LLM tools. Use this label when the comment is valuable mainly because it reports lived or practical experience. The author may draw a conclusion, but the primary warrant is "I used this," "we tried this," "at my company," or "in my workflow."

Examples of signals:
- Describes personal use of an AI tool, coding assistant, model, workflow, or product.
- Describes workplace experience with AI adoption, productivity, failure, or process changes.
- Reports implementation experience, debugging experience, evaluation experience, or operational constraints.
- Gives practical lessons learned from direct use.

Example data 1:
```

```

Example data 2:
```

```

#### `hot_takes`

The comment mainly asserts a judgment, prediction, critique, endorsement, worry, joke, or reaction without enough support to evaluate the claim.

Use this label when the comment may be interesting or emotionally resonant, but it does not provide much evidence, reasoning, or firsthand detail. This includes venting, confident predictions, dismissive reactions, broad claims, and short argumentative moves that mostly assert rather than demonstrate.

Examples of signals:
- Makes a broad claim about AI, jobs, companies, society, or technology without support.
- Expresses strong approval, skepticism, fear, frustration, or dismissal.
- Uses rhetorical framing more than evidence.
- Makes a joke, snarky observation, or low-substance reaction.
- Cites a fact or anecdote only decoratively, without using it to build an argument.

Example data 1:
```

```

Example data 2:
```

```

### Decision Rules and Hard Edge Cases

The core rule is to label by the comment's primary source of support, not by topic.

- If a comment contains both analysis and opinion, label it `supported_analysis` only when the reasoning, evidence, mechanism, or comparison is doing real work. If a comment is short but makes a clear mechanism-based point, it can still be `supported_analysis`. Length is not the label criterion; the criterion is whether the comment provides evaluable support.
- If a comment contains both firsthand experience and a broader claim, label it `firsthand_report` when the experience is the main reason the comment is credible. Label it `supported_analysis` when the experience is just one example inside a broader structured argument.
- If a comment is emotional or negative but grounded in specific experience, label it `firsthand_report`. If it is emotional or negative without concrete experience or reasoning, label it `hot_takes`. 
- If the comment states a conclusion confidently but gives little support, label it `hot_takes`. 
- If a comment includes technical vocabulary but does not actually explain a mechanism, tradeoff, or evidence chain, label it `hot_takes`. Technical-sounding language alone is not enough for `supported_analysis`.
- If a comment is mostly asking a question, label based on the substance around the question. A question with context, constraints, or a concrete problem may be `supported_analysis` or `firsthand_report`; a rhetorical or low-substance question is usually `hot_takes`.

Likely hard edge cases:

- **Experience plus sweeping conclusion:** "I tried Cursor for a month and now I think junior developers are obsolete." Label `firsthand_report` if the comment describes the month of use in enough detail; label `hot_takes` if the experience is only a thin setup for the sweeping claim.
- **One statistic plus strong framing:** A comment that cites one benchmark but mainly uses it to dunk on a company may be `hot_takes` unless the benchmark is interpreted carefully.
- **Venting from real workplace experience:** A frustrated comment about AI adoption at work should be `firsthand_report` if it describes specific events or practices; otherwise `hot_takes`.
- **Technical assertion without explanation:** "RAG is dead once context windows get big enough" is `hot_takes` unless the comment explains the mechanism, cost, latency, retrieval quality, or failure modes behind the claim.

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



### Definition of success

## AI Tool Plan

### Domain and label: strategy and pressure-testing

### Data gathering

### Annotation assistance

### Failure analysis




