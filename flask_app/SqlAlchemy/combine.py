import os
import re

# Folder containing exported SQL schema files
export_folder = r'C:\Users\Sujan\OneDrive\Desktop\export'

# Output file to combine all SQL scripts into one
output_file = r'C:\Users\Sujan\OneDrive\Desktop\export\combined_schema.sql'

def process_sql_file(file_path):
    try:
        with open(file_path, 'r') as sql_file:
            sql_commands = sql_file.read()

        # Extract CREATE TABLE statements
        create_table_statements = re.findall(r'CREATE TABLE[\s\S]*?;\n', sql_commands)

        # Process each CREATE TABLE statement
        cleaned_statements = []
        for statement in create_table_statements:
            # Remove SQLAlchemy-specific annotations and adjust formatting
            cleaned_statement = re.sub(r'<sqlalchemy.*?>', '', statement)
            cleaned_statement = re.sub(r'(\(.*?)([\[\]])', r'\1', cleaned_statement)  # Remove brackets around column definitions

            cleaned_statements.append(cleaned_statement.strip())

        return '\n\n'.join(cleaned_statements)

    except Exception as e:
        print(f"Error processing SQL file {file_path}: {e}")
        return None

def combine_sql_files(export_folder, output_file):
    try:
        with open(output_file, 'w') as combined_file:
            # Define the order of processing based on dependency
            file_order = [
                'users_schema.sql',
                'cart_schema.sql',
                'comments_schema.sql',
                'items_schema.sql',
                'orders_schema.sql',
                'pictures_schema.sql',
                'sessions_schema.sql',
                'test_schema.sql',
                'transactions_schema.sql'
            ]

            for filename in file_order:
                file_path = os.path.join(export_folder, filename)
                if os.path.exists(file_path):
                    print(f"Processing {filename}...")
                    # Process SQL file and get cleaned SQL commands
                    sql_commands = process_sql_file(file_path)
                    if sql_commands:
                        # Write SQL commands to the combined file
                        combined_file.write(f"-- SQL commands from {filename}\n")
                        combined_file.write(sql_commands)
                        combined_file.write("\n\n")
                else:
                    print(f"File {filename} not found.")

        print(f"Combined SQL files into {output_file} successfully.")

    except Exception as e:
        print(f"Error combining SQL files: {e}")

# Call the function to combine and clean SQL files
combine_sql_files(export_folder, output_file)
