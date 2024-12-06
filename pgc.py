import io
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from PyPDF2 import PdfReader


# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_file_path):
    """
    Extracts text from a given PDF file path.
    """
    with open(pdf_file_path, "rb") as pdf_file:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        if not text.strip():
            print(f"Warning: No text extracted from {pdf_file_path}. File might be empty or contain only images.")
        return text


# Function to normalize text
def normalize_text(text):
    """
    Normalizes the text by removing extra spaces, converting to lowercase, and stripping non-alphanumeric content.
    """
    return ' '.join(text.split()).lower()


# Function to check if text has sufficient meaningful content
def has_sufficient_content(text, word_threshold=10):
    """
    Checks if the text has sufficient content based on a word threshold.
    """
    return len(text.split()) > word_threshold


# Function to remove boilerplate text
def remove_boilerplate(text, boilerplate_phrases=None):
    """
    Removes common boilerplate phrases from the text.
    """
    if boilerplate_phrases is None:
        boilerplate_phrases = ["terms and conditions", "copyright", "all rights reserved"]
    for phrase in boilerplate_phrases:
        text = text.replace(phrase, "")
    return text


# Function to check plagiarism using TF-IDF and Cosine Similarity
def check_plagiarism(file_texts):
    """
    Compares text from multiple files using TF-IDF and cosine similarity.
    Returns a sorted list of plagiarism reports with similarity above a threshold.
    """
    non_empty_texts = [text for text in file_texts if text.strip()]
    if len(non_empty_texts) < len(file_texts):
        print("Warning: Some files are empty and will be excluded from plagiarism detection.")
    
    # Calculate the TF-IDF matrix for non-empty texts
    vectorizer = TfidfVectorizer().fit_transform(non_empty_texts)
    similarity_matrix = cosine_similarity(vectorizer)

    # Generate plagiarism report
    plagiarism_report = []
    for i in range(len(non_empty_texts)):
        for j in range(i + 1, len(non_empty_texts)):
            similarity = similarity_matrix[i][j]
            plagiarism_report.append({
                "file_1": f"File_{i+1}",
                "file_2": f"File_{j+1}",
                "similarity": round(similarity * 100, 2)
            })

    # Sort by similarity in descending order
    plagiarism_report.sort(key=lambda x: x["similarity"], reverse=True)
    return plagiarism_report



def main():
    print("Enhanced Plagiarism Checker")
    print("============================")
    
    # Input file paths from user
    num_files = int(input("Enter the number of files to compare: "))
    file_paths = []
    for i in range(num_files):
        path = input(f"Enter path for file {i+1}: ")
        file_paths.append(path)

    # Extract and preprocess text from the provided file paths
    file_texts = []
    for file_path in file_paths:
        try:
            raw_text = extract_text_from_pdf(file_path)
            normalized_text = normalize_text(raw_text)
            filtered_text = remove_boilerplate(normalized_text)

            if has_sufficient_content(filtered_text):
                file_texts.append(filtered_text)
                print(f"Processed text from {file_path}.")
            else:
                print(f"Skipped {file_path}: Not enough meaningful content.")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # Check if there are enough files to compare
    if len(file_texts) < 2:
        print("Not enough valid files to compare. Exiting.")
        return

    # Check plagiarism
    results = check_plagiarism_tfidf(file_texts)

    # Display results with a threshold
    threshold = 65  # Only show results with similarity above 65%
    print("\nPlagiarism Report (Similarities above 65%):")
    print("-------------------------------------------")
    filtered_results = [res for res in results if res["similarity"] > threshold]
    if filtered_results:
        for result in filtered_results:
            print(
                f"{result['file_1']} ↔ {result['file_2']} - {result['similarity']}% Similar"
            )
    else:
        print("No plagiarism detected above the threshold.")


if __name__ == "__main__":
    main()