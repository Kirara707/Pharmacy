import psycopg2
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        port="8888",
        database="pharmacy",
        user="pharm_user",
        password="Pharm_pass123!"
    )

def init_database():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 清空现有数据
        cur.execute("DELETE FROM sales_records")
        cur.execute("DELETE FROM medicines")
        cur.execute("DELETE FROM users")
        
        # 创建管理员账号
        admin_password = generate_password_hash('admin123')
        cur.execute("""
            INSERT INTO users (username, password_hash, role)
            VALUES (%s, %s, %s)
        """, ('admin', admin_password, 'admin'))
        
        # 创建示例药品
        medicines = [
            ('阿莫西林胶囊', '0.25g*24粒/盒', '哈药集团制药总厂', 15.8, 100),
            ('布洛芬片', '0.2g*24片/盒', '上海信谊药厂', 12.5, 150),
            ('感冒灵颗粒', '10g*10袋/盒', '白云山制药', 25.0, 80),
            ('维生素C片', '0.1g*100片/瓶', '北京同仁堂', 18.5, 200),
            ('板蓝根颗粒', '10g*20袋/盒', '广州白云山', 22.0, 120),
            ('创可贴', '100片/盒', '云南白药', 15.0, 300),
            ('红霉素软膏', '10g/支', '上海信谊药厂', 8.5, 150),
            ('藿香正气水', '10ml*10支/盒', '北京同仁堂', 16.8, 100),
            ('复方丹参片', '0.32g*36片/盒', '广州白云山', 28.5, 80),
            ('金银花露', '10ml*10支/盒', '哈药集团', 12.0, 200)
        ]
        
        for medicine in medicines:
            cur.execute("""
                INSERT INTO medicines (name, specification, manufacturer, price, stock)
                VALUES (%s, %s, %s, %s, %s)
            """, medicine)
        
        # 创建一些示例销售记录
        admin_id = 1  # 假设管理员ID为1
        for i in range(20):  # 创建20条销售记录
            medicine_id = random.randint(1, len(medicines))
            quantity = random.randint(1, 5)
            price = medicines[medicine_id-1][3]
            total_price = price * quantity
            created_at = datetime.now() - timedelta(days=random.randint(0, 30))
            
            cur.execute("""
                INSERT INTO sales_records (medicine_id, salesperson_id, quantity, total_price, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (medicine_id, admin_id, quantity, total_price, created_at))
            
            # 更新药品库存
            cur.execute("""
                UPDATE medicines 
                SET stock = stock - %s 
                WHERE id = %s
            """, (quantity, medicine_id))
        
        conn.commit()
        print("数据库初始化成功！")
        
    except Exception as e:
        conn.rollback()
        print(f"数据库初始化失败: {str(e)}")
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    init_database() 