import praw
import pandas as pd
import re
import numpy as np
import nltk
from nltk.tokenize import word_tokenize

# Download NLTK resources
nltk.download('punkt')

# Initialize PRAW with your credentials
reddit = praw.Reddit(client_id='Z',
                     client_secret='Y',
                     user_agent="my_app:MyRedditPrawScript:v1.0 (by X)")

def contains_media(submission):
    media_keywords = ['image', 'video']
    if any(re.search(r'\b{}\b'.format(keyword), submission.selftext, re.IGNORECASE) for keyword in media_keywords):
        return True

    media_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.gifv', '.mp4']
    if any(ext in submission.url.lower() for ext in media_extensions):
        return True

    return False

# Function to tokenize text
def tokenize_text(text):
    tokens = word_tokenize(text)
    return tokens

# Read the CSV file
data = pd.read_csv("....csv/ AntiVegan.csv")

# Initialize counters and lists
text_based_count = 0
media_based_count = 0
post_counts = []
unique_user_counts = []
top2_percentages = []
token_counts = []

# Iterate through each row and classify the links
for index, row in data.iterrows():
    permalink = row['permalink']
    full_url = f"https://www.reddit.com{permalink}"
    try:
        submission = reddit.submission(url=full_url)
        if contains_media(submission):
            media_based_count += 1
            print(f"{full_url} - Media Based")
        else:
            text_based_count += 1
            print(f"{full_url} - Text Based")

        # Count the number of posts in the conversation
        post_count = len(submission.comments.list())
        post_counts.append(post_count)

        # Tokenize the submission title and content
        title_tokens = tokenize_text(submission.title)
        content_tokens = tokenize_text(submission.selftext)

        # Calculate the total number of tokens in the submission
        total_tokens_submission = len(title_tokens) + len(content_tokens)

        # Count the number of tokens in comments
        comment_tokens = []
        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            comment_tokens.extend(tokenize_text(comment.body))

        # Calculate the total number of tokens in comments
        total_tokens_comments = len(comment_tokens)

        # Calculate the total number of tokens in the conversation
        total_tokens_conversation = total_tokens_submission + total_tokens_comments
        token_counts.append(total_tokens_conversation)

        # Count unique users and calculate top 2 users' contribution percentage
        unique_users = set()
        user_counts = {}

        submission.comments.replace_more(limit=None)
        total_comments = 0
        for comment in submission.comments.list():
            total_comments += 1
            unique_users.add(comment.author)
            user = str(comment.author)
            if user in user_counts:
                user_counts[user] += 1
            else:
                user_counts[user] = 1

        sorted_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)
        top2_total = sum(count for _, count in sorted_users[:2])
        top2_percentage = (top2_total / total_comments) * 100 if total_comments != 0 else 0

        unique_user_counts.append(len(unique_users))
        top2_percentages.append(top2_percentage)

    except Exception as e:
        print(f"Error processing URL {full_url}: {e}")

# Calculate mean and standard deviation of post counts
mean_posts = np.mean(post_counts)
std_dev_posts = np.std(post_counts)

# Calculate average number of tokens across posts
avg_tokens_per_post = np.mean(token_counts)

# Calculate average number of posts per submission
avg_posts_per_submission = np.mean(post_counts)

# Calculate average number of tokens combining submissions and posts within a conversation
avg_tokens_per_conversation = np.mean(token_counts) / np.mean(post_counts)

# Calculate the average number of unique users
avg_unique_users = np.mean(unique_user_counts)

# Calculate the average percentage of posts contributed by top 2 users across all conversations
avg_top2_percentage = np.mean(top2_percentages)

# Print statistics
print("Text-based conversations:", text_based_count)
print("Conversations containing images or videos:", media_based_count)
print("Total URLs processed:", len(data))
print("Mean number of posts per conversation:", mean_posts)
print("Standard deviation of posts per conversation:", std_dev_posts)
print("Average number of tokens across posts:", avg_tokens_per_post)
print("Average number of posts per submission:", avg_posts_per_submission)
print("Average number of tokens combining submissions and posts within a conversation:", avg_tokens_per_conversation)
print("Average number of unique users within each conversation:", avg_unique_users)
print("Average percentage of posts contributed by top 2 users across all conversations:", avg_top2_percentage)
