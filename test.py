import pickle

with open('C:/Users/krexw/Documents/GitHub/uas_2/models/male_cluster_model.pkl', 'rb') as f:
    model_data = pickle.load(f)

print(model_data.get('model'))  # This will likely print: None