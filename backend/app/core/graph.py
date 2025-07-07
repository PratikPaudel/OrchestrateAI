import os
from typing import List, TypedDict, Annotated, Dict, Any
import operator
import logging
import time

from langgraph.graph import StateGraph, END
from pydantic import BaseModel

# Import your agent classes
from app.agents.planner import PlannerAgent, ResearchPlan
from app.agents.searcher import SearcherAgent
from app.agents.summarizer import SummarizerAgent
from app.agents.reviewer import ReviewerAgent, Review
from app.agents.writer import WriterAgent
from app.core.rate_limiter import rate_limiter
from app.core.multi_llm import multi_llm_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orchestrateai.graph")

# --- 1. Define the State for the Graph ---
# The state is a dictionary that will be passed between nodes.
# It holds all the information gathered during the research process.

class GraphState(TypedDict):
    """State for the research graph."""
    query: str
    plan: ResearchPlan
    current_task_index: int
    search_results: List[Dict[str, Any]]
    research_data: List[Dict[str, Any]]
    final_report: str
    error: str


# --- 2. Instantiate Agents ---
# Create single instances of our agents to be used by the nodes.

planner_agent = PlannerAgent()
searcher_agent = SearcherAgent()
summarizer_agent = SummarizerAgent()
reviewer_agent = ReviewerAgent()
writer_agent = WriterAgent()


# --- 3. Define the Node Functions ---
# Each node in the graph is a function that takes the current state
# and returns a dictionary with the values to update in the state.

def planner_node(state: GraphState) -> dict:
    """Planner node that creates a research plan."""
    try:
        logger.info("--- 📝 Executing Planner Node ---")
        plan = planner_agent.create_plan(state["query"])
        logger.info(f"Plan created with {len(plan.plan)} tasks.")
        return {
            "plan": plan,
            "current_task_index": 0,
            "search_results": [],
            "research_data": [],
            "final_report": "",
            "error": ""
        }
    except Exception as e:
        logger.error(f"Planner node failed: {e}")
        return {"error": f"Planner node failed: {e}"}

def searcher_node(state: GraphState) -> dict:
    """Searcher node that finds relevant information."""
    try:
        current_task = state["plan"].plan[state["current_task_index"]]
        logger.info(f"--- 🔍 Executing Searcher Node for Task {state['current_task_index'] + 1} ---")
        logger.info(f"Searching for: {current_task}")
        
        search_results = searcher_agent.search(current_task)
        
        logger.info(f"Found {len(search_results)} search results.")
        return {"search_results": search_results}
    except Exception as e:
        logger.error(f"Searcher node failed: {e}")
        return {"error": f"Searcher node failed: {e}"}

def summarize_and_review_node(state: GraphState) -> dict:
    """Combined summarize and review node for efficiency."""
    try:
        logger.info(f"--- 📖 Executing Summarize & Review Node for Task {state['current_task_index'] + 1} ---")
        
        reviewed_summaries = []
        
        search_results = state.get("search_results", [])
        current_task = state["plan"].plan[state["current_task_index"]]
        
        for i, result in enumerate(search_results):
            logger.info(f"    - Processing result {i+1}/{len(search_results)}: {result['url']}")
            
            try:
                # Summarize the content
                logger.info(f"    - Summarizing URL: {result['url']}")
                summary = summarizer_agent.summarize(current_task, result["content"])
                
                # Review the summary
                logger.info(f"    - Reviewing Summary for: {result['url']}")
                review = reviewer_agent.review(summary, result["url"])
                
                if review.is_reliable:
                    logger.info(f"    - Source accepted: {result['url']}")
                    reviewed_summaries.append({
                        "url": result["url"],
                        "title": result.get("title", "Unknown"),
                        "summary": summary,
                        "review": review.dict(),
                        "task": current_task
                    })
                else:
                    logger.warning(f"    - Discarding unreliable source: {result['url']}")
                    
            except Exception as e:
                logger.error(f"    - Error processing {result['url']}: {e}")
                continue
        
        # Update the overall research data with the findings from this task
        logger.info(f"Task {state['current_task_index'] + 1} complete. Waiting 1 second before next task...")
        logger.info(f"Adding {len(reviewed_summaries)} reviewed summaries to research data")
        
        # Manually accumulate research data
        existing_research_data = state.get("research_data", [])
        updated_research_data = existing_research_data + reviewed_summaries
        logger.info(f"Total research data items: {len(updated_research_data)}")
        
        time.sleep(1)  # Reduced delay - rate limiter handles timing
        return {
            "research_data": updated_research_data,
            "current_task_index": state["current_task_index"] + 1
        }
    except Exception as e:
        logger.error(f"Summarize & Review node failed: {e}")
        return {"error": f"Summarize & Review node failed: {e}"}

def writer_node(state: GraphState) -> dict:
    """Writer node that creates the final report."""
    try:
        logger.info("--- ✍️ Executing Writer Node ---")
        
        # Debug: Log the research data structure
        logger.info(f"Research data type: {type(state['research_data'])}")
        logger.info(f"Research data length: {len(state['research_data'])}")
        if state['research_data']:
            logger.info(f"First item type: {type(state['research_data'][0])}")
            logger.info(f"First item keys: {list(state['research_data'][0].keys()) if isinstance(state['research_data'][0], dict) else 'Not a dict'}")
        
        # Prepare research data for the writer
        research_data_str = ""
        for item in state["research_data"]:
            try:
                if isinstance(item, dict):
                    url = item.get('url', 'Unknown URL')
                    task = item.get('task', 'Unknown Task')
                    summary = item.get('summary', 'No summary available')
                    
                    # Handle review data safely
                    review_data = item.get('review', {})
                    if isinstance(review_data, dict):
                        critique = review_data.get('critique', 'No critique available')
                    else:
                        critique = str(review_data) if review_data else 'No critique available'
                    
                    research_data_str += f"Source: {url}\n"
                    research_data_str += f"Task: {task}\n"
                    research_data_str += f"Summary: {summary}\n"
                    research_data_str += f"Review: {critique}\n"
                    research_data_str += "---\n"
                else:
                    logger.warning(f"Skipping non-dict item: {type(item)}")
            except Exception as item_error:
                logger.error(f"Error processing research item: {item_error}")
                continue
        
        if not research_data_str.strip():
            research_data_str = "No research data available."
        
        final_report = writer_agent.write_report(state["query"], research_data_str)
        logger.info("Final report written.")
        
        return {"final_report": final_report}
    except Exception as e:
        logger.error(f"Writer node failed: {e}")
        return {"error": f"Writer node failed: {e}"}

def error_node(state: GraphState) -> dict:
    error_msg = state.get('error', 'Unknown error')
    logger.error(f"Workflow halted due to error: {error_msg}")
    return {"final_report": f"ERROR: {error_msg}"}

# --- 4. Define Conditional Logic ---
# This function decides which node to run next based on the current state.

def should_continue(state: GraphState) -> str:
    """Determine if we should continue to the next task or finish."""
    try:
        if state["current_task_index"] < len(state["plan"].plan):
            logger.info("    - More tasks remaining. Looping back to searcher.")
            return "continue"
        else:
            logger.info("    - All tasks complete. Proceeding to writer.")
            return "finish"
    except Exception as e:
        logger.error(f"Error in should_continue: {e}")
        return "finish"


# --- 5. Build the Graph ---
# Wire all the nodes and edges together into a state machine.

workflow = StateGraph(GraphState)

# Add nodes to the graph
workflow.add_node("planner", planner_node)
workflow.add_node("searcher", searcher_node)
workflow.add_node("summarize_and_review", summarize_and_review_node)
workflow.add_node("writer", writer_node)
workflow.add_node("error", error_node)

# Set the entry point of the graph
workflow.set_entry_point("planner")

# Add edges to define the flow
workflow.add_edge("planner", "searcher")
workflow.add_edge("searcher", "summarize_and_review")
workflow.add_edge("writer", END) # The writer node is the final step
workflow.add_edge("error", END)

# Add the conditional edge for the research loop
workflow.add_conditional_edges(
    "summarize_and_review",
    should_continue,
    {
        "continue": "searcher",
        "finish": "writer",
        "error": "error",
    }
)

# Add conditional edges for error handling
workflow.add_conditional_edges(
    "planner",
    lambda state: "error" if state.get("error") else "searcher",
    {"searcher": "searcher", "error": "error"}
)

workflow.add_conditional_edges(
    "searcher",
    lambda state: "error" if state.get("error") else "summarize_and_review",
    {"summarize_and_review": "summarize_and_review", "error": "error"}
)

workflow.add_conditional_edges(
    "writer",
    lambda state: "error" if state.get("error") else END,
    {END: END, "error": "error"}
)

# Compile the graph into a runnable object
research_graph = workflow.compile()


# This allows you to run `python graph.py` to test the entire flow.
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    # Define the initial input for the graph
    inputs = {
        "query": "Is solar power a viable alternative to fossil fuels in 2024?"
    }

    # Stream the graph's execution and print the output of each step
    for output in research_graph.stream(inputs, stream_mode="values"):
        # The 'stream_mode="values"' yields the entire state object at each step
        print("\n" + "="*80)
        print("CURRENT STATE:")
        # Find the last key that was updated in this step
        last_key = list(output.keys())[-1]
        print(f"Last updated field: '{last_key}'")
        print(output[last_key])
        print("="*80 + "\n")

    # The final state contains the report
    final_report = list(research_graph.stream(inputs, stream_mode="values"))[-1]['final_report']
    print("\n--- ✅ FINAL REPORT ---")
    print(final_report)

def execute_research(query: str) -> Dict[str, Any]:
    """Execute the research workflow."""
    try:
        # Log rate limiter stats at start
        stats = rate_limiter.get_stats()
        logger.info(f"Starting research with rate limiter stats: {stats}")
        
        # Log multi-LLM stats at start
        llm_stats = multi_llm_client.get_stats()
        logger.info(f"Starting research with multi-LLM stats: {llm_stats}")
        
        result = research_graph.invoke({"query": query})
        
        # Log final rate limiter stats
        final_stats = rate_limiter.get_stats()
        logger.info(f"Research completed. Final rate limiter stats: {final_stats}")
        
        # Log final multi-LLM stats
        final_llm_stats = multi_llm_client.get_stats()
        logger.info(f"Research completed. Final multi-LLM stats: {final_llm_stats}")
        
        return result
    except Exception as e:
        logger.error(f"Research execution failed: {e}")
        return {"error": str(e)}