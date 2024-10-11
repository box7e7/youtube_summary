from fastapi import FastAPI, HTTPException, Request, Header
import subprocess
import openai
import os
import requests
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import markdown2
import dotenv

dotenv.load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# print("#################\n",openai.api_key,"\n#################")


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" to a list of trusted origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



def verify_token(token: str):
    try:
        response = requests.post("https://app.mehdi.cloud/verify", json={"token": token})
        response_data = response.json()
        print(response_data)
        if response.status_code == 200 and response_data.get("sub") == "Mehdi Neggazi" and response_data.get("role") == "read:write":
            return True
        return False
    except requests.RequestException:
        return False

@app.get("/transcription/{video_id}")
async def get_transcription(video_id: str, authorization: str = Header(...)):
    if not verify_token(authorization):
        raise HTTPException(status_code=401, detail="Authentication and Authorization failed.")
    try:
        # Execute the youtube_subtitle.sh script with the video_id as an argument
        result = subprocess.run(["bash", "youtube_subtitle.sh", f"https://youtu.be/{video_id}"], capture_output=True, text=True, check=True)
        
        # Return the script's output as the transcription
        return {"transcription": result.stdout}
    except subprocess.CalledProcessError as e:
        # If the script fails, raise an HTTP exception with the error message
        raise HTTPException(status_code=500, detail=f"Error getting transcription: {e.stderr}")

@app.get("/summarize/{video_id}")
async def summarize_video(video_id: str, authorization: str = Header(...)):
    if not verify_token(authorization):
        raise HTTPException(status_code=401, detail="Authentication and Authorization failed.")
    try:
        # Execute the youtube_subtitle.sh script with the video_id as an argument
        result = subprocess.run(["bash", "youtube_subtitle.sh", f"https://youtu.be/{video_id}"], capture_output=True, text=True, check=True)
        
        # Get the transcription output
        transcription = result.stdout
        
        # Define system instructions for the model
        system_instructions = (
            "Summarize the content of a YouTube video using its provided script by first detecting the main topic chapters present in the video, "
            "then providing a summary for each chapter. Finally, offer a comprehensive summary conclusion of the entire video.\n\n"
            "# Steps\n"
            "1. **Identify Main Topic Chapters:**\n"
            "   - Read through the provided script.\n"
            "   - Detect and list the main chapters or sections in the video. This can be based on title cards, changes in topic, or other indicators.\n"
            "2. **Summarize Each Chapter:**\n"
            "   - For each identified chapter, provide a concise summary capturing the key points discussed.\n"
            "   - Ensure the summaries are consistent in style and length.\n"
            "3. **Comprehensive Conclusion:**\n"
            "   - Provide an overall summary that encapsulates the entire video content.\n"
            "   - Highlight major themes, insights, or conclusions drawn from the video.\n"
            "# Output Format\n"
            "- **Main Chapters:** List of identified chapters.\n"
            "- **Chapter Summaries:** A series of short, uniform paragraphs summarizing each chapter.\n"
            "- **Comprehensive Conclusion:** A concluding paragraph summarizing the entire video.\n"
        )
        
        # Call OpenAI API for summarization
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": transcription}
            ]
        )
        
        # Extract and return the output
        summary_output = response.choices[0].message['content']
        return {"summary": summary_output,"transcription": transcription}
    except subprocess.CalledProcessError as e:
        # If the script fails, raise an HTTP exception with the error message
        raise HTTPException(status_code=500, detail=f"Error getting transcription: {e.stderr}")
    except openai.error.OpenAIError as e:
        # If the OpenAI API call fails, raise an HTTP exception with the error message
        raise HTTPException(status_code=500, detail=f"Error summarizing transcription: {str(e)}")

@app.get("/summarize_html/{video_id}", response_class=HTMLResponse)
async def summarize_video_html(video_id: str, authorization: str = Header(...)):
    if not verify_token(authorization):
        raise HTTPException(status_code=401, detail="Authentication and Authorization failed.")
    try:
        # Execute the youtube_subtitle.sh script with the video_id as an argument
        result = subprocess.run(["bash", "youtube_subtitle.sh", f"https://youtu.be/{video_id}"], capture_output=True, text=True, check=True)
        
        # Get the transcription output
        transcription = result.stdout
        
        # Define system instructions for the model
        system_instructions = (
            "Summarize the content of a YouTube video using its provided script by first detecting the main topic chapters present in the video, "
            "then providing a summary for each chapter. Finally, offer a comprehensive summary conclusion of the entire video.\n\n"
            "# Steps\n"
            "1. **Identify Main Topic Chapters:**\n"
            "   - Read through the provided script.\n"
            "   - Detect and list the main chapters or sections in the video. This can be based on title cards, changes in topic, or other indicators.\n"
            "2. **Summarize Each Chapter:**\n"
            "   - For each identified chapter, provide a concise summary capturing the key points discussed.\n"
            "   - Ensure the summaries are consistent in style and length.\n"
            "3. **Comprehensive Conclusion:**\n"
            "   - Provide an overall summary that encapsulates the entire video content.\n"
            "   - Highlight major themes, insights, or conclusions drawn from the video.\n"
            "# Output Format\n"
            "- **Main Chapters:** List of identified chapters.\n"
            "- **Chapter Summaries:** A series of short, uniform paragraphs summarizing each chapter.\n"
            "- **Comprehensive Conclusion:** A concluding paragraph summarizing the entire video.\n"
        )
        
        # Call OpenAI API for summarization
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": transcription}
            ]
        )
        
        # Extract the output and convert markdown to HTML
        summary_output = response.choices[0].message['content']
        summary_html = markdown2.markdown(summary_output)
        # Add custom CSS for a professional blog style
        css = """
        <style>
            body {
                font-family: 'Georgia', serif;
                line-height: 1.8;
                color: #333;
                margin: 20px;
                padding: 20px;
                background-color: #fefefe;
                max-width: 800px;
                margin-left: auto;
                margin-right: auto;
                box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
            }
            h1, h2, h3 {
                color: #2c3e50;
                font-weight: bold;
            }
            p {
                margin-bottom: 1.5em;
            }
            ul {
                margin-left: 20px;
                list-style-type: disc;
            }
            li {
                margin-bottom: 0.75em;
            }
            blockquote {
                font-style: italic;
                color: #555;
                border-left: 4px solid #ccc;
                margin-left: 0;
                padding-left: 15px;
            }
            a {
                color: #3498db;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
        """
        summary_html = css + summary_html
        return HTMLResponse(content=summary_html)
    except subprocess.CalledProcessError as e:
        # If the script fails, raise an HTTP exception with the error message
        raise HTTPException(status_code=500, detail=f"Error getting transcription: {e.stderr}")
    except openai.error.OpenAIError as e:
        # If the OpenAI API call fails, raise an HTTP exception with the error message
        raise HTTPException(status_code=500, detail=f"Error summarizing transcription: {str(e)}")

@app.post("/query/{video_id}")
async def query_video(video_id: str, request: Request, authorization: str = Header(...)):
    if not verify_token(authorization):
        raise HTTPException(status_code=401, detail="Authentication and Authorization failed.")
    try:
        # Execute the youtube_subtitle.sh script with the video_id as an argument
        result = subprocess.run(["bash", "youtube_subtitle.sh", f"https://youtu.be/{video_id}"], capture_output=True, text=True, check=True)
        
        # Get the transcription output
        transcription = result.stdout
        
        # Get the query from the request body
        body = await request.json()
        query = body.get("query")
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required in the request body.")
        
        # Define system instructions for the model
        system_instructions = (
            f"Transcription between delimiters:\n\n---\n{transcription}\n---\n\n"
            "Answer the following query based on the provided transcription."
        )
        
        # Call OpenAI API for querying
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": query}
            ]
        )
        
        # Extract and return the output
        answer_output = response.choices[0].message['content']
        return {"answer": answer_output,"transcription": transcription}
    except subprocess.CalledProcessError as e:
        # If the script fails, raise an HTTP exception with the error message
        raise HTTPException(status_code=500, detail=f"Error getting transcription: {e.stderr}")
    except openai.error.OpenAIError as e:
        # If the OpenAI API call fails, raise an HTTP exception with the error message
        raise HTTPException(status_code=500, detail=f"Error querying transcription: {str(e)}")
    


@app.post("/ask/{video_id}")
async def ask_video(video_id: str, request: Request, authorization: str = Header(...)):
    if not verify_token(authorization):
        raise HTTPException(status_code=401, detail="Authentication and Authorization failed.")
    try:
        # Extract transcript and query from request body
        body = await request.json()
        transcript = body.get("transcript")
        query = body.get("query")

        if not transcript or not query:
            raise HTTPException(status_code=400, detail="Both 'transcript' and 'query' fields are required.")

        # Define system instructions for the model
        system_instructions = (
            f"Transcription between delimiters:\n\n---\n{transcript}\n---\n\n"
            "Answer the following query based on the provided transcription."
        )

        # Call OpenAI API for querying
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": query}
            ]
        )

        # Extract and return the output
        answer_output = response.choices[0].message['content']
        return {"response": answer_output}

     
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

