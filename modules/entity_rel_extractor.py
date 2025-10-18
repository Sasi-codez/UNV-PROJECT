import re
import spacy
from neo4j import GraphDatabase
from typing import Dict, Any

# -----------------------------
# 1️⃣ Load spaCy model
# -----------------------------
nlp = spacy.load("en_core_web_lg")

# -----------------------------
# 2️⃣ Entity & Relation Extractor
# -----------------------------
def extract_entities_relations(text: str) -> Dict[str, Any]:
    doc = nlp(text)
    entities = {"books": [], "authors": [], "publishers": [], "genres": []}
    relations = []

    # --- Books (quoted titles) ---
    for b in re.findall(r"['\"](.*?)['\"]", text):
        entities["books"].append({"title": b})

    # --- Named entities ---
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            entities["authors"].append({"name": ent.text})
        elif ent.label_ == "ORG":
            entities["publishers"].append({"name": ent.text})
        elif ent.label_ == "WORK_OF_ART":
            entities["books"].append({"title": ent.text})

    # --- Genres (pattern-based) ---
    genres = re.findall(
        r"\b(Fiction|Fantasy|Romance|Mystery|Thriller|Non[- ]?Fiction|Biography|Science Fiction)\b",
        text, re.IGNORECASE
    )
    for g in genres:
        entities["genres"].append({"name": g.capitalize()})

    # --- Relations ---
    for book in entities["books"]:
        title = book["title"]

        if match := re.search(r"written by ([A-Z][a-zA-Z.\s]+)", text):
            relations.append({"book": title, "relation": "written_by", "target": match.group(1).strip()})

        if match := re.search(r"published by ([A-Z][a-zA-Z&\s]+)", text):
            relations.append({"book": title, "relation": "published_by", "target": match.group(1).strip()})

        if match := re.search(r"belongs to the ([A-Za-z\s]+) genre", text):
            relations.append({"book": title, "relation": "belongs_to_genre", "target": match.group(1).strip()})
        elif genres:
            relations.append({"book": title, "relation": "belongs_to_genre", "target": genres[0].capitalize()})

    # --- Deduplicate ---
    for k in entities:
        uniq, seen = [], set()
        for e in entities[k]:
            val = list(e.values())[0].lower()
            if val not in seen:
                uniq.append(e)
                seen.add(val)
        entities[k] = uniq

    return {"entities": entities, "relations": relations}

# -----------------------------
# 3️⃣ Neo4j Insertion Module
# -----------------------------
def store_in_neo4j(driver, entities: Dict[str, Any], relations: list):
    with driver.session() as session:
        # Create entities
        for book in entities["books"]:
            session.run("MERGE (b:Book {title: $title})", title=book["title"])

        for author in entities["authors"]:
            session.run("MERGE (a:Author {name: $name})", name=author["name"])

        for pub in entities["publishers"]:
            session.run("MERGE (p:Publisher {name: $name})", name=pub["name"])

        for genre in entities["genres"]:
            session.run("MERGE (g:Genre {name: $name})", name=genre["name"])

        # Create relationships
        for rel in relations:
            if rel["relation"] == "written_by":
                session.run("""
                    MATCH (b:Book {title: $book}), (a:Author {name: $target})
                    MERGE (b)-[:WRITTEN_BY]->(a)
                """, **rel)
            elif rel["relation"] == "published_by":
                session.run("""
                    MATCH (b:Book {title: $book}), (p:Publisher {name: $target})
                    MERGE (b)-[:PUBLISHED_BY]->(p)
                """, **rel)
            elif rel["relation"] == "belongs_to_genre":
                session.run("""
                    MATCH (b:Book {title: $book}), (g:Genre {name: $target})
                    MERGE (b)-[:BELONGS_TO_GENRE]->(g)
                """, **rel)

# -----------------------------
# 4️⃣ Main Pipeline Function
# -----------------------------
def process_chunks(driver, chunks: list):
    for i, chunk in enumerate(chunks, 1):
        print(f"\n🧩 Processing Chunk {i}")
        result = extract_entities_relations(chunk)
        store_in_neo4j(driver, result["entities"], result["relations"])
        print(f"✅ Stored entities & relations from chunk {i}")

# -----------------------------
# ✅ Usage Example
# -----------------------------
if __name__ == "__main__":
    # your Neo4j driver (you said you’ll provide)
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

    chunks = [
        "The book 'The Great Gatsby' was written by F. Scott Fitzgerald and published by Scribner in 1925. It belongs to the Fiction genre.",
        "Harry Potter and the Philosopher's Stone, written by J.K. Rowling and published by Bloomsbury, is a Fantasy novel."
    ]

    process_chunks(driver, chunks)
    driver.close()
