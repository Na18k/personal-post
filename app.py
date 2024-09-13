import sqlite3
import hashlib
import base64
from datetime import datetime
import os
import json

def load_messages(language='en'):
	"""Carrega mensagens do arquivo JSON com base no idioma selecionado."""
	with open('msg.json', 'r', encoding='utf-8') as file:
		messages = json.load(file)
	return messages.get(language, messages['en'])

# Configurar idioma (pode ser uma escolha do usuário no futuro)
language = 'en'  # ou 'pt', 'es', 'ru', 'zh', 'ja'
messages = load_messages(language)


# Função para limpar a tela
def clear_screen():
	"""Limpa a tela do terminal."""
	if os.name == 'nt':  # Para Windows
		os.system('cls')
	else:  # Para Linux/Unix/MacOS
		os.system('clear')

def encode_content(content):
	"""Codifica o conteúdo do post usando base64."""
	return base64.b64encode(content.encode('utf-8')).decode('utf-8')

def decode_content(encoded_content):
	"""Decodifica o conteúdo do post usando base64."""
	return base64.b64decode(encoded_content.encode('utf-8')).decode('utf-8')

def main():
	"""Função principal para interação com o usuário."""
	clear_screen()
	print(messages['welcome'])

	blog = PersonalPost()

	while True:
		if blog.verify_first_acess():
			choice = 1

		else: 
			print(f"\n1. {messages['create_user']}")
			print(f"2. {messages['login']}")
			print(f"3. {messages['exit']}")
			choice = input(messages['enter_choice'])




		if choice == '1':
			username = input(messages['enter_username'])
			password = input(messages['enter_password'])
			blog.create_user(username, password)

		elif choice == '2':
			username = input(messages['enter_username'])
			password = input(messages['enter_password'])
			user_id = blog.login(username, password)
			if user_id:
				while True:
					print(f"\n1. {messages['add_post']}")
					print(f"2. {messages['list_posts']}")
					print(f"3. {messages['logout']}")
					post_choice = input(messages['enter_choice'])

					if post_choice == '1':
						title = input(messages['enter_title'])
						content = input(messages['enter_content'])
						blog.add_post(user_id, title, content)

					elif post_choice == '2':
						blog.list_posts(user_id)

					elif post_choice == '3':
						print(messages['logged_out'])
						break

					else:
						print(messages['invalid_choice'])

		elif choice == '3':
			break

		else:
			print(messages['invalid_choice'])




class PersonalPost:
	def __init__(self):
		# Caminho absoluto do banco de dados no diretório atual
		db_path = os.path.join(os.getcwd(), 'database/database.db')

		# Conectar ao banco de dados SQLite
		self.conn = sqlite3.connect(db_path)
		self.cursor = self.conn.cursor()

		# Criar as tabelas 'users' e 'posts' se elas não existirem
		self.cursor.execute('''
		CREATE TABLE IF NOT EXISTS user (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			username TEXT NOT NULL UNIQUE,
			password TEXT NOT NULL
		)
		''')

		self.cursor.execute('''
		CREATE TABLE IF NOT EXISTS posts (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			user_id INTEGER,
			title TEXT NOT NULL,
			content TEXT NOT NULL,
			created_at TEXT NOT NULL,
			FOREIGN KEY (user_id) REFERENCES users (id)
		)
		''')

		self.conn.commit()  # Confirma as operações de criação de tabela



	def hash_password(password):
		"""Gera um hash SHA-256 para a senha."""
		return hashlib.sha256(password.encode('utf-8')).hexdigest()

	def verify_password(stored_password, provided_password):
		"""Verifica se a senha fornecida corresponde ao hash armazenado."""
		return stored_password == hashlib.sha256(provided_password.encode('utf-8')).hexdigest()

	def login(self, username, password):
		self.cursor.execute('SELECT id, password FROM users WHERE username = ?', (username,))
		user = self.cursor.fetchone()
		if user and self.verify_password(user[1], password):
			print("Login successful!")
			return user[0]  # Retorna o ID do usuário autenticado
		else:
			print("Invalid username or password.")
			return None


	def first_register(self, username, password):
		"""Cria um novo usuário com uma senha hash."""
		hashed_password = self.hash_password(password)
		try:
			cursor.execute('INSERT INTO user (username, password) VALUES (?, ?)', (username, hashed_password))
			conn.commit()  # Confirma a inserção do novo usuário
			print("User created successfully!")
		except sqlite3.IntegrityError:
			print("Username already exists. Please try a different one.")


	def verify_first_acess(self):
		"""
			Verifica se já possui um usuario no banco de dadodos
		"""
		

		self.cursor.execute('''
			SELECT * FROM user;		
		''')
		if self.cursor.fetchone():
			return True
		
		else:
			return False


	def add_post(self, user_id, title, content):
		"""Adiciona um novo post ao banco de dados, codificando o conteúdo."""
		created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		encoded_content = encode_content(content)
		self.cursor.execute('INSERT INTO posts (user_id, title, content, created_at) VALUES (?, ?, ?, ?)',
					(user_id, title, encoded_content, created_at))
		self.conn.commit()  # Confirma a inserção do novo post
		print("Post added successfully!")


	def list_posts(user_id):
		"""Lista todos os posts do usuário no banco de dados, decodificando o conteúdo."""
		cursor.execute('SELECT id, title, content, created_at FROM posts WHERE user_id = ?', (user_id,))
		posts = cursor.fetchall()

		if posts:
			# Definir cabeçalhos e calcular larguras de coluna
			headers = ["ID", "Title", "Content", "Created At"]
			max_id_width = max(len(str(post[0])) for post in posts)
			max_title_width = max(len(post[1]) for post in posts)
			max_content_width = 40  # Limitar o comprimento do conteúdo para exibição
			max_created_width = max(len(post[3]) for post in posts)

			# Imprimir cabeçalhos
			print(f"{'ID'.ljust(max_id_width)} | {'Title'.ljust(max_title_width)} | {'Content'.ljust(max_content_width)} | {'Created At'.ljust(max_created_width)}")
			print('-' * (max_id_width + max_title_width + max_content_width + max_created_width + 10))

			# Imprimir dados formatados
			for post in posts:
				decoded_content = decode_content(post[2])
				truncated_content = (decoded_content[:max_content_width - 3] + '...') if len(decoded_content) > max_content_width else decoded_content

				print(f"{str(post[0]).ljust(max_id_width)} | {post[1].ljust(max_title_width)} | {truncated_content.ljust(max_content_width)} | {post[3].ljust(max_created_width)}")
		else:
			print("No posts found.")



if __name__ == "__main__":
	main()

# Fechar a conexão com o banco de dados ao sair
conn.close()
