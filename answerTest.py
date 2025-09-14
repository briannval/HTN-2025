from db.opensearch import OpenSearchClient
from modules.cohere_answer import CohereAnswer
from modules.listen import listen_for_query

def answerTest():
    opensearch_client = OpenSearchClient()
    query = input("Enter your query: ")
    res = opensearch_client.search_by_text(query)
    res_prompt = opensearch_client.get_search_by_text_results_prompt(res)
    cohere_answer = CohereAnswer()
    print(cohere_answer.generate_contextual_answer(query, res_prompt))


answerTest()
