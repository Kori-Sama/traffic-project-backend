import os
import asyncio
import pandas as pd
from datetime import datetime
import sys
import time
from tqdm.asyncio import tqdm

# Add root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db.core import init_db, close_db, get_db

# Maximum concurrent files being processed
MAX_CONCURRENT_FILES = 3
# Semaphore to control concurrency
semaphore = asyncio.Semaphore(MAX_CONCURRENT_FILES)
# Chunk size for processing each file
CHUNK_SIZE = 5000

async def import_single_file(db, file_path, gantry_map, file_index):
    async with semaphore:
        filename = os.path.basename(file_path)
        total_records = 0
        
        try:
            # First, count total lines to initialize tqdm (fast way)
            num_lines = sum(1 for _ in open(file_path)) - 1 # Subtract header
            if num_lines <= 0: return 0
            
            # Sub-progress bar for each file, positioned by file_index
            pbar = tqdm(
                total=num_lines, 
                desc=f"📄 {filename[:20]}", 
                unit="rec", 
                leave=False,
                position=file_index + 1
            )
            
            # Read CSV in chunks using pandas
            chunk_iter = pd.read_csv(file_path, chunksize=CHUNK_SIZE)
            
            for chunk in chunk_iter:
                records = []
                for _, row in chunk.iterrows():
                    code = str(row['门架名称'])
                    gantry_id = gantry_map.get(code)
                    
                    if not gantry_id:
                        continue
                    
                    start_time = pd.to_datetime(row['时间段起始'])
                    end_time = start_time + pd.Timedelta(minutes=5)
                    
                    records.append((
                        gantry_id, 
                        start_time, 
                        end_time, 
                        int(row['流量']), 
                        float(row['平均速度(km/h)']), 
                        int(row['速度匹配样本数'])
                    ))
                
                if records:
                    await db.executemany("""
                        INSERT INTO gantry_traffic_flow (gantry_id, start_time, end_time, traffic_volume, avg_speed, sample_count)
                        VALUES ($1, $2, $3, $4, $5, $6)
                        ON CONFLICT (gantry_id, start_time) DO UPDATE
                        SET traffic_volume = EXCLUDED.traffic_volume,
                            avg_speed = EXCLUDED.avg_speed,
                            sample_count = EXCLUDED.sample_count
                    """, records)
                    
                total_records += len(records)
                pbar.update(len(chunk))
                
            pbar.close()
            # print(f"✅ Finished {filename}")
            return total_records
        except Exception as e:
            # print(f"❌ Error processing {filename}: {e}")
            return 0

async def import_traffic_flow_concurrent():
    db = await get_db()
    data_dir = 'data/处理后5min数据result/'
    if not os.path.exists(data_dir):
        print(f"Directory not found: {data_dir}")
        return

    files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    # Load gantry mapping (code -> id)
    print("Loading gantry mapping...")
    gantry_rows = await db.fetch("SELECT gantry_id, gantry_code FROM gantry")
    gantry_map = {r['gantry_code']: r['gantry_id'] for r in gantry_rows}
    
    print(f"Starting concurrent import of {len(files)} files (Concurrency={MAX_CONCURRENT_FILES})...")
    start_time = time.time()
    
    # Overall progress bar
    main_pbar = tqdm(total=len(files), desc="Overall Progress", position=0)
    
    # Process files. We use file_index to position sub-bars
    tasks = []
    for i, f in enumerate(files):
        async def wrapped_import(f_path, idx):
            res = await import_single_file(db, f_path, gantry_map, idx % MAX_CONCURRENT_FILES)
            main_pbar.update(1)
            return res
        tasks.append(wrapped_import(f, i))
        
    results = await asyncio.gather(*tasks)
    main_pbar.close()
    
    # Move cursor below bars
    print("\n" * (MAX_CONCURRENT_FILES + 1))
    
    total_records = sum(results)
    elapsed = time.time() - start_time
    print(f"🚀 Total records imported: {total_records}")
    print(f"⏱️ Total time: {elapsed:.2f}s ({total_records/max(elapsed, 0.001):.1f} rec/s)")

async def main():
    await init_db()
    try:
        await import_traffic_flow_concurrent()
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())
