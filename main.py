from crewai.flow.flow import Flow, listen, start, router, and_, or_
from pydantic import BaseModel
from crewai.agent import Agent
from crewai import LLM
from tools import web_search_tool
from seo_crew import SeoCrew
from typing import List

from virality_crew import ViralityCrew


class BlogPost(BaseModel):
    title: str = ""
    subtitle: str = ""
    sections: list[str] = []


class Tweet(BaseModel):
    content: str = ""
    hashtags: str = ""


class LinkedinPost(BaseModel):
    hook: str = ""
    content: str = ""
    call_to_action: str = ""


class Score(BaseModel):
    score: int = 0
    reason: str = ""


class ContentPipelineFlowState(BaseModel):

    # Inputs
    content_type: str = ""
    topic: str = ""

    # Internal
    max_length: int = 0
    research: str = ""
    score: Score | None = None

    # Content
    blog_post: BlogPost | None = None
    tweet: Tweet | None = None
    linkedin_post: LinkedinPost | None = None


class ContentPipelineFlow(Flow[ContentPipelineFlowState]):

    @start()
    def init_content_pipeline(self):
        if self.state.content_type not in ["blog", "tweet", "linkedin"]:
            raise ValueError("The content type must be either blog, tweet, or linkedin")

        if self.state.topic == "":
            raise ValueError("The topic must be provided")

        if self.state.content_type == "tweet":
            self.state.max_length = 150
        elif self.state.content_type == "blog":
            self.state.max_length = 800
        elif self.state.content_type == "linkedin":
            self.state.max_length = 500

    @listen(init_content_pipeline)
    def conduct_research(self):
        researcher = Agent(
            role="Head Researcher",
            backstory="You're like a digital detective who loves digging up fascinating facts and insights. You have a knack for finding the good stuff that others miss.",
            goal=f"Find the most interesting and useful information about: {self.state.topic}",
            tools=[web_search_tool],
        )

        self.state.research = response = researcher.kickoff(
            f"Find the most interesting and useful information about: {self.state.topic}"
        )

    @router(conduct_research)
    def conduct_research_router(self):
        content_type = self.state.content_type

        if content_type == "tweet":
            return "make_tweet"
        elif content_type == "blog":
            return "make_blog"
        elif content_type == "linkedin":
            return "make_linkedin_post"

    @listen(or_("make_tweet", "remake_tweet"))
    def handle_make_tweet(self):
        tweet = self.state.tweet

        llm = LLM(
            model="openai/gpt-5-mini",
            response_format=Tweet,
        )

        if tweet is None:
            result = llm.call(
                f"""
            Make a tweet that can go viral on the topic {self.state.topic} using the following research: 
            
            <research>
            =================
            {self.state.research}
            =================
            </research>
            """
            )
        else:
            result = llm.call(
                f"""
            You wrote this tweet on {self.state.topic}, but it does not have a good virality score.
            because of {self.state.score.reason}
            
            Improve it.
            
            <tweet>
            =================
            {self.state.tweet.model_dump_json()}
            =================
            </tweet>
            
            Use the following research.
            
            <research>
            =================
            {self.state.research}
            =================
            </research>
            """
            )
        self.state.tweet = Tweet.model_validate_json(result)

    @listen(or_("make_blog", "remake_blog"))
    def handle_make_blog(self):
        blog_post = self.state.blog_post

        llm = LLM(
            model="openai/gpt-5-mini",
            response_format=BlogPost,
        )

        if blog_post is None:
            result = llm.call(
                f"""
            Make a blog post with SEO practices on the topic {self.state.topic} using the following research: 
            
            <research>
            =================
            {self.state.research}
            =================
            </research>
            """
            )
        else:
            result = llm.call(
                f"""
            You wrote this blog post on {self.state.topic}, but it does not have a good SEO score.
            because of {self.state.score.reason}
            
            Improve it.
            
            <blog_post>
            =================
            {self.state.blog_post.model_dump_json()}
            =================
            </blog_post>
            
            Use the following research.
            
            <research>
            =================
            {self.state.research}
            =================
            </research>
            """
            )
        self.state.blog_post = BlogPost.model_validate_json(result)

    @listen(or_("make_linkedin_post", "remake_linkedin_post"))
    def handle_make_linkedin_post(self):
        linkedin_post = self.state.linkedin_post

        llm = LLM(
            model="openai/gpt-5-mini",
            response_format=LinkedinPost,
        )

        if linkedin_post is None:
            result = llm.call(
                f"""
            Make a linkedin post that can go viral on the topic {self.state.topic} using the following research: 
            
            <research>
            =================
            {self.state.research}
            =================
            </research>
            """
            )
        else:
            result = llm.call(
                f"""
            You wrote this linkedin post on {self.state.topic}, but it does not have a good virality score.
            because of {self.state.score.reason}
            
            Improve it.
            
            <linkedin_post>
            =================
            {self.state.linkedin_post.model_dump_json()}
            =================
            </linkedin_post>
            
            Use the following research.
            
            <research>
            =================
            {self.state.research}
            =================
            </research>
            """
            )
        self.state.linkedin_post = LinkedinPost.model_validate_json(result)

    @listen(handle_make_blog)
    def check_seo(self):
        result = (
            SeoCrew()
            .crew()
            .kickoff(
                inputs={
                    "topic": self.state.topic,
                    "blog_post": self.state.blog_post.model_dump_json(),
                }
            )
        )

        self.state.score = result.pydantic

    @listen(or_("handle_make_tweet", "handle_make_linkedin_post"))
    def check_virality(self):
        result = (
            ViralityCrew()
            .crew()
            .kickoff(
                inputs={
                    "topic": self.state.topic,
                    "content": (
                        self.state.tweet.model_dump_json()
                        if self.state.content_type == "tweet"
                        else self.state.linkedin_post.model_dump_json()
                    ),
                    "content_type": self.state.content_type,
                }
            )
        )

    @router(or_("check_seo", "check_virality"))
    def score_router(self):
        content_type = self.state.content_type
        score = self.state.score

        if score.score >= 8:
            return "check_passed"
        else:
            if content_type == "blog":
                return "remake_blog"
            elif content_type == "tweet":
                return "remake_tweet"
            elif content_type == "linkedin":
                return "remake_linkedin_post"

    @listen("check_passed")
    def finalize_content(self):
        """Finalize the content"""
        print("🎉 Finalizing content...")

        if self.state.content_type == "blog":
            print(f"📝 Blog Post: {self.state.blog_post.title}")
            print(f"🔍 SEO Score: {self.state.score.score}/100")
        elif self.state.content_type == "tweet":
            print(f"🐦 Tweet: {self.state.tweet}")
            print(f"🚀 Virality Score: {self.state.score.score}/100")
        elif self.state.content_type == "linkedin":
            print(f"💼 LinkedIn: {self.state.linkedin_post.title}")
            print(f"🚀 Virality Score: {self.state.score.score}/100")

        print("✅ Content ready for publication!")
        return (
            self.state.linkedin_post
            if self.state.content_type == "linkedin"
            else (
                self.state.tweet
                if self.state.content_type == "tweet"
                else self.state.blog_post
            )
        )


flow = ContentPipelineFlow()
# flow.plot()

flow.kickoff(
    inputs={
        "content_type": "blog",
        "topic": "AI Dog Training",
    },
)
