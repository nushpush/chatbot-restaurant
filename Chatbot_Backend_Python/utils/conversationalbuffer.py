from flask import jsonify 
def update_history(history, history_array):
    history_array.append(history)
    if len(history_array) > 10:
        history_array.pop(0)
    return history_array