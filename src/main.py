from get_daily_arxiv import get_daily_arxiv
from datetime import datetime, timedelta, date
import os
import json
import openai
import argparse

def classify(topic_des, title, abstract, llm_config):
    prompt = '''Prompt:You are given the title and abstract of a research paper. Your task is to determine whether the paper is related to the topic of "{topic_des}" Based on the information provided in the title and abstract, categorize the paper's relevance to this topic as one of the following: "Relevant," "Not Relevant," or "Uncertain." Provide your assessment solely in the form of one of these three options.
    Title: {title}
    Abstract: {abstract}
    Assessment: [Relevant/Not Relevant/Uncertain]
    '''.format(topic_des=topic_des, title=title, abstract=abstract)

    openai.api_key = llm_config['api_key']
    openai.api_base = llm_config['api_base']
    
    chat_completion = openai.ChatCompletion.create(
        model=llm_config['model'],
        messages=[{ "role": "user", "content": prompt}]
    )
    return chat_completion.choices[0].message.content.lower()


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)



def update_topic(paper_dicts, topics_config, llm_config):
    for topic, topic_des in topics_config.items():
        readme_file = os.path.join(topic, 'README.md')

        reademe_lines = []
        with open(readme_file, 'r', encoding='utf-8') as f:
            reademe_lines = f.readlines()
        
        insert_position = -1
        for i, line in enumerate(reademe_lines):
            if f'# {topic}' in line:
                insert_position = i + 1
                break

        
        if insert_position != -1:
            for paper in paper_dicts:
                label = classify(topic_des, paper['title'], paper['abstract'], llm_config) # Determine relevance
                with open('src/classify.log', 'a+', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'arxiv_id': paper['arxiv_id'],
                        'title': paper['title'],
                        'topic': topic,
                        'label': label
                    })+'\n')

                if label == 'relevant' or label == 'uncertain':
                    prefix = ''
                    if label == 'uncertain':
                        prefix = '‼️' 
                    authors = ','.join(paper['authors'])
                    publish_time = paper['published'].strftime("%Y-%m-%d")
                    paper_content = '- {prefix} [{title}]({pdf_url}). {authors}. [{publish_time}]\n'.format(
                        prefix = prefix,
                        title = paper['title'],
                        pdf_url = paper['pdf_url'],
                        authors = authors,
                        publish_time = publish_time
                    )
                    reademe_lines.insert(insert_position, paper_content)
        
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.writelines(reademe_lines)
                

def update_daily_arxiv(paper_dicts):
    today = date.today()
    yesterday = today - timedelta(days=1) # get yesterday papers
    year = yesterday.year
    month = yesterday.month


    if not os.path.exists(f'Papers/{year}'):
        os.mkdir(f'Papers/{year}')

    json_file = f'Papers/{year}/{year}-{month:02}-ArxivPapers.json'

    papers = []
    if os.path.exists(json_file): # if file exists, read first
        with open(json_file, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                papers.append(json.loads(line)) 
        papers.extend(paper_dicts)
    else: # else add new papers
        papers = paper_dicts


    with open(json_file, 'w', encoding='utf-8') as f:
        for paper in papers:
            f.write(json.dumps(paper, cls=ComplexEncoder)+'\n')


def init_topic_readme(topic):
    with open(os.path.join(topic, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(f'# {topic}\n')

def main(topics_config, llm_config):
    # init topics dir and README
    if not os.path.exists('src/classify.log'):
        open('src/classify.log', 'w').close()
    if not os.path.exists('Papers'):
        os.mkdir('Papers')
    for topic, _ in topics_config.items():
        if not os.path.exists(topic):
            os.mkdir(topic)
            init_topic_readme(topic)

    papers = get_daily_arxiv() # get yesterday papers
    paper_dicts = [paper.model_dump() for paper in papers]    # Convert Pydantic model to dict and remove _id if present
    print('papers: {num}'.format(num = len(paper_dicts)))
    update_topic(paper_dicts, topics_config, llm_config)
    update_daily_arxiv(paper_dicts)



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--key', type=str)
    args = parser.parse_args()

    llm_config = {
        'api_key': args.key,
        'api_base': 'https://api3.chatweb.plus/v1',
        'model': 'gpt-4o-mini'
    }
    topics_config = {
        'Synthesis Data': 'Synthesis Data using Large Language Models (LLM).',
        'Multi Agent': 'Multi-Agent'
    }
    main(topics_config, llm_config)
    
 
