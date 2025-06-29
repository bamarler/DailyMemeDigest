# ==============================================================================
# FILE: src/database.py
# Database operations
# ==============================================================================

import sqlite3
import json
from typing import List, Optional
from .models import GeneratedMeme
from .config import Config

class Database:
    """Database operations for memes and votes"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_db()
    
    def init_db(self):
        """Initialize SQLite database with tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Memes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memes (
                id TEXT PRIMARY KEY,
                template_name TEXT NOT NULL,
                meme_text TEXT NOT NULL,
                news_source TEXT NOT NULL,
                news_title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                votes INTEGER DEFAULT 0,
                image_data TEXT
            )
        ''')
        
        # Votes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meme_id TEXT NOT NULL,
                user_ip TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(meme_id, user_ip),
                FOREIGN KEY (meme_id) REFERENCES memes (id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memes_created_at ON memes(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memes_votes ON memes(votes)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_votes_meme_id ON votes(meme_id)')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized")
    
    def save_meme(self, meme: GeneratedMeme) -> bool:
        """Save a generated meme to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO memes (id, template_name, meme_text, news_source, news_title, image_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                meme.id,
                meme.template_name,
                json.dumps(meme.meme_text),
                meme.news_source,
                getattr(meme, 'news_title', None),
                meme.image_data
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error saving meme: {e}")
            return False
    
    def get_memes(self, limit: int = 20, sort_by: str = 'recent') -> List[GeneratedMeme]:
        """Get memes from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if sort_by == 'popular':
                order_clause = 'ORDER BY votes DESC, created_at DESC'
            else:
                order_clause = 'ORDER BY created_at DESC'
            
            cursor.execute(f'''
                SELECT id, template_name, meme_text, news_source, news_title, 
                       created_at, votes, image_data
                FROM memes 
                {order_clause}
                LIMIT ?
            ''', (limit,))
            
            memes = []
            for row in cursor.fetchall():
                meme = GeneratedMeme(
                    id=row[0],
                    template_name=row[1],
                    meme_text=json.loads(row[2]) if row[2] else {},
                    news_source=row[3],
                    created_at=row[5],
                    votes=row[6],
                    image_data=row[7]
                )
                
                # Add news_title if available
                if row[4]:
                    meme.news_title = row[4]
                
                memes.append(meme)
            
            conn.close()
            return memes
            
        except Exception as e:
            print(f"❌ Error getting memes: {e}")
            return []
    
    def vote_meme(self, meme_id: str, user_ip: str) -> bool:
        """Vote for a meme (one vote per IP per meme)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Try to add vote
            cursor.execute('INSERT INTO votes (meme_id, user_ip) VALUES (?, ?)', (meme_id, user_ip))
            
            # Update meme vote count
            cursor.execute('UPDATE memes SET votes = votes + 1 WHERE id = ?', (meme_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.IntegrityError:
            # Already voted
            return False
        except Exception as e:
            print(f"❌ Error voting: {e}")
            return False
    
    def get_meme_by_id(self, meme_id: str) -> Optional[GeneratedMeme]:
        """Get a specific meme by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, template_name, meme_text, news_source, news_title,
                       created_at, votes, image_data
                FROM memes 
                WHERE id = ?
            ''', (meme_id,))
            
            row = cursor.fetchone()
            if row:
                meme = GeneratedMeme(
                    id=row[0],
                    template_name=row[1],
                    meme_text=json.loads(row[2]) if row[2] else {},
                    news_source=row[3],
                    created_at=row[5],
                    votes=row[6],
                    image_data=row[7]
                )
                
                if row[4]:
                    meme.news_title = row[4]
                
                conn.close()
                return meme
            
            conn.close()
            return None
            
        except Exception as e:
            print(f"❌ Error getting meme by ID: {e}")
            return None
    
    def get_stats(self) -> dict:
        """Get database statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total memes
            cursor.execute('SELECT COUNT(*) FROM memes')
            total_memes = cursor.fetchone()[0]
            
            # Total votes
            cursor.execute('SELECT SUM(votes) FROM memes')
            total_votes = cursor.fetchone()[0] or 0
            
            # Most popular template
            cursor.execute('''
                SELECT template_name, COUNT(*) as count 
                FROM memes 
                GROUP BY template_name 
                ORDER BY count DESC 
                LIMIT 1
            ''')
            popular_template = cursor.fetchone()
            
            conn.close()
            
            return {
                'total_memes': total_memes,
                'total_votes': total_votes,
                'most_popular_template': popular_template[0] if popular_template else None
            }
            
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {'total_memes': 0, 'total_votes': 0, 'most_popular_template': None}
