class informations:
	def __init__(self, language = 'english'):
		if language == 'english':
			self.close = 'Close'
			self.question1 = 'You are sure you want to get out?'
			self.plugin_name = "Quick Survey Plugin"
			self.plugin_menu = "&Survey Tools"
			self.plugin_ok1 = "Device GPS found"
			self.plugin_error_gps1 = "Device GPS not found. Check GPS Information"
			self.plugin_error_gps2 = "Device GPS not found. Check GPS Information and restart plugin"
		else:
			self.close = 'Cerrar'
			self.question1 = 'Esta seguro que desea Cerrar?'
			self.plugin_name = "Captura Rapido GPS"
			self.plugin_menu = "&Herramiento de Captura"
			self.plugin_ok1 = "Dispositivo GNSS correctamente configurado"
			self.plugin_error_gps1 = "Dispositivo GNSS no encontrado, Verifique Informacion GPS"
			self.plugin_error_gps2 = "Dispositivo GNSS no encontrado, Verifique Informacion GPS y reinicie el complemento"

