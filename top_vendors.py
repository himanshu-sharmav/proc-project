import numpy as np
import pandas as pd
import json

def load_and_prepare_data(json_data):
    # Load the JSON data
    # data = json.loads(json_data)
    df_from_json = pd.json_normalize(json_data['data'])

    # Drop rows with missing 'Rate' or 'Total Business'
    df_from_json = df_from_json.dropna(subset=['Rate', 'Total_Business'])

    # Select relevant features
    features = df_from_json[['Rate', 'Total_Business']]

    # Standardize the features
    def standardize(features):
        return (features - np.mean(features, axis=0)) / np.std(features, axis=0)

    scaled_features = standardize(features.values)

    # Implementing K-Means algorithm from scratch
    def kmeans(X, n_clusters, n_init=10, max_iter=300):
        best_inertia = None
        best_labels = None
        best_centers = None

        for _ in range(n_init):
            initial_centroids = X[np.random.choice(X.shape[0], n_clusters, replace=False)]
            centroids = initial_centroids
            for _ in range(max_iter):
                labels = np.argmin(np.linalg.norm(X[:, np.newaxis] - centroids, axis=2), axis=1)
                new_centroids = np.array([X[labels == j].mean(axis=0) for j in range(n_clusters)])
                if np.all(centroids == new_centroids):
                    break
                centroids = new_centroids
            inertia = np.sum([np.linalg.norm(X[labels == j] - centroids[j])**2 for j in range(n_clusters)])
            if best_inertia is None or inertia < best_inertia:
                best_inertia = inertia
                best_labels = labels
                best_centers = centroids

        return best_labels, best_centers, best_inertia

    # Determine the maximum number of clusters to consider
    max_clusters = min(10, scaled_features.shape[0])  # Limit to the number of samples if less than 10
    inertia = []
    for i in range(1, max_clusters + 1):
        labels, centers, cluster_inertia = kmeans(scaled_features, n_clusters=i)
        inertia.append(cluster_inertia)

    # Find the elbow point (optimal k) using a simple heuristic
    optimal_k = np.argmax(np.diff(inertia)) + 2

    # Apply K-Means clustering
    labels, centers, _ = kmeans(scaled_features, n_clusters=optimal_k)
    df_from_json['Cluster'] = labels

    return df_from_json

def get_top_vendors_in_cluster(cluster_id, df_from_json, industry, top_n):
    cluster_df = df_from_json[(df_from_json['Cluster'] == cluster_id) & (df_from_json['Industry'] == industry)]
    if cluster_df.empty:
        return pd.DataFrame()

    cluster_df['Score'] = cluster_df['Rate'] * 0.7 + cluster_df['Total_Business'] * 0.3
    top_vendors = cluster_df.sort_values(by='Score', ascending=False).head(top_n)
    # print(top_vendors)
    return top_vendors[['Organization', 'email', 'Industry', 'Location', 'Rate', 'Total_Business','PK','SK']]

def recommend_vendors(industry, df_from_json, top_n):
    industry_location_df = df_from_json[df_from_json['Industry'] == industry]
    industry_clusters = industry_location_df['Cluster'].unique()
    recommendations = pd.DataFrame()
    for cluster in industry_clusters:
        top_vendors = get_top_vendors_in_cluster(cluster, df_from_json, industry, top_n)
        recommendations = pd.concat([recommendations, top_vendors])
    if recommendations.empty:
        return recommendations
    recommendations['Score'] = recommendations['Rate'] * 0.7 + recommendations['Total_Business'] * 0.3
    recommendations = recommendations.sort_values(by='Score', ascending=False).head(top_n)
    # print(recommendations)
    return recommendations[['Organization', 'email', 'Industry', 'Location', 'Rate', 'Total_Business','PK','SK']]


