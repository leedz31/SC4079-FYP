import os
import json
import subprocess
from neo4j import GraphDatabase

# Auth details to connect to Neo4j graph database
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password")
OUTPUT_FOLDER = "./Query results"

def get_next_available_filename():
    # Check for existing output JSON files and determine the next available filename
    base_name = "output"
    extension = ".json"
    existing_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.startswith(base_name) and f.endswith(extension)]

    if not existing_files:
        return os.path.join(OUTPUT_FOLDER, f"{base_name}{extension}")

    index = 2
    while f"{base_name}{index}{extension}" in existing_files:
        index += 1

    return os.path.join(OUTPUT_FOLDER, f"{base_name}{index}{extension}")

def discover_gadget_chains(tx, srcname, limit):
    result = tx.run("""
        query to be executed
    """, srcname=srcname, limit=limit)

    gadget_chains = []

    for record in result:
        path = record["path"]
        nodes = list(path.nodes)
        relationships = list(path.relationships)

        # Start and end nodes
        path_structure = {
            "path": {
                "start": extract_node_info(nodes[0]),
                "end": extract_node_info(nodes[-1]),
                "segments": []
            }
        }

        # Construct segments
        for i in range(len(relationships)):
            segment = {
                "start": extract_node_info(nodes[i]),
                "relationship": extract_relationship_info(relationships[i]),
                "end": extract_node_info(nodes[i + 1])
            }
            path_structure["path"]["segments"].append(segment)

        gadget_chains.append(path_structure)

    return gadget_chains

def extract_node_info(node):
    """Extracts detailed node information."""
    return {
        "identity": node.id,
        "labels": list(node.labels),
        "properties": dict(node),
        "elementId": node.element_id
    }

def extract_relationship_info(relationship):
    """Extracts detailed relationship information."""
    return {
        "identity": relationship.id,
        "start": relationship.start_node.id,
        "end": relationship.end_node.id,
        "type": relationship.type,
        "properties": dict(relationship),
        "elementId": relationship.element_id,
        "startNodeElementId": relationship.start_node.element_id,
        "endNodeElementId": relationship.end_node.element_id
    }

def main():
    # Ensure that the output folder exists
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    try:
        # Creates driver and session objects, then executes the query on the database
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            with driver.session(database="neo4j") as session:
                paths = session.execute_read(discover_gadget_chains, "readObject", 5)

        # Checks if there is an existing JSON file with the same name in the Results folder
        output_filename = get_next_available_filename()
        
        # Save results to JSON for LLM processing
        with open(output_filename, "w") as f:
            json.dump(paths, f, indent=4)
        print(f"Query results saved to {output_filename}")

        # Close session and driver
        session.close()
        driver.close()

        # Call subprocess to process JSON file into correct format for LLM processing
        subprocess.run(["python", "parse_results.py", output_filename])

    except Exception as e:
        print(f"An error has occured: {e}")

if __name__ == "__main__":
    main()
