from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from functools import wraps
from models import db, User, Medicine, SalesRecord
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8080", "http://localhost:8082", "http://localhost:8084", "http://localhost:8085"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# 配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://pharm_user:Pharm_pass123!@localhost:8888/pharmacy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # 在生产环境中应该使用环境变量
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# 初始化扩展
db.init_app(app)
jwt = JWTManager(app)

def get_db_connection():
    return psycopg2.connect(
        dbname="pharmacy",
        user="pharm_user",
        password="Pharm_pass123!",
        host="localhost",
        port="8888"
    )

# 创建数据库表
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 创建用户表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password_hash VARCHAR(120) NOT NULL,
            role VARCHAR(20) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建药品表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description VARCHAR(100) NOT NULL,
            price NUMERIC(10,2) NOT NULL,
            stock INTEGER NOT NULL,
            manufacturer VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建销售记录表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales_records (
            id SERIAL PRIMARY KEY,
            medicine_id INTEGER REFERENCES medicines(id),
            salesperson_id INTEGER REFERENCES users(id),
            quantity INTEGER NOT NULL,
            total_price NUMERIC(10,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()

# 初始化管理员用户
def init_admin():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 更新管理员密码
    password_hash = generate_password_hash('admin123')
    cur.execute(
        "UPDATE users SET password_hash = %s WHERE username = 'admin'",
        (password_hash,)
    )
    conn.commit()
    print('管理员密码已重置！')
    
    cur.close()
    conn.close()

# 初始化数据库和管理员
with app.app_context():
    init_db()
    init_admin()

# 根路由
@app.route('/')
def index():
    return jsonify({
        'message': '药店管理系统API服务',
        'version': '1.0.0',
        'status': 'running'
    })

# 健康检查接口
@app.route('/health')
def health_check():
    try:
        # 检查数据库连接
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.fetchone()
        cur.close()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# 权限检查装饰器
def role_required(roles):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT role FROM users WHERE id = %s", (user_id,))
            user = cur.fetchone()
            cur.close()
            conn.close()
            
            if not user or user[0] not in roles:
                return jsonify({'message': '权限不足'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 用户认证
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': '请提供用户名和密码'}), 400
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, username, password_hash, role FROM users WHERE username = %s", (data.get('username'),))
        user = cur.fetchone()
        if not user:
            return jsonify({'message': '用户不存在'}), 401
        if not check_password_hash(user[2], data.get('password')):
            return jsonify({'message': '密码错误'}), 401
        access_token = create_access_token(identity=str(user[0]))
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user[0],
                'username': user[1],
                'role': user[3]
            }
        })
    except Exception as e:
        return jsonify({'message': f'登录失败: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

# 药品管理
@app.route('/api/medicines', methods=['GET'])
@jwt_required()
def get_medicines():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, description, price, stock, manufacturer, created_at, updated_at 
            FROM medicines 
            ORDER BY created_at DESC
        """)
        medicines = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify([{
            'id': m[0],
            'name': m[1],
            'description': str(m[2]) if m[2] is not None else '',
            'price': float(m[3]) if m[3] is not None else 0.0,
            'stock': m[4],
            'manufacturer': m[5],
            'created_at': m[6].isoformat() if m[6] else None,
            'updated_at': m[7].isoformat() if m[7] else None
        } for m in medicines])
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'message': f'获取药品列表失败: {str(e)}'}), 500

@app.route('/api/medicines', methods=['POST'])
@role_required(['admin'])
def add_medicine():
    data = request.get_json()
    if not data or not all(key in data for key in ['name', 'description', 'price', 'stock', 'manufacturer']):
        return jsonify({'message': '请提供完整的药品信息'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO medicines (name, description, price, stock, manufacturer)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data['name'],
            data['description'],
            data['price'],
            data['stock'],
            data['manufacturer']
        ))
        medicine_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({'message': '添加成功', 'id': medicine_id})
    except Exception as e:
        conn.rollback()
        return jsonify({'message': f'添加药品失败: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/medicines/<int:medicine_id>', methods=['PUT'])
@role_required(['admin'])
def update_medicine(medicine_id):
    data = request.get_json()
    if not data or not all(key in data for key in ['name', 'description', 'price', 'stock', 'manufacturer']):
        return jsonify({'message': '请提供完整的药品信息'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE medicines 
            SET name=%s, description=%s, price=%s, stock=%s, manufacturer=%s, updated_at=%s
            WHERE id=%s
        """, (
            data['name'],
            data['description'],
            data['price'],
            data['stock'],
            data['manufacturer'],
            datetime.now(),
            medicine_id
        ))
        if cur.rowcount == 0:
            return jsonify({'message': '药品不存在'}), 404
        conn.commit()
        return jsonify({'message': '药品信息已更新'})
    except Exception as e:
        conn.rollback()
        return jsonify({'message': f'更新药品失败: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/medicines/<int:medicine_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_medicine(medicine_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # 检查是否有相关的销售记录
        cur.execute("SELECT COUNT(*) FROM sales_records WHERE medicine_id = %s", (medicine_id,))
        sales_count = cur.fetchone()[0]
        
        if sales_count > 0:
            return jsonify({'message': f'无法删除该药品，存在 {sales_count} 条相关销售记录'}), 400
        
        # 删除药品
        cur.execute("DELETE FROM medicines WHERE id = %s", (medicine_id,))
        if cur.rowcount == 0:
            return jsonify({'message': '药品不存在'}), 404
        
        conn.commit()
        return jsonify({'message': '药品删除成功'})
    except Exception as e:
        conn.rollback()
        import traceback
        print(traceback.format_exc())
        return jsonify({'message': f'删除药品失败: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

# 销售记录
@app.route('/api/sales', methods=['POST'])
@jwt_required()
def create_sale():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    # 检查药品库存
    cur.execute("SELECT price, stock FROM medicines WHERE id = %s", (data['medicine_id'],))
    medicine = cur.fetchone()
    if not medicine or medicine[1] < data['quantity']:
        cur.close()
        conn.close()
        return jsonify({'message': '库存不足'}), 400
    # 创建销售记录
    total_price = medicine[0] * data['quantity']
    cur.execute("""
        INSERT INTO sales_records (medicine_id, salesperson_id, quantity, total_price, created_at)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (
        data['medicine_id'],
        int(get_jwt_identity()),
        data['quantity'],
        total_price,
        datetime.now()
    ))
    sale_id = cur.fetchone()[0]
    # 更新库存
    cur.execute("""
        UPDATE medicines 
        SET stock = stock - %s 
        WHERE id = %s
    """, (data['quantity'], data['medicine_id']))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': '销售成功', 'id': sale_id})

@app.route('/api/sales', methods=['GET'])
@jwt_required()
def get_sales():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT s.id, s.medicine_id, m.name, s.quantity, s.total_price, s.created_at, u.username
            FROM sales_records s
            JOIN medicines m ON s.medicine_id = m.id
            LEFT JOIN users u ON s.salesperson_id = u.id
            ORDER BY s.created_at DESC
        """)
        sales = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify([{
            'id': s[0],
            'medicine_id': s[1],
            'medicine_name': s[2],
            'quantity': s[3],
            'total_price': float(s[4]),
            'created_at': s[5].isoformat() if s[5] else None,
            'salesperson': s[6]
        } for s in sales])
    except Exception as e:
        return jsonify({'message': f'获取销售记录失败: {str(e)}'}), 500

@app.route('/api/sales/<int:sale_id>', methods=['DELETE'])
@jwt_required()
@role_required(['admin'])
def delete_sale(sale_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # 获取销售记录信息以便恢复库存
        cur.execute("""
            SELECT medicine_id, quantity 
            FROM sales_records 
            WHERE id = %s
        """, (sale_id,))
        sale = cur.fetchone()
        
        if not sale:
            return jsonify({'message': '销售记录不存在'}), 404
        
        medicine_id, quantity = sale
        
        # 删除销售记录
        cur.execute("DELETE FROM sales_records WHERE id = %s", (sale_id,))
        
        # 恢复药品库存
        cur.execute("""
            UPDATE medicines 
            SET stock = stock + %s 
            WHERE id = %s
        """, (quantity, medicine_id))
        
        conn.commit()
        return jsonify({'message': '销售记录删除成功，库存已恢复'})
    except Exception as e:
        conn.rollback()
        import traceback
        print(traceback.format_exc())
        return jsonify({'message': f'删除销售记录失败: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

# 用户管理
@app.route('/api/users', methods=['GET'])
@jwt_required()
@role_required(['admin', 'pharmacy_admin'])
def get_users():
    try:
        print("get_users called, user:", get_jwt_identity())
        user_id = int(get_jwt_identity())
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, username, role, created_at 
            FROM users 
            ORDER BY created_at DESC
        """)
        users = cur.fetchall()
        cur.close()
        conn.close()
        print("users fetched:", users)
        return jsonify([{
            'id': u[0],
            'username': u[1],
            'role': u[2],
            'created_at': u[3].isoformat() if u[3] else None
        } for u in users])
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'message': f'获取用户列表失败: {str(e)}'}), 500

@app.route('/api/users', methods=['POST'])
@jwt_required()
@role_required(['admin'])
def add_user():
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password') or not data.get('role'):
            return jsonify({'message': '请提供完整的用户信息'}), 400
        conn = get_db_connection()
        cur = conn.cursor()
        # 检查用户名是否已存在
        cur.execute("SELECT id FROM users WHERE username = %s", (data['username'],))
        if cur.fetchone():
            return jsonify({'message': '用户名已存在'}), 400
        # 创建新用户
        password_hash = generate_password_hash(data['password'])
        cur.execute("""
            INSERT INTO users (username, password_hash, role, created_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (data['username'], password_hash, data['role'], datetime.now()))
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': '用户创建成功', 'id': user_id})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'message': f'创建用户失败: {str(e)}'}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@role_required(['admin'])
def delete_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # 检查是否为当前登录用户
        current_user_id = int(get_jwt_identity())
        if user_id == current_user_id:
            return jsonify({'message': '不能删除当前登录的用户'}), 400
        
        # 检查用户是否存在
        cur.execute("SELECT username, role FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        # 检查是否有相关的销售记录
        cur.execute("SELECT COUNT(*) FROM sales_records WHERE salesperson_id = %s", (user_id,))
        sales_count = cur.fetchone()[0]
        
        if sales_count > 0:
            return jsonify({'message': f'无法删除该用户，存在 {sales_count} 条相关销售记录'}), 400
        
        # 删除用户
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        return jsonify({'message': f'用户 {user[0]} 删除成功'})
    except Exception as e:
        conn.rollback()
        import traceback
        print(traceback.format_exc())
        return jsonify({'message': f'删除用户失败: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True) 