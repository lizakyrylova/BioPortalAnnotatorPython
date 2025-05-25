import csv
import re
import requests
from pathlib import Path
from typing import List


def load_terms(term_path: str) -> List[str]:
    """
    Load non-empty, stripped terms from a plain text file.

    :param term_path: Path to .txt file with terms (one per line).
    :return: List of non-empty, stripped terms.
    """
    return [
        term.strip()
        for term in Path(term_path).read_text(encoding="utf-8").splitlines()
        if term.strip()
    ]


def normalize_ontologies(ontologies: str) -> List[str]:
    """
    Normalize ontology list input into a clean list of acronyms.

    :param ontologies: Comma-separated string of ontology acronyms.
    :return: List of acronyms or [''] to query all ontologies.
    """
    return [o.strip() for o in ontologies.split(",") if o.strip()] or [""]


def get_completeness(input_term: str, match_label: str) -> str:
    """
    Determine the match quality between input and ontology label.

    :param input_term: Original input term.
    :param match_label: Label returned by BioPortal.
    :return: 'Complete', 'Component', 'Partial', or '' if irrelevant.
    """
    t_norm = input_term.lower()
    l_norm = match_label.lower()

    if t_norm == l_norm:
        return "Complete"
    if " " in l_norm and l_norm in t_norm:
        return "Component"
    if re.search(rf"\b{re.escape(l_norm)}\b", t_norm):
        return "Partial"

    return ""  # Uninformative match


def annotate_terms(
    api_key: str,
    term_path: str,
    ontologies: str,
    out_path: str,
    *,
    include_synonyms: bool = True,
    whole_word_only: bool = False,
    longest_only: bool = True,
    direct_matches_only: bool = True,
    require_complete_match: bool = False,
    timeout: int = 30,
) -> None:
    """
    Annotate biomedical terms using the NCBO BioPortal Annotator API.

    :param api_key: BioPortal API key.
    :param term_path: Path to input file (.txt with one term per line).
    :param ontologies: Comma-separated list of ontology acronyms.
    :param out_path: Path to output .csv file.
    :param include_synonyms: Whether to include synonyms in search.
    :param whole_word_only: Restrict matches to whole words only.
    :param longest_only: Keep only the longest matching concept.
    :param direct_matches_only: Avoid hierarchy-based matches.
    :param require_complete_match: Keep only exact matches (e.g. for drugs).
    :param timeout: Timeout in seconds for API requests.
    """
    base_url = "https://data.bioontology.org/annotator"
    terms = load_terms(term_path)
    if not terms:
        raise ValueError("Input term list is empty.")

    onto_list = normalize_ontologies(ontologies)

    with open(out_path, "w", encoding="utf-8", newline="") as fout:
        writer = csv.writer(fout)
        writer.writerow(["Term", "Match", "Completeness", "Ontology", "IRI"])

        for term in terms:
            for ont in onto_list:
                params = {
                    "apikey": api_key,
                    "text": term,
                    "exclude_synonyms": str(not include_synonyms).lower(),
                    "whole_word_only": str(whole_word_only).lower(),
                    "longest_only": str(longest_only).lower(),
                }

                if ont:
                    params["ontologies"] = ont

                if direct_matches_only:
                    params.update({
                        "expand_class_hierarchy": "false",
                        "class_hierarchy_max_level": "0",
                    })

                try:
                    response = requests.get(base_url, params=params, timeout=timeout)
                    response.raise_for_status()
                except requests.RequestException as exc:
                    print(
                        "[WARN]", exc,
                        f"— term={term}", f"ontology={ont or 'ALL'}"
                    )
                    continue

                for annotation in response.json():
                    label = annotation["annotations"][0]["text"]
                    iri = annotation["annotatedClass"]["@id"]
                    completeness = get_completeness(term, label)

                    if not completeness:
                        continue

                    if require_complete_match and completeness != "Complete":
                        continue

                    writer.writerow([
                        term, label, completeness, ont or "ALL", iri
                    ])

    print(f"Results saved to {out_path}")


if __name__ == "__main__":
    # Example configuration for diseases
    result_path = "output_samples/disease_terms_output.csv"
    term_path = "input_samples/disease_list.txt"
    api_key = "your-api-key-here"
    ontologies = "DOID,MESH" #for diseases, for example

    annotate_terms(
        api_key=api_key,
        term_path=term_path,
        ontologies=ontologies,
        out_path=result_path,
        require_complete_match=False,  # Set to True for drug input
    )