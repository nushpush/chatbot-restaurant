from transformers import pipeline

# Initialize the zero-shot classification pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def is_food_related(sentence):
    # Define broader categories, including both food-related and general topics
    candidate_labels = [
        "food", 
        "cooking", 
        "ingredients", 
        "recipes", 
        "restaurants",
        "politics", 
        "history", 
        "geography", 
        "science",
        "technology"
    ]

    # Classify the input sentence
    result = classifier(sentence, candidate_labels)
    
    # Check if any of the top categories match food-related labels with a high confidence score
    food_related_labels = ["food", "cooking", "ingredients", "recipes", "restaurants"]
    for label, score in zip(result['labels'], result['scores']):
        print(f"Label: {label}, Score: {score}")
        if label in food_related_labels and score > 0.5:  # Higher confidence threshold for food-related topics
            return True

    # If none of the food-related categories are matched with high confidence, return False
    return False
