import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

class MLModel:
    def __init__(self, user_profiles):
        self.user_profiles = user_profiles
        self.model = None
        self.scaler = StandardScaler()

    def calculate_similarity(self, user, neighbor):
        user_profile = self.user_profiles[user]
        neighbor_profile = self.user_profiles[neighbor]

        # Calculate mutual friends
        user_friends = set(user_profile['friends'])
        neighbor_friends = set(neighbor_profile['friends'])
        mutual_friends = len(user_friends.intersection(neighbor_friends))

        # Calculate shared interests
        user_interests = set(user_profile['interests'])
        neighbor_interests = set(neighbor_profile['interests'])
        shared_interests = len(user_interests.intersection(neighbor_interests))

        # Calculate age similarity
        age_similarity = 1 - abs(user_profile['age'] - neighbor_profile['age']) / 100

        # Calculate activity similarity
        user_activities = set(user_profile['activities'].split(', '))
        neighbor_activities = set(neighbor_profile['activities'].split(', '))
        activity_similarity = len(user_activities.intersection(neighbor_activities)) / len(user_activities.union(neighbor_activities)) if user_activities.union(neighbor_activities) else 0

        # Calculate occupation similarity
        occupation_similarity = 1 if user_profile['occupation'] == neighbor_profile['occupation'] else 0

        # Calculate location similarity
        location_similarity = 1 if user_profile['location'] == neighbor_profile['location'] else 0

        return mutual_friends, shared_interests, age_similarity, activity_similarity, occupation_similarity, location_similarity
    def train_model(self, classifier_type='logistic'):
        X = []
        y = []
        
        for user, profile in self.user_profiles.items():
            for friend in profile['friends']:
                similarities = self.calculate_similarity(user, friend)
                X.append(similarities)
                y.append(1)  # They are friends

                # Generate negative samples (non-friends)
                for non_friend in self.user_profiles:
                    if non_friend != user and non_friend not in profile['friends']:
                        similarities = self.calculate_similarity(user, non_friend)
                        X.append(similarities)
                        y.append(0)  # They are not friends

        X = np.array(X)
        y = np.array(y)
        # X = [
        # # Each row represents a user pair (user1, user2)
        #     [
        #         mutual_friends_count,      # Number of mutual friends
        #         interaction_score,         # Like/comment frequency
        #         profile_similarity,        # Based on interests/demographics
        #         connection_age,           # How long they've known each other
        #         communication_frequency,   # Message frequency
        #         group_overlap,            # Shared groups/communities
        #         geographic_distance       # Physical location proximity
        #     ]
        # ]
        # y = [
        #     1,  # Connected/Friends
        #     0   # Not Connected
        # ]
        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # Scale the features
        self.scaler.fit(X_train)
        X_train = self.scaler.transform(X_train)
        X_test = self.scaler.transform(X_test)

        # Choose classifier type
        if classifier_type == 'logistic':
            self.model = LogisticRegression(random_state=42)
        elif classifier_type == 'decision_tree':
            self.model = DecisionTreeClassifier(random_state=42)
        elif classifier_type == 'random_forest':
            self.model = RandomForestClassifier(random_state=42)
        elif classifier_type == 'svm':
            self.model = SVC(probability=True, random_state=42)
        elif classifier_type == 'knn':
            self.model = KNeighborsClassifier(n_neighbors=3)
        elif classifier_type == 'neural_network':
            self.model = MLPClassifier(hidden_layer_sizes=(10,), max_iter=1000, random_state=42)
        
        # Train the model
        self.model.fit(X_train, y_train)

        # Evaluate the model
        train_accuracy = self.model.score(X_train, y_train)
        test_accuracy = self.model.score(X_test, y_test)
        print("Training accuracy:", train_accuracy)
        print("Test accuracy:", test_accuracy)

    def predict_friendship(self, user, neighbor):
        similarities = self.calculate_similarity(user, neighbor)
        features = np.array([similarities])
        features = self.scaler.transform(features)
        
        proba = 0
        count = 0
        for similarity in similarities:
            if similarity > 1:
                proba += 1
            else :
                proba += similarity
        proba = proba / len(similarities) * 100
        return proba, similarities
