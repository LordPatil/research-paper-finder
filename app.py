from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)

def get_papers_from_arxiv(topic, sort_by='relevance'):
    base_url = "http://export.arxiv.org/api/query?"
    search_query = f"search_query=title:{topic}"  # Search specifically in titles

    # Determine sorting parameter
    if sort_by == 'year_asc':
        sort_param = "sortBy=submittedDate"
        order = False
    elif sort_by == 'year_desc':
        sort_param = "sortBy=submittedDate"
        order = True
    else:  # Default to relevance
        sort_param = "sortBy=relevance"
        order = None

    url = f"{base_url}{search_query}&{sort_param}&max_results=50"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.text
        papers = []

        # Parsing arXiv XML response
        import xml.etree.ElementTree as ET
        root = ET.fromstring(data)

        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            authors = ', '.join([author.find('{http://www.w3.org/2005/Atom}name').text for author in entry.findall('{http://www.w3.org/2005/Atom}author')])
            doi = entry.find('{http://www.w3.org/2005/Atom}id').text.split('/')[-1]  # Extract arXiv ID
            published_date = entry.find('{http://www.w3.org/2005/Atom}published').text
            year = datetime.strptime(published_date, '%Y-%m-%dT%H:%M:%SZ').year
            
            papers.append({
                "title": title,
                "authors": authors,
                "doi": doi,
                "year": year
            })

        # Sorting logic
        if sort_by == 'year_asc':
            papers.sort(key=lambda x: x['year'])
        elif sort_by == 'year_desc':
            papers.sort(key=lambda x: x['year'], reverse=True)
        
        return papers
    else:
        return {"error": "Failed to fetch data"}

@app.route('/', methods=['GET', 'POST'])
def index():
    papers = []
    sort_by = request.form.get('sort_by', 'relevance')  # Default to relevance if not specified
    topic = request.form.get('topic')  # Safely get topic

    if request.method == 'POST' and topic:
        papers = get_papers_from_arxiv(topic, sort_by)
        
        if isinstance(papers, dict) and 'error' in papers:
            return render_template('index.html', error=papers['error'], papers=None, sort_by=sort_by)

    return render_template('index.html', papers=papers, sort_by=sort_by)

if __name__ == '__main__':
    app.run(debug=True)

