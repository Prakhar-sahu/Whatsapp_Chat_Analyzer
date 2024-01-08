from urlextract import URLExtract
# from wordcloud import WordCloud
# import plotly.express as px
import pandas as pd
from collections import Counter
import emoji
extract=URLExtract()
def fetch_stats(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # fetch the number of messages
    num_messages = df.shape[0]

    # fetch the total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # fetch number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))
        

    return num_messages,len(words),num_media_messages,len(links)

def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x,df

# def create_wordcloud(selected_user,df):
#     if selected_user != 'Overall':
#         df = df[df['user'] == selected_user]
    
#     font_path="C:\Windows\Fonts\Consolas"
#     wc = WordCloud(width=500,height=500,min_font_size=10,background_color='white',font_path=font_path)
#     # temp['message'] = temp['message'].apply(remove_stop_words)
#     df_wc = wc.generate(df['message'].str.cat(sep=" "))
#     return df_wc
# def plotly_wordcloud(selected_user, df):
#     df_wc = create_wordcloud(selected_user, df)

#     wordcloud_fig = px.imshow(df_wc.to_array(), binary_string=True)
#     wordcloud_fig.update_layout(title_text='Word Cloud')
    
#     return wordcloud_fig

def most_common_words(selected_user,df):

    f = open('stop_hinglish.txt','r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []

    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df
def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    emojis = []

    for message in df['message']:
        emoji_list = emoji.emoji_list(message)
        emojis.extend(emoji_info['emoji'] for emoji_info in emoji_list)

    emoji_count = Counter(emojis)
    emoji_df = pd.DataFrame(list(emoji_count.items()), columns=['Emoji', 'Count'])
    emoji_df = emoji_df.sort_values(by='Count', ascending=False)

    return emoji_df

def monthly_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap