from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import hashlib
import os
from base64 import b64encode, b64decode
from jose import JWTError, jwt
from datetime import datetime, timedelta

# 👆 YUKARIDAKİ İMPORTLARIN ANLAMI:
# Bu kısım projenin "Alet Çantası"dır.
# FastAPI: Web sunucusunu kurar.
# SQLAlchemy: Veritabanı ile konuşur (SQL komutları yerine Python kullanmamızı sağlar).
# Pydantic: Veri doğrulama yapar (Gelen veri sayı mı, yazı mı?).
# Jose & Passlib (hashlib): Şifreleme ve Token (Giriş Kartı) işlemleri içindir.

# ===========================
# 1. AYARLAR
# ===========================
SQLALCHEMY_DATABASE_URL = "sqlite:///./genel_veri.db"
# 👆 Veritabanı dosyasının adını ve yerini belirledik.

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
# 👆 Veritabanı motorunu çalıştırdık. "check_same_thread=False" SQLite için gereklidir.

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 👆 Her veritabanı işlemi (ekle/sil) için geçici bir "Oturum" (Session) açacak yapıyı kurduk.

Base = declarative_base()
# 👆 Veritabanı tablolarımızı oluştururken kullanacağımız temel sınıf.

SECRET_KEY = "cok-gizli-ve-uzun-rastgele-bir-yazi-buraya-yazin"
# 👆 EN KRİTİK AYAR: Bu, sunucunun "Dijital İmzası"dır. Token'ları bununla mühürleriz.

ALGORITHM = "HS256"
# 👆 Şifreleme algoritmasının adı.

ACCESS_TOKEN_EXPIRE_MINUTES = 30
# 👆 Bir kullanıcı giriş yaptıktan sonra Token'ı (Oda Kartı) kaç dakika geçerli olsun? (30 dk)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# 👆 FastAPI'ye diyoruz ki: "Güvenlik için OAuth2 kullanacağız ve giriş yapma adresi '/token' olacak."

# ===========================
# 2. VERİTABANI MODELLERİ (Tablo Tasarımları)
# ===========================
class UserDB(Base):
    __tablename__ = "users"
    # 👆 Tablonun adı veritabanında "users" olacak.

    id = Column(Integer, primary_key=True, index=True)
    # 👆 Her kullanıcının benzersiz bir numarası (ID) olacak.
    
    username = Column(String, unique=True, index=True)
    # 👆 Kullanıcı adı (String) olacak ve eşsiz (unique) olacak. İki kişi aynı adı alamaz.
    
    hashed_password = Column(String)
    # 👆 Şifreler "1234" diye değil, şifrelenmiş karmaşık kodlar olarak saklanacak.
    
    items = relationship("ItemDB", back_populates="owner")
    # 👆 İLİŞKİ: Bu kullanıcının birden fazla ürünü olabilir. Onlara "items" diyerek ulaşacağız.

class ItemDB(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Integer)
    category = Column(String, default="Genel") 
    # 👆 YENİ SÜTUN: Ürünün kategorisi (Elektronik, Giyim vb.). Boş bırakılırsa "Genel" yazar.

    owner_id = Column(Integer, ForeignKey("users.id"))
    # 👆 SAHİPLİK: Bu ürün kime ait? "users" tablosundaki "id"ye bir kanca (ForeignKey) atıyoruz.
    
    owner = relationship("UserDB", back_populates="items")
    # 👆 İLİŞKİ: Bu ürünün sahibine "owner" diyerek ulaşabiliriz.

Base.metadata.create_all(bind=engine)
# 👆 SİHİRLİ KOMUT: Yukarıda tasarladığımız tabloları (UserDB, ItemDB) veritabanında gerçekten oluşturur.

# ===========================
# 3. PYDANTIC MODELLERİ (Veri Kontrol Şemaları)
# ===========================
# Bu sınıflar veritabanı için değil, Frontend'den gelen veriyi kontrol etmek içindir.

class UserCreate(BaseModel):
    username: str
    password: str
    # 👆 Kayıt olurken sadece kullanıcı adı ve şifre istenir.

class UserOut(BaseModel):
    id: int
    username: str
    class Config:
        orm_mode = True
    # 👆 Kullanıcıya yanıt verirken ID ve İsim döneriz ama ŞİFREYİ GİZLERİZ (password alanı yok).

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    # 👆 Giriş başarılı olunca kullanıcıya dönecek olan "Dijital Kimlik Kartı" formatı.

class ItemCreate(BaseModel):
    name: str
    price: int
    category: str 
    # 👆 Ürün eklerken Frontend'den bu 3 bilginin gelmesi zorunludur.

class ItemOut(BaseModel):
    id: int
    name: str
    price: int
    category: str
    class Config:
        orm_mode = True
    # 👆 Ürün listesini gösterirken bu formatta veri göndeririz.

# ===========================
# 4. YARDIMCI FONKSİYONLAR (Arka Plan İşçileri)
# ===========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    # 👆 Bu fonksiyon, her istek geldiğinde veritabanı bağlantısını açar, iş bitince kapatır.

def get_password_hash(password: str) -> str:
    salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return b64encode(salt + pwd_hash).decode('ascii')
    # 👆 ŞİFRELEME: Kullanıcının girdiği "123456" şifresini alır, tuzlayıp karıştırır ve "karmaşık bir kod" haline getirir.

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        decoded = b64decode(hashed_password.encode('ascii'))
        salt = decoded[:16]
        stored_hash = decoded[16:]
        new_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000)
        return new_hash == stored_hash
    except Exception:
        return False
    # 👆 ŞİFRE KONTROL: Giriş yaparken girilen şifre ile veritabanındaki şifreli hali eşleşiyor mu diye bakar.

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
    # 👆 KART BASIM: Kullanıcı adı ve son kullanma tarihini alır, SECRET_KEY ile imzalayıp Token oluşturur.

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulama başarısız",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if user is None:
        raise credentials_exception
    return user
    # 👆 BODYGUARD (En Önemli Kod): 
    # 1. Gelen Token'ı kontrol eder.
    # 2. Sahte mi, süresi dolmuş mu bakar.
    # 3. Geçerliyse, bu Token'ın sahibi olan kullanıcıyı bulur ve "current_user" olarak döndürür.

# ===========================
# 5. UYGULAMA VE ENDPOINTLER (Kapılar)
# ===========================
app = FastAPI()
# 👆 Uygulamayı başlatıyoruz.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 👆 GÜMRÜK KAPISI (CORS): Frontend (Vue.js - 5173 portu) ile Backend'in konuşmasına izin veriyoruz.

@app.get("/")
def read_root():
    return {"mesaj": "FastAPI Kategori Sistemi Hazır!", "durum": "aktif"}
    # 👆 Test Kapısı: Tarayıcıdan girince "Hazır" mesajı verir.

@app.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # 1. Kullanıcı adı var mı diye bak.
    db_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Kullanıcı adı zaten alınmış")
    
    # 2. Şifreyi gizle (Hashle).
    hashed_pwd = get_password_hash(user.password)
    
    # 3. Yeni kullanıcıyı oluştur ve kaydet.
    new_user = UserDB(username=user.username, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
    # 👆 KAYIT OLMA İŞLEMİ.

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Kullanıcıyı bul.
    user = db.query(UserDB).filter(UserDB.username == form_data.username).first()
    
    # 2. Şifreyi kontrol et.
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Hatalı giriş")
    
    # 3. Her şey doğruysa Token (Kart) bas ve ver.
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "username": user.username}
    # 👆 GİRİŞ YAPMA İŞLEMİ.

# --- CRUD İŞLEMLERİ (Kullanıcıya Özel) ---

@app.get("/products", response_model=list[ItemOut])
def get_items(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    # 👆 DİKKAT: 'current_user' sayesinde sadece o an giriş yapmış kişinin ürünlerini filtreliyoruz.
    items = db.query(ItemDB).filter(ItemDB.owner_id == current_user.id).all()
    return items
    # 👆 LİSTELEME: Sadece benim ürünlerimi getir.

@app.post("/products", response_model=ItemOut)
def create_item(item: ItemCreate, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    # 👆 EKLEME: Ürünü eklerken 'owner_id' kısmına otomatik olarak giriş yapan kişinin ID'sini yazıyoruz.
    db_item = ItemDB(name=item.name, price=item.price, category=item.category, owner_id=current_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.put("/products/{product_id}", response_model=ItemOut)
def update_product(
    product_id: int,
    product_update: ItemCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    # 1. Ürünü bul (Hem ID tutmalı hem de sahibi sen olmalısın).
    db_product = db.query(ItemDB).filter(ItemDB.id == product_id, ItemDB.owner_id == current_user.id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    
    # 2. Yeni bilgileri üzerine yaz.
    db_product.name = product_update.name
    db_product.price = product_update.price
    db_product.category = product_update.category 
    
    # 3. Kaydet.
    db.commit()
    db.refresh(db_product)
    return db_product
    # 👆 GÜNCELLEME İŞLEMİ.

@app.delete("/products/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    # 1. Silinecek ürünü bul (Başkası senin ürününü silemez).
    item = db.query(ItemDB).filter(ItemDB.id == item_id, ItemDB.owner_id == current_user.id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    
    # 2. Sil.
    db.delete(item)
    db.commit()
    return {"mesaj": "Silindi"}
    # 👆 SİLME İŞLEMİ.