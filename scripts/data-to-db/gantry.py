import os
import pandas as pd
import psycopg2
from datetime import datetime
import re
import tqdm
import time

# Database connection parameters
DB_PARAMS = {
    'dbname': 'traffic',
    'user': 'kori',
    'password': '123456',  # Replace with your actual password
    'host': 'localhost',
    'port': '5432'
}

# Define the gantry data
GANTRY_DATA = [
    (1, 731, 'G004242003007310010', '荆门枢纽-荆门南1',
     '荆门南', '荆宜分中心', 112.180864, 30.92213, 'k1043', 1),
    (2, 251, 'G004242003002510010', '荆门南—荆门西1', '荆门西',
     '荆宜分中心', 112.13812, 30.911968, 'k1047', 1),
    (3, 271, 'G004242003002710010', '荆门西-淯溪1', '荆门西',
     '荆宜分中心', 112.116491, 30.906371, 'k1049', 1),
    (4, 281, 'G004242003002810010', '淯溪-当阳东1',
     '育溪', '荆宜分中心', 111.9221, 30.81368, 'k1070', 1),
    (5, 291, 'G004242003002910010', '当阳东-当阳西1', '当阳东',
     '荆宜分中心', 111.833292, 30.775778, 'k1081', 1),
    (6, 301, 'G004242003003010010', '当阳西-保宜荆宜交界1',
     '当阳西', '荆宜分中心', 111.728802, 30.760547, 'k1091', 1),
    (7, 311, 'G004242003003110010', '保宜荆宜交界-双莲1',
     '双莲', '荆宜分中心', 111.636806, 30.748879, 'k1100', 1),
    (8, 321, 'G004242003003210010', '双莲-宜巴起点1', '双莲',
     '荆宜分中心', 111.61552, 30.746076, 'k1102', 1),
    (9, 331, 'G004242003003310010', '宜巴起点-鸦鹊岭1',
     '鸦鹊岭', '荆宜分中心', 111.532779, 30.706233, 'k4', 1),
    (10, 341, 'G004242003003410010', '鸦鹊岭-荆宜汉宜交界1',
     '鸦鹊岭', '荆宜分中心', 111.51833, 30.69206, 'k6', 1),

    (20, 732, 'G004242003007320010', '荆门南-荆门枢纽1',
     '荆门南', '荆宜分中心', 112.180864, 30.92213, 'k1043', 2),
    (19, 252, 'G004242003002520010', '荆门西—荆门南1',
     '荆门西', '荆宜分中心', 112.13812, 30.911968, 'k1047', 2),
    (18, 272, 'G004242003002720010', '淯溪-荆门西1', '荆门西',
     '荆宜分中心', 112.116491, 30.906371, 'k1049', 2),
    (17, 282, 'G004242003002820010', '当阳东-淯溪1',
     '育溪', '荆宜分中心', 111.9221, 30.81368, 'k1070', 2),
    (16, 292, 'G004242003002920010', '当阳西-当阳东1', '当阳东',
     '荆宜分中心', 111.833292, 30.775778, 'k1081', 2),
    (15, 302, 'G004242003003020010', '保宜荆宜交界-当阳西1',
     '当阳西', '荆宜分中心', 111.728802, 30.760547, 'k1091', 2),
    (14, 312, 'G004242003003120010', '双莲-保宜荆宜交界1',
     '双莲', '荆宜分中心', 111.636806, 30.748879, 'k1100', 2),
    (13, 322, 'G004242003003220010', '宜巴起点-双莲1',
     '双莲', '荆宜分中心', 111.61552, 30.746076, 'k1102', 2),
    (12, 332, 'G004242003003320010', '鸦鹊岭-宜巴起点1',
     '鸦鹊岭', '荆宜分中心', 111.532779, 30.706233, 'k4', 2),
    (11, 342, 'G004242003003420010', '荆宜汉宜交界-鸦鹊岭1',
     '鸦鹊岭', '荆宜分中心', 111.51833, 30.69206, 'k6', 2)
]

# Mapping from file name to gantry unique code
GANTRY_MAPPING = {
    '4_281': 281,
    '5_291': 291,
    '6_301': 301,
    '7_311': 311,
    '8_321': 321,
    '13_322': 322,
    '14_312': 312,
    '15_302': 302,
    '16_292': 292,
    '17_282': 282
}


def create_database_connection():
    """Create and return a database connection."""
    print("Connecting to database...")
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        print("Database connection established successfully.")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


def insert_gantry_data(conn):
    """Insert gantry data into the database."""
    cursor = conn.cursor()

    try:
        print(f"Inserting {len(GANTRY_DATA)} gantry records...")
        for i, gantry in enumerate(tqdm.tqdm(GANTRY_DATA, desc="Inserting gantry data")):
            cursor.execute(
                """
                INSERT INTO gantry 
                (sequence_number, unique_number, gantry_code, gantry_name, toll_station, 
                subcenter, longitude, latitude, stake_number, direction)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (gantry_code) DO NOTHING
                """,
                gantry
            )
        conn.commit()
        print("✅ Gantry data inserted successfully.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting gantry data: {e}")
    finally:
        cursor.close()


def get_gantry_id_by_unique_number(conn, unique_number):
    """Get gantry ID from unique number."""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT gantry_id FROM gantry WHERE unique_number = %s",
            (unique_number,)
        )
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        cursor.close()


def count_lines_in_file(file_path):
    """Count the number of lines in a file for progress tracking."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return sum(1 for _ in file)


def process_vehicle_data_file(conn, file_path, unique_number):
    """Process and import vehicle passage data from a file."""
    cursor = conn.cursor()

    try:
        # Get gantry_id from the unique_number
        gantry_id = get_gantry_id_by_unique_number(conn, unique_number)
        if not gantry_id:
            print(f"❌ No gantry found with unique number {unique_number}")
            return

        # Count total lines for progress tracking
        total_lines = count_lines_in_file(file_path)
        print(
            f"Processing file: {os.path.basename(file_path)} ({total_lines} records)")

        # Read the file
        data = []
        batch_size = 10000  # Adjust batch size based on your system's memory
        current_batch = []

        with open(file_path, 'r', encoding='utf-8') as file:
            # Setup progress bar
            pbar = tqdm.tqdm(total=total_lines,
                             desc=f"Processing {os.path.basename(file_path)}")

            # Skip header if present (0,1,2)
            first_line = file.readline().strip()
            pbar.update(1)

            if first_line == "0,1,2":
                pass  # Skip the header
            else:
                # If not a header, reprocess the first line
                parts = first_line.split(',')
                if len(parts) >= 3:
                    gantry_num, timestamp, plate_info = parts[0], parts[1], parts[2]
                    vehicle_type = 0
                    plate = plate_info

                    # Extract vehicle type if available
                    if '_' in plate_info:
                        plate, vehicle_type = plate_info.split('_')
                        try:
                            vehicle_type = int(vehicle_type)
                        except ValueError:
                            vehicle_type = 0

                    current_batch.append(
                        (gantry_id, timestamp, plate, vehicle_type))

            # Process remaining lines
            for line in file:
                pbar.update(1)
                parts = line.strip().split(',')
                if len(parts) >= 3:
                    gantry_num, timestamp, plate_info = parts[0], parts[1], parts[2]
                    vehicle_type = 0
                    plate = plate_info

                    # Extract vehicle type if available
                    if '_' in plate_info:
                        plate, vehicle_type = plate_info.split('_')
                        try:
                            vehicle_type = int(vehicle_type)
                        except ValueError:
                            vehicle_type = 0

                    current_batch.append(
                        (gantry_id, timestamp, plate, vehicle_type))

                # Process in batches to avoid memory issues
                if len(current_batch) >= batch_size:
                    data.extend(current_batch)
                    current_batch = []

            # Add remaining records
            if current_batch:
                data.extend(current_batch)

            pbar.close()

        # Bulk insert data
        if data:
            print(f"Inserting {len(data)} records to database...")
            insert_pbar = tqdm.tqdm(
                total=len(data), desc="Inserting to database")

            # Process in chunks to avoid PostgreSQL parameter limit
            chunk_size = 1000
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i+chunk_size]
                args_str = ','.join(cursor.mogrify(
                    "(%s,%s,%s,%s)", x).decode('utf-8') for x in chunk)
                cursor.execute(
                    f"INSERT INTO vehicle_passage (gantry_id, passage_time, vehicle_plate, vehicle_type) VALUES {args_str}"
                )
                conn.commit()
                insert_pbar.update(len(chunk))

            insert_pbar.close()
            print(
                f"✅ Imported {len(data)} records from {os.path.basename(file_path)}")
        else:
            print(f"⚠️ No data found in {file_path}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error processing file {file_path}: {e}")
    finally:
        cursor.close()


def main():
    """Main function to import all gantry data."""
    start_time = time.time()
    print("Starting data import process...")

    conn = create_database_connection()
    if not conn:
        return

    try:
        # Insert gantry data
        # insert_gantry_data(conn)

        # Process vehicle passage data
        data_dir = r'c:\Users\29230\Code\Python\traffic-backend\0门架数据'

        # Get the list of files to process
        data_files = [f for f in os.listdir(data_dir) if f.endswith('.txt')]
        print(f"Found {len(data_files)} data files to process.")

        for i, filename in enumerate(data_files):
            print(f"\n[{i+1}/{len(data_files)}] Processing file: {filename}")
            file_base = filename.split('.')[0]  # Remove extension
            if file_base in GANTRY_MAPPING:
                unique_number = GANTRY_MAPPING[file_base]
                file_path = os.path.join(data_dir, filename)
                process_vehicle_data_file(conn, file_path, unique_number)
            else:
                print(f"⚠️ Unknown file format: {filename}")

        elapsed_time = time.time() - start_time
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)

        print(f"\n✅ Data import completed successfully.")
        print(
            f"Total execution time: {int(hours):02}:{int(minutes):02}:{int(seconds):02}")
    finally:
        conn.close()
        print("Database connection closed.")


if __name__ == "__main__":
    main()
