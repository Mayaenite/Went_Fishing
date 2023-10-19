import os
import mss
import cv2
import pyautogui
import numpy
from PIL import Image,ImageEnhance
import sys
import glob
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile,QIODevice,QSize,Slot,Signal
import rc_icons
import mouse
import keyboard
UI_LOADER = QUiLoader()
_this_dir = os.path.dirname(__file__).replace("\\","/")
########################################################################
class Point:

	"""A point identified by (x,y) coordinates.

	supports: +, -, *, /, str, repr
	"""

	def __init__(self, x=0.0, y=0.0):
		self.x = x
		self.y = y

	def __add__(self, p):
		"""Point(x1+x2, y1+y2)"""
		return Point(self.x+p.x, self.y+p.y)

	def __sub__(self, p):
		"""Point(x1-x2, y1-y2)"""
		return Point(self.x-p.x, self.y-p.y)

	def __mul__( self, scalar ):
		"""Point(x1*x2, y1*y2)"""
		return Point(self.x*scalar, self.y*scalar)

	def __div__(self, scalar):
		"""Point(x1/x2, y1/y2)"""
		return Point(self.x/scalar, self.y/scalar)

	def __str__(self):
		return "(%s, %s)" % (self.x, self.y)

	def __repr__(self):
		return "%s(%r, %r)" % (self.__class__.__name__, self.x, self.y)

########################################################################
class Rect:

	"""A rectangle identified by two points.

    The rectangle stores left, top, right, and bottom values.
    """
	#----------------------------------------------------------------------
	def __init__(self, pt1:Point, pt2:Point):
		"""Initialize a rectangle from two points."""
		self.set_points(pt1, pt2)
	#----------------------------------------------------------------------
	def set_points(self, pt1:Point, pt2:Point):
		"""Reset the rectangle coordinates."""
		self.left = min(pt1.x, pt2.x)
		self.top = min(pt1.y, pt2.y)
		self.right = max(pt1.x, pt2.x)
		self.bottom = max(pt1.y, pt2.y)
	#----------------------------------------------------------------------
	@property
	def top_left(self):
		"""Return the top-left corner as a Point."""
		return Point(self.left, self.top)
	#----------------------------------------------------------------------
	@property
	def bottom_right(self):
		"""Return the bottom-right corner as a Point."""
		return Point(self.right, self.bottom)
	#----------------------------------------------------------------------
	@property
	def lenght(self):
		""""""
		return self.bottom_right.x - self.top_left.x
	#----------------------------------------------------------------------
	@property
	def width(self):
		""""""
		return self.bottom_right.x - self.top_left.x

#_position = pyautogui.position
##----------------------------------------------------------------------
#def position(x=None, y=None):
	#""""""
	#p = _position(x=x, y=y)
	#return Point(x=p.x, y=p.y)

#----------------------------------------------------------------------
def Get_Monitor(monitor):
	""""""
	sct = mss.mss()
	try:
		mon = sct.monitors[monitor]
	except:
		mon = sct.monitors[1]
	return mon
		
#----------------------------------------------------------------------
def Find_MatchTemplate_Center(imageCast,imageTemplate):
	""""""
	width  = imageTemplate.shape[1]
	height = imageTemplate.shape[0]
	
	match_res = cv2.matchTemplate(imageCast, imageTemplate, cv2.TM_CCOEFF_NORMED)
	min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match_res)
	return Get_Rectangle_Center(max_loc[0], max_loc[1], width, height)

#----------------------------------------------------------------------
def Get_Rectangle_Center(top,left,width,height):
	""""""
	pt1 = top + (height / 2)
	pt2 = left + (width / 2)
	return (pt1,pt2)	
#----------------------------------------------------------------------
def Create_CV2_Image(fp,flags=cv2.IMREAD_UNCHANGED):
	""""""
	res = cv2.imread(fp, flags=flags)
	res = cv2.cvtColor(res, cv2.COLOR_RGB2RGBA)
	return res

#----------------------------------------------------------------------
def Convert_Pil_To_CV2_Image(pil_img):
	""""""
	cv2_image = cv2.cvtColor(numpy.asarray(pil_img), cv2.COLOR_RGB2RGBA)
	return cv2_image
	
#----------------------------------------------------------------------
def Convert_CV2_To_Pil_Image(cv2_img):
	""""""
	cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_RGB2RGBA)
	pil_img = Image.fromarray(cv2_img)
	#isinstance(pil_img,Image)
	return pil_img


#----------------------------------------------------------------------
def Capture_Screen_Section(top,left,width,height,save_to_file=False):
	""" capture only a part of the screen"""
	with mss.mss() as sct:
		# The screen part to capture
		monitor = {"top": left, "left": top, "width": width, "height": height}
	
		# Grab the data
		sct_img = sct.grab(monitor)
		#isinstance(sct_img,mss.screenshot.ScreenShot)
		
		if save_to_file:
			mss.tools.to_png(sct_img.rgb, sct_img.size, output=r"Screen_Shots\screen_grab_section.png")
			sct_img = Create_CV2_Image(r"Screen_Shots\screen_grab_section.png")
		else:
			sct_img = numpy.asanyarray(sct_img)
		sct_img = cv2.cvtColor(sct_img, cv2.COLOR_RGB2RGBA)
		return sct_img
	
#----------------------------------------------------------------------
def Capture_Screen(monitor=1,flags=cv2.COLOR_RGB2RGBA):
	""""""
	sct = mss.mss()
	mon = Get_Monitor(monitor)
	screen_shot = sct.grab(mon)
	screen_shot = numpy.asanyarray(screen_shot)
	screen_shot = cv2.cvtColor(screen_shot, flags)
	return screen_shot

#----------------------------------------------------------------------
def Build_Widget_From_Ui_File(ui_file_name,loader):
	""""""
	ui_file = QFile(ui_file_name)

	if not ui_file.open(QIODevice.ReadOnly):
		print("Cannot open {}: {}".format(ui_file_name, ui_file.errorString()))
	else:
		widget = loader.load(ui_file, None)
		ui_file.close()
		if not widget:
			print(loader.errorString())
			return None
		else:
			return widget
	return None
#----------------------------------------------------------------------
def Load_Bloxburg_Auto_Fishing_UI():
	""""""
	global UI_LOADER

	current_dir = os.path.dirname(__file__)
	file_ui = list(glob.glob(f"{current_dir}/**/Bloxburg_Fishing.ui"))[0]
	#file_ui = os.path.join(current_dir,"UI_Files\\Bloxburg_Fishing.ui")
	widget = Build_Widget_From_Ui_File(file_ui, UI_LOADER)
	isinstance(widget,QWidget)
	return widget


#----------------------------------------------------------------------
def get_bobber_Tops():
	""""""
	res = []
	for img in glob.glob(f"{_this_dir}/**/Ball_*.png"):
		res.append(Create_CV2_Image(img))
	return res


########################################################################
class Simple_Rectangle(object):
	""""""
	#----------------------------------------------------------------------
	def __init__(self,top,left,width,height):
		"""Constructor"""
		self.top     = top
		self.left    = left
		self.width   = width
		self.height  = height
	#----------------------------------------------------------------------
	@property
	def top_left(self):
		""""""
		return (self.top,self.left)

########################################################################
class Main_Window(QWidget):
	def __init__(self,parent=None):
		""""""
		#----------------------------------------------------------------------
		def Build_Area_Rectangle():
			""""""
			width       = self.ui_widget.Bottom_Slider.value() - self.ui_widget.Top_Slider.value()
			height      = self.ui_widget.Right_Slider.value() - self.ui_widget.Left_Slider.value()
			self.rect   = Simple_Rectangle(self.ui_widget.Top_Slider.value(), self.ui_widget.Left_Slider.value(), width, height)
		
		#----------------------------------------------------------------------
		def Setup_Connections():
			for slider in [self.ui_widget.Bottom_Slider,self.ui_widget.Left_Slider,self.ui_widget.Right_Slider,self.ui_widget.Top_Slider]:
				slider.valueChanged.connect(self._Update_Rect_On_Slider_Changed)
			
			self.ui_widget.Start_Fishing_Button.clicked.connect(self.start_stop_Fishing_Timer)
			self.ui_widget.Show_Tracker_Button.clicked.connect(self.start_stop_Tracking_Window_Timer)
			self.ui_widget.Mouse_Location_Setup_Button.clicked.connect(self._Setup_Mouse_Location_Selection)
			self.ui_widget.Set_Cast_Pull_Location_Button.clicked.connect(self._Set_Cast_Pull_Location)
			self.ui_widget.Window_Size_comboBox.currentIndexChanged[str].connect(self._Update_On_Window_Size_comboBox_Changed)
			
		def show_tracker_button_hot_key_callback(keyevent):
			if self.ui_widget.Show_Tracker_Button.isEnabled():
				self.ui_widget.Show_Tracker_Button.click()
		def start_stop_fishing_hot_key_callback(keyevent):
			if self.ui_widget.Start_Fishing_Button.isEnabled():
				self.ui_widget.Start_Fishing_Button.click()
		
		super(Main_Window,self).__init__(parent)
		self.setWindowFlags(Qt.WindowStaysOnTopHint)
		self.layout = QVBoxLayout()
		self.ui_widget = Load_Bloxburg_Auto_Fishing_UI()
		keyboard.on_press_key("F5", show_tracker_button_hot_key_callback, suppress=False)
		keyboard.on_press_key("F4", start_stop_fishing_hot_key_callback, suppress=False)
		#self.start_fishing_shortcut = QShortcut(QKeySequence(self.tr("`", "Test")),self)		
		#self.start_fishing_shortcut.activated.connect(self.start_stop_Tracking_Window_Timer)
		
		self.layout.addWidget(self.ui_widget)
		self.setLayout(self.layout)
		self._cast_pull_button_location = None
		self._sleeping = False
		self.screen_shot_image = None
		self._check_for_fish_timer = None
		self._proccess_fish_timer = None
		self._is_proccessing_fish = False
		self._casting_pole_timer  = None
		self._is_casting_pole     = False
		self._update_tracker_window_timer = None
		self.first_run = True
		self.bobber_tops = get_bobber_Tops()
		
		img = list(glob.glob(f"{_this_dir}/**/Pull_Button.jpg"))[0]
		self.Pull_Button_icon = Create_CV2_Image(img)
		
		img = list(glob.glob(f"{_this_dir}/**/Cast_Button.png"))[0]
		self.Cast_Button_icon = Create_CV2_Image(img)
		
		Setup_Connections()
		Build_Area_Rectangle()
		
		self.addAction(self.ui_widget.actionPause_Tracking)
		self.addAction(self.ui_widget.actionShow_Tracker)
		self.addAction(self.ui_widget.actionHide_Tracker)
	#----------------------------------------------------------------------
	@Slot(str)
	def _Update_On_Window_Size_comboBox_Changed(self,val):
		""""""
		wh =  int(val)
		geo = self.geometry()
		geo.setWidth(wh)
		geo.setHeight(wh)
		self.setGeometry(geo)
		self.ui_widget.setGeometry(geo)
		self.setMaximumSize(wh, wh)
		self.setMinimumSize(wh, wh)
		self.resize(wh, wh)
	#----------------------------------------------------------------------
	def _Update_Rect_On_Slider_Changed(self):
		""""""
		if not self.ui_widget.Top_Slider.value() >= self.ui_widget.Bottom_Slider.value():
			if not self.ui_widget.Left_Slider.value() >= self.ui_widget.Right_Slider.value():
				self.rect.top = self.ui_widget.Top_Slider.value()
				self.rect.left = self.ui_widget.Left_Slider.value()
				self.rect.width = self.ui_widget.Bottom_Slider.value() - self.ui_widget.Top_Slider.value()
				self.rect.height = self.ui_widget.Right_Slider.value() - self.ui_widget.Left_Slider.value()
				self.Take_Screen_Shot()
		
	#----------------------------------------------------------------------
	def Set_Rect_Slider_Locations(self,rect:Rect):
		""""""
		self.ui_widget.Top_Slider.setValue(rect.top_left.x)
		self.ui_widget.Left_Slider.setValue(rect.top_left.y)
		self.ui_widget.Bottom_Slider.setValue(rect.bottom_right.x)
		self.ui_widget.Right_Slider.setValue(rect.bottom_right.y)
		self._Update_Rect_On_Slider_Changed()
		self._mouse_point_collector = None

	#----------------------------------------------------------------------
	def _Build_Mouse_Click_Locations(self):
		""""""
		if not self._click_count:
			self.pos_A = pyautogui.position()
			self._click_count += 1
		else:
			self.pos_B = pyautogui.position()
			mouse.unhook_all()
			
			rect = Rect(self.pos_A,self.pos_B)
			self.Set_Rect_Slider_Locations(rect)
			
	#----------------------------------------------------------------------
	def _Setup_Mouse_Location_Selection(self):
		""""""
		mouse.unhook_all()
		self._click_count = 0
		self.mouse_callback = mouse.on_click(self._Build_Mouse_Click_Locations)
		
	#----------------------------------------------------------------------
	def _Set_Cast_Pull_Location(self):
		""""""
		#----------------------------------------------------------------------
		def set_location():
			self._cast_pull_button_location = pyautogui.position()
			mouse.unhook_all()
			self.ui_widget.Start_Fishing_Button.setEnabled(True)
		self.mouse_callback = mouse.on_click(set_location)
		
	#----------------------------------------------------------------------
	def Move_to_cast_pull_button(self):
		""""""
		if self._cast_pull_button_location != None:
			pyautogui.moveTo(self._cast_pull_button_location)
	#----------------------------------------------------------------------
	def Take_Screen_Shot(self):
		""""""
		self.Update_Sreen_Shot()
		cv2.imwrite(f"{_this_dir}/Screen_Shots/screen_grab_with_rec.jpg",self.screen_shot_image)
		pixmap = QPixmap(f"{_this_dir}/Screen_Shots/screen_grab_with_rec.jpg")
		image = pixmap.toImage()
		geo = self.ui_widget.Screen_Shot_Image.geometry()	
		size = QSize(geo.width(), geo.height())
		image = image.scaled(size, aspectMode=Qt.KeepAspectRatio, mode=Qt.SmoothTransformation)
		self.ui_widget.Screen_Shot_Image.setPixmap(QPixmap(image))
	#----------------------------------------------------------------------
	def Update_Sreen_Shot(self):
		""""""
		self.screen_shot_image = self._do_Image_Enhancments(Capture_Screen_Section(self.rect.top, self.rect.left, self.rect.width, self.rect.height))
	#----------------------------------------------------------------------
	def start_Proccess_Fish_Timer(self):
		""""""
		if self._proccess_fish_timer == None:
			self._is_proccessing_fish = True
			self._proccess_fish_timer = self.startTimer(4000)
	#----------------------------------------------------------------------
	def start_Casting_Fishing_Pole_Timer(self):
		""""""
		if self._casting_pole_timer == None:
			self._is_casting_pole = True
			self._casting_pole_timer = self.startTimer(4000)
	#----------------------------------------------------------------------
	def start_stop_Fishing_Timer(self):
		""""""
		if self._check_for_fish_timer == None:
			#self._cast_fishing_pole()
			self._check_for_fish_timer = self.startTimer(300)
			self.ui_widget.Start_Fishing_Button.setText("Stop Fishing")
			self.ui_widget.Show_Tracker_Button.setEnabled(False)
		else:
			self.killTimer(self._check_for_fish_timer)
			self._check_for_fish_timer = None
			self.ui_widget.Start_Fishing_Button.setText("Start Fishing")
			self.ui_widget.Show_Tracker_Button.setEnabled(True)
			
	#----------------------------------------------------------------------
	def start_stop_Tracking_Window_Timer(self):
		""""""
		if self._update_tracker_window_timer == None:
			self.Creat_Tracker_Window()
			self._update_tracker_window_timer = self.startTimer(300)
			self.ui_widget.Show_Tracker_Button.setText("Hide Tracker")
			self.ui_widget.Start_Fishing_Button.setEnabled(False)
		
		elif not self._update_tracker_window_timer == None:
			self.killTimer(self._update_tracker_window_timer)
			self._update_tracker_window_timer = None
			cv2.destroyAllWindows()
			self.ui_widget.Show_Tracker_Button.setText("Show Tracker")
			self.ui_widget.Start_Fishing_Button.setEnabled(True)
	
	
	#----------------------------------------------------------------------
	def _do_Image_Enhancments(self,screen_image):
		""""""
		pil_screen_image = Convert_CV2_To_Pil_Image(screen_image)
		pil_screen_image = ImageEnhance.Color(pil_screen_image).enhance(self.ui_widget.Color_Value.value())
		pil_screen_image = ImageEnhance.Brightness(pil_screen_image).enhance(self.ui_widget.Brightness_Value.value())
		pil_screen_image = ImageEnhance.Contrast(pil_screen_image).enhance(self.ui_widget.Contrast_Value.value())
		pil_screen_image = ImageEnhance.Sharpness(pil_screen_image).enhance(self.ui_widget.Sharpness_Value.value())
		
		return Convert_Pil_To_CV2_Image(pil_screen_image)
	#----------------------------------------------------------------------
	def _find_Best_Match(self,screen_image):
		""""""
		locs,vals = [],[]
		try:
			for item in self.bobber_tops:
				match_res = cv2.matchTemplate(screen_image, item, cv2.TM_CCOEFF_NORMED)
				min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match_res)
				vals.append(max_val)
				locs.append(max_loc)
			
			index       = vals.index(max(vals))
			best_loc    = locs[index]
			best_val    = vals[index]
			best_bobber = self.bobber_tops[index]
			return best_loc,best_val,best_bobber
		except:
			pass
		return None,None,None
	
	#----------------------------------------------------------------------
	def _pick_up_fish(self):
		""""""
		print("Picking Up Fish")
		if not self.ui_widget.Start_Fishing_Button.text() == "Start Fishing":
			self.Move_to_cast_pull_button() # Move the mouse to XY coordinates.
			pyautogui.doubleClick()
			self.Move_to_cast_pull_button() 
			pyautogui.doubleClick()
		self.start_Proccess_Fish_Timer()
	#----------------------------------------------------------------------
	def _cast_fishing_pole(self):
		""""""
		if not self._is_proccessing_fish:
			if not self.ui_widget.Start_Fishing_Button.text() == "Start Fishing":
				print("Casting Pole")
				self.Move_to_cast_pull_button() # Move the mouse to XY coordinates.
				pyautogui.doubleClick()
				self.Move_to_cast_pull_button() 
				pyautogui.doubleClick()
			self.start_Casting_Fishing_Pole_Timer()
		
	#----------------------------------------------------------------------
	def timerEvent(self, event):
		#----------------------------------------------------------------------
		def is_proccessing_fish(event):
			return event.timerId() == self._proccess_fish_timer
		#----------------------------------------------------------------------
		def is_casting_poll(event):
			return event.timerId() == self._casting_pole_timer
		#----------------------------------------------------------------------
		def is_checking_for_fish(event):
			return event.timerId() == self._check_for_fish_timer
		#----------------------------------------------------------------------
		def is_time_to_update_tracker_window(event):
			return event.timerId() == self._update_tracker_window_timer
		
		if is_proccessing_fish(event):
			print("Finished Picking Up Fish")
			self._is_proccessing_fish = False
			self.killTimer(self._proccess_fish_timer)
			self._proccess_fish_timer = None
			self._cast_fishing_pole()
			
		elif is_casting_poll(event):
			print("Finished Casting Pole")
			self._is_casting_pole = False
			self.killTimer(self._casting_pole_timer)
			self._casting_pole_timer = None
			
		elif is_checking_for_fish(event):
			
			screen_image             = Capture_Screen_Section(self.rect.top, self.rect.left, self.rect.width, self.rect.height,save_to_file=False)
			enhanced_screen_image    = self._do_Image_Enhancments(screen_image)
			best_loc,best_val,bobber = self._find_Best_Match(enhanced_screen_image)
			if best_val is not None:
				self.ui_widget.Match_Value.setValue(best_val)
			
			if not self._is_proccessing_fish and not self._is_casting_pole:
				if best_val <= self.ui_widget.Threshhold_Value.value():
					if not self.ui_widget.Start_Fishing_Button.text() == "Start Fishing":
						self._pick_up_fish()
			
		elif is_time_to_update_tracker_window(event):
			
			screen_image             = Capture_Screen_Section(self.rect.top, self.rect.left, self.rect.width, self.rect.height,save_to_file=False)
			
			enhanced_screen_image    = self._do_Image_Enhancments(screen_image)
			best_loc,best_val,bobber = self._find_Best_Match(enhanced_screen_image)
			if best_val is not None:
				self.ui_widget.Match_Value.setValue(best_val)
			if bobber is not None:
				w  = bobber.shape[1]
				h  = bobber.shape[0]
				
				res = cv2.rectangle(enhanced_screen_image, best_loc, (best_loc[0] + w, best_loc[1] + h) ,(0,255,255), thickness=2)
				if self.ui_widget.Match_Value.value() < self.ui_widget.Threshhold_Value.value():
					self.ui_widget.Pickup_Threshold_frame.setStyleSheet('background-color: rgb(255, 0, 0);\nfont: 75 8pt "MS Shell Dlg 2";\ncolor: rgb(0, 0, 0);')
				else:
					self.ui_widget.Pickup_Threshold_frame.setStyleSheet('')
				self.show_To_Tracker_Display(res)
			
	#----------------------------------------------------------------------
	def Creat_Tracker_Window(self):
		""""""
		cv2.namedWindow("Tracker Display")
		cv2.setWindowProperty("Tracker Display", cv2.WND_PROP_TOPMOST, 1)
	#----------------------------------------------------------------------
	def show_To_Tracker_Display(self,image):
		""""""
		cv2.imshow("Tracker Display", image)

#img = cv2.imread(r'd:\Wing_Projects\Learning_Image_Recognition\Test_Images\Bobber_Top.jpg')
#cv2.imshow('My Image', img)
#while True:
	#k = cv2.waitKey(0) & 0xFF
	#print(k)
	#if k == 27:
		#cv2.destroyAllWindows()
		#break

if __name__ == '__main__':
	mon = Get_Monitor(1)
	mon_w = mon["width"]
	mon_h = mon["height"]
	w = mon_w / 4 + 97
	h = mon_h / 4 + 267
	
	app = QApplication(sys.argv)
	mainWin = Main_Window()
	geo = mainWin.geometry()
	wh =  int(mainWin.ui_widget.Window_Size_comboBox.currentText())
	geo.setWidth(wh)
	geo.setHeight(wh)
	mainWin.setGeometry(geo)
	mainWin.ui_widget.setGeometry(geo)
	mainWin.setMaximumSize(wh, wh)
	mainWin.setMinimumSize(wh, wh)
	
	mainWin.setWindowTitle("Mayaenite's Gone Fishing")
	
	mainWin.show()
	sys.exit(app.exec_())
	