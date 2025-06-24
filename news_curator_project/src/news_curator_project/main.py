import os
# Import your Crew class from within the project package
from news_curator_project.crew import NewsCuratorCrew

def run():
    print("--- Personalized News Curator Chatbot ---")
    print("Tell me what news you're interested in (e.g., 'latest tech news', 'finance highlights', 'health news summary').")
    print("Type 'exit' to quit.")

    # Initialize your Crew
    # Corrected: Directly instantiate NewsCuratorCrew, not NewsCuratorProject()
    news_curator_app = NewsCuratorCrew()

    while True:
        user_query = input("\nYou: ")
        if user_query.lower() in ["exit", "quit", "bye"]:
            print("News Curator: Goodbye! Stay informed!")
            break

        try:
            # Kick off the crew with the user's query
            print("\n--- Processing your request... ---")
            # Corrected: Call kickoff on the news_curator_app instance
            result = news_curator_app.kickoff(user_input=user_query)
            print("\n--- Here is your personalized news summary ---")
            print(f"News Curator: {result}")
        except Exception as e:
            print(f"\nNews Curator Error: An error occurred during news curation. {e}")
            # For detailed debugging during development, you might uncomment:
            # import traceback
            # traceback.print_exc()

if __name__ == "__main__":
    # Set your OpenAI API key as an environment variable before running.
    # For example, create a .env file in your project root with:
    # OPENAI_API_KEY="your_api_key_here"
    # And then use: from dotenv import load_dotenv; load_dotenv()
    # Or set it directly in your terminal:
    # On Windows (PowerShell): $env:OPENAI_API_KEY="your_api_key_here"
    # On macOS/Linux (Bash/Zsh): export OPENAI_API_KEY="your_api_key_here"
    
    run()

