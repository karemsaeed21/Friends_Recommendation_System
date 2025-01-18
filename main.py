import tkinter as tk
from gui_module import FriendRecommendationApp
from ml_module import MLModel
from search_module import FriendRecommendation
import csv
import networkx as nx

def load_user_profiles(filename):
    user_profiles = {}
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row['name']
            interests = row['interests'].split(', ')
            friends = row['friends'].split(', ')
            age = int(row['age'])
            location = row['location']
            occupation = row['occupation']
            activities = row['activities']
            user_profiles[name] = {
                'interests': interests,
                'friends': friends,
                'age': age,
                'location': location,
                'occupation': occupation,
                'activities': activities
            } # Add the user profile to the dictionary with the name as the key for easy access
    return user_profiles
def create_social_network(user_profiles):
    social_network = nx.Graph()
    for user, profile in user_profiles.items():
        for friend in profile['friends']:
            social_network.add_edge(user, friend)
    return social_network

if __name__ == "__main__":
    # Load user profiles from CSV
    user_profiles = load_user_profiles('/Users/karem/Documents/GitHub/Friends_Recommendation_System/user_profiles.csv')
    # Create the social network graph
    social_network = create_social_network(user_profiles)
    # Initialize the machine learning model
    ml_model = MLModel(user_profiles)
    ml_model.train_model(classifier_type='knn')  # Choose the classifier type
    # Initialize the friend recommendation system
    friend_recommendation = FriendRecommendation(social_network, user_profiles, ml_model)
    # Initialize and run the GUI application
    root = tk.Tk()
    app = FriendRecommendationApp(root, ml_model, friend_recommendation)
    root.mainloop()
