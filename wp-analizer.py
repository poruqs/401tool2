import sqlite3
import pandas as pd
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt

class WhatsAppAnalyzer:
    def __init__(self, db_path="msgstore.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        
    def analyze_messages(self):
        df = pd.read_sql_query("""
            SELECT 
                timestamp/1000 as datetime,
                key_remote_jid as contact,
                data as message,
            FROM messages 
            ORDER BY datetime
        """, self.conn)
        df['datetime'] = pd.to_datetime(df['datetime'], unit='s')
        return df

    def visualize_activity(self):
        df = self.analyze_messages()
        plt.figure(figsize=(12,6))
        df.groupby(df['datetime'].dt.hour).count()['message'].plot(kind='bar')
        plt.savefig('activity.png')
        print("📊 Aktivite grafiği oluşturuldu: activity.png")

    def extract_media_metadata(self):
        media_df = pd.read_sql_query("SELECT * FROM message_media", self.conn)
        for _, row in media_df.iterrows():
            try:
                img = Image.open(BytesIO(row['media_data']))
                print(f"📷 {row['message_id']}: {img.size} pixels")
            except:
                continue

# Kullanım:
# analyzer = WhatsAppAnalyzer()
# analyzer.visualize_activity()