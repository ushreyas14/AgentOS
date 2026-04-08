# Multi-Agent Productivity System

This project is a multi-agent system built with the Google Agent Development Kit (ADK). It features a coordinator agent that delegates tasks to specialist agents for managing tasks, calendar events, and notes.

## Setup

1.  **Set API Key**: Before running the application, you need to set your Google API key as an environment variable.

    ```bash
    export GOOGLE_API_KEY="your-api-key-here"
    ```

2.  **Install Dependencies**: Install the required Python packages.

    ```bash
    pip install -r requirements.txt
    ```

## Running the Streamlit UI

To run the web-based user interface locally:

```bash
streamlit run streamlit_app.py
```

## Deployment with Docker

You can build and run this application as a Docker container.

1.  **Build the Docker image**:

    ```bash
    docker build -t multi-agent-system .
    ```

2.  **Run the Docker container**: Make sure to pass your `GOOGLE_API_KEY` as an environment variable to the container.

    ```bash
    docker run -p 8501:8501 -e GOOGLE_API_KEY=$GOOGLE_API_KEY multi-agent-system
    ```

    You can then access the application at `http://localhost:8501`.