from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from flask_cors import CORS
import os
import json
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# CORS configuration
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": ["http://localhost:5000", "http://127.0.0.1:5000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

# Upload configuration
UPLOAD_FOLDER = 'uploads'
AUDIO_FOLDER = os.path.join(UPLOAD_FOLDER, 'audio')
COVER_FOLDER = os.path.join(UPLOAD_FOLDER, 'covers')
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'flac', 'm4a'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5MB

# Create upload folders
os.makedirs(AUDIO_FOLDER, exist_ok=True)
os.makedirs(COVER_FOLDER, exist_ok=True)

# File validation
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# === DATA STRUCTURES ===

# 1. Singly Linked List - Song Node
class SongNode:
    def __init__(self, song_id, title, artist, duration, genre, audio_path, cover_path):
        self.id = song_id
        self.title = title
        self.artist = artist
        self.duration = duration
        self.genre = genre
        self.audio_path = audio_path
        self.cover_path = cover_path
        self.next = None

# 2. Singly Linked List - Playlist
class Playlist:
    def __init__(self):
        self.head = None
        self.current = None
    
    def add_song(self, song):
        new_node = SongNode(song['id'], song['title'], song['artist'], 
                          song['duration'], song['genre'], 
                          song['audio_path'], song['cover_path'])
        if not self.head:
            self.head = new_node
            self.current = new_node
        else:
            temp = self.head
            while temp.next:
                temp = temp.next
            temp.next = new_node
    
    def get_all_songs(self):
        songs = []
        temp = self.head
        while temp:
            songs.append({
                'id': temp.id,
                'title': temp.title,
                'artist': temp.artist,
                'duration': temp.duration,
                'genre': temp.genre,
                'audio_path': temp.audio_path,
                'cover_path': temp.cover_path
            })
            temp = temp.next
        return songs
    
    def remove_song(self, song_id):
        if not self.head:
            return False
        
        if self.head.id == song_id:
            self.head = self.head.next
            return True
        
        temp = self.head
        while temp.next:
            if temp.next.id == song_id:
                temp.next = temp.next.next
                return True
            temp = temp.next
        return False
    
    def clear(self):
        self.head = None
        self.current = None

# 3. Queue - Song Queue
class SongQueue:
    def __init__(self):
        self.items = []
    
    def enqueue(self, song):
        self.items.append(song)
    
    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)
        return None
    
    def peek(self):
        if not self.is_empty():
            return self.items[0]
        return None
    
    def is_empty(self):
        return len(self.items) == 0
    
    def get_all(self):
        return self.items.copy()
    
    def clear(self):
        self.items = []

# 4. Stack - History
class HistoryStack:
    def __init__(self):
        self.items = []
    
    def push(self, song):
        self.items.append(song)
        if len(self.items) > 50:  # Max 50 history
            self.items.pop(0)
    
    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        return None
    
    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        return None
    
    def is_empty(self):
        return len(self.items) == 0
    
    def get_all(self):
        return self.items.copy()
    
    def clear(self):
        self.items = []

# 5. Binary Search Tree - Search
class TreeNode:
    def __init__(self, song):
        self.song = song
        self.left = None
        self.right = None

class SongBST:
    def __init__(self):
        self.root = None
    
    def insert(self, song):
        if not self.root:
            self.root = TreeNode(song)
        else:
            self._insert_recursive(self.root, song)
    
    def _insert_recursive(self, node, song):
        if song['title'].lower() < node.song['title'].lower():
            if node.left is None:
                node.left = TreeNode(song)
            else:
                self._insert_recursive(node.left, song)
        else:
            if node.right is None:
                node.right = TreeNode(song)
            else:
                self._insert_recursive(node.right, song)
    
    def search(self, query):
        results = []
        self._search_recursive(self.root, query.lower(), results)
        return results
    
    def _search_recursive(self, node, query, results):
        if node is None:
            return
        
        if (query in node.song['title'].lower() or 
            query in node.song['artist'].lower() or 
            query in node.song['genre'].lower()):
            results.append(node.song)
        
        self._search_recursive(node.left, query, results)
        self._search_recursive(node.right, query, results)

# 6. Graph - Recommendations
class RecommendationGraph:
    def __init__(self):
        self.graph = {}
    
    def add_edge(self, song1_id, song2_id):
        if song1_id not in self.graph:
            self.graph[song1_id] = []
        if song2_id not in self.graph:
            self.graph[song2_id] = []
        
        if song2_id not in self.graph[song1_id]:
            self.graph[song1_id].append(song2_id)
        if song1_id not in self.graph[song2_id]:
            self.graph[song2_id].append(song1_id)
    
    def get_recommendations(self, song_id):
        if song_id in self.graph:
            return self.graph[song_id]
        return []

# === GLOBAL DATA ===
songs_library = []
user_playlists = {}
user_favorites = {}
user_queues = {}
user_history = {}
song_bst = SongBST()
recommendation_graph = RecommendationGraph()

# === PERSISTENSI DATA ===
DATA_FILE = 'songs_data.json'

def save_songs():
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(songs_library, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print("Error saving songs:", e)

def load_songs():
    global songs_library, song_bst, recommendation_graph
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                songs_library = json.load(f)
            song_bst = SongBST()
            recommendation_graph = RecommendationGraph()
            for song in songs_library:
                song_bst.insert(song)
            for song in songs_library:
                for other in songs_library:
                    if song['id'] != other['id'] and song['genre'] == other['genre']:
                        recommendation_graph.add_edge(song['id'], other['id'])
        except Exception as e:
            print("Error loading songs:", e)

# Load saat start
load_songs()

# Demo users
users = {
    'user': {'password': 'user123', 'role': 'user'},
    'admin': {'password': 'admin123', 'role': 'admin'}
}

# Sample songs dengan placeholder (akan diganti saat admin upload)
songs_library = [
    {
        'id': 1,
        'title': 'Sample Song 1',
        'artist': 'Sample Artist',
        'duration': 180,
        'genre': 'Pop',
        'audio_path': None,
        'cover_path': None
    },
    {
        'id': 2,
        'title': 'Sample Song 2',
        'artist': 'Sample Artist',
        'duration': 200,
        'genre': 'Rock',
        'audio_path': None,
        'cover_path': None
    }
]

# Build BST
for song in songs_library:
    song_bst.insert(song)

# Demo users
users = {
    'user': {'password': 'user123', 'role': 'user'},
    'admin': {'password': 'admin123', 'role': 'admin'}
}

# === ROUTES ===

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username in users and users[username]['password'] == password:
        session['username'] = username
        session['role'] = users[username]['role']
        
        # Initialize user data
        if username not in user_playlists:
            user_playlists[username] = {}
        if username not in user_favorites:
            user_favorites[username] = Playlist()
        if username not in user_queues:
            user_queues[username] = SongQueue()
        if username not in user_history:
            user_history[username] = HistoryStack()
        
        return jsonify({
            'success': True,
            'role': users[username]['role'],
            'redirect': '/admin' if users[username]['role'] == 'admin' else '/user'
        })
    
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/user')
def user_page():
    if 'username' not in session or session.get('role') != 'user':
        return redirect('/')
    return render_template('user.html', username=session['username'])

@app.route('/admin')
def admin_page():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect('/')
    return render_template('admin.html', username=session['username'])

# === FILE SERVING ===

@app.route('/uploads/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

@app.route('/uploads/covers/<filename>')
def serve_cover(filename):
    return send_from_directory(COVER_FOLDER, filename)

# === API ENDPOINTS ===

@app.route('/api/songs', methods=['GET'])
def get_songs():
    return jsonify({'songs': songs_library})

@app.route('/api/songs/<int:song_id>', methods=['GET'])
def get_song(song_id):
    song = next((s for s in songs_library if s['id'] == song_id), None)
    if song:
        return jsonify(song)
    return jsonify({'error': 'Song not found'}), 404

@app.route('/api/play_next/<int:song_id>', methods=['GET'])
def play_next(song_id):
    # cari rekomendasi berdasarkan graph
    rec_ids = recommendation_graph.get_recommendations(song_id)
    if not rec_ids:
        return jsonify({'song': None, 'message': 'No recommendations found'})
    
    # ambil lagu pertama dari rekomendasi
    next_song = next((s for s in songs_library if s['id'] == rec_ids[0]), None)
    if next_song:
        # tambahkan ke history user jika login
        if 'username' in session:
            username = session['username']
            if username not in user_history:
                user_history[username] = HistoryStack()
            user_history[username].push(next_song)
        return jsonify({'song': next_song})
    return jsonify({'song': None})


@app.route('/api/songs', methods=['POST'])
def add_song():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        title = request.form.get('title')
        artist = request.form.get('artist')
        duration = int(request.form.get('duration', 0))
        genre = request.form.get('genre')

        audio_path, cover_path = None, None
        if 'audio_file' in request.files:
            audio_file = request.files['audio_file']
            if audio_file and allowed_file(audio_file.filename, ALLOWED_AUDIO_EXTENSIONS):
                filename = secure_filename(f"{datetime.now().timestamp()}_{audio_file.filename}")
                audio_file.save(os.path.join(AUDIO_FOLDER, filename))
                audio_path = f'/uploads/audio/{filename}'
        if 'cover_file' in request.files:
            cover_file = request.files['cover_file']
            if cover_file and allowed_file(cover_file.filename, ALLOWED_IMAGE_EXTENSIONS):
                filename = secure_filename(f"{datetime.now().timestamp()}_{cover_file.filename}")
                cover_file.save(os.path.join(COVER_FOLDER, filename))
                cover_path = f'/uploads/covers/{filename}'

        new_id = max([s['id'] for s in songs_library], default=0) + 1
        new_song = {
            'id': new_id,
            'title': title,
            'artist': artist,
            'duration': duration,
            'genre': genre,
            'audio_path': audio_path,
            'cover_path': cover_path
        }

        songs_library.append(new_song)
        song_bst.insert(new_song)
        for song in songs_library:
            if song['id'] != new_id and song['genre'] == genre:
                recommendation_graph.add_edge(new_id, song['id'])

        save_songs()  # simpan sebelum return
        return jsonify({'success': True, 'song': new_song})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/songs/<int:song_id>', methods=['PUT'])
def update_song(song_id):
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        song = next((s for s in songs_library if s['id'] == song_id), None)
        if not song:
            return jsonify({'error': 'Song not found'}), 404

        song['title'] = request.form.get('title', song['title'])
        song['artist'] = request.form.get('artist', song['artist'])
        song['duration'] = int(request.form.get('duration', song['duration']))
        song['genre'] = request.form.get('genre', song['genre'])

        if 'audio_file' in request.files:
            audio_file = request.files['audio_file']
            if audio_file and allowed_file(audio_file.filename, ALLOWED_AUDIO_EXTENSIONS):
                if song['audio_path']:
                    old_path = song['audio_path'].replace('/uploads/audio/', '')
                    try: os.remove(os.path.join(AUDIO_FOLDER, old_path))
                    except: pass
                filename = secure_filename(f"{datetime.now().timestamp()}_{audio_file.filename}")
                audio_file.save(os.path.join(AUDIO_FOLDER, filename))
                song['audio_path'] = f'/uploads/audio/{filename}'
        if 'cover_file' in request.files:
            cover_file = request.files['cover_file']
            if cover_file and allowed_file(cover_file.filename, ALLOWED_IMAGE_EXTENSIONS):
                if song['cover_path']:
                    old_path = song['cover_path'].replace('/uploads/covers/', '')
                    try: os.remove(os.path.join(COVER_FOLDER, old_path))
                    except: pass
                filename = secure_filename(f"{datetime.now().timestamp()}_{cover_file.filename}")
                cover_file.save(os.path.join(COVER_FOLDER, filename))
                song['cover_path'] = f'/uploads/covers/{filename}'

        save_songs()
        return jsonify({'success': True, 'song': song})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/songs/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    global songs_library
    song = next((s for s in songs_library if s['id'] == song_id), None)
    if not song:
        return jsonify({'error': 'Song not found'}), 404

    if song['audio_path']:
        audio_path = song['audio_path'].replace('/uploads/audio/', '')
        try: os.remove(os.path.join(AUDIO_FOLDER, audio_path))
        except: pass
    if song['cover_path']:
        cover_path = song['cover_path'].replace('/uploads/covers/', '')
        try: os.remove(os.path.join(COVER_FOLDER, cover_path))
        except: pass

    songs_library = [s for s in songs_library if s['id'] != song_id]
    save_songs()
    return jsonify({'success': True})

@app.route('/api/search', methods=['GET'])
def search_songs():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'results': []})
    
    results = song_bst.search(query)
    return jsonify({'results': results})

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    if 'username' not in session:
        return jsonify({'favorites': []})
    
    username = session['username']
    if username not in user_favorites:
        user_favorites[username] = Playlist()
    
    return jsonify({'favorites': user_favorites[username].get_all_songs()})

@app.route('/api/favorites/<int:song_id>', methods=['POST'])
def add_favorite(song_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    username = session['username']
    song = next((s for s in songs_library if s['id'] == song_id), None)
    
    if not song:
        return jsonify({'error': 'Song not found'}), 404
    
    if username not in user_favorites:
        user_favorites[username] = Playlist()
    
    user_favorites[username].add_song(song)
    return jsonify({'success': True})

@app.route('/api/favorites/<int:song_id>', methods=['DELETE'])
def remove_favorite(song_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    username = session['username']
    if username in user_favorites:
        user_favorites[username].remove_song(song_id)
    
    return jsonify({'success': True})

@app.route('/api/queue', methods=['GET'])
def get_queue():
    if 'username' not in session:
        return jsonify({'queue': []})
    
    username = session['username']
    if username not in user_queues:
        user_queues[username] = SongQueue()
    
    return jsonify({'queue': user_queues[username].get_all()})

@app.route('/api/queue/<int:song_id>', methods=['POST'])
def add_to_queue(song_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    username = session['username']
    song = next((s for s in songs_library if s['id'] == song_id), None)
    
    if not song:
        return jsonify({'error': 'Song not found'}), 404
    
    if username not in user_queues:
        user_queues[username] = SongQueue()
    
    user_queues[username].enqueue(song)
    return jsonify({'success': True})

@app.route('/api/queue/next', methods=['POST'])
def get_next_in_queue():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    username = session['username']
    if username not in user_queues:
        user_queues[username] = SongQueue()
    
    next_song = user_queues[username].dequeue()
    return jsonify({'song': next_song})

@app.route('/api/queue/<int:song_id>', methods=['DELETE'])
def remove_from_queue(song_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    username = session['username']
    if username not in user_queues:
        return jsonify({'success': True})
    
    # Remove specific song from queue
    queue = user_queues[username]
    queue.items = [s for s in queue.items if s['id'] != song_id]
    
    return jsonify({'success': True})

@app.route('/api/queue/clear', methods=['POST'])
def clear_queue():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    username = session['username']
    if username in user_queues:
        user_queues[username].clear()
    
    return jsonify({'success': True})

@app.route('/api/history', methods=['GET'])
def get_history():
    if 'username' not in session:
        return jsonify({'history': []})
    
    username = session['username']
    if username not in user_history:
        user_history[username] = HistoryStack()
    
    return jsonify({'history': user_history[username].get_all()})

@app.route('/api/history/<int:song_id>', methods=['POST'])
def add_to_history(song_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    username = session['username']
    song = next((s for s in songs_library if s['id'] == song_id), None)
    
    if not song:
        return jsonify({'error': 'Song not found'}), 404
    
    if username not in user_history:
        user_history[username] = HistoryStack()
    
    user_history[username].push(song)
    return jsonify({'success': True})

@app.route('/api/recommendations/<int:song_id>', methods=['GET'])
def get_recommendations(song_id):
    rec_ids = recommendation_graph.get_recommendations(song_id)
    recommendations = [s for s in songs_library if s['id'] in rec_ids]
    return jsonify({'recommendations': recommendations})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    total_users = len([u for u in users.values() if u['role'] == 'user'])
    
    return jsonify({
        'total_songs': len(songs_library),
        'total_users': total_users,
        'total_playlists': sum(len(p) for p in user_playlists.values())
    })

# === PLAYLIST ENDPOINTS ===

@app.route('/api/playlists', methods=['GET'])
def get_playlists():
    if 'username' not in session:
        return jsonify({'playlists': []})
    
    username = session['username']
    if username not in user_playlists:
        user_playlists[username] = {}
    
    playlists_data = []
    for name, playlist in user_playlists[username].items():
        playlists_data.append({
            'name': name,
            'songs': playlist.get_all_songs(),
            'count': len(playlist.get_all_songs())
        })
    
    return jsonify({'playlists': playlists_data})

@app.route('/api/playlists', methods=['POST'])
def create_playlist():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    playlist_name = data.get('name')
    
    if not playlist_name:
        return jsonify({'error': 'Playlist name required'}), 400
    
    username = session['username']
    if username not in user_playlists:
        user_playlists[username] = {}
    
    if playlist_name in user_playlists[username]:
        return jsonify({'error': 'Playlist already exists'}), 400
    
    user_playlists[username][playlist_name] = Playlist()
    return jsonify({'success': True, 'message': 'Playlist created'})

@app.route('/api/playlists/<playlist_name>', methods=['DELETE'])
def delete_playlist(playlist_name):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    username = session['username']
    if username in user_playlists and playlist_name in user_playlists[username]:
        del user_playlists[username][playlist_name]
        return jsonify({'success': True})
    
    return jsonify({'error': 'Playlist not found'}), 404

@app.route('/api/playlists/<playlist_name>/songs/<int:song_id>', methods=['POST'])
def add_song_to_playlist(playlist_name, song_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    username = session['username']
    song = next((s for s in songs_library if s['id'] == song_id), None)
    
    if not song:
        return jsonify({'error': 'Song not found'}), 404
    
    if username not in user_playlists:
        user_playlists[username] = {}
    
    if playlist_name not in user_playlists[username]:
        return jsonify({'error': 'Playlist not found'}), 404
    
    user_playlists[username][playlist_name].add_song(song)
    return jsonify({'success': True})

@app.route('/api/playlists/<playlist_name>/songs/<int:song_id>', methods=['DELETE'])
def remove_song_from_playlist(playlist_name, song_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    username = session['username']
    
    if username in user_playlists and playlist_name in user_playlists[username]:
        user_playlists[username][playlist_name].remove_song(song_id)
        return jsonify({'success': True})
    
    return jsonify({'error': 'Playlist not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
