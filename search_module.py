import networkx as nx

class FriendRecommendation:
    def __init__(self, social_network, user_profiles, ml_model):
        self.social_network = social_network
        self.user_profiles = user_profiles
        self.ml_model = ml_model

    def find_recommendations(self, user):
        visited = set() # Keep track of visited nodes
        queue = [(user, 0)] # Start with the user at depth 0
        recommendations = {} # Store recommendations with probability and similarities

        while queue:
            current, depth = queue.pop(0)
            if current in visited:
                continue

            visited.add(current) 

            for neighbor in self.social_network.neighbors(current):
                # If depth is 0, we move one level deeperx
                if depth == 0:
                    queue.append((neighbor, depth + 1))
                # If depth is 1, neighbor is two hops away
                elif depth == 1:
                    if neighbor != user and neighbor not in self.social_network.neighbors(user):
                        probability, similarities = self.ml_model.predict_friendship(user, neighbor)
                        recommendations[neighbor] = (probability, similarities)
        # Debug-print to see each neighbor's probability and similarities
        for name, (prob, sims) in recommendations.items():
            print(f"Neighbor: {name},prop: {prob}, Similarities: {sims}")
        # Sort by probability descending
        return sorted(recommendations.items(), key=lambda x: -x[1][0])
