import logging
import os
from configparser import ConfigParser


class SensorConfig:

	def __init__(self, file_path):
		self.file_path = file_path
		self.sensors = None
		self.confp = ConfigParser(inline_comment_prefixes=('#', ';'))
		if not os.path.isfile(file_path):
			logging.error("Failed to load config: '{}' is not a file".format(file_path))
		elif not self.confp.read(file_path):
			logging.error("Failed to load conig: couldn't parse '{}'".format(file_path))
		self.file_lastm = os.stat(file_path).st_mtime

	def add_sensor_(self, address, rorg, func, type_, publish_rssi):
		if address == 'CONFIG':
			logging.warning("Tried to add Sensor CONFIG")
			return
		if address in self.confp.sections():
			logging.warning("Tried to add Sensor {} which already exists".format(address))
			return

		publish_rssi = 1 if publish_rssi else 0
		self.confp[address] = {
			'address': int(address, base=16), 'rorg': rorg, 'func': func, 'type': type_, 'publish_rssi': publish_rssi
		}
		new_sens = {'name': self.confp['CONFIG']['mqtt_prefix'] + address}
		for key in self.confp[address]:
			try:
				new_sens[key] = int(self.confp[address][key], 0)
			except KeyError:
				new_sens[key] = None
		self.sensors.append(new_sens)
		self.save_to_file()

	def add_sensor(self, address, eep, publish_rssi=True):
		eep = eep.split('-')
		self.add_sensor_(address, int(eep[0], 16), int(eep[1], 16), int(eep[2], 16), publish_rssi)

	def print_sections(self):
		for section in (self.confp.sections()):
			print(section)
			for key in self.confp[section]:
				print("    {}: {}".format(key, self.confp[section][key]))

	def save_to_file(self):
		with open(self.file_path, 'w') as f:
			self.confp.write(f)
		self.file_lastm = os.stat(self.file_path).st_mtime

	def reload_file(self):
		self.confp = ConfigParser(inline_comment_prefixes=('#', ';'))
		if not self.confp.read(self.file_path):
			logging.error("Failed to reload conig: couldn't parse '{}'".format(self.file_path))

	def reload_changes(self):
		last_m = os.stat(self.file_path).st_mtime
		if self.file_lastm < last_m:
			logging.debug("Reloading Changed Config")
			self.file_lastm = last_m
			self.sensors = None
			self.reload_file()

	def remove_sensor(self, address):
		if address == 'CONFIG':
			logging.warning("Tried to remove Sensor CONFIG, this would remove the Config Section")
			return
		if address not in self.confp.sections():
			logging.warning("Tried to remove Sensor {} which doesn't exist".format(address))
			return
		self.confp.remove_section(address)

	def get_sensors(self):
		self.reload_changes()
		if self.sensors is not None:
			return self.sensors

		self.sensors = []
		for section in self.confp.sections():
			if section == 'CONFIG':
				continue
			new_sens = {'name': self.confp['CONFIG']['mqtt_prefix'] + section}
			for key in self.confp[section]:
				try:
					new_sens[key] = int(self.confp[section][key], 0)
				except KeyError:
					new_sens[key] = None
			self.sensors.append(new_sens)
		return self.sensors

	def get_config_section(self):
		self.reload_changes()
		return self.confp['CONFIG']


# Test
if __name__ == '__main__':
	print('-' * 50)
	config_file = "test_conf.conf"
	sc = SensorConfig(config_file)
	sc.add_sensor("0x01A64F7F", "D5-00-01")
	sc.save_to_file()
	sc.print_sections()
	print('-' * 50)
	sc.remove_sensor("0x01A64F7F")
	sc.print_sections()
	print('-' * 50)
