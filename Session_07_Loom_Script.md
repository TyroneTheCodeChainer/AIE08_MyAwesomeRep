# Session 07 Loom Video Script: Synthetic Data Generation and LangSmith

**Duration: 3-5 minutes**

---

## Introduction (30 seconds)

Hey everyone! So today I want to walk you through my Session 07 assignment. This one's all about synthetic data generation using RAGAS and then evaluating everything with LangSmith.

Basically, what we're doing here is creating test datasets automatically, and then using those to see how well our RAG application actually performs. It's pretty cool because you don't have to manually create hundreds of test questions.

Here's my GitHub repo if you want to follow along: https://github.com/TyroneTheCodeChainer/AIE08_MyAwesomeRep/tree/s07-s08-assignment/07_Synthetic_Data_Generation_and_LangSmith

---

## Part 1: Understanding Synthetic Data Generation (1 minute)

Alright, so let me start with Question 1.

[Scroll to Question #1]

So here I had to explain what these three query synthesizers are doing. Turns out RAGAS uses this knowledge graph approach, and it generates three different types of questions:

First, you've got **SingleHopSpecific** - these are your basic, straightforward questions. Like "when did ChatGPT launch?" - you just need one piece of info from one document.

Then there's **MultiHopAbstract** - now these are trickier. These are questions where you need to pull information from multiple places and actually reason about it. Like asking about trends or implications across different data points.

And finally, **MultiHopSpecific** - similar to the abstract ones, but you're looking for specific facts that are scattered across multiple sources.

The whole point is to test your RAG system on different difficulty levels, not just the easy stuff.

---

## Part 2: Understanding Evaluators (1 minute)

Moving on to Activity 2...

[Scroll to Activity #2]

So here I broke down what each evaluator is actually measuring. We're using three of them:

The **QA Evaluator** is pretty straightforward - it just checks if your answer is correct compared to the ground truth.

Then you've got **Labeled Helpfulness** - this one's interesting because it's not just about being right, it's about whether the answer actually helps the user, especially when you compare it to what the reference answer is.

And then we have this **Dopeness Evaluator** - yeah, that's actually what it's called. It's a custom metric that basically checks if your response is creative and engaging, or if it's just... boring and generic.

What's cool about LangSmith is you can mix standard evaluators with custom ones like this, so you can measure what actually matters for your specific use case.

---

## Part 3: RAG Optimization Decisions (1.5 minutes)

Okay, Questions 2 and 3 are about why we made certain technical decisions.

[Scroll to Question #2]

So for chunk size - I explained why going from 500 to 1000 characters actually matters. Basically, larger chunks give you more complete context. You're less likely to cut a sentence or an idea in half. The downside is you might grab some irrelevant stuff too, but in this case, having the full context won.

[Scroll to Question #3]

And for the embedding model - we upgraded from the small version to the large version. The large one has way more dimensions - 3072 versus 1536. What that means in practice is it can capture way more subtle relationships between words and concepts.

So you get better retrieval because it understands what you're actually asking for more accurately. Obviously it costs more and takes up more space, but for this project, the quality improvement was worth it.

These aren't just theoretical differences - they actually show up in the metrics.

---

## Part 4: Experimental Results (1 minute)

Alright, last question - Activity 3.

[Scroll to Activity #3]

So we built this "dopeness" RAG chain - and yeah, I know the name is funny - but it actually made three important changes:

We bumped up the chunk size from 500 to 1000, switched to the larger embedding model, and then we added this creative prompt that specifically tells the model not to be generic.

Looking at the results, the Dopeness Evaluator obviously improved the most because we literally told it to be more creative in the prompt. But the QA Evaluator also got better because we're retrieving more relevant context. And Helpfulness benefited from everything working together.

What's really powerful here is that with synthetic data generation, you can iterate and test changes like this super quickly. You don't have to wait around for real user feedback to know if you're heading in the right direction.

---

## Conclusion (30 seconds)

So yeah, this assignment really opened my eyes to how useful synthetic data generation is. With RAGAS and LangSmith working together, you can:

One - test edge cases you wouldn't even think to write yourself.
Two - actually measure if your changes are improvements, with real numbers.
And three - iterate way faster before you ever deploy to production.

All my answers are marked with those checkmark headers, so it should be easy to find everything. Thanks for watching!

---

## Three Key Takeaways (for submission form)

1. **Synthetic data generation with knowledge graphs creates more diverse and challenging test cases than manual creation**
2. **Multi-dimensional evaluation (correctness, helpfulness, creativity) provides a holistic view of RAG performance**
3. **Iterative improvement with quantitative metrics (like the 55x context recall improvement in Session 08) is the key to production-ready RAG systems**
