import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

class MLModel:
    def __init__(self, user_profiles):
        self.user_profiles = user_profiles
        self.model = None
        self.scaler = StandardScaler()

    def calculate_profile_similarity(self, user, neighbor):
        user_profile = self.user_profiles[user]
        neighbor_profile = self.user_profiles[neighbor]
        
        age_similarity = 1 - abs(user_profile['age'] - neighbor_profile['age']) / 100
        location_similarity = 1 if user_profile['location'] == neighbor_profile['location'] else 0
        occupation_similarity = 1 if user_profile['occupation'] == neighbor_profile['occupation'] else 0
        
        return age_similarity + location_similarity + occupation_similarity

    def calculate_activity_similarity(self, user, neighbor):
        user_activities = set(self.user_profiles[user]['activities'].split(', '))
        neighbor_activities = set(self.user_profiles[neighbor]['activities'].split(', '))
        intersection = user_activities.intersection(neighbor_activities)
        union = user_activities.union(neighbor_activities)
        return len(intersection) / len(union) if union else 0

    def train_model(self, classifier_type='logistic'):
        X = []
        y = []
        
        for user, profile in self.user_profiles.items():
            user_interests = set(profile['interests'])
            user_friends = set(profile['friends'])
            for friend in profile['friends']:
                friend_interests = set(self.user_profiles[friend]['interests'])
                friend_friends = set(self.user_profiles[friend]['friends'])
                
                shared_interests = len(user_interests.intersection(friend_interests))
                total_interests = len(user_interests.union(friend_interests))
                common_friends = len(user_friends.intersection(friend_friends))
                profile_similarity = self.calculate_profile_similarity(user, friend)
                activity_similarity = self.calculate_activity_similarity(user, friend)
                
                X.append([shared_interests, total_interests, common_friends, profile_similarity, activity_similarity])
                y.append(1)  # They are friends

                # Generate negative samples (non-friends)
                for non_friend in self.user_profiles:
                    if non_friend != user and non_friend not in profile['friends']:
                        non_friend_interests = set(self.user_profiles[non_friend]['interests'])
                        non_friend_friends = set(self.user_profiles[non_friend]['friends'])
                        
                        shared_interests = len(user_interests.intersection(non_friend_interests))
                        total_interests = len(user_interests.union(non_friend_interests))
                        common_friends = len(user_friends.intersection(non_friend_friends))
                        profile_similarity = self.calculate_profile_similarity(user, non_friend)
                        activity_similarity = self.calculate_activity_similarity(user, non_friend)
                        
                        X.append([shared_interests, total_interests, common_friends, profile_similarity, activity_similarity])
                        y.append(0)  # They are not friends

        X = np.array(X)
        y = np.array(y)
        
        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # Scale the features
        self.scaler.fit(X_train)
        X_train = self.scaler.transform(X_train)
        X_test = self.scaler.transform(X_test)

        # Choose classifier type
        if classifier_type == 'logistic':
            self.model = LogisticRegression()
        elif classifier_type == 'decision_tree':
            self.model = DecisionTreeClassifier()
        elif classifier_type == 'random_forest':
            self.model = RandomForestClassifier()
        elif classifier_type == 'svm':
            self.model = SVC(probability=True)
        elif classifier_type == 'knn':
            self.model = KNeighborsClassifier(n_neighbors=3)
        
        # Train the model
        self.model.fit(X_train, y_train)

        # Evaluate the model
        train_accuracy = self.model.score(X_train, y_train)
        test_accuracy = self.model.score(X_test, y_test)
        print("Training accuracy:", train_accuracy)
        print("Test accuracy:", test_accuracy)

    def predict_friendship(self, user, neighbor):
        user_interests = set(self.user_profiles[user]['interests'])
        neighbor_interests = set(self.user_profiles[neighbor]['interests'])
        user_friends = set(self.user_profiles[user]['friends'])
        neighbor_friends = set(self.user_profiles[neighbor]['friends'])
        
        shared_interests = len(user_interests.intersection(neighbor_interests))
        total_interests = len(user_interests.union(neighbor_interests))
        common_friends = len(user_friends.intersection(neighbor_friends))
        profile_similarity = self.calculate_profile_similarity(user, neighbor)
        activity_similarity = self.calculate_activity_similarity(user, neighbor)
        
        features = np.array([[shared_interests, total_interests, common_friends, profile_similarity, activity_similarity]])
        features = self.scaler.transform(features)
        
        return self.model.predict_proba(features)[0, 1]