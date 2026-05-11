
def generate_summary(llm, responses):
    prompt = f'''
Analyze the following exit interview responses and provide:
1. Top reasons for leaving
2. Overall sentiment
3. Improvement suggestions
4. Recommendation likelihood
5. Executive summary

Responses:
{responses}
'''
    return llm.invoke(prompt).content
