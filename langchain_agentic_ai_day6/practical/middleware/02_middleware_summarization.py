from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware


# Single condition: trigger if tokens >= 4000
agent = create_agent(
    model="gpt-5.5",
    tools=[your_weather_tool, your_calculator_tool],
    middleware=[
        SummarizationMiddleware(
            model="gpt-5.4-mini",
            trigger=("tokens", 4000),
            keep=("messages", 20),
        ),
    ],
)

# Multiple conditions: trigger if number of tokens >= 3000 OR messages >= 6
agent2 = create_agent(
    model="gpt-5.5",
    tools=[your_weather_tool, your_calculator_tool],
    middleware=[
        SummarizationMiddleware(
            model="gpt-5.4-mini",
            trigger=[
                ("tokens", 3000),
                ("messages", 6),
            ],
            keep=("messages", 20),
        ),
    ],
)

# AND logic: trigger only when tokens >= 4000 AND messages >= 10
agent3 = create_agent(
    model="gpt-5.5",
    tools=[your_weather_tool, your_calculator_tool],
    middleware=[
        SummarizationMiddleware(
            model="gpt-5.4-mini",
            trigger={"tokens": 4000, "messages": 10},
            keep=("messages", 20),
        ),
    ],
)

# Combine AND and OR: trigger if (tokens >= 5000 AND messages >= 3)
# OR (tokens >= 3000 AND messages >= 6)
agent4 = create_agent(
    model="gpt-5.5",
    tools=[your_weather_tool, your_calculator_tool],
    middleware=[
        SummarizationMiddleware(
            model="gpt-5.4-mini",
            trigger=[
                {"tokens": 5000, "messages": 3},
                {"tokens": 3000, "messages": 6},
            ],
            keep=("messages", 20),
        ),
    ],
)

# Using fractional limits
agent5 = create_agent(
    model="gpt-5.5",
    tools=[your_weather_tool, your_calculator_tool],
    middleware=[
        SummarizationMiddleware(
            model="gpt-5.4-mini",
            trigger=("fraction", 0.8),
            keep=("fraction", 0.3),
        ),
    ],
)