"""
MySQL 데이터베이스 연결 관리
"""
import mysql.connector
from mysql.connector import Error
from typing import Optional
import os

class DatabaseConnection:
    """MySQL 데이터베이스 연결 관리 클래스"""
    
    def __init__(self, host: str = "localhost", port: int = 3306, 
                 database: str = "examplesdb", user: str = "root", password: str = "root1234"):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection: Optional[mysql.connector.MySQLConnection] = None
    
    def connect(self) -> bool:
        """데이터베이스에 연결"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                print(f"✅ MySQL 데이터베이스 '{self.database}'에 성공적으로 연결되었습니다!")
                return True
        except Error as e:
            print(f"❌ 데이터베이스 연결 실패: {e}")
            return False
        return False
    
    def disconnect(self):
        """데이터베이스 연결 해제"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔌 데이터베이스 연결이 해제되었습니다.")
    
    def get_connection(self) -> Optional[mysql.connector.MySQLConnection]:
        """연결 객체 반환"""
        return self.connection
    
    def is_connected(self) -> bool:
        """연결 상태 확인"""
        return self.connection and self.connection.is_connected()

# 전역 연결 인스턴스
db_connection = DatabaseConnection()

def get_db_connection() -> DatabaseConnection:
    """전역 데이터베이스 연결 인스턴스 반환"""
    return db_connection
