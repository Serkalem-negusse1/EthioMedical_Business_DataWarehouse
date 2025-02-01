import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from datetime import datetime
import re
from collections import Counter

# Load dataset
df = pd.read_csv("telegram_data.csv", encoding="latin1")

# Display basic info
print("Initial Data Overview:")
print(df.info())
print(df.head())

# Convert date column to datetime format
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Drop rows where Date could not be parsed
df = df.dropna(subset=['Date'])

# Drop duplicates
df = df.drop_duplicates()

# Fill missing messages with empty strings
df['Message'] = df['Message'].fillna("")

# Function to clean message text
def clean_text(text):
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
    text = text.lower()  # Convert to lowercase
    return text

df['Cleaned_Message'] = df['Message'].apply(clean_text)

# Plot message frequency over time
plt.figure(figsize=(12, 6))
df['Date'].dt.date.value_counts().sort_index().plot(kind='line')
plt.title('Messages Over Time')
plt.xlabel('Date')
plt.ylabel('Number of Messages')
plt.xticks(rotation=45)
plt.show()

# Word Cloud of most common words
all_text = ' '.join(df['Cleaned_Message'])
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text)
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.title("Most Common Words in Messages")
plt.show()

# Top active channels
plt.figure(figsize=(10, 5))
df['Channel Title'].value_counts().nlargest(10).plot(kind='bar', color='skyblue')
plt.title('Top 10 Active Channels')
plt.xlabel('Channel Title')
plt.ylabel('Number of Messages')
plt.xticks(rotation=45, ha='right')  # Align labels to the right
plt.show()


# Save cleaned data
df.to_csv("cleaned_telegram_data.csv", index=False)
print("Data Cleaning and EDA Completed. Cleaned data saved to 'cleaned_telegram_data.csv'")
