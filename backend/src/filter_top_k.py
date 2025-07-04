import json
from typing import List, Dict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_jsons(raw_json_list: List[str]) -> List[Dict]:
    return [json.loads(j) if isinstance(j, str) else j for j in raw_json_list]

def rank_articles(articles: List[Dict], keywords: List[str]) -> List[Dict]:
    documents = [
        " ".join([article.get("title", ""), article.get("description", ""), article.get("content", "")])
        for article in articles
    ]

    query = " ".join(keywords)

    vectorizer = TfidfVectorizer(stop_words='english')
    doc_vectors = vectorizer.fit_transform(documents + [query])

    cosine_scores = cosine_similarity(doc_vectors[:-1], doc_vectors[-1])

    for i, article in enumerate(articles):
        article["relevance_score"] = cosine_scores[i][0]

    return sorted(articles, key=lambda x: (x["relevance_score"], x["publishedAt"]), reverse=True)

def get_top_articles(raw_json_list: List, num_to_select: int, user_keywords: List[str]) -> List[Dict]:
    articles = load_jsons(raw_json_list)
    ranked_articles = rank_articles(articles, user_keywords)
    print(f"filtered and returned {num_to_select} articles")
    return ranked_articles[:num_to_select]

# Sample Call
if __name__ == "__main__":
    raw_jsons = [
        json.dumps({
            "source": {
                "id": "the-onion",
                "name": "The Onion"
            },
            "author": "Jane Doe",
            "title": "Cat becomes mayor of small town",
            "description": "In a shocking turn of events, a cat has been elected mayor.",
            "url": "https://www.theonion.com/cat-mayor",
            "urlToImage": "https://www.theonion.com/cat.jpg",
            "publishedAt": "2025-06-10T08:30:00Z",
            "content": "The cat reportedly promised free tuna for all."
        }),
        json.dumps({
            "source": {
                "id": "bloomberg",
                "name": "Bloomberg"
            },
            "author": "Erik Wasson, Steven T. Dennis",
            "title": "Trump Tax Bill Advances in Senate After Vance Pressures Holdouts - Bloomberg.com",
            "description": "President Donald Trump’s $4.5 trillion tax cut bill prevailed in a crucial Senate test vote...",
            "url": "https://www.bloomberg.com/news/articles/2025-06-29/senate-republicans-advance-trump-tax-bill-on-crucial-test-vote",
            "urlToImage": "https://assets.bwbx.io/images/users/iqjWHBFdfxIU/iVChjRUChjJg/v1/1200x800.jpg",
            "publishedAt": "2025-06-29T11:21:06Z",
            "content": "President Donald Trumps $4.5 trillion tax cut bill prevailed in a crucial Senate test vote..."
        })
    ]

    selected_articles = get_top_articles(
        raw_json_list=raw_jsons,
        num_to_select=3,
        user_keywords=["Trump", "funny", "election"]
    )

    # print(json.dumps(selected_articles, indent=2))
