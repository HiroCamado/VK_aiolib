# libs
from aiohttp import ClientSession
from asyncio import create_task
from json import loads
# libs



class GroupBot:
	"""
	Для взаимодействия с группой с помощью токена группы.
	Обеспечивает взаимодействие с одним ботом. Можно создать несколько.
	"""
	_session = None

	def __init__(self, token, group_id, version=5.131):
		self._token = token
		self._group_id = group_id
		self._version = version

	@property
	def token(self):
		return self._token

	@property
	def group_id(self):
		return self._group_id

	@property
	def session(self):
		if self._session is None:
			self._session = self.create_session()
			return self._session
		else:
			return self._session

	@session.setter
	def session(self, new_session):
		self._session = new_session

	def create_session(self):
		return ClientSession()

	async def close_session(self):
		if self._session is not None:
			await self.session.close()

	def __del__(self):
		"""закроет сессию, чтобы избежать ошибок при завершении работы"""
		create_task(self.close_session())

	async def get_server(self):
		"""
		получает адрес сервера, ключ и последний ts
		:return: dict
		"""
		return await (
			await self.session.get(
					'https://api.vk.com/method/groups.getLongPollServer?'
					f'group_id={self.group_id}&access_token={self.token}&v={self._version}')
		).json()

	async def long_poll(self, wait=25):
		"""
		запускает процесс получения обновлений
		:param wait: время ожидания события. От 0 до 90, но желательно не превышать 30 во избежание проблем
		"""
		result = await self.get_server()
		if 'error' in result:
			print('ошибка при получении long_poll_server. проверьте токен, id группы и версию')
			return
		response = result['response']
		self.__lp__ = self.LongPollSession(self.session, response, wait)
		return self.__lp__

	class LongPollSession:
		"""
		класс реализует получение обновлений.
		подразумевает изначально получить адрес сервера, ключ и ts
		"""
		def __init__(self, session, response, wait):
			self.session = session
			self.key = response['key']
			self.server = response['server']
			self.ts = response['ts']
			self.wait = wait

		async def request(self):
			"""
			получает и проверяет обновления на предмет ошибки
			:return: dict
			"""
			result = await self.session.get(
					f'{self.server}?act=a_check&key={self.key}&ts={self.ts}&wait={self.wait}'
			)
			response = await result.json()
			if 'failed' in response:
				pass
			self.ts = response['ts']
			return response['updates']

		async def wait_update(self, wait=None):
			if wait is not None:
				self.wait = wait
			return await self.__aiter__().__anext__()


		async def __aiter__(self):
			while True:
				yield await self.request()
