import json
import os
import shutil

QUEUE_DIR = "/home/ubuntu/el-monstruo-bridge/bridge/state_fabric/queue"
ARCHIVE_DIR = os.path.join(QUEUE_DIR, "archive")


def process_queue():
    if not os.path.exists(QUEUE_DIR):
        return []

    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)

    processed_decisions = []

    for filename in os.listdir(QUEUE_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(QUEUE_DIR, filename)
            try:
                with open(filepath, "r") as f:
                    decision = json.load(f)

                # Basic validation
                if decision.get("signature") == "T1" and decision.get("decision") in ["APPROVE", "REJECT", "MODIFY"]:
                    processed_decisions.append(decision)

                    # Move to archive
                    shutil.move(filepath, os.path.join(ARCHIVE_DIR, filename))
                else:
                    print(f"Invalid decision format or signature in {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    return processed_decisions


if __name__ == "__main__":
    decisions = process_queue()
    print(f"Processed {len(decisions)} decisions.")
