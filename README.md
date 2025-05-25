# BioPortalAnnotatorPython
This repository contains a Python script (`bioportal_annotator.py`) designed to annotate biomedical terms (such as diseases or drugs) using the [NCBO BioPortal Annotator API](https://bioportal.bioontology.org/annotator). It maps terms to standard biomedical ontology IDs.

## Repository Structure

```
bioportal-annotator/
├── README.md
├── requirements.txt
├── bioportal_annotator.py
├── input_samples/
│   ├── disease_list.txt
│   └── drug_list.txt
├── output_samples/
│   ├── disease_terms_output.csv
│   └── drug_terms_output.csv
```

## Why BioPortal?

BioPortal Annotator is an excellent choice for biomedical term annotation due to:

* **Comprehensive Coverage**: Offers hundreds of up-to-date biomedical ontologies.
* **Continuous Updates**: Frequently refreshed with the latest terms and ontologies.
* **Ease of Use**: Simple REST-based API, requiring minimal setup and overhead.
* **Accessibility**: Freely available API keys with a straightforward registration process.

## Match Types Explained

The annotator identifies three match types:

* **Complete Match**: Exact match between input and ontology term.

  * Example: Input: "Asthma" → Match: "Asthma"

* **Component Match**: Multi-word ontology term entirely contained within input.

  * Example: Input: "Chronic Asthma Attack" → Match: "Asthma Attack"

* **Partial Match**: Single-word ontology term that appears as a whole word within input.

  * Example: Input: "Pulmonary Embolism" → Match: "Embolism"

## Input Format

Input files should contain one biomedical term per line. The provided examples (`disease_list.txt` and `drug_list.txt`) were compiled from 20 randomized terms from our research data, representing a diverse range of possible inputs.

### Important Note

From personal research, annotation success varied significantly between diseases and drugs:

* **Drug ID retrieval**: 792 IDs assigned out of 2,083 unique terms across four datasets (\~38%). Most successful annotations were generic names. Long IUPAC strings, such as "1-azabicyclo\[2.2.2]octan-3-one, 2-(4-morpholinylmethyl)-...", typically failed.

* **Disease ID retrieval**: 2,734 IDs assigned out of 2,855 unique terms (\~96%). Nearly all missed annotations were due to spelling errors in the source text.

### Recommendations

This annotation method is not perfect. To improve results:

* Standardize your input terms as much as possible.
* Avoid long chemical descriptors (e.g., IUPAC names) unless specifically supported by your target ontologies.
* Double-check for spelling errors.

## Requirements

* **Python 3.6 or higher**
* **BioPortal API key** ([Sign up here](https://bioportal.bioontology.org/accounts/new))

### Installation

Install dependencies using `pip`:

```bash
pip install -r requirements.txt
```

## Usage Instructions

Edit the provided sample usage section (`__main__`) in `bioportal_annotator.py` or create your own scripts.

### Disease Annotation Example

```python
annotate_terms(
    api_key="your-api-key-here",
    term_path="input_samples/disease_list.txt",
    ontologies="DOID,MESH",
    out_path="output_samples/disease_terms_output.csv",
    require_complete_match=False
)
```

### Drug Annotation Example

For drug terms, use stricter matching by enabling `require_complete_match`:

```python
annotate_terms(
    api_key="your-api-key-here",
    term_path="input_samples/drug_list.txt",
    ontologies="CHEBI,DRON,RXNORM,NCIT,MESH,MDM",
    out_path="output_samples/drug_terms_output.csv",
    require_complete_match=True
)
```

### Annotating from All Ontologies

To search across **all public ontologies**, set `ontologies` to an empty string:

```python
ontologies=""
```

## Output Format

The script outputs a CSV file containing:

* `Term`: Original input term
* `Match`: Ontology label returned by BioPortal
* `Completeness`: Match quality (`Complete`, `Component`, or `Partial`)
* `Ontology`: Ontology acronym
* `IRI`: Ontology concept URL (IRI)

## Citation and Acknowledgement

Please acknowledge the [NCBO BioPortal Annotator](https://bioportal.bioontology.org) when using results obtained from this script. Code was written based on the following API documentation: (https://data.bioontology.org/documentation)

---
