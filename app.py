# ==============================================================================
# FILE: app.py
# Main Flask application - entry point
# ==============================================================================

from flask import Flask, render_template, request, jsonify
import os
from src.config import Config
from src.database import Database
from src.news_aggregator import NewsAPIAggregator
from src.meme_generator import generate_meme_image
from src.models import GeneratedMeme
from datetime import datetime
import uuid
import random
from src.meme_generator import generate_meme_image

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize components
    db = Database()
    news_aggregator = NewsAPIAggregator(Config.NEWS_API_KEY)
    meme_generator = AIMemeGenerator()
    
    

    @app.route('/api/generate', methods=['POST'])
    def generate_meme():
        
            # print("🎲 Starting meme generation...")
            
            # # Get recent news
            # news_items = news_aggregator.get_recent_news(hours_back=48, max_articles=10)
            
            # if not news_items:
            #     return jsonify({'error': 'No recent AI news found'})
            
            # # Pick random news item
            # news_item = random.choice(news_items)
            # print(f"📰 Selected news: {news_item.title[:50]}...")
            
            # # Generate meme
            # result = meme_generator.create_complete_meme(news_item)
            
            # if result['success']:
            #     # Save to database
            #     meme = GeneratedMeme(
            #         id=str(uuid.uuid4()),
            #         template_name=result['template_name'],
            #         meme_text=result['meme_text'],
            #         news_source=result['news_source'],
            #         created_at=datetime.now().isoformat(),
            #         image_data=result['image_data']
            #     )
                
            #     if 'news_title' in result:
            #         meme.news_title = result['news_title']
                
            #     db.save_meme(meme)
                
            #     print("🎉 Meme generated and saved successfully!")
                
            #     return jsonify({
            #         'success': True,
            #         'meme': {
            #             'id': meme.id,
            #             'template_name': meme.template_name,
            #             'text': meme.meme_text,
            #             'news_source': meme.news_source,
            #             'news_title': getattr(meme, 'news_title', ''),
            #             'image_data': meme.image_data
            #         }
            #     })
            # else:
            #     return jsonify({'error': 'Meme generation failed'})


                
        # except Exception as e:
        #     print(f"❌ Error in meme generation: {e}")
        #     return jsonify({'error': str(e)})

        #memes = generate_meme_image(prompt_url_list=None)
        pass



    

    @app.route('/api/memes')
    def get_memes():
        try:
            sort_by = request.args.get('sort', 'recent')
            limit = int(request.args.get('limit', 20))
            memes = db.get_memes(limit=limit, sort_by=sort_by)
            
            return jsonify({
                'memes': [{
                    'id': m.id,
                    'template_name': m.template_name,
                    'text': m.meme_text,
                    'news_source': m.news_source,
                    'news_title': getattr(m, 'news_title', ''),
                    'created_at': m.created_at,
                    'votes': m.votes,
                    'image_data': m.image_data
                } for m in memes]
            })
        except Exception as e:
            return jsonify({'error': str(e)})

    @app.route('/api/news')
    def get_news():
        try:
            news_items = news_aggregator.get_recent_news(hours_back=24, max_articles=5)
            return jsonify({
                'news': [{
                    'title': item.title,
                    'source': item.source,
                    'published': item.published,
                    'url': item.url
                } for item in news_items]
            })
        except Exception as e:
            return jsonify({'error': str(e)})
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("🎭 Starting AI Meme Factory...")
    print("🔑 Make sure to set your OPENAI_API_KEY and NEWS_API_KEY environment variables!")
    print(f"📰 News API Key configured: {'✅' if Config.NEWS_API_KEY != 'your-news-api-key-here' else '❌'}")
    print(f"🤖 OpenAI API Key configured: {'✅' if Config.OPENAI_API_KEY != 'your-openai-key-here' else '❌'}")
    app.run(debug=True, host='0.0.0.0', port=5000)
