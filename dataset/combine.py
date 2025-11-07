import pandas as pd
import json
import os
import glob
import random

INPUT_DIRECTORY = 'final'
OUTPUT_FILE = 'group7_combined_data.csv'
ROWS_PER_FILE = 5

def clean_target_instruction(instruction_str):
    if not isinstance(instruction_str, str) or not instruction_str.startswith('["'):
        return instruction_str
    try:
        parsed_list = json.loads(instruction_str)
        if isinstance(parsed_list, list) and len(parsed_list) > 0:
            return parsed_list[0]
        else:
            return instruction_str
    except json.JSONDecodeError:
        return instruction_str.strip('[]"\' ')

def process_and_combine_csvs(input_dir, output_file, num_rows):
    csv_files = glob.glob(os.path.join(input_dir, '*.csv'))
    
    if not csv_files:
        print(f"Error: No CSV files found in the '{input_dir}' directory.")
        return

    print(f"Found {len(csv_files)} CSV files to process.")

    all_processed_rows = []

    for file_path in csv_files:
        print(f"\nProcessing file: {os.path.basename(file_path)}")
        try:
            df = pd.read_csv(file_path)

            if len(df) < num_rows:
                print(f"  Warning: File has fewer than {num_rows} rows. Using all {len(df)} rows.")
                sample_df = df
            else:
                sample_df = df.sample(n=num_rows, random_state=42)

            for index, row in sample_df.iterrows():
                try:
                    distractors_list = json.loads(row['distractors'])
                    if not distractors_list:
                        print(f"  Skipping row {index} due to empty distractors list.")
                        continue
                    
                    selected_pair = random.choice(distractors_list)
                    selected_bot_turn = selected_pair['bot turn']
                    selected_distractor = selected_pair['distractor']
                    

                    conversation = json.loads(row['conversation_json'])                        
                    
                    new_row = row.to_dict()

                    new_row['target_system_instruction'] = clean_target_instruction(row['target_system_instruction'])
                    new_row['conversation_json'] = json.dumps(conversation, indent=2)
                    
                    new_row['distractors'] = json.dumps([selected_pair], indent=2)

                    all_processed_rows.append(new_row)

                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    print(f"  Skipping row {index} due to a processing error: {e}")
                    continue
        
        except Exception as e:
            print(f"Error reading or processing file {file_path}: {e}")

    if not all_processed_rows:
        print("No rows were successfully processed. Output file will not be created.")
        return
        
    final_df = pd.DataFrame(all_processed_rows)

    final_df = final_df[df.columns]
    
    final_df.to_csv(output_file, index=False)
    print(f"\nSuccessfully processed {len(all_processed_rows)} rows and saved to '{output_file}'")


if __name__ == "__main__":
    if not os.path.exists(INPUT_DIRECTORY):
        os.makedirs(INPUT_DIRECTORY)
        print(f"Created directory '{INPUT_DIRECTORY}'. Please place your four CSV files inside it and run the script again.")
    else:
        process_and_combine_csvs(INPUT_DIRECTORY, OUTPUT_FILE, ROWS_PER_FILE)