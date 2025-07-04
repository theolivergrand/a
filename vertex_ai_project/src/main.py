import xml.etree.ElementTree as ET
import base64
import zlib
import urllib.parse


# -*- coding: utf-8 -*-
"""
Main script for Vertex AI project.
"""

def parse_drawio_diagram(file_path):
    """
    Parses a Draw.io diagram (.drawio file) and extracts information about nodes and edges.
    This function handles the decoding and decompression of the diagram data.

    Args:
        file_path (str): The path to the Draw.io diagram file (.drawio).

    Returns:
        dict: A dictionary containing 'nodes' and 'edges' information.
              Nodes are represented as {id: label}.
              Edges are represented as {source_id: [target_id1, target_id2, ...]}.
    """
    try:
        # 1. Parse the outer XML to get the diagram content
        outer_tree = ET.parse(file_path)
        diagram_node = outer_tree.find('.//diagram')
        if diagram_node is None or diagram_node.text is None:
            print("Error: <diagram> tag not found or it is empty.")
            return None
        
        encoded_data = diagram_node.text

        # 2. Decode from Base64
        decoded_data = base64.b64decode(encoded_data)
        
        # 3. Decompress (raw deflate)
        # The wbits parameter is set to -15 to handle raw deflate data without zlib header
        decompressed_data = zlib.decompress(decoded_data, -15)
        
        # 4. URL Decode
        inner_xml_string = urllib.parse.unquote(decompressed_data.decode('utf-8'))

        # 5. Parse the inner XML containing the graph model
        root = ET.fromstring(inner_xml_string)
        
        nodes = {}
        edges = {}

        # 6. Extract nodes and edges from the inner XML model
        for cell in root.findall(".//mxCell"):
            cell_id = cell.get("id")
            cell_value = cell.get("value")
            cell_source = cell.get("source")
            cell_target = cell.get("target")

            # It's a node if it has a value and is not an edge.
            # We also ignore the root cells (id 0 and 1) which are containers.
            if cell_value and not cell_source and not cell_target and cell_id not in ['0', '1']:
                nodes[cell_id] = cell_value
            # It's an edge if it has a source and a target
            elif cell_source and cell_target:
                if cell_source not in edges:
                    edges[cell_source] = []
                # Also capture the edge's label if it exists
                edge_label = cell.get('value', '')
                edges[cell_source].append({'target': cell_target, 'label': edge_label})

        return {"nodes": nodes, "edges": edges}

    except FileNotFoundError:
        print(f"Error: Diagram file not found at {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred during diagram parsing: {e}")
        return None


def main():
    """Main function."""
    print("Project setup complete. You can start coding now!")
    diagram_path = "vertex_ai_project/agent_flow.drawio"
    diagram_data = parse_drawio_diagram(diagram_path)

    if diagram_data:
        print("Diagram parsed successfully!")
        print("\n--- NODES ---")
        for node_id, label in diagram_data["nodes"].items():
            print(f"ID: {node_id}, Label: {label}")
        
        print("\n--- EDGES ---")
        for source_id, targets in diagram_data["edges"].items():
            for target_info in targets:
                print(f"From: {source_id} -> To: {target_info['target']} (Label: '{target_info['label']}')")
    else:
        print("Failed to parse diagram.")
    
    if diagram_data:
        run_agent(diagram_data)

# --- Agent Logic ---

def get_user_input():
    """Placeholder for getting user input."""
    print("ACTION: Getting user input (e.g., image or link)...")
    # In a real scenario, this would handle file uploads or URL inputs.
    return {"data": "path/to/image.jpg"}

def process_with_vertex_ai(data):
    """Placeholder for processing data with Vertex AI."""
    print(f"ACTION: Processing '{data}' with Vertex AI...")
    # This would call the Vertex AI SDK.
    return {"analysis": "detected UI elements...", "feedback_needed": True}

def return_result_and_get_feedback(analysis):
    """Placeholder for showing results and asking for feedback."""
    print(f"ACTION: Returning result: {analysis}")
    print("ACTION: Asking for user feedback...")
    # This could be a simple input() in a console app.
    feedback = input("Are there any refinements? (Type your feedback or leave empty to finish): ")
    return feedback

def process_feedback(feedback):
    """Placeholder for processing user feedback."""
    print(f"ACTION: Processing feedback: '{feedback}'...")
    # This might involve another call to Vertex AI with refined instructions.
    return {"data": "path/to/image.jpg_with_feedback"}

def find_start_node(nodes):
    """Finds the node with 'Начало' in its label."""
    for node_id, label in nodes.items():
        if 'начало' in label.lower():
            return node_id
    return None

def run_agent(diagram):
    """Executes the agent logic based on the parsed diagram."""
    nodes = diagram['nodes']
    edges = diagram['edges']
    
    start_node_id = find_start_node(nodes)
    if not start_node_id:
        print("\nERROR: Could not find a starting node in the diagram.")
        return

    print("\n--- Running Agent Workflow ---")
    current_node_id = start_node_id
    agent_data = None # This will hold the data as it flows through the agent

    while current_node_id:
        node_label = nodes.get(current_node_id, "Unknown Node")
        print(f"\nExecuting step: {node_label.replace('<br>', ' ')}")

        # Map node labels to functions
        if 'начало' in node_label.lower():
            pass # Starting point
        elif 'получить ввод' in node_label.lower():
            agent_data = get_user_input()
        elif 'обработать с помощью vertex' in node_label.lower():
            agent_data = process_with_vertex_ai(agent_data)
        elif 'вернуть результат' in node_label.lower():
            feedback = return_result_and_get_feedback(agent_data)
            if feedback:
                # If there is feedback, we need to find the node for processing feedback.
                # This is a simple implementation. A real one would use edge labels.
                feedback_node_id = None
                for target_id, label in nodes.items():
                    if 'обработать обратную связь' in label.lower():
                        feedback_node_id = target_id
                        break
                current_node_id = feedback_node_id
                agent_data = feedback # Pass feedback to the next step
                continue # Skip normal transition
            else:
                # No feedback, end of process
                current_node_id = None
                continue

        elif 'обработать обратную связь' in node_label.lower():
            agent_data = process_feedback(agent_data)
            # After processing feedback, loop back to Vertex AI processing
            feedback_loop_target = None
            for target_id, label in nodes.items():
                if 'обработать с помощью vertex' in label.lower():
                    feedback_loop_target = target_id
                    break
            current_node_id = feedback_loop_target
            continue

        else:
            print(f"Warning: No action defined for node '{node_label}'")

        # Transition to the next node
        if current_node_id and current_node_id in edges:
            # Simple transition, assumes one exit path unless handled by special logic above
            current_node_id = edges[current_node_id][0]['target']
        else:
            # End of workflow
            current_node_id = None
            
    print("\n--- Agent Workflow Finished ---")

if __name__ == "__main__":
    main() 