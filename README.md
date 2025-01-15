This project implements a **personalized podcast recommendation solution** with [**Neon**](https://neon.tech/), [**Azure OpenAI**](https://azure.microsoft.com/en-us/products/ai-services/openai-service), and [**Azure Functions**](https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview). The solution dynamically analyzes user preferences and podcast data to provide highly relevant suggestions in real-time. It uses the **Generative Feedback Loops** (GFL) mechanism to continuously learn from new user interactions and content updates. Read more on how to guide blog.

## What is Generative Feedback Loops

As vector search and Retrieval Augmented Generation(RAG) become mainstream for Generative AI (GenAI) use cases, we’re looking ahead to what’s next. GenAI primarily operates in a one-way direction, generating content based on input data. Generative Feedback Loops (GFL) are focused on optimizing and improving the AI’s outputs over time through a cycle of feedback and learnings based on the production data.  In GFL, results generated from Large Language Models (LLMs) like GPT are vectorized, indexed, and saved back into vector storage for better-filtered semantic search operations. This creates a dynamic cycle that adapts LLMs to new and continuously changing data, and user needs. GFL offers personalized, up-to-date summaries and suggestions.

![What is Generative Feedback Loops](/assets/what-is-feedback-loop.png)

---

## Features

1. **Add New Podcasts**:
    - Automatically generates embeddings and summaries using Azure OpenAI and stores them in Neon.
2. **Update User Preferences**:
    - Updates user listening history and generates embeddings for personalization.
3. **Recommend Podcasts**:
    - Provides personalized podcast recommendations based on user preferences and podcast similarity using the Neon `pgvector` extension.
4. **Feedback Loop**:
    - Continuously adapts recommendations by incorporating new user preferences and podcast data.

---

## Tech Stack

- **Python**: Backend implementation.
- **Azure Functions**: Expose APIs for podcast management and recommendations.
- **Azure OpenAI**: Generate embeddings and summaries using `text-embedding-ada-002` and `gpt-4`.
- **Neon**: Serverless PostgreSQL database with `pgvector` extension for storing embeddings and performing similarity queries.

---

## How It Works

![Generative Feedback Loops with Neon serverless Postgres, Azure Functions, and Azure OpenAI](/assets/feedback-loops-in-azure.png)

1. **Add Podcast**:
    - Generates an embedding and summary using Azure OpenAI.
    - Saves the podcast data, embedding, and summary in Neon.
2. **Update User History**:
    - Generates an embedding for the user's updated listening history.
    - Saves the updated preferences and embedding in Neon.
3. **Recommend Podcasts**:
    - Fetches the user's embedding from Neon.
    - Finds the most relevant podcasts using `pgvector` similarity.
    - Generates a short description for each recommendation using GPT.
    - Stores the recommendation and GPT output in the `suggested_podcasts` table.

---

## Feedback Loop

1. **Real-Time Updates**:
    - Each new podcast or updated user preference is reflected immediately in the system.
2. **Dynamic Recommendations**:
    - Recommendations evolve based on user interactions and new data.
3. **Adaptability**:
    - The system automatically scales with more users and podcasts.

---

## Project Structure

```
generative-feedback-loops-example/
├── .env                    # Environment variables (Neon connection string, Azure OpenAI keys, etc.)
├── requirements.txt        # Python dependencies
├── host.json
├── local.settings.json
├── function_app.py         # Single file with all Azure Function definitions
├── utils/
│   ├── database.py         # Database utilities for Neon
│   ├── openai_client.py    # Azure OpenAI client utility
│   └── config.py           # Configuration management
├── data/
│   └── sample_data.sql     # Sample SQL data for podcasts and users
```

---

## Set Up Database

**Create a Neon Project**

1. Navigate to the [Neon Console](https://console.neon.tech/)
2. Click "New Project"
3. Select **Azure** as your cloud provider
4. Choose East US 2 as your region
5. Give your project a name (e.g., "generative-feedback-loop")
6. Click "Create Project"
7. Once the project is created successfully, copy the Neon **connection string.** You can find the connection details in the **Connection Details** widget on the Neon **Dashboard.**

**Set Up Database Tables**

Open the SQL editor in Neon and execute the following script to set up the schema:

```sql
-- Create a table to store vector embeddings
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE podcast_episodes (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    transcript TEXT NOT NULL,
    embedding VECTOR(1536)
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    listening_history TEXT,
    embedding VECTOR(1536)
);

CREATE TABLE suggested_podcasts (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    podcast_id INT NOT NULL,
    suggested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    similarity_score FLOAT,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (podcast_id) REFERENCES podcast_episodes (id) ON DELETE CASCADE
);
```

**Insert Sample Data**

Add sample users:

```sql
INSERT INTO users (name, listening_history)
VALUES
('Alice', 'Interested in AI, deep learning, and neural networks.'),
('Bob', 'Enjoys podcasts about robotics, automation, and machine learning.'),
('Charlie', 'Fascinated by space exploration, astronomy, and astrophysics.'),
('Diana', 'Prefers topics on fitness, nutrition, and mental health.'),
('Eve', 'Likes discussions on blockchain, cryptocurrency, and decentralized finance.'),
('Frank', 'Follows podcasts about history, culture, and ancient civilizations.');
```

## Azure Functions Setup Instructions

### 1. Prerequisites

- [Python 3.8 or later version](https://www.python.org/)
- [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=macos%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-csharp) installed
- A free [Neon account](https://console.neon.tech/signup)
- An [Azure account](https://azure.microsoft.com/free/) with an active subscription

### 2. Clone the Repository

```bash
git clone https://github.com/neondatabase-labs/generative-feedback-loops-example
cd generative-feedback-loops-example
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory with the following:

```
DATABASE_URL=your-neon-database-connection-string
OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
OPENAI_API_KEY=your-azure-openai-key
EMBEDDING_MODEL=text-embedding-ada-002
GPT_MODEL=gpt-4
```

### 4. Install Dependencies**

```bash
pip install -r requirements.txt
```

### 5. Start Azure Functions**

```bash
func start
```

---

### API Endpoints

### 1. Add Podcast

- **Description**: Add a new podcast episode.
- **Endpoint**: `POST /add_podcast`
- **Request Body**:
    
    ```json
    
    {
      "title": "Future of Robotics",
      "transcript": "This episode discusses robotics, AI, and automation..."
    }
    ```
    
- **Response**:
    
    ```json
    
    {
      "status": "Podcast 'Future of Robotics' added successfully."
    }
    ```
    

### **2. Update User History**

- **Description**: Updates user listening history and generates embeddings.
- **Endpoint**: `POST /update_user_history`
- **Request Body**:
    
    ```json
    
    {
      "user_id": 1,
      "listening_history": "Exploring robotics, AI, and automation advancements."
    }
    ```
    
- **Response**:
    
    ```json
    
    {
      "status": "User 1's history updated."
    }
    ```
    

### **3. Recommend Podcasts**

- **Description**: Fetches personalized podcast recommendations.
- **Endpoint**: `GET /recommend_podcasts?user_id=<user_id>`
- **Response**:
    
    ```json
    [
      {
        "id": 1,
        "title": "AI and the Future",
        "original_description": "Full transcript about AI and its future...",
        "short_description": "AI shapes tomorrow.",
        "similarity": 0.123
      }
    ]
    ```
    
### Future Improvements

1. **Enhanced User Analytics**:
    - Track user interactions (e.g., likes, skips) for better recommendations.
2. **Filter Expired Suggestions**:
    - Automatically expire old recommendations after a set period.
3. **Frontend Integration**:
    - Build a web or mobile app to provide an interactive UI for users.