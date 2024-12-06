from sklearn.feature_extraction.text import TfidfVectorizer
from spellchecker import SpellChecker
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util
import numpy as np
from Levenshtein import distance as levenshtein_distance
import re
import spacy

# Load embedding model and NLP model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
nlp = spacy.load("en_core_web_sm")


        
# Cosine Similarity
def cosine_similarity_score(doc1, doc2):
    if not doc1 or not doc2:
        return 0
    vectorizer = TfidfVectorizer().fit_transform([doc1, doc2])
    vectors = vectorizer.toarray()
    cosine_sim = cosine_similarity(vectors)
    return cosine_sim[0][1]

# Jaccard Similarity
def jaccard_similarity_score(doc1, doc2):
    words_doc1 = set(doc1.split())
    words_doc2 = set(doc2.split())
    return len(words_doc1.intersection(words_doc2)) / len(words_doc1.union(words_doc2)) if words_doc1 or words_doc2 else 0

# Levenshtein Similarity
def levenshtein_similarity_score(doc1, doc2):
    if not doc1 or not doc2:
        return 0
    return 1 - (levenshtein_distance(doc1, doc2) / max(len(doc1), len(doc2)))

# Embedding Similarity using Sentence-BERT
def embedding_similarity_score(doc1, doc2):
    if not doc1 or not doc2:
        return 0
    embeddings = embedding_model.encode([doc1, doc2])
    return util.cos_sim(embeddings[0], embeddings[1]).item()

# Extract important keywords from the key text
def extract_keywords(text):
    vectorizer = TfidfVectorizer(max_features=10)
    tfidf_matrix = vectorizer.fit_transform([text])
    tfidf_terms = vectorizer.get_feature_names_out()
    doc = nlp(text)
    entities = {ent.text for ent in doc.ents}
    keywords = set(tfidf_terms).union(entities)
    return keywords

# Keyword Matching with Dynamic Keywords
def keyword_match_score(doc1, doc2):
    keywords = extract_keywords(doc1)
    words = set(doc2.split())
    matches = sum(1 for word in keywords if word in words)
    return matches / len(keywords) if keywords else 0

# Numeric Consistency Check
def numeric_consistency_score(doc1, doc2):
    nums_doc1 = set(re.findall(r'\b\d+\b', doc1))
    nums_doc2 = set(re.findall(r'\b\d+\b', doc2))
    return len(nums_doc1.intersection(nums_doc2)) / len(nums_doc1) if nums_doc1 else 1

# Named Entity Matching
def entity_match_score(doc1, doc2):
    entities_doc1 = {ent.text.lower() for ent in nlp(doc1).ents}
    entities_doc2 = {ent.text.lower() for ent in nlp(doc2).ents}
    return len(entities_doc1.intersection(entities_doc2)) / len(entities_doc1) if entities_doc1 else 1

# Grammar and sentence structure checking (simplified)
def grammar_error_score(doc_text):
    doc_nlp = nlp(doc_text)
    sentences = list(doc_nlp.sents)
    error_count = 0

    for sent in sentences:
        if not any(token.dep_ == 'nsubj' for token in sent) or not any(token.dep_ == 'ROOT' for token in sent):
            error_count += 1

    return 1 - (error_count / len(sentences)) if sentences else 1

# Initialize the spell checker
spell = SpellChecker()

# Function to calculate spelling error score
def spelling_error_score(doc_text):
    # Tokenize the text into words
    words = re.findall(r'\b\w+\b', doc_text)
    # Identify misspelled words
    misspelled = spell.unknown(words)
    # Calculate penalty based on the number of misspelled words
    error_penalty = len(misspelled)
    return 1 - (error_penalty / len(words)) if words else 1, error_penalty

# Update the grading function to include spelling error checking
def grade_assignment(student_text, key_text, total_marks, x):
    # Calculate similarity scores
    cosine_sim = cosine_similarity_score(student_text, key_text)
    jaccard_sim = jaccard_similarity_score(student_text, key_text)
    levenshtein_sim = levenshtein_similarity_score(student_text, key_text)
    embedding_sim = embedding_similarity_score(student_text, key_text)
    keyword_sim = keyword_match_score(key_text, student_text)
    numeric_sim = numeric_consistency_score(key_text, student_text)
    entity_sim = entity_match_score(key_text, student_text)
    grammar_penalty = grammar_error_score(student_text)
    spelling_penalty_score, spelling_error_count = spelling_error_score(student_text)  # Get spelling penalty and count

    # Assign weights to each algorithm
    if x == 1: #Normal
        cosine_weight = 0.2
        jaccard_weight = 0.15
        levenshtein_weight = 0.1
        embedding_weight = 0.3
        keyword_weight = 0.05
        numeric_weight = 0.05
        entity_weight = 0.05
        grammar_weight = 0.05
        spelling_weight = 0.05
    elif x == 2: #technical
        cosine_weight = 0.2
        jaccard_weight = 0.15
        levenshtein_weight = 0.1
        embedding_weight = 0.05
        keyword_weight = 0.4
        numeric_weight = 0.08
        entity_weight = 0.01
        grammar_weight = 0
        spelling_weight = 0.01       
    elif x == 3: #grammar
        cosine_weight = 0.2
        jaccard_weight = 0.15
        levenshtein_weight = 0.1
        embedding_weight = 0.05
        keyword_weight = 0.05
        numeric_weight = 0.01
        entity_weight = 0.01
        grammar_weight = 0.42
        spelling_weight = 0.01
    elif x == 4: #spelling
        cosine_weight = 0.2
        jaccard_weight = 0.15
        levenshtein_weight = 0.1
        embedding_weight = 0.05
        keyword_weight = 0.05
        numeric_weight = 0.01
        entity_weight = 0.01
        grammar_weight = 0.01
        spelling_weight = 0.42       
    elif x == 5: #tech and grammar
        cosine_weight = 0.2
        jaccard_weight = 0.15
        levenshtein_weight = 0.1
        embedding_weight = 0.05
        keyword_weight = 0.20
        numeric_weight = 0.05
        entity_weight = 0.01
        grammar_weight = 0.23
        spelling_weight = 0.01      
    elif x == 6: #tech and spelling
        cosine_weight = 0.2
        jaccard_weight = 0.15
        levenshtein_weight = 0.1
        embedding_weight = 0.05
        keyword_weight = 0.22
        numeric_weight = 0.05
        entity_weight = 0.01
        grammar_weight = 0.01
        spelling_weight = 0.22  
        #1.02
    elif x == 7: #spelling and grammar
        cosine_weight = 0.2
        jaccard_weight = 0.15
        levenshtein_weight = 0.1
        embedding_weight = 0.05
        keyword_weight = 0.05
        numeric_weight = 0.01
        entity_weight = 0.01
        grammar_weight = 0.23
        spelling_weight = 0.20  
    elif x == 8: #tech and grammar and spelling
        cosine_weight = 0.2
        jaccard_weight = 0.15
        levenshtein_weight = 0.1
        embedding_weight = 0.05
        keyword_weight = 0.15
        numeric_weight = 0.04
        entity_weight = 0.01
        grammar_weight = 0.15
        spelling_weight = 0.15

    # Calculate individual weighted scores for each algorithm
    cosine_marks = cosine_sim * cosine_weight * total_marks * spelling_penalty_score
    jaccard_marks = jaccard_sim * jaccard_weight * total_marks * spelling_penalty_score
    levenshtein_marks = levenshtein_sim * levenshtein_weight * total_marks * spelling_penalty_score
    embedding_marks = embedding_sim * embedding_weight * total_marks * spelling_penalty_score
    keyword_marks = keyword_sim * keyword_weight * total_marks * spelling_penalty_score
    numeric_marks = numeric_sim * numeric_weight * total_marks * spelling_penalty_score
    entity_marks = entity_sim * entity_weight * total_marks * spelling_penalty_score
    penalty_marks = grammar_weight * total_marks * (1 - grammar_penalty)  # Grammar penalty

    # Sum up the weighted scores to get the final score
    final_score = (
        cosine_marks + 
        jaccard_marks + 
        levenshtein_marks + 
        embedding_marks + 
        keyword_marks + 
        numeric_marks + 
        entity_marks - penalty_marks + 5
    )

    #check_plagiarism_tfidf(file_texts)

    # Ensure the final score does not exceed total marks
    final_score = min(round(final_score), total_marks)
    # plagiarism flag = kuhan_func(uploads/)
    percentage = (final_score / total_marks) * 100

    # #Test cases
    # if(x == 8):
    #     technical = True
    #     grammar = True
    #     spelling = True
    # elif(technical and not grammar and not spelling):
    #     x = 2
    # elif(grammar and not technical and not spelling):
    #     x = 3
    # elif(spelling and not technical and not grammar):
    #     x = 4
    # elif(technical and grammar and not spelling):
    #     x = 5
    # elif(technical and spelling and not grammar):
    #     x = 6
    # elif(grammar and spelling and not technical):
    #     x = 7
    # else:
    #     x = 1

# PDF Generation:
# TITLE: GRADESHEET FOR SUBJECTIVE ASSIGNMENTS
# 1. Assignment ID ()
# 2. Key ID ()
# 3. Given Assignment Marks
# 4. x --> Assignment specs (tech->true/false, grammar, spelling)
# 5. Print the weighted contributions
# 6. Obtained Marks
# 7. Plagiarism flag = True/False



    check_plagiarism(file_texts)


    # Print the contribution of each algorithm
    print("\nRaw marks assigned by each algorithm:")
    print(f"Cosine Similarity: {cosine_sim:.2f}")
    print(f"Jaccard Similarity: {jaccard_sim:.2f}")
    print(f"Levenshtein Similarity: {levenshtein_sim:.2f}")
    print(f"Embedding Similarity: {embedding_sim:.2f}")
    print(f"Keyword Matching: {keyword_sim:.2f}")
    print(f"Numeric Consistency: {numeric_sim:.2f}")
    print(f"Entity Matching: {entity_sim:.2f}")
    print(f"Grammar Penalty Score: {penalty_marks:.2f}")
    print(f"Spelling Error Penalty Count: {spelling_error_count}")  # Print spelling penalty count

    # Print the weighted contributions
    print("\n\nMarks assigned by each algorithm (weighted):")
    print(f"Cosine Similarity: {cosine_marks:.2f} out of {total_marks * cosine_weight:.2f}")
    print(f"Jaccard Similarity: {jaccard_marks:.2f} out of {total_marks * jaccard_weight:.2f}")
    print(f"Levenshtein Similarity: {levenshtein_marks:.2f} out of {total_marks * levenshtein_weight:.2f}")
    print(f"Embedding Similarity: {embedding_marks:.2f} out of {total_marks * embedding_weight:.2f}")
    print(f"Keyword Matching: {keyword_marks:.2f} out of {total_marks * keyword_weight:.2f}")
    print(f"Numeric Consistency: {numeric_marks:.2f} out of {total_marks * numeric_weight:.2f}")
    print(f"Entity Matching: {entity_marks:.2f} out of {total_marks * entity_weight:.2f}")
    print(f"Grammar Penalty: -{penalty_marks:.2f} out of {total_marks * grammar_weight:.2f}")

    print(f"\nMarks Obtained: {final_score:.2f} out of {total_marks:.2f}")
    print(f"\nPercentage: {percentage:.2f} out of 100\n\n")

    return final_score

    

# pip freeze > requirements.txt