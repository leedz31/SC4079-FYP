import json
import os
import sys

input_filename = sys.argv[1]

# method_keys_to_extract = ["identity"]
method_property_keys_to_extract = ["NAME", "IS_SERIALIZABLE", "SUB_SIGNATURE", "IS_SINK", "CLASSNAME"]
relationship_property_keys_to_extract = ["INVOKER_TYPE"]

output_folder = "./Processed results"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def process_json_file(input_filename):
    with open(input_filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    for index, item in enumerate(data):
        count = 1
        chain = {
            "chain_id": index+1,
            "gadget_chain": []
        }

        segments = item["path"]["segments"]
        for segment in segments:

            # Extract metadata about the start method
            start_dict = segment["start"]
            src_method = {}
            # src_method = {key.lower(): start_dict[key] for key in method_keys_to_extract if key in start_dict}
            src_method.update({key.lower(): start_dict["properties"].get(key) for key in method_property_keys_to_extract})
            src_method.update({'code_snippet':""})

            # Extract metadata about the relationship
            rs_dict = segment["relationship"]
            relationship = {
                # "START_IDENTITY": rs_dict["start"],
                # "END_IDENTITY": rs_dict["end"],
                "type": rs_dict["type"],
                **{key.lower(): rs_dict["properties"].get(key) for key in relationship_property_keys_to_extract}
            }

            # Extract metadata about the end method
            end_dict = segment["end"]
            dest_method = {}
            # dest_method = {key.lower(): end_dict[key] for key in method_keys_to_extract if key in end_dict}
            dest_method.update({key.lower(): end_dict["properties"].get(key) for key in method_property_keys_to_extract})
            dest_method.update({'code_snippet':""})

            step = {
                "step": count,
                "source": src_method,
                "relationship": relationship,
                "destination": dest_method
            }

            chain["gadget_chain"].append(step)
            count+=1
        
        output_filename = os.path.join(output_folder, f"chain_{index+1}.json")
        if os.path.exists(output_filename):
            print("Error: File of same name already exists in this folder")
            break
        else:
            with open(output_filename, "w") as output_file:
                json.dump(chain, output_file, indent=4)
            print(f"Saved chain {index+1} to {output_filename}")  

process_json_file(input_filename)