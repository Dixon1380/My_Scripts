import openai
import requests
import discord
import json
import os
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
import jwt
import asyncio

# Load environment variables (store API keys in .env file for security)
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
GHOST_API_URL = os.getenv("GHOST_API_URL")  
GHOST_ADMIN_API_KEY = os.getenv("GHOST_ADMIN_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
REQUESTS_FILE = "blog_requests.json"


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

async def notify_new_blog():
    """Checks for new blog posts and notifies Discord"""
    last_notified = None

    while True:
        response = requests.get("https://bytewhere.com/ghost/api/content/posts/?key=YOUR_CONTENT_API_KEY")
        if response.status_code == 200:
            posts = response.json().get("posts", [])
            if posts:
                latest = posts[0]
                title = latest["title"]
                url = f"https://bytewhere.com/{latest['slug']}"
                
                if last_notified != title:
                    last_notified = title
                    channel = bot.get_channel(DISCORD_CHANNEL_ID)  # Replace with actual channel ID
                    await channel.send(f"📢 **New Blog Published!**\n**{title}**\n🔗 {url} @everyone")

        await asyncio.sleep(3600)  # Check every hour


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
        prompt = f"Summarize the following blog post: {blog_text[:3000]}"  # Limit content to 3000 chars
        ai_response = openai_create(prompt)
        return ai_response.choices[0].message.content
    
    return "Couldn't fetch the blog post."

# Initialize Discord Bot
intents = discord.Intents.default()

intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Discord Command: Help
@bot.command(name="help")
async def help_command(ctx):
    help_text = """
    **🤖 Available Commands:**
    - `!help` → Shows this help message
    - `!latest` → Get the latest blog post
    - `!schedule` → See the upcoming blog schedule
    - `!recommend` → Recommend the best blog post for you
    - `!summary [blog_url]` → Summarize a blog for you
    - `!topics` → Get a list of topics covered
    - `!request [topic]` → Request a blog on a specific topic
    - `!search [keyword]` → Search blogs on our site using that keyword
    - `!digest` → Get weekly digest 
    - `!about` → Learn more about this bot
    """
    await ctx.send(help_text)

# Discord Command: Get Latest Blog post   
@bot.command(name="latest")
async def latest_blog(ctx):
    """Fetches the latest published blog post from Ghost API"""
    GHOST_API_URL = "https://bytewhere.com/ghost/api/content/posts/?key=YOUR_CONTENT_API_KEY"
    
    response = requests.get(GHOST_API_URL)
    if response.status_code == 200:
        posts = response.json().get("posts", [])
        if posts:
            latest = posts[0]
            title = latest["title"]
            url = f"https://bytewhere.com/{latest['slug']}"
            await ctx.send(f"📰 **Latest Blog Post:**\n**{title}**\n🔗 {url}")
        else:
            await ctx.send("❌ No blog posts found.")
    else:
        await ctx.send("⚠️ Could not fetch latest blog post. Try again later.")

# Discord Command: Schedule Blogs
@bot.command(name="schedule")
async def blog_schedule(ctx):
    """Fetch upcoming scheduled posts"""
    GHOST_API_URL = "https://bytewhere.com/ghost/api/admin/posts/?key=YOUR_ADMIN_API_KEY&filter=status:scheduled"
    
    response = requests.get(GHOST_API_URL)
    if response.status_code == 200:
        posts = response.json().get("posts", [])
        if posts:
            schedule_list = "\n".join([f"📅 **{p['title']}** - {p['published_at']}" for p in posts])
            await ctx.send(f"📆 **Upcoming Scheduled Posts:**\n{schedule_list}")
        else:
            await ctx.send("❌ No upcoming posts scheduled.")
    else:
        await ctx.send("⚠️ Could not fetch scheduled posts. Try again later.")

# Discord Command: Did You Know?
@bot.command(name="fact")
async def tech_fact(ctx):
    """Fetches a random AI-generated fun fact"""
    fact_prompt = "Tell me a cool fun fact about computers or the internet. Format it like this: Did you know [fact]?"
    
    ai_fact = openai_create(fact_prompt, content="You are a tech expert sharing fun facts.")
    fact = ai_fact.choices[0].message.content
    await ctx.send(f"💡 **Did you know:** {fact}")


@bot.command(name="poll")
async def start_poll(ctx, *, question):
    """Creates a poll with AI-generated choices"""
    poll_prompt = f"Generate 3 voting options for this question:\n{question}"
    
    ai_choices = openai_create(poll_prompt, content="You are an AI that generates poll choices.").choices[0].message.content.split("\n")

    poll_message = await ctx.send(f"📊 **POLL:** {question}\n1️⃣ {ai_choices[0]}\n2️⃣ {ai_choices[1]}\n3️⃣ {ai_choices[2]}")
    await poll_message.add_reaction("1️⃣")
    await poll_message.add_reaction("2️⃣")
    await poll_message.add_reaction("3️⃣")

@bot.command(name="request")
async def request_topic(ctx, *, topic):
    """Saves user blog topic requests"""
    try:
        with open(REQUESTS_FILE, "r") as file:
            requests_list = json.load(file)
    except FileNotFoundError:
        requests_list = []

    requests_list.append({"user": ctx.author.name, "topic": topic})

    with open(REQUESTS_FILE, "w") as file:
        json.dump(requests_list, file, indent=4)

    await ctx.send(f"✅ Your request for **'{topic}'** has been saved! It will be considered for future blog posts.")


# Discord Command: Recommend Blog Post
@bot.command(name="recommend")
async def recommend(ctx, *, query: str):
    await ctx.send("🔍 Finding the best blog post for you...")
    recommendation = recommend_blog(query)
    await ctx.send(recommendation)

# Discord Command: Summarize Blog Post via url
@bot.command(name="summary")
async def summary(ctx, *, url: str):
    await ctx.send("📄 Summarizing blog post...")
    summary_text = summarize_blog(url)
    await ctx.send(summary_text)
# Discord command: Shows a list of topics
@bot.command(name="topics")
async def blog_topics(ctx):
    topics = [
        "💻 Computer Literacy",
        "🛡 Cybersecurity",
        "📊 Data Privacy",
        "🤖 AI & Automation",
        "🌐 Web Development",
        "📱 Digital Trends",
    ]
    await ctx.send(f"🔍 **Here are the blog categories we cover:**\n" + "\n".join(topics))

# Discord Command: Learn about Bytewhere    
@bot.command(name="about")
async def about_bot(ctx):
    """Displays bot information"""
    about_text = (
        "🤖 **ByteWhere Blog Bot** - Your friendly blog assistant!\n"
        "🚀 I can help you stay updated with the latest blog posts, upcoming topics, and even take your topic requests!\n"
        "🔗 Check out our blog: [ByteWhere](https://bytewhere.com)\n"
        "📢 Use `!help` to see what I can do!"
    )
    await ctx.send(about_text)

@bot.command(name="search")
async def search_blog(ctx, *, keyword):
    """Searches for blog posts containing the keyword"""
    response = requests.get(f"https://bytewhere.com/ghost/api/content/posts/?key=YOUR_CONTENT_API_KEY&filter=title:{keyword}")
    
    if response.status_code == 200:
        posts = response.json().get("posts", [])
        if posts:
            result_list = "\n".join([f"🔗 **{p['title']}**: https://bytewhere.com/{p['slug']}" for p in posts])
            await ctx.send(f"🔍 **Search Results for '{keyword}':**\n{result_list}")
        else:
            await ctx.send(f"❌ No results found for '{keyword}'.")

@bot.command(name="digest")
async def weekly_digest(ctx):
    """Sends the top posts of the week"""
    response = requests.get("https://bytewhere.com/ghost/api/content/posts/?key=YOUR_CONTENT_API_KEY&limit=5")
    
    if response.status_code == 200:
        posts = response.json().get("posts", [])
        digest_list = "\n".join([f"🔗 **{p['title']}**: https://bytewhere.com/{p['slug']}" for p in posts])
        await ctx.send(f"📅 **Weekly Blog Digest:**\n{digest_list}")
    else:
        await ctx.send("⚠️ Could not fetch the weekly digest.")


# Start Discord Bot
print_message("Chatbot is running....")
bot.run(DISCORD_BOT_TOKEN)
