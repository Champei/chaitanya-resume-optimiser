from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
import os

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,
    api_key=os.getenv("OPENAI_API_KEY")
)

def run_crew_review(ats_result: dict) -> dict:
    reviewer = Agent(
        role="ATS Resume Evaluator",
        goal="Evaluate resume-job match based strictly on extracted data",
        backstory=(
            "You are an ATS expert who reviews structured resume data, "
            "job descriptions, and ATS scores. You do not invent information. "
            "You only reason about what is provided."
        ),
        llm=llm,
        allow_delegation=False
    )

    task = Task(
        description=(
            "Given the following ATS analysis data, explain:\n"
            "1. Why the ATS score is what it is\n"
            "2. Strengths of the resume\n"
            "3. Gaps relative to the job description\n"
            "4. Whether the score feels fair\n\n"
            f"DATA:\n{ats_result}"
        ),
        agent=reviewer,
        expected_output="A concise, structured evaluation without adding new facts."
    )

    crew = Crew(
        agents=[reviewer],
        tasks=[task]
    )

    explanation = crew.kickoff()

    return {
        "structured_result": ats_result,
        "agent_review": explanation
    }
