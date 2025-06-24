import os
import json
from crewai import Agent, Task, Crew, Process

# --- Robust BaseTool Import (Try multiple common paths) ---
try:
    from crewai.tools import BaseTool
except ImportError:
    try:
        from crewai_tools.tool_base import BaseTool
    except ImportError:
        try:
            from crewai_tools.tools import BaseTool
        except ImportError:
            try:
                from crewai_tools.tools.base import BaseTool
            except ImportError:
                raise ImportError("Could not import BaseTool from 'crewai_tools' or its known submodules. "
                                  "Please ensure 'crewai_tools' is installed correctly and is up-to-date.")

from langchain_openai import ChatOpenAI

# --- Define a Mock News API Tool ---
# This tool simulates fetching news articles.
class NewsAPITool(BaseTool):
    name: str = "News API Tool"
    description: str = "Fetches mock news articles based on a given topic. Returns a JSON string of articles."

    def _run(self, topic: str) -> str:
        """
        Simulates fetching news articles for a given topic.
        In a real scenario, this would make an API call to a news service.
        """
        mock_news_data = {
            "technology": [
                {"title": "New AI Breakthrough in Robotics", "content": "Researchers at TechLab announce a significant advancement in AI-driven robotic navigation, promising more autonomous systems.", "source": "Tech Daily"},
                {"title": "Quantum Computing Market Update", "content": "The market for quantum computing solutions is expected to grow by 25% this year, driven by investments in national research programs.", "source": "Quantum Insights"},
                {"title": "Cybersecurity Threats on the Rise", "content": "A recent report indicates a sharp increase in sophisticated phishing attacks targeting remote workers.", "source": "Security Weekly"}
            ],
            "finance": [
                {"title": "Global Stock Markets Show Resilience", "content": "Despite inflationary pressures, major global stock indices have shown unexpected resilience in the last quarter.", "source": "Financial Times"},
                {"title": "Interest Rate Hikes Expected Soon", "content": "Central banks are signaling further interest rate increases to combat persistent inflation, impacting borrowing costs.", "source": "Bloomberg"},
                {"title": "Cryptocurrency Volatility Continues", "content": "Bitcoin and Ethereum experience further price swings as regulatory uncertainty impacts investor confidence.", "source": "CoinDesk"}
            ],
            "health": [
                {"title": "New Cancer Drug Shows Promising Results", "content": "Clinical trials for a novel cancer therapy have yielded positive early results, offering new hope for patients.", "source": "Health Journal"},
                {"title": "Mental Health Awareness Campaign Launches", "content": "A nationwide campaign aims to destigmatize mental health issues and provide resources for support.", "source": "Public Health News"},
                {"title": "Vaccine Development Progress Update", "content": "Scientists are making steady progress on new vaccines for emerging infectious diseases.", "source": "Medical Gazette"}
            ]
        }

        topic_lower = topic.lower()
        found_articles = []
        for key, articles in mock_news_data.items():
            if topic_lower in key or any(topic_lower in article['title'].lower() for article in articles):
                found_articles.extend(articles)

        if not found_articles:
            return json.dumps({"status": "error", "message": f"No specific news found for '{topic}'. Showing general news."})

        return json.dumps({"status": "success", "articles": found_articles, "topic": topic})

# --- Initialize the News API Tool ---
news_api_tool = NewsAPITool()

class NewsCuratorCrew:
    def __init__(self):
        # --- Define the LLM (Large Language Model) ---
        self.news_curator_llm = ChatOpenAI(model_name="gpt-4o-mini")

        # --- 1. Define Agents ---

        # Agent 1: Interest Profiler
        self.interest_profiler = Agent(
            role='User Interest Profiler',
            goal='Accurately identify and confirm user news interests and preferences (topics, sources, desired summary length).',
            backstory=(
                "You are an attentive AI assistant specializing in understanding user preferences. "
                "Your primary goal is to extract clear, actionable news interests from user input to ensure relevant content delivery."
            ),
            verbose=True,
            allow_delegation=False,
            llm=self.news_curator_llm
        )

        # Agent 2: News Gatherer
        self.news_gatherer = Agent(
            role='News Article Fetcher',
            goal='Fetch relevant and recent news articles based on identified user interests using external tools.',
            backstory=(
                "You are a diligent news librarian, skilled at querying news databases and APIs. "
                "Your mission is to find the most pertinent articles that match the specified topics, ensuring a rich data source for summarization."
            ),
            verbose=True,
            allow_delegation=False,
            llm=self.news_curator_llm,
            tools=[news_api_tool] # Provide the news API tool to this agent
        )

        # Agent 3: Summarizer/Synthesizer
        self.summarizer = Agent(
            role='News Summarizer and Synthesizer',
            goal='Condense lengthy news articles into concise, informative summaries or highlight specific aspects as requested by the user.',
            backstory=(
                "You are an expert journalist, capable of distilling complex information into easily digestible summaries. "
                "You prioritize clarity, conciseness, and accuracy, adapting your output style based on the user's specific needs (e.g., economic impact, key takeaways)."
            ),
            verbose=True,
            allow_delegation=False,
            llm=self.news_curator_llm
        )

        # --- 2. Define Tasks ---

        # Task 1: Profile User Interests
        self.profile_interests_task = Task(
            description=(
                "Analyze the user's input: '{user_input}'. "
                "Identify the primary news topics, any mentioned preferred sources (if any), and desired summary style (e.g., 'brief', 'detailed', 'economic impact only'). "
                "Output a clear, structured summary of the user's interest for the news gathering agent. "
                "Example output: {{'topic': 'Technology', 'summary_style': 'brief'}}"
            ),
            expected_output=(
                "A JSON string containing the extracted 'topic' (str) and 'summary_style' (str, default to 'general'). "
                "Example: {{'topic': 'AI development', 'summary_style': 'brief'}}"
            ),
            agent=self.interest_profiler,
            human_input=False
        )

        # Task 2: Gather News Articles
        self.gather_news_task = Task(
            description=(
                "Using the identified 'topic' from the previous task's context, utilize the 'News API Tool' to fetch relevant news articles. "
                "Parse the JSON output from the tool and extract the 'articles' list. "
                "Pass the list of article dictionaries to the next task for summarization."
                "The tool requires a 'topic' parameter. For example: `news_api_tool.run(topic='AI')`"
            ),
            expected_output=(
                "A list of dictionaries, where each dictionary represents a news article with 'title', 'content', and 'source' keys. "
                "Example: `[{'title': 'Article 1', 'content': '...', 'source': '...'}]`"
            ),
            agent=self.news_gatherer,
            tools=[news_api_tool], # Explicitly pass the tool to the task
            context=[self.profile_interests_task] # This passes the output of the profiling task
        )

        # Task 3: Summarize News
        self.summarize_news_task = Task(
            description=(
                "Given the list of news articles from the previous task's context, read through them. "
                "Based on the original 'summary_style' identified in the first task (available in context), "
                "generate a concise and informative summary of the key takeaways from ALL provided articles. "
                "If a specific summary style was requested (e.g., 'economic impact'), focus on that aspect. "
                "Ensure the summary is easy to read and no longer than 3-5 sentences."
            ),
            expected_output=(
                "A concise, well-written summary of the news articles, tailored to the requested summary style, "
                "not exceeding 5 sentences. If no articles were found, state that clearly."
            ),
            agent=self.summarizer,
            context=[self.gather_news_task, self.profile_interests_task] # Pass both contexts: articles AND original preferences
        )

    def setup_crew(self) -> Crew:
        return Crew(
            agents=[self.interest_profiler, self.news_gatherer, self.summarizer],
            tasks=[self.profile_interests_task, self.gather_news_task, self.summarize_news_task],
            process=Process.sequential, # Tasks run in sequence
            verbose=True # See detailed execution logs
        )

    def kickoff(self, user_input: str) -> str:
        crew = self.setup_crew()
        # The user_input is passed to the first task using the 'inputs' dictionary
        result = crew.kickoff(inputs={'user_input': user_input})
        return result

