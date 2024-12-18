class FriendRecommendation:
    def __init__(self, social_network, user_profiles, ml_model):
        self.social_network = social_network
        self.user_profiles = user_profiles
        self.ml_model = ml_model

    def find_recommendations(self, user):
        visited = set()
        queue = [(user, 0)]
        recommendations = {}

        while queue:
            current, depth = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            for neighbor in self.social_network.neighbors(current):
                if depth == 0:
                    queue.append((neighbor, depth + 1))
                elif depth == 1 and neighbor != user and neighbor not in self.social_network.neighbors(user):
                    recommendations[neighbor] = self.ml_model.predict_friendship(user, neighbor)

        return sorted(recommendations.items(), key=lambda x: -x[1])