import streamlit as st
from functions.get_ai import get_ai_recommended_poses
import json
from youtubesearchpython import VideosSearch
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient

SENDGRID_API_KEY = st.secrets["SENDGRID_API_KEY"]

st.set_page_config(
    page_title="Yoga Connect",
    page_icon="🧘",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://twitter.com/dotAadarsh',
        'Report a bug': "https://github.com/dotAadarsh",
        'About': "Get personalized yoga recommendations and email follow-ups for a fulfilling practice!"
    }
)

def send_dynamic_email(to_emails, data):
    FROM_EMAIL = st.secrets["FROM_EMAIL"]
    TEMPLATE_ID = st.secrets["TEMPLATE_ID"]

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=[to_emails]
    )
    message.dynamic_template_data = data
    
    message.template_id = TEMPLATE_ID

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print("Dynamic Messages Sent!")
        return "Dynamic Messages Sent!"

    except Exception as e:
        print(f"Error: {e}")
        return "Error sending email"

def fetch_video_url(search_query):
    videosSearch = VideosSearch(search_query, limit=1)
    results = videosSearch.result()
    for video in results['result']:
        return video['link']

def main():
    """
    Main function for the Yoga Connect application.
    """
    # Set the title and description for the application
    st.title("Yoga Connect 🧘")
    st.write("Get personalized yoga recommendations and email follow-ups for a fulfilling practice!")

    # Check if user_data exists in the session state, if not, initialize it as an empty dictionary
    if "user_data" not in st.session_state:
        st.session_state.user_data = {}

    # Prompt the user to select their yoga experience level
    st.session_state.user_data["experience_level"] = st.selectbox("Yoga Experience Level", ["Beginner", "Intermediate", "Advanced"])

    # Prompt the user to select their yoga goals
    st.session_state.user_data["goals"] = st.multiselect("Yoga Goals", ["Flexibility", "Strength", "Relaxation"])

    # Prompt the user to enter any physical limitations (optional)
    st.session_state.user_data["limitations"] = st.text_input("Physical Limitations (optional)", "")

    # Prompt the user to enter their email address
    st.session_state.user_data["email"] = st.text_input("Enter your email address")

    # If the "Get Yoga Recommendations and Send Email" button is clicked
    if st.button("Get Yoga Recommendations and Send Email"):
        # Get AI-recommended yoga poses based on user data
        recommended_poses = get_ai_recommended_poses(st.session_state.user_data)

        # Load the recommended poses data into the session state
        st.session_state.data = json.loads(recommended_poses)

        # Set the flag to show the recommendations
        st.session_state.show_recommendations = True

    # If the flag to show recommendations is set to True
    if st.session_state.get("show_recommendations", False):
        data = st.session_state.data
        
        # Display the title for the yoga poses section
        st.title("Yoga Poses")
        st.write("Here are some popular yoga poses and their details:")
        
        video_urls = []
        
        # Iterate over each yoga pose in the data
        for pose in data["yoga_poses"]:
            # Display the pose name as a subheader
            st.subheader(pose["name"])

            # Display the Sanskrit name of the pose
            st.write("Sanskrit Name: ", pose["sanskrit_name"])

            # Display the benefits of the pose
            st.write("Benefits: ", pose["benefits"])
            
            # Display the best time to do the pose
            st.write("Best Time to Do: ", pose["best_time_to_do"])

            # Display suggestions and tips for the pose
            st.write("Suggestions & Tips: ", pose["suggestions_tips"])

            # Fetch the video URL for the pose
            search_query = pose["name"]
            video_url = fetch_video_url(search_query)
            video_urls.append(video_url)

            # Display the video URL and embed the video
            st.write("Video URL: ", video_url)
            st.video(video_url)
            
            # Add a separator between poses
            st.write("---")

        # Update the yoga poses data with the corresponding video URLs
        for pose, url in zip(data["yoga_poses"], video_urls):
            pose["youtube_url"] = url

        # Send a dynamic email with the user data and yoga poses data
        send_dynamic_email(st.session_state.user_data["email"], data)
    
        # Display a toast message indicating that the email was sent successfully
        st.toast(f"Email sent successfully to {st.session_state.user_data['email']}! Check your inbox!")

if __name__ == "__main__":
    main()
