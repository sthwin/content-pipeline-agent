from crewai.project import CrewBase, agent, task, crew
from crewai import Agent, Task, Crew
from pydantic import BaseModel


class Score(BaseModel):
    score: int = 0
    reason: str = ""


# 마지막 태스크의 output이 crew의 전체 output이 됨


@CrewBase
class SeoCrew:

    @agent
    def seo_expert(self):
        return Agent(
            role="SEO Specialist",
            goal="Analyze blog posts for SEO optimization and provide a score with detailed reasoning. Be Very strict demanding, don't give underserved good scores.",
            backstory="""You are a seasoned SEO expert with a knack for identifying and improving SEO elements in blog posts.
            You analyze blog posts for keyword usage, meta descriptions, content structure, readability, and search intent alignment to help content rank better in search engines.
            """,
            verbose=True,
        )

    @task
    def seo_audit(self):
        return Task(
            description="""Analyze the blog post for SEO effectiveness and provide:
            
            1. An SEO score from 0-10 based on:
                - Keyword optimization
                - Title effectiveness
                - Content structure (headers, paragraphs)
                - Content length and quality
                - Readability
                - Search intent alignment
                
            2. A clear reason explaining the score, focusing on:
                - Main strengths (if score is high)
                - Critical weaknesses that need improvement (if score is low)
                - The most important factor affecting the score
                
            Blog post to analyze: {blog_post}
            Target topic: {topic}
            """,
            expected_output="""A Score object with:
            - score: integer from 0-10 rating the SEO quality
            - reason: string explaining the main factors affecting the score
            """,
            agent=self.seo_expert(),
            output_pydantic=Score,
            verbose=True,
        )

    @crew
    def crew(self):
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
        )
