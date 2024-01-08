import streamlit as st
import matplotlib.pyplot as plt
import preprocessor, helper
import seaborn as sns
from io import BytesIO
import base64
import pandas as pd
from textblob import TextBlob

# Set a nice Streamlit page style
st.set_page_config(page_title="Whatsapp Chat Analyzer", layout="wide", initial_sidebar_state="expanded")

# Sidebar
st.sidebar.title("Whatsapp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("Choose a file")

# Main content
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    st.dataframe(df)

    # Fetching unique users
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")
    selected_user = st.sidebar.selectbox("Show analysis of", user_list)

    # Button to trigger analysis
    if st.sidebar.button("Show Analysis"):

        # Fetching statistics
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

        # Display top statistics
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Messages", num_messages)

        with col2:
            st.metric("Total Words", words)

        with col3:
            st.metric("Media Shared", num_media_messages)

        with col4:
            st.metric("Links Shared", num_links)

        # Busiest users
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values, color='skyblue')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)

        # Most common words
        most_common_df = helper.most_common_words(selected_user, df)

        fig, ax = plt.subplots()

        ax.bar(most_common_df[0], most_common_df[1], color='salmon')
        plt.xticks(rotation='vertical')

        st.title('Most Common Words')
        st.pyplot(fig)

        # Emoji analysis
        emoji_df = helper.emoji_helper(selected_user, df)
        st.title("Emoji Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)

        with col2:
            try:
                fig, ax = plt.subplots()
                ax.pie(emoji_df['Count'].head(), labels=emoji_df['Emoji'].head(), autopct="%0.2f", colors=sns.color_palette("pastel"))

                image_stream = BytesIO()
                fig.savefig(image_stream, format='png')
                plt.close(fig)

                image_stream.seek(0)
                image_base64 = base64.b64encode(image_stream.read()).decode("utf-8")
                st.image(f"data:image/png;base64,{image_base64}")

            except UserWarning as w:
                if "missing from current font" in str(w):
                    missing_emoji = str(w).split("'")[1]
                    print(f"Warning: Emoji {missing_emoji} not supported by the font.")
                    emoji_df['Emoji'] = emoji_df['Emoji'].replace(missing_emoji, f"{missing_emoji} (text)")

                    fig, ax = plt.subplots()
                    ax.pie(emoji_df['Count'].head(), labels=emoji_df['Emoji'].head(), autopct="%0.2f", colors=sns.color_palette("pastel"))

                    image_stream = BytesIO()
                    fig.savefig(image_stream, format='png')
                    plt.close(fig)
                    image_stream.seek(0)
                    image_base64 = base64.b64encode(image_stream.read()).decode("utf-8")
                    st.image(f"data:image/png;base64,{image_base64}")

        # Monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='mediumseagreen')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='darkslategray')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Activity map
        st.title('Activity Map')
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='plum')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='gold')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # Weekly Activity Map
        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap, cmap="Blues")
        st.pyplot(fig)

        # Sentiment Analysis
        st.title("Sentiment Analysis")

        if selected_user != 'Overall':
            user_messages = df[df['user'] == selected_user]['message']
            overall_sentiment = TextBlob(' '.join(user_messages)).sentiment

            # Add a sentiment emoji and color-coded labels
            sentiment_label = "😐 Neutral"
            if overall_sentiment.polarity > 0:
                sentiment_label = "😊 Positive"
            elif overall_sentiment.polarity < 0:
                sentiment_label = "😞 Negative"

            st.subheader(f"Overall Sentiment for {selected_user}: {sentiment_label}")
            st.write(f"Polarity: {overall_sentiment.polarity:.2f}, Subjectivity: {overall_sentiment.subjectivity:.2f}")

            # Use color-coded labels
            if overall_sentiment.polarity > 0:
                st.success("Positive Sentiment")
            elif overall_sentiment.polarity < 0:
                st.error("Negative Sentiment")
            else:
                st.warning("Neutral Sentiment")

        else:
            overall_sentiment = TextBlob(' '.join(df['message'])).sentiment

            # Add a sentiment emoji and color-coded labels
            sentiment_label = "😐 Neutral"
            if overall_sentiment.polarity > 0:
                sentiment_label = "😊 Positive"
            elif overall_sentiment.polarity < 0:
                sentiment_label = "😞 Negative"

            st.subheader(f"Overall Sentiment for the entire conversation: {sentiment_label}")
            st.write(f"Polarity: {overall_sentiment.polarity:.2f}, Subjectivity: {overall_sentiment.subjectivity:.2f}")

            # Use color-coded labels
            if overall_sentiment.polarity > 0:
                st.success("Positive Sentiment")
            elif overall_sentiment.polarity < 0:
                st.error("Negative Sentiment")
            else:
                st.warning("Neutral Sentiment")
