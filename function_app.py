import azure.functions as func
import logging
from utils.database import execute_query
from utils.openai_client import generate_embeddings, generate_summary

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


# Add Podcast API
@app.route(route="add_podcast")
def add_podcast(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Extract data from request
        data = req.get_json()
        title = data.get("title")
        transcript = data.get("transcript")

        if not title or not transcript:
            return func.HttpResponse(
                "Missing 'title' or 'transcript' in the request body.", status_code=400
            )

        # Generate embedding and summary
        embedding = generate_embeddings(transcript)
        prompt = f"Summarize the following podcast transcript:\n{transcript}\nSummary:"
        summary = generate_summary(prompt)

        # Insert into the database
        execute_query(
            "INSERT INTO podcast_episodes (title, transcript, embedding, description) VALUES (%s, %s, %s, %s);",
            [title, transcript, embedding, summary],
        )

        return func.HttpResponse(
            f"Podcast '{title}' added successfully.", status_code=201
        )
    except Exception as e:
        logging.error(f"Error in add_podcast: {e}")
        return func.HttpResponse("Failed to add podcast.", status_code=500)


# Update User Listening History API
@app.route(route="update_user_history")
def update_user_history(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Extract data from request
        data = req.get_json()
        user_id = data.get("user_id")
        listening_history = data.get("listening_history")

        if not user_id or not listening_history:
            return func.HttpResponse(
                "Missing 'user_id' or 'listening_history' in the request body.",
                status_code=400,
            )

        # Generate new embedding for the listening history
        embedding = generate_embeddings(listening_history)

        # Update user history and embedding in the database
        execute_query(
            "UPDATE users SET listening_history = %s, embedding = %s WHERE id = %s;",
            [listening_history, embedding, user_id],
        )

        return func.HttpResponse(
            f"Listening history for user {user_id} updated successfully.",
            status_code=200,
        )
    except Exception as e:
        logging.error(f"Error in update_user_history: {e}")
        return func.HttpResponse(
            "Failed to update user listening history.", status_code=500
        )


# Recommend Podcasts API
@app.route(route="recommend_podcasts")
def recommend_podcasts(req: func.HttpRequest) -> func.HttpResponse:
    try:
        user_id = req.params.get("user_id")
        if not user_id:
            return func.HttpResponse(
                "Missing 'user_id' in query parameters.", status_code=400
            )

        # Fetch the user's embedding from the database
        user = execute_query("SELECT embedding FROM users WHERE id = %s;", [user_id])
        if not user or not user[0][0]:
            return func.HttpResponse(
                f"No embedding found for user ID {user_id}.", status_code=404
            )

        user_embedding = user[0][0]

        # Query for the most relevant podcasts
        query = """
            SELECT id, title, description, embedding <-> %s AS similarity
            FROM podcast_episodes
            WHERE embedding IS NOT NULL
            ORDER BY similarity ASC
            LIMIT 5;
        """
        recommendations = execute_query(query, [user_embedding])

        # Store recommendations in the suggested_podcasts table with GPT-generated short descriptions
        response = []
        for rec in recommendations:
            podcast_id = rec[0]
            title = rec[1]
            description = rec[2]
            similarity = rec[3]

            # Call GPT to generate a short description
            prompt = f"Summarize the following podcast in 5 words or less:\n\nPodcast: {title}\nDescription: {description}\n\nSummary:"
            short_description = generate_summary(prompt)

            # Save the recommendation with the GPT-generated description
            execute_query(
                """
                INSERT INTO suggested_podcasts (user_id, podcast_id, similarity_score)
                VALUES (%s, %s, %s);
                """,
                [user_id, podcast_id, similarity],
            )

            response.append(
                {
                    "id": podcast_id,
                    "title": title,
                    "description": short_description,
                    "similarity": similarity,
                }
            )

        return func.HttpResponse(str(response), status_code=200)
    except Exception as e:
        logging.error(f"Error in recommend_podcasts: {e}")
        return func.HttpResponse("Failed to fetch recommendations.", status_code=500)
