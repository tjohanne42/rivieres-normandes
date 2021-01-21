import pandas as pd
import pygame as pg
from pygame.locals import *
import numpy as np
import atexit
import time
import os
import concurrent.futures
import random

WHITE_TXT = (200, 200, 200)
GREEN = (41, 94, 60)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BUTTON_BG = (60, 70, 90)
BUTTON_BG_A = (40, 50, 70)

class Visualisation(object):

	def __init__(self):
		self.init_pygame()
		self.init_variables()
		# parralel script to auto increase date
		f1 = concurrent.futures.ThreadPoolExecutor().submit(self.loop_increase_date)
		# for debugging:
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
		# we're just adjusting size for two size of screen
		info = pg.display.Info()
		if info.current_w >= 1660 and info.current_h >= 900:
			# 1680+ screen
			self.window_width, self.window_height = 1660, 900
			self.display_mode = 0
		else:
			# small screen :c
			self.window_width, self.window_height= 1140, 700
			self.display_mode = 1
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
		# load the grayscale map
		self.map_surface_800 = pg.image.load("assets/gray_map_800.png")
		self.map_surface_500 = pg.image.load("assets/gray_map_500.png")
		# position of stations on the map, needed to check lambert 93 positions to place them
		self.stations_pos = 	{
								"Monne" : [(614, 245), (383, 153)],
								"Barge" : [(620, 331), (387, 207)],
								"Ving Bec" : [(394, 211), (246, 132)],
								"Odon T2" : [(352, 193), (219, 120)],
								"Odon T4" : [(402, 139), (251, 87)],
								"Odon T5" : [(435, 123), (271, 76)],
								"Orne T1" : [(412, 260), (257, 162)],
								"Orne T3" : [(418, 175), (261, 109)],
								"Orne T2" : [(398, 233), (248, 145)],
								"Selune T4" : [(118, 408), (73, 255)],
								"Selune T2" : [(132, 417), (82, 260)],
								"Selune T5" : [(112, 406), (69, 253)],
								"Selune T1" : [(172, 423), (108, 264)],
								"Touques T1" : [(673, 336), (421, 210)],
								"Touques T3" : [(665, 247), (416, 154)],
								"Touques T4" : [(662, 188), (414, 117)],
								"Touques T6" : [(631, 56), (394, 35)]
								}
		# it is what it is :D some questions? put it to True
		self.super_sayan = False
		# surface (_a mean "active")
		self.surface = 	{
						"hour" : self.button(100, 40, bg=BUTTON_BG, text="hour"),
						"hour_a" : self.button(100, 40, bg=BUTTON_BG_A, text="hour"),
						"day" : self.button(100, 40, bg=BUTTON_BG, text="day"),
						"day_a" : self.button(100, 40, bg=BUTTON_BG_A, text="day"),
						"month" : self.button(100, 40, bg=BUTTON_BG, text="month"),
						"month_a" : self.button(100, 40, bg=BUTTON_BG_A, text="month"),
						"super_sayan" : self.button(100, 40, bg=BUTTON_BG, text="don't push", text_size=15),
						"super_sayan_a" : self.button(100, 40, bg=BUTTON_BG_A, text="don't push", text_size=15, text_color=RED),
						"date_ms" : self.button(120, 40, bg=BUTTON_BG, text="change ms"),
						"date_ms_a" : self.button(120, 40, bg=BUTTON_BG_A, text="change ms"),
						"previous" : self.button(60, 40, bg=BUTTON_BG, text="previous", text_size=15),
						"previous_a" : self.button(60, 40, bg=BUTTON_BG_A, text="previous", text_size=15),
						"stop" : self.button(60, 40, bg=BUTTON_BG, text="stop", text_size=15),
						"stop_a" : self.button(60, 40, bg=BUTTON_BG_A, text="stop", text_size=15),
						"next" : self.button(60, 40, bg=BUTTON_BG, text="next", text_size=15),
						"next_a" : self.button(60, 40, bg=BUTTON_BG_A, text="next", text_size=15),
						"date1" : self.button(140, 40, bg=BUTTON_BG, text="change date"),
						"date1_a" : self.button(140, 40, bg=BUTTON_BG_A, text="change date"),
						"date2" : self.button(140, 40, bg=BUTTON_BG, text="change date"),
						"date2_a" : self.button(140, 40, bg=BUTTON_BG_A, text="change date"),
						"map_actual" : []
						}
		# buttons
		self.hold = "noone"
		self.user_text = "noone"
		self.interactive_rect = {
								"hour" : pg.Rect(120, 10, 100, 40),
								"day" : pg.Rect(230, 10, 100, 40),
								"month" : pg.Rect(340, 10, 100, 40),
								"super_sayan" : pg.Rect(450, 10, 100, 40),
								"date_ms" : pg.Rect(680, 10, 120, 40),
								"previous" : pg.Rect(950, 10, 60, 40),
								"stop" : pg.Rect(1010, 10, 60, 40),
								"next" : pg.Rect(1070, 10, 60, 40),
								"date1" : pg.Rect(20, 60, 140, 40),
								"date2" : pg.Rect(20, 60, 140, 40)
								}
		# current mode for df 0 : hour 1 : day 2 : month
		self.df_mode = 1
		# current dates we're printing
		self.date_actual_index = [0, 17 * 180]
		# load map surfaces
		self.surface["map_actual"].append(self.load_map_surface(self.df_mode, self.date_actual_index[0]))
		self.surface["map_actual"].append(self.load_map_surface(self.df_mode, self.date_actual_index[1]))
		# variables for auto increase date
		self.stop = False
		self.increase_date_ms = 1000 / 30
		
	def button(self, width, height, bg=(60, 70, 90), text=False, text_size=20, text_color=WHITE_TXT):
		# return a button surface
		surface = pg.Surface((width, height))
		surface.fill(bg)
		pg.draw.rect(surface, (0, 0, 0), pg.Rect(0, 0, width, height), width=2, border_radius=1)
		if text != False:
			text_surface = self.fonts[text_size].render(text, True, text_color)
			surface.blit(text_surface, (width / 2 - text_surface.get_size()[0] / 2, height / 2 - text_surface.get_size()[1] / 2))
		return surface

	def load_map_surface(self, df_mode, date_index):
		# return the surface
		# load the surface we wanna display, map with circles and some stats
		if self.display_mode == 0:
			width, height = self.map_surface_800.get_size()
			target_rect = pg.Rect(0, 0, width, 780)
			map_actual_surface = pg.Surface(target_rect.size, pg.SRCALPHA)
			map_actual_surface.blit(self.map_surface_800, (0, 0))
			radius_max = 40
			radius_min = 10
			stats_width = 580
		elif self.display_mode == 1:
			width, height = self.map_surface_500.get_size()
			target_rect = pg.Rect(0, 0, width, 570)
			map_actual_surface = pg.Surface(target_rect.size, pg.SRCALPHA)
			map_actual_surface.blit(self.map_surface_500, (0, 0))
			radius_max = 30
			radius_min = 5
			stats_width = 370
		# for each station we're gonna display circles with dynamic color and size and some stats
		opposite_color_size = 100
		x = 0
		temp_actual = {}
		mean = 0
		mini = self.temp_max[df_mode]
		maxi = self.temp_min[df_mode]
		stats_temp_str = [""] * 9
		for key, value in self.stations_pos.items():
			# stats
			temp_actual[key] = self.df_temp[df_mode]["Teau"][date_index + x]
			stats_temp_str[int(x / 2)] += key + ":"
			if x % 2 == 0 and x != 16:
				stats_temp_str[int(x / 2)] += " " * (30 - len(stats_temp_str[int(x / 2)]))
			if self.super_sayan:
				radius_max = 100
				temp_actual[key] = random.uniform(self.temp_min[df_mode], self.temp_max[df_mode])
			mean += temp_actual[key]
			if temp_actual[key] < mini:
				mini = temp_actual[key]
			if temp_actual[key] > maxi:
				maxi = temp_actual[key]
			# cicrlces
			if temp_actual[key] < self.temp_mean[df_mode]:
				mean_add = self.temp_mean[df_mode] - self.temp_min[df_mode]
				temp_add = temp_actual[key] - self.temp_min[df_mode]
				pourcent = temp_add * 100 / mean_add
				# blue
				color = (opposite_color_size - (100 - pourcent) * 100 / opposite_color_size, 0, 127 + (100 - pourcent) * 128 / 100)
				if self.super_sayan:
					color = (opposite_color_size - (100 - pourcent) * 100 / opposite_color_size, random.randint(0, 127), 127 + (100 - pourcent) * 128 / 100)
				radius = radius_min + (radius_max - radius_min) / 2 * pourcent / 100
			else:
				max_add = self.temp_max[df_mode] - self.temp_mean[df_mode]
				temp_add = temp_actual[key] - self.temp_mean[df_mode]
				pourcent = temp_add * 100 / max_add
				# red
				color = (127 + pourcent * 128 / 100, 0, opposite_color_size - pourcent * 100 / opposite_color_size)
				if self.super_sayan:
					color = (127 + pourcent * 128 / 100, random.randint(0, 127), opposite_color_size - pourcent * 100 / opposite_color_size)
				radius = radius_min + (radius_max - radius_min) / 2 + (radius_max - radius_min) / 2 * pourcent / 100
			# draw
			self.draw_circle_alpha(map_actual_surface, color, 170, value[self.display_mode], radius)
			text = self.fonts[12].render(str(round(temp_actual[key], 2)), True, (color[0], color[1], color[2]))
			map_actual_surface.blit(text, (90 + x % 2 * 210, stats_width + 60 + int(x / 2) * 15))
			x += 1
		# stats
		date_actual_surface = self.fonts[20].render(self.df_temp[df_mode]["date_mesure"][date_index], True, WHITE_TXT)
		map_actual_surface.blit(date_actual_surface, (0, stats_width))
		mean /= x
		global_stats_str = "mean :        min :        max : "
		global_stats = self.fonts[20].render(global_stats_str, True, WHITE_TXT)
		map_actual_surface.blit(global_stats, (0, stats_width + 30))
		y = 4 - len(str(round(mean, 2)))
		z = 4 - len(str(round(mini, 2)))
		global_stats_str = " " * 7 + str(round(mean, 2)) + " " * (9 + y) + str(round(mini, 2)) + " " * (9 + z) + str(round(maxi, 2))
		global_stats = self.fonts[20].render(global_stats_str, True, WHITE_TXT)
		map_actual_surface.blit(global_stats, (0, stats_width + 30))
		x = 0
		for temp_str in stats_temp_str:
			text = self.fonts[12].render(temp_str, True, WHITE_TXT)
			map_actual_surface.blit(text, (0, stats_width + 60 + x * 15))
			x += 1
		return map_actual_surface

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
			while time.time() * 1000 - timer < self.increase_date_ms:
				sleep_time = self.increase_date_ms - (time.time() * 1000 - timer)
				if sleep_time >= 1000:
					sleep_time = 1000
				time.sleep(sleep_time / 1000)
				if not self.running:
					exit()
			timer = time.time() * 1000
			if not self.stop:
				self.increase_date(True, True)

	def increase_date(self, index1=False, index2=False):
		# everything's in the title
		if index1:
			self.date_actual_index[0] += 17
			if self.date_actual_index[0] >= len(self.df_temp[self.df_mode]):
				self.date_actual_index[0] = 0
			self.surface["map_actual"][0] = self.load_map_surface(self.df_mode, self.date_actual_index[0])
		if index2:
			self.date_actual_index[1] += 17
			if self.date_actual_index[1] >= len(self.df_temp[self.df_mode]):
				self.date_actual_index[1] = 0
			self.surface["map_actual"][1] = self.load_map_surface(self.df_mode, self.date_actual_index[1])

	def decrease_date(self, index1=False, index2=False):
		# everything's in the title
		if index1:
			self.date_actual_index[0] -= 17
			if self.date_actual_index[0] < 0:
				self.date_actual_index[0] = len(self.df_temp[self.df_mode]) - 17
			self.surface["map_actual"][0] = self.load_map_surface(self.df_mode, self.date_actual_index[0])
		if index2:
			self.date_actual_index[1] -= 17
			if self.date_actual_index[1] < 0:
				self.date_actual_index[1] = len(self.df_temp[self.df_mode]) - 17
			self.surface["map_actual"][1] = self.load_map_surface(self.df_mode, self.date_actual_index[1])

	def reset_date(self, index1=False, index2=False):
		# everything's in the title
		if index1:
			self.date_actual_index[0] = 0
			self.surface["map_actual"][0] = self.load_map_surface(self.df_mode, self.date_actual_index[0])
		if index2:
			if self.df_mode == 0:
				self.date_actual_index[1] = 17 * 12 * 180
			elif self.df_mode == 1:
				self.date_actual_index[1] = 17 * 180
			else:
				self.date_actual_index[1] = 17 * 6
			self.surface["map_actual"][1] = self.load_map_surface(self.df_mode, self.date_actual_index[1])

	def pos_in_interactive(self, name, mx, my, addwidth=0, addheight=0):
		# check if mx, my is in interactive Rect
		if pg.Rect(self.interactive_rect[name].x - addwidth / 2, self.interactive_rect[name].y - addheight / 2,
			self.interactive_rect[name].width + addwidth, self.interactive_rect[name].height + addheight).collidepoint((mx, my)):
			return True
		return False

	def event(self, event):
		# user events
		if event.type == pg.MOUSEMOTION:
			mx, my = pg.mouse.get_pos()
			if self.hold != "noone" and not self.pos_in_interactive(self.hold, mx, my):
				self.hold = "noone"
		elif event.type == pg.VIDEORESIZE:
			self.window_width, self.window_height = event.size
			if self.window_width >= 1660 and self.window_height >= 870:
				if self.display_mode == 1:
					self.display_mode = 0
					self.surface["map_actual"][0] = self.load_map_surface(self.df_mode, self.date_actual_index[0])
					self.surface["map_actual"][1] = self.load_map_surface(self.df_mode, self.date_actual_index[1])
			else:
				if self.display_mode == 0:
					self.display_mode = 1
					self.surface["map_actual"][0] = self.load_map_surface(self.df_mode, self.date_actual_index[0])
					self.surface["map_actual"][1] = self.load_map_surface(self.df_mode, self.date_actual_index[1])
		elif event.type == pg.KEYDOWN:
			if self.user_text != "noone":
				# could do it with ascii values, but well ...
				if event.key == pg.K_0 or event.key == pg.K_KP0:
					self.user_text_str += "0"
				if event.key == pg.K_1 or event.key == pg.K_KP1:
					self.user_text_str += "1"
				elif event.key == pg.K_2 or event.key == pg.K_KP2:
					self.user_text_str += "2"
				elif event.key == pg.K_3 or event.key == pg.K_KP3:
					self.user_text_str += "3"
				elif event.key == pg.K_4 or event.key == pg.K_KP4:
					self.user_text_str += "4"
				elif event.key == pg.K_5 or event.key == pg.K_KP5:
					self.user_text_str += "5"
				elif event.key == pg.K_6 or event.key == pg.K_KP6:
					self.user_text_str += "6"
				elif event.key == pg.K_7 or event.key == pg.K_KP7:
					self.user_text_str += "7"
				elif event.key == pg.K_8 or event.key == pg.K_KP8:
					self.user_text_str += "8"
				elif event.key == pg.K_9 or event.key == pg.K_KP9:
					self.user_text_str += "9"
				elif event.key == pg.K_BACKSPACE:
					size = len(self.user_text_str)
					if size > 0:
						self.user_text_str = self.user_text_str[0:size - 1]
				elif event.key == pg.K_PERIOD or event.key == pg.K_KP_PERIOD:
					self.user_text_str += "."
				elif event.key == pg.K_COMMA:
					self.user_text_str += ","
				elif event.key == pg.K_MINUS or event.key == pg.K_KP_MINUS:
					if self.user_text_unvalid.find("-") == -1:
						self.user_text_str += "-"
				elif event.key == pg.K_SPACE:
					if self.user_text_unvalid.find(" ") == -1:
						self.user_text_str += " "
				elif event.key == pg.K_SLASH or event.key == pg.K_KP_DIVIDE:
					if self.user_text_unvalid.find("/") == -1:
						self.user_text_str += "/"
				elif event.key == pg.K_COLON:
					if self.user_text_unvalid.find(":") == -1:
						self.user_text_str += ":"
				elif event.key == pg.K_ESCAPE:
					self.user_text = "noone"
				elif event.key == pg.K_RETURN:
					if self.user_text == "date_ms":
						self.increase_date_ms = float(self.user_text_str.replace(",", "."))
					elif self.user_text == "date1":
						if self.user_text_str.find(" ") != -1:
							tmp_text = self.user_text_str.split(" ")
							tmp_text[0] = tmp_text[0].replace("/", "-")
							tmp_text[1] = tmp_text[1].replace("/", ":")
							tmp_text[1] = tmp_text[1].replace("-", ":")
							self.user_text_str = tmp_text[0] + " " + tmp_text[1]
						else:
							self.user_text_str = self.user_text_str.replace("/", "-")
						try :
							self.date_actual_index[0] = self.df_temp[self.df_mode].loc[self.df_temp[self.df_mode]["date_mesure"] == self.user_text_str].index[0]
							self.surface["map_actual"][0] = self.load_map_surface(self.df_mode, self.date_actual_index[0])
						except:
							print("could not find", self.user_text_str)
					elif self.user_text == "date2":
						if self.user_text_str.find(" ") != -1:
							tmp_text = self.user_text_str.split(" ")
							tmp_text[0] = tmp_text[0].replace("/", "-")
							tmp_text[1] = tmp_text[1].replace("/", ":")
							tmp_text[1] = tmp_text[1].replace("-", ":")
							self.user_text_str = tmp_text[0] + " " + tmp_text[1]
						else:
							self.user_text_str = self.user_text_str.replace("/", "-")
						try :
							self.date_actual_index[1] = self.df_temp[self.df_mode].loc[self.df_temp[self.df_mode]["date_mesure"] == self.user_text_str].index[0]
							self.surface["map_actual"][1] = self.load_map_surface(self.df_mode, self.date_actual_index[1])
						except:
							print("could not find", self.user_text_str)
					self.user_text = "noone"
			elif event.key == pg.K_SPACE:
				if not self.stop:
					self.stop = True
				else:
					self.stop = False
			elif event.key == K_LEFT:
				self.stop = True
				self.decrease_date(True, True)
			elif event.key == K_RIGHT:
				self.stop = True
				self.increase_date(True, True)
		elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
			mx, my = pg.mouse.get_pos()
			for key, value in self.interactive_rect.items():
				if self.pos_in_interactive(key, mx, my):
					self.hold = key
			if self.user_text != "noone":
				self.user_text = "noone"
		elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
			if self.hold == "hour":
				self.df_mode = 0
				self.reset_date(True, True)
			elif self.hold == "day":
				self.df_mode = 1
				self.reset_date(True, True)
			elif self.hold == "month":
				self.df_mode = 2
				self.reset_date(True, True)
			elif self.hold == "super_sayan":
				if not self.super_sayan:
					self.super_sayan = True
				else:
					self.super_sayan = False
				self.reset_date(True, True)
			elif self.hold == "previous":
				self.stop = True
				self.decrease_date(True, True)
			elif self.hold == "stop":
				if not self.stop:
					self.stop = True
				else:
					self.stop = False
			elif self.hold == "next":
				self.stop = True
				self.increase_date(True, True)
			elif self.hold == "date_ms":
				self.user_text = "date_ms"
				self.user_text_str = ""
				self.user_text_unvalid = "- :/"
			elif self.hold == "date1":
				self.user_text = "date1"
				self.user_text_str = ""
				self.user_text_unvalid = ""
			elif self.hold == "date2":
				self.user_text = "date2"
				self.user_text_str = ""
				self.user_text_unvalid = ""
			if self.hold != "noone":
				self.hold = "noone"

	def display(self, fps=False):
		# fill background
		self.screen.fill((60, 70, 90))

		# display fps
		if not fps:
			fps_real_time_surface = self.fonts[15].render("FPS : -", True, WHITE_TXT)
		else:
			fps_real_time_surface = self.fonts[15].render("FPS : " + str(fps), True, WHITE_TXT)
		self.screen.blit(fps_real_time_surface, (20, 20))

		# display map surface
		size = self.surface["map_actual"][0].get_size()[0]
		left = (self.window_width - size * 2) / 3
		self.screen.blit(self.surface["map_actual"][0], (left, 110))
		self.screen.blit(self.surface["map_actual"][1], (left * 2 + size, 110))


		# user can change date
		self.interactive_rect["date1"].x = left
		self.interactive_rect["date2"].x = left * 2 + size
		if self.user_text == "date1":
			if len(self.user_text_str) < 1:
				date_text = self.fonts[20].render("new date here", True, WHITE_TXT)
			else:
				date_text = self.fonts[20].render(self.user_text_str, True, WHITE_TXT)
			self.screen.blit(date_text, (self.interactive_rect["date1"].x + self.interactive_rect["date1"].width + 10, self.interactive_rect["date1"].y + 10))
		elif self.user_text == "date2":
			if len(self.user_text_str) < 1:
				date_text = self.fonts[20].render("new date here", True, WHITE_TXT)
			else:
				date_text = self.fonts[20].render(self.user_text_str, True, WHITE_TXT)
			self.screen.blit(date_text, (self.interactive_rect["date2"].x + self.interactive_rect["date2"].width + 10, self.interactive_rect["date2"].y + 10))
		
		# display buttons
		mx, my = pg.mouse.get_pos()
		for key, value in self.interactive_rect.items():
			if self.hold != key and self.pos_in_interactive(key, mx, my):
				self.screen.blit(self.surface[key + "_a"], (self.interactive_rect[key].x, self.interactive_rect[key].y))
			else:
				self.screen.blit(self.surface[key], (self.interactive_rect[key].x, self.interactive_rect[key].y))

		# user can change MS
		ms_date = self.fonts[20].render("MS: " + str(round(self.increase_date_ms, 1)), True, WHITE_TXT)
		self.screen.blit(ms_date, (560, 20))
		if self.user_text == "date_ms":
			if len(self.user_text_str) < 1:
				date_ms_text = self.fonts[20].render("new ms here", True, WHITE_TXT)
			else:
				date_ms_text = self.fonts[20].render(self.user_text_str, True, WHITE_TXT)
			self.screen.blit(date_ms_text, (810, 20))


		# draw new frame
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
