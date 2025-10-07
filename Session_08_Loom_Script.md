# Session 08 Loom Video Script: Evaluating RAG and Agents with Ragas

**Duration: 4-6 minutes**

---

## Introduction (30 seconds)

Hey everyone! So this is my Session 08 walkthrough. This one's split into two notebooks - one for evaluating RAG systems and another for evaluating agents. Both use Ragas, but they measure different things because, well, RAG and agents have different jobs to do.

Let me show you what I found. Here's the GitHub repo: https://github.com/TyroneTheCodeChainer/AIE08_MyAwesomeRep/tree/s07-s08-assignment/08_Evaluating_RAG_With_Ragas

---

## Part 1: RAG Evaluation Notebook (2.5 minutes)

Alright, let's start with the RAG evaluation notebook.

### Question 1: Chunk Overlap

[Scroll to chunk_overlap question]

So the first question was about chunk overlap. Basically, when you're splitting documents into chunks, you can choose to have some overlap between them or not.

In the baseline system, there was zero overlap. That means if important information happened to fall right at the edge of a chunk, it could get cut in half and lose context.

But when you set it to like 30 characters of overlap, you create this buffer zone. So information at the boundaries gets captured in both chunks. This way, you're way less likely to miss something important just because of bad luck with where the split happened.

### Question 2: Performance Comparison

[Scroll to performance comparison question]

Okay, this next question is where things get really wild. Check out these numbers:

The baseline system had a Context Recall of 0.0119. That's... that's basically terrible. Like, it's barely finding the right context at all. Faithfulness was 0.54, Answer Relevancy was 0.23 - not great across the board.

But then with the rerank system - and here's the crazy part - Context Recall jumped to 0.6581. That's a 55 times improvement. Fifty-five times! Faithfulness went up to 0.82, Answer Relevancy hit 0.94.

So what changed? Two main things:

First, we added Cohere's Rerank model. The way this works is, you do a broad search and pull back like 20 documents. Then the reranker looks at all of them and picks the actual top 5 most relevant ones. It's way more accurate than just relying on semantic similarity alone.

Second, we fixed the chunking. The baseline was using 50-character chunks with no overlap. That's way too small - you're just fragmenting everything. We went to 500 characters with 30 character overlap, which gives you actual complete thoughts in each chunk.

What this really shows is that retrieval quality is usually the bottleneck. You can have the best LLM in the world, but if you're feeding it garbage context, you're gonna get garbage answers.

---

## Part 2: Agent Evaluation Notebook (2 minutes)

Now let's jump to the agent evaluation notebook.

### Question 1: What is a Trace?

[Scroll to trace question]

So first question here - what's a trace?

Basically, a trace is the full record of everything that happened when the agent ran. It's got the user's question, what tools the agent decided to use, what those tools returned, and the final answer it gave.

Think of it like a detailed transcript of the agent's decision-making process. And this is super useful for evaluation because you're not just checking if the final answer is right - you can see if the agent made good decisions along the way.

### Question 2: How Metrics Are Calculated

[Scroll to metrics calculation question]

Alright, so for this question I had to explain how three different metrics actually work.

**Tool Call Accuracy** - this one checks if the agent called the right tools with the right parameters. There's an LLM judge that compares what the agent did versus what it should have done. It's a simple pass/fail - 1 if it's correct, 0 if it's not.

Like in the example, when someone asked about copper prices, the agent correctly called the get_metal_price tool with copper as the parameter, so it got a 1.

**Agent Goal Accuracy** - this is about whether the agent actually achieved what the user wanted. Another LLM judge looks at the whole conversation and decides if the goal was met.

The silver price example is perfect - user asked for the price of 10 grams, agent got the per-gram price and did the math correctly, so it scored a 1.

**Topic Adherence** - now this one's interesting. It checks if the agent stayed on topic. You give it a list of acceptable topics, and it measures how much of the response is actually about those topics.

The eagle example is hilarious - someone asked how fast an eagle can fly, and the agent answered it. But the reference topics were about metals, so it scored a 0. It failed because it should have said "I only answer questions about metals."

That last one's really important for production because you don't want your agent wandering off and answering random stuff.

---

## Part 3: Key Insights (1 minute)

So three big things I took away from this:

First - you really need quantitative evaluation. That 55x improvement in context recall? You'd never catch that just by eyeballing responses. Numbers don't lie.

Second - retrieval quality is usually your biggest problem. The baseline had a decent LLM, but the retrieval was so bad that nothing else mattered. Fix retrieval first.

And third - agents need different metrics than RAG. RAG is about faithfulness and relevance. Agents need to be measured on tool usage, goal achievement, and staying in scope. Different tools for different jobs.

All my answers have those checkmark headers, so they should be easy to find for grading.

---

## Conclusion (30 seconds)

So yeah, this assignment covered the whole evaluation lifecycle. From generating synthetic data to measuring improvements to making sure agents behave correctly.

The whole ecosystem - Ragas, LangSmith, Cohere Rerank - makes it actually possible to build stuff you can trust in production. You're not just guessing if it works.

Anyway, thanks for watching!

---

## Three Key Takeaways (for submission form)

1. **Context Recall improved 55x (0.0119 → 0.6581) with reranking, proving retrieval quality is the primary bottleneck in RAG systems**
2. **Chunk size and overlap significantly impact performance - baseline used 50 chars with no overlap (too small), while optimized used 500 chars with 30 overlap**
3. **Agent evaluation requires specialized metrics (Tool Call Accuracy, Goal Accuracy, Topic Adherence) that go beyond standard RAG metrics to ensure agents make correct decisions and stay within scope**
