from crewai.flow.flow import Flow, listen, start, router, and_, or_
from pydantic import BaseModel


class ContentPipelineFlowState(BaseModel):

    # Inputs
    content_type: str = ""
    topic: str = ""

    # Internal
    max_length: int = 0


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
        print("Researching...")
        return True

    @router(conduct_research)
    def router(self):
        content_type = self.state.content_type

        if content_type == "tweet":
            return "make_tweet"
        elif content_type == "blog":
            return "make_blog"
        elif content_type == "linkedin":
            return "make_linkedin_post"

    @listen("make_tweet")
    def handle_make_tweet(self):
        print("Making tweet...")

    @listen("make_blog")
    def handle_make_blog(self):
        print("Making blog post...")

    @listen("make_linkedin_post")
    def handle_make_linkedin_post(self):
        print("Making LinkedIn post...")

    @listen(handle_make_blog)
    def check_seo(self):
        print("Checking Blog SEO...")

    @listen(or_(handle_make_tweet, handle_make_linkedin_post))
    def check_virality(self):
        print("Checking virality...")

    @listen(or_(check_seo, check_virality))
    def finalize_content(self):
        print("Finalizing content...")


flow = ContentPipelineFlow()
flow.plot()

# flow.kickoff(
#     inputs={
#         "content_type": "tweet",
#         "topic": "AI Dog Training",
#     }
# )
