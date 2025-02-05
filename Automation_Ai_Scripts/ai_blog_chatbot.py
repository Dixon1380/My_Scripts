import openai
import requests
import discord
import json
import os
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
import jwt

# Load environment variables (store API keys in .env file for security)
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
GHOST_API_URL = os.getenv("GHOST_API_URL")  
GHOST_ADMIN_API_KEY = os.getenv("GHOST_ADMIN_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")


def print_message(message):
    print(message)
    
def openai_create(prompt, content="You are an AI assistant", model="gpt-4-turbo"):
    """
    Calls OpenAI's API to generate text using a specified model.

    :param prompt: The user input or task description.
    :param content: The system's instruction (default: "You are an AI assistant.")
    :param model: The GPT model to use (default: "gpt-4-turbo").
    :return: The AI-generated response.
    """
    try:
        output = openai.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": content},
                    {"role": "user", "content": prompt}]
        )
        return output
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return None
    
# Generates token for Ghost API 
def generate_token(key):
    key_id, secret = key.split(":")  # Extract key ID and secret

    iat = int(datetime.now().timestamp())
    exp = iat + 5 * 60  # Token expires in 5 minutes

    header = {"alg": "HS256", "kid": key_id, "typ": "JWT"}
    payload = {
        "exp": exp,
        "iat": iat,
        "aud": "/admin/"  # Correct audience format
    }

    # Generate the JWT token
    token = jwt.encode(payload, bytes.fromhex(secret), algorithm="HS256", headers=header)
    return token

# Initialize Discord Bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Fetch blog posts from Ghost API
def fetch_blog_posts():
    jwt_token = generate_token(GHOST_ADMIN_API_KEY)
    
    params = {"key": jwt_token, "limit": "all"}

    response = requests.get(GHOST_API_URL, params=params)

    if response.status_code == 200:
        print_message("Response code", response.status_code)
        return response.json().get("posts", [])
    return []

# AI Blog Post Recommendation
def recommend_blog(user_query):
    blog_posts = fetch_blog_posts()
    
    prompt = f"""
    You are an AI assistant for a tech blog. Based on the user's query, recommend the most relevant blog post from the following:
    {json.dumps(blog_posts, indent=2)}
    
    User Query: {user_query}
    Provide a response that includes:
    - The best matching blog post title
    - A short summary of the blog post
    - A direct link to the full post
    """
    
    response = openai_create(prompt)

    return response.choices[0].message.content

# AI Blog Post Summarizer
def summarize_blog(blog_url):
    response = requests.get(blog_url)
    if response.status_code == 200:
        blog_text = response.text  # Assume it's HTML, needs parsing
        prompt = f"Summarize the following blog post:
        {blog_text[:3000]}"  # Limit content to 3000 chars
        
        ai_response = openai_create(prompt)
        return ai_response.choices[0].message.content
    
    return "Couldn't fetch the blog post."

# Discord Command: Recommend Blog Post
@bot.command(name="recommend")
async def recommend(ctx, *, query: str):
    await ctx.send("🔍 Finding the best blog post for you...")
    recommendation = recommend_blog(query)
    await ctx.send(recommendation)

# Discord Command: Summarize Blog Post
@bot.command(name="summary")
async def summary(ctx, *, url: str):
    await ctx.send("📄 Summarizing blog post...")
    summary_text = summarize_blog(url)
    await ctx.send(summary_text)

# Start Discord Bot
bot.run(DISCORD_BOT_TOKEN)
