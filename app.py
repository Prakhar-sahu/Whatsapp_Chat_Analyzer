# app.py
import streamlit as st
import matplotlib.pyplot as plt
import preprocessor,helper
import seaborn as sns
from io import BytesIO
import base64
import pandas as pd
st.sidebar.title("Whatsapp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    # st.text(data)
    df=preprocessor.preprocess(data)
    st.dataframe(df)
    #fetching unique userrs 
    user_list=df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,"Overall")
    selected_user = st.sidebar.selectbox("show analysis of",user_list)
    #button
    if st.sidebar.button("Show Analysis"):
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user,df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)
        
        #busiest users
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x,new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values,color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

            
            # WordCloud
            # st.title("Wordcloud")
            # wordcloud_plot = helper.plotly_wordcloud(selected_user, df)
            # # df_wc = helper.create_wordcloud(selected_user,df)
            # # fig,ax = plt.subplots()
            # # ax.imshow(df_wc)
            # # st.pyplot(fig)
            # st.plotly_chart(wordcloud_plot)

        # most common words
        most_common_df = helper.most_common_words(selected_user,df)

        fig,ax = plt.subplots()

        ax.bar(most_common_df[0],most_common_df[1])
        plt.xticks(rotation='vertical')

        st.title('Most commmon words')
        st.pyplot(fig)

        # emoji analysis
        # sns.set_theme()
        emoji_df = helper.emoji_helper(selected_user,df)
        st.title("Emoji Analysis")

        col1,col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)
        
        with col2:
            try:
                plt.rcParams['font.family'] = 'c:\Windows\Fonts\SEGUIEMJ.TTF'  
                fig, ax = plt.subplots()
                ax.pie(emoji_df['Count'].head(), labels=emoji_df['Emoji'].head(), autopct="%0.2f")

                # Save the plot to a BytesIO object
                image_stream = BytesIO()
                fig.savefig(image_stream, format='png')
                plt.close(fig)

                # Display the image using base64 encoding
                image_stream.seek(0)
                image_base64 = base64.b64encode(image_stream.read()).decode("utf-8")
                st.image(f"data:image/png;base64,{image_base64}")

            except UserWarning as w:
                if "missing from current font" in str(w):
                    missing_emoji = str(w).split("'")[1]
                    print(f"Warning: Emoji {missing_emoji} not supported by the font.")
                    emoji_df['Emoji'] = emoji_df['Emoji'].replace(missing_emoji, f"{missing_emoji} (text)")

                    # Regenerate the pie chart with updated emoji labels
                    fig, ax = plt.subplots()
                    ax.pie(emoji_df['Count'].head(), labels=emoji_df['Emoji'].head(), autopct="%0.2f")

                    # Save and display the regenerated plot
                    image_stream = BytesIO()
                    fig.savefig(image_stream, format='png')
                    plt.close(fig)
                    image_stream.seek(0)
                    image_base64 = base64.b64encode(image_stream.read()).decode("utf-8")
                    st.image(f"data:image/png;base64,{image_base64}")

        # monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user,df)
        fig,ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'],color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

         # daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # activity map
        st.title('Activity Map')
        col1,col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user,df)
            fig,ax = plt.subplots()
            ax.bar(busy_day.index,busy_day.values,color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values,color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user,df)
        fig,ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)
