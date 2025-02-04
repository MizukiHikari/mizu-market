from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from datetime import datetime, UTC
from sqlalchemy import func

# Inisiasi Flask dan konfigurasi
app = Flask(__name__)  # Membuat instance aplikasi
app.secret_key = os.urandom(24)  # Mengatur kunci rahasia
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'  # Menentukan URI database
db = SQLAlchemy(app)  # Menginisialisasi SQLAlchemy

def format_price(price):  # Fungsi untuk memformat harga
    return f"IDR {price:,.0f}".replace(',', '.')  # Format harga dalam IDR

# Model untuk produk
class Product(db.Model):  # Mendefinisikan model produk
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    category = db.Column(db.String(50), nullable=False)  # Kategori produk
    name = db.Column(db.String(50), nullable=False)  # Nama produk
    price = db.Column(db.Integer, nullable=False)  # Harga produk
    stock = db.Column(db.Integer, nullable=False)  # Stok produk
    image_path = db.Column(db.String(255), nullable=False)  # Path gambar produk

# Model untuk Keranjang Belanja
class CartItem(db.Model):  # Model item keranjang
    id = db.Column(db.Integer, primary_key=True)  # ID unik
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)  # Referensi ke produk
    quantity = db.Column(db.Integer, nullable=False)  # Jumlah produk
    total_price = db.Column(db.Integer, nullable=False)  # Total harga
    product = db.relationship('Product', backref='cart_items')  # Relasi ke model Product

class Transaction(db.Model):  # Model transaksi
    id = db.Column(db.Integer, primary_key=True)  # ID unik
    buyer_name = db.Column(db.String(100), nullable=False)  # Nama pembeli
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)  # ID produk dibeli
    quantity = db.Column(db.Integer, nullable=False)  # Jumlah produk dibeli
    total_price = db.Column(db.Integer, nullable=False)  # Total harga transaksi
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))  # Waktu transaksi
    product = db.relationship('Product', backref='transactions')  # Relasi ke model Product

    def __init__(self, buyer_name, product_id, quantity, total_price, timestamp=None):  # Konstruktor
        self.buyer_name = buyer_name  # Nama pembeli
        self.product_id = product_id  # ID produk
        self.quantity = quantity  # Jumlah produk
        self.total_price = total_price  # Total harga
        self.timestamp = timestamp  # Waktu transaksi

# Route untuk menambah produk
@app.route('/add_product', methods=['POST'])  # Endpoint untuk menambah produk
def add_product():
    # Mengambil data dari form untuk kategori, nama, harga, dan stok produk
    category = request.form.get('category')
    name = request.form.get('name')
    price = int(request.form.get('price'))
    stock = int(request.form.get('stock'))

    # Cek apakah file gambar diunggah
    image = request.files['image']  # Mengambil file gambar
    if image and image.filename != '':
        # Amankan nama file dan simpan ke direktori lokal
        filename = secure_filename(image.filename)  # Mengamankan nama file
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Menyimpan file gambar
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Mendapatkan path gambar
    else:
        image_path = None  # Jika tidak ada gambar diunggah

    # Simpan produk baru beserta path gambar
    new_product = Product(category=category, name=name, price=price, stock=stock, image_path=image_path)  # Membuat produk baru
    db.session.add(new_product)  # Menambahkan produk ke sesi
    db.session.commit()  # Menyimpan perubahan ke database

    return redirect(url_for('inventory'))  # Mengalihkan ke halaman inventaris

# Route untuk mendapatkan data produk untuk modal edit
@app.route('/get_product/<int:product_id>', methods=['GET'])  # Endpoint untuk mendapatkan data produk berdasarkan ID
def get_product(product_id):
    product = Product.query.get(product_id)  # Mengambil produk dari database
    if product:
        return jsonify({'id': product.id, 'category': product.category, 'name': product.name, 'price': product.price, 'stock': product.stock})  # Mengembalikan data produk sebagai JSON
    return jsonify({'error': 'Product not found'}), 404  # Mengembalikan error jika produk tidak ditemukan

# Route untuk mengedit produk
@app.route('/edit_product/<int:product_id>', methods=['POST'])  # Endpoint untuk mengedit produk berdasarkan ID
def edit_product(product_id):
    product = Product.query.get(product_id)  # Mengambil produk dari database
    if product:
        # Mengambil data input untuk kategori, nama, harga, dan stok
        category = request.form.get('category')
        name = request.form.get('name')
        price = request.form.get('price')
        stock = request.form.get('stock')

        # Validasi input harga dan stok
        if price.isdigit() and stock.isdigit():
            try:
                # Memperbarui detail produk
                product.category = category
                product.name = name
                product.price = int(price)  # Mengonversi harga ke integer
                product.stock = int(stock)  # Mengonversi stok ke integer
                db.session.commit()  # Menyimpan perubahan ke database
                
                # Mengembalikan data produk yang diperbarui sebagai JSON
                return jsonify({
                    'id': product.id,
                    'category': product.category,
                    'name': product.name,
                    'price': product.price,
                    'stock': product.stock
                })
            except Exception as e:
                db.session.rollback()  # Mengembalikan perubahan jika terjadi error
                return jsonify({'error': str(e)}), 500  # Mengembalikan error 500 jika terjadi kesalahan
        else:
            return jsonify({'error': 'Invalid input'}), 400  # Mengembalikan error 400 untuk input tidak valid

    # Mengembalikan error jika produk tidak ditemukan
    return jsonify({'error': 'Product not found'}), 404  

# Route untuk menghapus produk
@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    product = Product.query.get(product_id)  # Mencari produk berdasarkan ID
    if product:
        db.session.delete(product)  # Menghapus produk
        db.session.commit()  # Menyimpan perubahan
    return redirect(url_for('inventory'))  # Kembali ke halaman inventaris

# Route untuk mencatat penjualan
@app.route('/shop')
def shop():
    categories = db.session.query(Product.category).distinct().all()  # Mengambil kategori unik
    products = Product.query.all()  # Mengambil semua produk
    cart_items = CartItem.query.all()  # Mengambil item keranjang
    total = sum(item.product.price * item.quantity for item in cart_items) if cart_items else 0  # Menghitung total harga
    total_items = sum(item.quantity for item in cart_items) if cart_items else 0  # Menghitung total jumlah item
    return render_template('shop.html', products=products, cart_items=cart_items, total=total, total_items=total_items, format_price=format_price, categories=categories)  # Mengirim data ke template

# Route untuk menambahkan item ke keranjang
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))  # Mengambil jumlah dari formulir
    product = Product.query.get(product_id)  # Ambil produk dari database
    if not product:
        return "Product not found", 404  # Jika produk tidak ditemukan

    cart_item = CartItem.query.filter_by(product_id=product_id).first()  # Mengecek apakah item sudah ada di keranjang
    
    if cart_item:
        cart_item.quantity += quantity  # Tambah jumlah jika ada
        cart_item.total_price = cart_item.quantity * product.price  # Perbarui total_price
    else:
        total_price = product.price * quantity  # Hitung total_price
        new_cart_item = CartItem(product_id=product_id, quantity=quantity, total_price=total_price)  # Buat item baru
        db.session.add(new_cart_item)  # Tambahkan item baru ke sesi
    
    db.session.commit()  # Menyimpan perubahan ke database
    return redirect(url_for('shop'))  # Kembali ke halaman shop

# Route untuk menghapus item dari keranjang
@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    cart_item = CartItem.query.get(item_id)  # Mencari item keranjang berdasarkan ID
    if cart_item:
        db.session.delete(cart_item)  # Menghapus item dari sesi
        db.session.commit()  # Menyimpan perubahan ke database
    return redirect(url_for('shop'))  # Kembali ke halaman shop

# Route untuk checkout
@app.route('/checkout', methods=['POST'])
def checkout():
    buyer_name = request.form.get('buyer_name')  # Mengambil nama pembeli
    cart_items = CartItem.query.all()  # Mengambil semua item dari keranjang
    total_amount = 0  # Inisialisasi total pembayaran

    for item in cart_items:
        product = Product.query.get(item.product_id)  # Ambil produk berdasarkan ID
        if product:
            product.stock -= item.quantity  # Kurangi stok produk
            total_amount += item.product.price * item.quantity  # Hitung total harga

    db.session.commit()  # Simpan perubahan stok produk

    # Membuat catatan transaksi
    for item in cart_items:
        transaction = Transaction(
            buyer_name=buyer_name,
            product_id=item.product_id,
            quantity=item.quantity,
            total_price=item.product.price * item.quantity,
            timestamp=datetime.now()  # Waktu transaksi
        )
        db.session.add(transaction)  # Tambahkan transaksi ke sesi

    # Mengosongkan keranjang setelah checkout
    for item in cart_items:
        db.session.delete(item)  # Hapus item dari keranjang
    db.session.commit()  # Simpan perubahan ke database

    flash(f'Transaksi berhasil untuk {buyer_name}. Total Amount: {f"IDR {total_amount:,.0f}".replace(",", ".")}', 'success')  # Pesan sukses
    return redirect(url_for('shop'))  # Kembali ke halaman shop

# Route untuk menghapus transaksi
@app.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)  # Mencari transaksi berdasarkan ID
    if transaction:
        db.session.delete(transaction)  # Hapus transaksi
        db.session.commit()  # Simpan perubahan
        flash('Transaction successfully deleted', 'success')
    else:
        flash('Transaction not found', 'error')
    return redirect(url_for('transaction_history'))  # Kembali ke halaman histori transaksi

# Route untuk melihat detail transaksi
@app.route('/view_transaction/<int:transaction_id>')
def view_transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)  # Mencari transaksi
    buyer_name = transaction.buyer_name
    timestamp = transaction.timestamp

    # Menghapus detik dan mikrodetik dari timestamp
    truncated_timestamp = timestamp.replace(second=0, microsecond=0)

    # Mengambil semua transaksi untuk pembeli dan timestamp yang sama
    transactions = Transaction.query.filter_by(buyer_name=buyer_name).filter(func.strftime('%Y-%m-%d %H:%M', Transaction.timestamp) == truncated_timestamp.strftime('%Y-%m-%d %H:%M')).all()

    # Menyimpan data transaksi dalam dictionary
    data = {
        'buyer_name': buyer_name,
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'transactions': []
    }

    # Menambahkan detail setiap transaksi ke dalam dictionary
    for t in transactions:
        product = t.product
        data['transactions'].append({
            'product_name': product.name,
            'product_image': product.image_path,  # Menambahkan gambar produk
            'quantity': t.quantity,
            'total_price': t.total_price
        })

    return jsonify(data)  # Mengembalikan data transaksi dalam format JSON

# Route untuk halaman utama (dashboard)
@app.route('/')
def index():
    return render_template('index.html')  # Mengembalikan template index

# Route untuk halaman penyimpanan (inventory)
@app.route('/inventory')
def inventory():
    products = Product.query.all()  # Mengambil semua produk
    return render_template('inventory.html', products=products)  # Mengembalikan template inventory

# Route untuk halaman histori transaksi
@app.route('/history')
def transaction_history():
    transactions = Transaction.query.all()  # Mengambil semua transaksi
    return render_template('history.html', transactions=transactions)  # Mengembalikan template history

# Menentukan folder penyimpanan gambar
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Mengonfigurasi folder upload

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Membuat tabel jika belum ada
    app.run(host='0.0.0.0', port=6969, debug=True)  # Menjalankan server