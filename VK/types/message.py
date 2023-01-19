from VK.types.attachments.photo import Photo

#from attachments.video import Video
#from attachments.audio import Audio
#from attachments.docs import Docs
# существуют другие типы вложений: link и другие

# полученное сообщение

class Message:

	# является ли ответом на что-либо
	reply_message = None

	# поддерживаемые типы
	__available_types__ = {
		'photo': Photo
	}

	def __init__(self, data):
		# основные параметры
		message_dict = data['object']['message']
		for attr in message_dict.keys():
			if type(attr) is str or type(attr) is int:
				self.__setattr__(attr, message_dict[attr])

		# вложения
		# # вложенные файлы разного типа
		self.attachments =  [attachment(attach) for attach in message_dict[ 'attachments' ]]
		# # пересланные сообщения (из других диалогов или более одного из текущего)
		self.fwd_messages = [Message(msg)       for msg    in message_dict['fwd_messages']]

		# ответ на сообщение
		if 'reply_message' in message_dict:
			self.reply_message = Message(message_dict['reply_message'])

	def __choose_attachment__(self, data):
		"""выбор класса по типу вложения"""
		_type = data['type']
		if _type in self.__available_types__:
			return self.__available_types__[_type](data[_type])
		else:
			return data

	def __repr__(self):
		return str(
				f'Message(from_id={self.from_id}, '
				f'attachments={len(self.attachments)}, '
				f'fwd_message={len(self.fwd_messages)}, '
				f'date={self.date})'
		)


