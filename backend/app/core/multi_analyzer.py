from typing import List, Dict, Any, Tuple
from app.core.detector import detect_plagiarism


def analyze_multiple(files_data: List[Tuple[str, str]], language: str) -> Dict[str, Any]:
    """
    Runs pairwise comparison on all provided files.
    
    Args:
        files_data: A list of tuples containing (filename, source_code).
        language: The programming language of the files.
        
    Returns:
        A similarity matrix represented as a dictionary where the key is 
        "{file1} vs {file2}" and the value is the detailed detection result.
    """
    matrix = {}
    
    n = len(files_data)
    for i in range(n):
        for j in range(i + 1, n):
            name1, code1 = files_data[i]
            name2, code2 = files_data[j]
            
            # Create a unique key for this pair comparison
            pair_key = f"{name1} vs {name2}"
            
            # Run the existing integrated detector
            result = detect_plagiarism(code1, code2, language)
            
            matrix[pair_key] = {
                "file1": name1,
                "file2": name2,
                "result": result
            }
            
    return matrix


def get_suspicious_pairs(matrix: Dict[str, Any], threshold: float = 70.0) -> List[Dict[str, Any]]:
    """
    Filters the similarity matrix for pairs above the threshold.
    
    Returns:
        A list of suspicious pairs ranked by final_score in descending order.
        The most suspicious pairs will be at the top.
    """
    suspicious = []
    
    for pair_key, data in matrix.items():
        score = data["result"]["final_score"]
        if score >= threshold:
            suspicious.append({
                "pair": pair_key,
                "file1": data["file1"],
                "file2": data["file2"],
                "final_score": score,
                "verdict": data["result"]["verdict"],
                "details": data["result"]
            })
            
    # Rank them by highest score first
    suspicious.sort(key=lambda x: x["final_score"], reverse=True)
    
    return suspicious
