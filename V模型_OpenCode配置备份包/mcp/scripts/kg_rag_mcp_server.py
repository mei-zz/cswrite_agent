from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
from neo4j import GraphDatabase


WORKSPACE = Path(__file__).resolve().parents[1]
DEFAULT_NEO4J_URI = "bolt://localhost:7687"
DEFAULT_NEO4J_USER = "neo4j"
DEFAULT_NEO4J_PASSWORD = "kgneo4j2026"
DEFAULT_EMBEDDING_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_EMBEDDING_MODEL = "text-embedding-v3"


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_dotenv(WORKSPACE / ".env")


@dataclass
class Config:
    neo4j_uri: str = os.getenv("KG_NEO4J_URI", DEFAULT_NEO4J_URI)
    neo4j_user: str = os.getenv("KG_NEO4J_USER", DEFAULT_NEO4J_USER)
    neo4j_password: str = os.getenv("KG_NEO4J_PASSWORD", DEFAULT_NEO4J_PASSWORD)
    embedding_base_url: str = os.getenv(
        "KG_EMBEDDING_BASE_URL", DEFAULT_EMBEDDING_BASE_URL
    ).rstrip("/")
    embedding_model: str = os.getenv("KG_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
    embedding_api_key: str = os.getenv("KG_EMBEDDING_API_KEY")
    if not embedding_api_key:
        embedding_api_key = os.getenv("GRAPHRAG_API_KEY", "")


CONFIG = Config()
DRIVER = GraphDatabase.driver(
    CONFIG.neo4j_uri,
    auth=(CONFIG.neo4j_user, CONFIG.neo4j_password),
)

mcp = FastMCP(
    "kg-rag-neo4j",
    instructions=(
        "Use these tools to retrieve Chinese technical RAG context from the local "
        "Neo4j knowledge graph. Prefer kg_hybrid_search for normal questions, "
        "entity_lookup for entity details, and graph_expand for relationship exploration."
    ),
)


def run_read(query: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    with DRIVER.session(database=os.getenv("KG_NEO4J_DATABASE", "neo4j")) as session:
        result = session.run(query, parameters or {})
        return [record.data() for record in result]


def compact_text(value: str | None, max_chars: int = 1200) -> str:
    if not value:
        return ""
    text = " ".join(str(value).split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3] + "..."


def normalize_top_k(top_k: int, default: int = 8, maximum: int = 30) -> int:
    try:
        value = int(top_k)
    except Exception:
        value = default
    return max(1, min(value, maximum))


def embed_query(query: str) -> list[float]:
    if not CONFIG.embedding_api_key:
        raise RuntimeError(
            "Missing embedding API key. Set KG_EMBEDDING_API_KEY or GRAPHRAG_API_KEY."
        )
    url = f"{CONFIG.embedding_base_url}/embeddings"
    payload = {"model": CONFIG.embedding_model, "input": query}
    headers = {
        "Authorization": f"Bearer {CONFIG.embedding_api_key}",
        "Content-Type": "application/json",
    }
    with httpx.Client(timeout=60) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
    return [float(value) for value in data["data"][0]["embedding"]]


def enrich_text_units(ids: list[str]) -> list[dict[str, Any]]:
    if not ids:
        return []
    rows = run_read(
        """
        MATCH (t:TextUnit)
        WHERE t.id IN $ids
        OPTIONAL MATCH (d:Document)-[:HAS_TEXT_UNIT]->(t)
        OPTIONAL MATCH (t)-[:MENTIONS]->(e:Entity)
        WITH t, d, collect(DISTINCT {id: e.id, title: e.title, type: e.type}) AS entities
        RETURN t.id AS id,
               t.human_readable_id AS human_readable_id,
               t.n_tokens AS n_tokens,
               t.text AS text,
               d.id AS document_id,
               d.title AS document_title,
               entities[0..20] AS entities
        """,
        {"ids": ids},
    )
    by_id = {row["id"]: row for row in rows}
    return [by_id[item] for item in ids if item in by_id]


def format_text_unit_result(row: dict[str, Any], score: float | None = None) -> dict[str, Any]:
    result = {
        "text_unit_id": row.get("id"),
        "text_unit_human_readable_id": row.get("human_readable_id"),
        "document_id": row.get("document_id"),
        "document_title": row.get("document_title"),
        "n_tokens": row.get("n_tokens"),
        "text": compact_text(row.get("text"), 1600),
        "mentioned_entities": row.get("entities") or [],
    }
    if score is not None:
        result["score"] = float(score)
    return result


@mcp.tool()
def kg_fulltext_search(query: str, top_k: int = 8) -> dict[str, Any]:
    """Search original TextUnit evidence with Neo4j full-text index."""
    top_k = normalize_top_k(top_k)
    rows = run_read(
        """
        CALL db.index.fulltext.queryNodes('textunit_text_fulltext', $query)
        YIELD node, score
        OPTIONAL MATCH (d:Document)-[:HAS_TEXT_UNIT]->(node)
        OPTIONAL MATCH (node)-[:MENTIONS]->(e:Entity)
        WITH node, score, d, collect(DISTINCT {id: e.id, title: e.title, type: e.type}) AS entities
        RETURN node.id AS id,
               node.human_readable_id AS human_readable_id,
               node.n_tokens AS n_tokens,
               node.text AS text,
               d.id AS document_id,
               d.title AS document_title,
               entities[0..20] AS entities,
               score AS score
        ORDER BY score DESC
        LIMIT $top_k
        """,
        {"query": query, "top_k": top_k},
    )
    return {
        "query": query,
        "route": "fulltext",
        "results": [format_text_unit_result(row, row.get("score")) for row in rows],
    }


@mcp.tool()
def kg_vector_search(query: str, top_k: int = 8) -> dict[str, Any]:
    """Search original TextUnit evidence with Neo4j vector index."""
    top_k = normalize_top_k(top_k)
    query_vector = embed_query(query)
    rows = run_read(
        """
        CALL db.index.vector.queryNodes('textunit_embedding_vector', $top_k, $query_vector)
        YIELD node, score
        OPTIONAL MATCH (d:Document)-[:HAS_TEXT_UNIT]->(node)
        OPTIONAL MATCH (node)-[:MENTIONS]->(e:Entity)
        WITH node, score, d, collect(DISTINCT {id: e.id, title: e.title, type: e.type}) AS entities
        RETURN node.id AS id,
               node.human_readable_id AS human_readable_id,
               node.n_tokens AS n_tokens,
               node.text AS text,
               d.id AS document_id,
               d.title AS document_title,
               entities[0..20] AS entities,
               score AS score
        ORDER BY score DESC
        LIMIT $top_k
        """,
        {"query_vector": query_vector, "top_k": top_k},
    )
    return {
        "query": query,
        "route": "vector",
        "embedding_model": CONFIG.embedding_model,
        "results": [format_text_unit_result(row, row.get("score")) for row in rows],
    }


@mcp.tool()
def entity_lookup(name: str, limit: int = 10) -> dict[str, Any]:
    """Find entities by exact/fuzzy title and return descriptions plus source evidence."""
    limit = normalize_top_k(limit, default=10, maximum=30)
    rows = run_read(
        """
        MATCH (e:Entity)
        WHERE toLower(e.title) CONTAINS toLower($name)
           OR toLower(e.description) CONTAINS toLower($name)
        OPTIONAL MATCH (t:TextUnit)-[:MENTIONS]->(e)
        OPTIONAL MATCH (d:Document)-[:HAS_TEXT_UNIT]->(t)
        WITH e, collect(DISTINCT {
            text_unit_id: t.id,
            document_title: d.title,
            text: left(t.text, 500)
        }) AS evidence
        RETURN e.id AS id,
               e.title AS title,
               e.type AS type,
               e.description AS description,
               e.frequency AS frequency,
               e.degree AS degree,
               evidence[0..5] AS evidence
        ORDER BY e.degree DESC, e.frequency DESC
        LIMIT $limit
        """,
        {"name": name, "limit": limit},
    )
    for row in rows:
        row["description"] = compact_text(row.get("description"), 900)
        for evidence in row.get("evidence") or []:
            evidence["text"] = compact_text(evidence.get("text"), 500)
    return {"query": name, "results": rows}


@mcp.tool()
def graph_expand(entity_name: str, hops: int = 1, relationship_type: str = "", limit: int = 30) -> dict[str, Any]:
    """Expand graph relationships around an entity by 1 or 2 hops."""
    hops = max(1, min(int(hops), 2))
    limit = normalize_top_k(limit, default=30, maximum=80)
    rel_filter = relationship_type.strip()
    if hops == 1:
        query = """
        MATCH (center:Entity)
        WHERE toLower(center.title) CONTAINS toLower($name)
        MATCH (center)-[r:RELATED]-(neighbor:Entity)
        WHERE $rel_type = '' OR r.relationship_type = $rel_type
        RETURN center.title AS center,
               neighbor.title AS neighbor,
               neighbor.type AS neighbor_type,
               r.relationship_type AS relationship_type,
               r.description AS description,
               r.weight AS weight
        ORDER BY r.weight DESC
        LIMIT $limit
        """
    else:
        query = """
        MATCH (center:Entity)
        WHERE toLower(center.title) CONTAINS toLower($name)
        MATCH path=(center)-[r1:RELATED]-(mid:Entity)-[r2:RELATED]-(neighbor:Entity)
        WHERE ($rel_type = '' OR r1.relationship_type = $rel_type OR r2.relationship_type = $rel_type)
          AND center <> neighbor
        RETURN center.title AS center,
               mid.title AS mid,
               neighbor.title AS neighbor,
               neighbor.type AS neighbor_type,
               r1.relationship_type AS first_relationship_type,
               r1.description AS first_description,
               r2.relationship_type AS second_relationship_type,
               r2.description AS second_description,
               coalesce(r1.weight, 0) + coalesce(r2.weight, 0) AS weight
        ORDER BY weight DESC
        LIMIT $limit
        """
    rows = run_read(
        query,
        {
            "name": entity_name,
            "rel_type": rel_filter,
            "limit": limit,
        },
    )
    for row in rows:
        for key in ("description", "first_description", "second_description"):
            if key in row:
                row[key] = compact_text(row.get(key), 600)
    return {
        "entity_name": entity_name,
        "hops": hops,
        "relationship_type": rel_filter or None,
        "results": rows,
    }


@mcp.tool()
def kg_hybrid_search(query: str, top_k: int = 8, include_graph: bool = True) -> dict[str, Any]:
    """Run full-text + vector retrieval and return merged RAG context with optional graph expansion."""
    top_k = normalize_top_k(top_k)
    fulltext = kg_fulltext_search(query, top_k=top_k)["results"]
    try:
        vector = kg_vector_search(query, top_k=top_k)["results"]
    except Exception as exc:
        vector = []
        vector_error = str(exc)
    else:
        vector_error = None

    scores: dict[str, dict[str, Any]] = {}
    for route_name, items in (("fulltext", fulltext), ("vector", vector)):
        for rank, item in enumerate(items, start=1):
            key = item["text_unit_id"]
            entry = scores.setdefault(
                key,
                {
                    "item": item,
                    "routes": [],
                    "rrf_score": 0.0,
                },
            )
            entry["routes"].append(route_name)
            entry["rrf_score"] += 1.0 / (60 + rank)

    merged = sorted(scores.values(), key=lambda item: item["rrf_score"], reverse=True)[
        :top_k
    ]
    evidence = []
    entity_titles: list[str] = []
    for entry in merged:
        item = entry["item"]
        item["routes"] = entry["routes"]
        item["rrf_score"] = entry["rrf_score"]
        evidence.append(item)
        for entity in item.get("mentioned_entities") or []:
            title = entity.get("title")
            if title and title not in entity_titles:
                entity_titles.append(title)

    graph_context = []
    if include_graph:
        for title in entity_titles[:5]:
            expanded = graph_expand(title, hops=1, limit=8).get("results", [])
            graph_context.append({"entity": title, "neighbors": expanded})

    return {
        "query": query,
        "routes": ["fulltext", "vector"],
        "vector_error": vector_error,
        "evidence": evidence,
        "graph_context": graph_context,
        "answering_instruction": (
            "Use the returned TextUnit evidence as primary facts. Cite document_title "
            "and text_unit_id when answering. Use graph_context only to expand related concepts."
        ),
    }


SAFE_CYPHER_PREFIXES = ("MATCH ", "CALL DB.INDEX", "SHOW ")
FORBIDDEN_CYPHER = re.compile(
    r"\b(CREATE|MERGE|DELETE|DETACH|SET|REMOVE|DROP|LOAD\s+CSV|CALL\s+DBMS|CALL\s+APOC)\b",
    re.IGNORECASE,
)


@mcp.tool()
def neo4j_read_cypher(cypher: str, parameters_json: str = "{}", limit: int = 50) -> dict[str, Any]:
    """Run a guarded read-only Cypher query for diagnostics and advanced retrieval."""
    query = cypher.strip()
    upper = query.upper()
    if not upper.startswith(SAFE_CYPHER_PREFIXES):
        raise ValueError("Only MATCH, SHOW, and CALL db.index.* read queries are allowed.")
    if FORBIDDEN_CYPHER.search(query):
        raise ValueError("Write/admin Cypher is not allowed.")
    params = json.loads(parameters_json or "{}")
    rows = run_read(query, params)
    limit = normalize_top_k(limit, default=50, maximum=200)
    return {"rows": rows[:limit], "truncated": len(rows) > limit}


@mcp.tool()
def kg_status() -> dict[str, Any]:
    """Return Neo4j KG-RAG health and index status."""
    counts = run_read(
        """
        MATCH (d:Document) WITH count(d) AS documents
        MATCH (t:TextUnit) WITH documents, count(t) AS text_units
        MATCH (t:TextUnit) WHERE t.embedding IS NOT NULL WITH documents, text_units, count(t) AS text_units_with_embeddings
        MATCH (e:Entity) WITH documents, text_units, text_units_with_embeddings, count(e) AS entities
        MATCH (:Entity)-[r:RELATED]->(:Entity)
        RETURN documents, text_units, text_units_with_embeddings, entities, count(r) AS relationships
        """
    )
    indexes = run_read(
        """
        SHOW INDEXES
        YIELD name, type, state, populationPercent, labelsOrTypes, properties
        WHERE name IN ['textunit_text_fulltext', 'textunit_embedding_vector']
        RETURN name, type, state, populationPercent, labelsOrTypes, properties
        ORDER BY name
        """
    )
    return {
        "neo4j_uri": CONFIG.neo4j_uri,
        "embedding_model": CONFIG.embedding_model,
        "counts": counts[0] if counts else {},
        "indexes": indexes,
    }


def self_test() -> None:
    print(json.dumps(kg_status(), ensure_ascii=False, indent=2))
    print(json.dumps(kg_fulltext_search("烧录器 通讯协议", top_k=2), ensure_ascii=False, indent=2))
    print(json.dumps(kg_hybrid_search("烧录器如何和上位机通信？", top_k=2), ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
