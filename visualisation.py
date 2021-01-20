import pandas as pd
import pygame as pg
from pygame.locals import *
import numpy as np
import atexit
import time
import os
import concurrent.futures

WHITE_TXT = (200, 200, 200)
GREEN = (41, 94, 60)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

class Visualisation(object):

	def __init__(self):
		self.init_pygame()
		self.init_variables()
		# parralel script to auto increase date
		f1 = concurrent.futures.ThreadPoolExecutor().submit(self.loop_increase_date)
		# for debugging
		#self.loop_increase_date()

	def init_pygame(self):
		# typical init pygame
		try:
			os.environ["SDL_VIDEO_CENTERED"] = "1"
		except:
			print("os.environ['SDL_VIDEO_CENTERED'] = '1' failed")
		pg.init()
		icon_surface = pg.image.load('assets/icon.ico')
		pg.display.set_icon(icon_surface)
		pg.display.set_caption("Rivières Normandes Visualisation")
		info = pg.display.Info()
		screen_width, screen_height = info.current_w, info.current_h
		# we're just adjusting size for two size of screen
		if screen_width >= 1660 and screen_height >= 800:
			self.window_width, self.window_height = 1660, 800
			# current mode for display 0 : 800(width)
			self.display_mode = 0
		self.screen = pg.display.set_mode((self.window_width, self.window_height), HWSURFACE | DOUBLEBUF | RESIZABLE)
		self.fonts = self.load_fonts("assets/Inconsolata-Bold.ttf", 1, 30)
		self.clock = pg.time.Clock()
		self.fps = 60
		self.running = True
		atexit.register(pg.quit)

	def load_fonts(self, path, minsize, maxsize):
		# load multiple size of font
		fonts = []
		i = minsize
		while i < maxsize:
			fonts.append(pg.font.Font(path, i))
			i += 1
		return fonts

	def quit(self):
		self.running = False

	def init_variables(self):
		# load dataframes and some stats
		self.df_temp = [pd.read_csv("csv/temp_hour.csv"), pd.read_csv("csv/temp_day.csv"),  pd.read_csv("csv/temp_month.csv")]
		self.temp_mean = [self.df_temp[0]["Teau"].mean(), self.df_temp[1]["Teau"].mean(), self.df_temp[2]["Teau"].mean()]
		self.temp_min = [self.df_temp[0]["Teau"].min(), self.df_temp[1]["Teau"].min(), self.df_temp[2]["Teau"].min()]
		self.temp_max = [self.df_temp[0]["Teau"].max(), self.df_temp[1]["Teau"].max(), self.df_temp[2]["Teau"].max()]
		# grayscale the png, it takes way more time than expected so we're gonna save the new png
		"""
		surface = pg.image.load("assets/20190731-bv-orne-touques-selune-c00-reseautemperature-ca-1.png")
		arr = pg.surfarray.array3d(surface)
		avgs = [[(r*0.298 + g*0.587 + b*0.114) for (r,g,b) in col] for col in arr]
		arr = np.array([[[avg,avg,avg] for avg in col] for col in avgs])
		self.map_surface = pg.surfarray.make_surface(arr)
		pg.image.save(self.map_surface, "assets/gray_map_1653x1167.png")
		"""
		# resize the map, to save time we're gonna do it with paint :3
		# load the grayscale map (800 = width)
		self.map_surface_800 = pg.image.load("assets/gray_map_800.png")
		# position of stations on the map, needed to check lambert 93 positions to place them
		self.stations_pos = {
									"Monne" : [(614, 245), (0, 0)],
									"Barge" : [(620, 331), (0, 0)],
									"Ving Bec" : [(394, 211), (0, 0)],
									"Odon T2" : [(352, 193), (0, 0)],
									"Odon T4" : [(402, 139), (0, 0)],
									"Odon T5" : [(435, 123), (0, 0)],
									"Orne T1" : [(412, 260), (0, 0)],
									"Orne T3" : [(418, 175), (0, 0)],
									"Orne T2" : [(398, 233), (0, 0)],
									"Selune T4" : [(118, 408), (0, 0)],
									"Selune T2" : [(132, 417), (0, 0)],
									"Selune T5" : [(112, 406), (0, 0)],
									"Selune T1" : [(172, 423), (0, 0)],
									"Touques T1" : [(673, 336), (0, 0)],
									"Touques T3" : [(665, 247), (0, 0)],
									"Touques T4" : [(662, 188), (0, 0)],
									"Touques T6" : [(631, 56), (0, 0)]
								}
		# current mode for df 0 : hour 1 : day 2 : month
		self.df_mode = 1
		# current date we're printing
		self.date_actual_index = 0
		self.map_actual_surface, self.temp_actual, self.date_actual_surface = self.load_map_surface(self.df_mode, self.date_actual_index)
		# variables for auto increase date
		self.stop = False
		self.increase_ms = 1000 / 30

	def load_map_surface(self, df_mode, date_index):
		# load the surface we wanna display, map with circles
		if self.display_mode == 0:
			width, height = self.map_surface_800.get_size()
			target_rect = pg.Rect(0, 0, width, height)
			map_actual_surface = pg.Surface(target_rect.size, pg.SRCALPHA)
			map_actual_surface.blit(self.map_surface_800, (0, 0))
			radius_max = 40
			radius_min = 10

		# for each station we're gonna display circle with dynamic color and size
		x = 0
		temp_actual = {}
		for key, value in self.stations_pos.items():

			temp_actual[key] = self.df_temp[df_mode]["Teau"][date_index + x]

			if temp_actual[key] < self.temp_mean[df_mode]:
				mean_add = self.temp_mean[df_mode] - self.temp_min[df_mode]
				temp_add = temp_actual[key] - self.temp_min[df_mode]
				pourcent = temp_add * 100 / mean_add
				# blue
				color = (100 - (100 - pourcent) * 100 / 100, 0, 127 + (100 - pourcent) * 128 / 100)
				radius = radius_min + (radius_max - radius_min) / 2 * pourcent / 100
			else:
				max_add = self.temp_max[df_mode] - self.temp_mean[df_mode]
				temp_add = temp_actual[key] - self.temp_mean[df_mode]
				pourcent = temp_add * 100 / max_add
				# red
				color = (127 + pourcent * 128 / 100, 0, 100 - pourcent * 100 / 100)
				radius = radius_min + (radius_max - radius_min) / 2 + (radius_max - radius_min) / 2 * pourcent / 100
			self.draw_circle_alpha(map_actual_surface, color, 170, value[self.display_mode], radius)
			x += 1
		date_actual_surface = self.fonts[20].render(self.df_temp[df_mode]["date_mesure"][date_index], True, WHITE_TXT)
		# load dic with all temp for this date and mode and date_surface
		return map_actual_surface, temp_actual, date_actual_surface

	def draw_circle_alpha(self, surface, color, alpha, center, radius):
		# typical circle display with pygame with alpha colors
		target_rect = pg.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
		shape_surf = pg.Surface(target_rect.size, pg.SRCALPHA)
		color = color[0], color[1], color[2], alpha
		pg.draw.circle(shape_surf, color, (radius, radius), radius)
		surface.blit(shape_surf, target_rect)

	def loop_increase_date(self):
		# loop running in backgroup to auto increase date if we want
		timer = time.time() * 1000
		while self.running:
			while time.time() * 1000 - timer < self.increase_ms:
				sleep_time = self.increase_ms - (time.time() * 1000 - timer)
				if sleep_time >= 1000:
					sleep_time = 1000
				time.sleep(sleep_time / 1000)
				if not self.running:
					exit()
			timer = time.time() * 1000
			if not self.stop:
				self.increase_date()

	def increase_date(self):
		self.date_actual_index += 17
		try:
			self.df_temp[self.df_mode]["date_mesure"][self.date_actual_index]
		except:
			self.date_actual_index = 0
		self.map_actual_surface, self.temp_actual, self.date_actual_surface = self.load_map_surface(self.df_mode, self.date_actual_index)

	def decrease_date(self):
		self.date_actual_index -= 17
		if self.date_actual_index < 0:
			self.date_actual_index = len(self.df_temp[self.df_mode]) - 18
		self.map_actual_surface, self.temp_actual, self.date_actual_surface = self.load_map_surface(self.df_mode, self.date_actual_index)

	def event(self, event):
		if event.type == pg.VIDEORESIZE:
			self.window_width, self.window_height = event.size
			print(self.window_width, self.window_height)
		elif event.type == pg.KEYDOWN:
			if event.key == pg.K_SPACE:
				if not self.stop:
					self.stop = True
				else:
					self.stop = False
			if event.key == K_LEFT:
				self.stop = True
				self.decrease_date()
			if event.key == K_RIGHT:
				self.stop = True
				self.increase_date()

	def display(self, fps=False):
		# fill background
		self.screen.fill((60, 70, 90))

		# display fps
		if not fps:
			fps_real_time_surface = self.fonts[15].render("FPS : -", True, WHITE_TXT)
		else:
			fps_real_time_surface = self.fonts[15].render("FPS : " + str(fps), True, WHITE_TXT)
		self.screen.blit(fps_real_time_surface, (20, 10))

		# display map with circles
		self.screen.blit(self.map_actual_surface, (20, 40))

		# display date
		self.screen.blit(self.date_actual_surface, (20, 620))

		# apply new display
		pg.display.flip()
		

if __name__ == "__main__":

	visu = Visualisation()
	visu.fps = 60
	# count real time fps
	timer = time.time()
	count_fps = 0
	last_count_fps = False
	# main loop
	running = True
	while running:
		# get all user event
		for event in pg.event.get():
			if event.type == pg.QUIT:
				# when user clicks on quit button
				running = False
			else:
				visu.event(event)
		# display
		visu.display(last_count_fps)
		# limit the frame rate
		visu.clock.tick(visu.fps)
		# count real time fps
		count_fps += 1
		if time.time() - timer >= 1:
			last_count_fps = count_fps
			count_fps = 0
			timer = time.time()
visu.quit()
