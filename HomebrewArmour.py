# Lukas Freudenberg
# 
# 2025-11-01, ver.1.0
# 
# HomebrewArmour includes and starts a GUI for managing the homebrew armour system for the campaign "Tyrannei der Drachen" run by Lukas Freudenberg.

# Changelog
# 2025-11-01: Initial functional version
# 2025-10-22: Started development

import time
import os
import tkinter as tk
from LFLib import LFLib as L

# Helper function to get the index of an element in a list.
# This function recursively goes through all elements of a list.
# If a list contains sublists, they will be searched for the items.
# 
# @param searchList The list containing the sublists to search.
# @param element The element to look for.
# @return The index in searchList where element was found. If searchList contains sublists, this is the index of the sublist containing element.
def indexInList(searchList, element):
	# Iterate over all entries
	for index, entry in enumerate(searchList):
		# Check if entry is a list itself
		if isinstance(entry, list):
			# If so, recursively look in the sublist
			foundIndex = indexInList(entry, element)
			if not None == foundIndex:
				# return the first instance found - this can greatly improve performance for larger lists
				return index
		# Check if element matches list entry
		elif entry == element:
			return index
	# If this point is reached, the element wasn't found
	return None

# Helper function to validate integer input
def validateIntegerInput(character):
	if character.isdigit() or character == "":
		return True
	return False

class HBA:
	# Constructor method
	def __init__(self):
		# Default styles for widgets
		# Background colour
		self.bgc = "#101010"
		# Text colour
		self.fgc = "#ffffff"
		# Remove button colour
		self.rbc = "#CD0000"
		# Remove button text colour
		self.rbtc = "#000000"
		# Text font
		self.font = "Arial"
		# Font size for control buttons
		self.cfsize = 44
		# Font size for general labels
		self.glfsize = 14
		# Font size for remove button
		self.rbfsize = 14
		# Font size for reduced damage label
		self.rdlfsize = 20
		# Font size for damage buttons
		self.dbfsize = 44
		# Path of the currently active armour file
		self.armour = "./armour.hba"
		
		# Initialize all components
		# Create control window
		self.window = tk.Tk()
		L.window = self.window
		self.window.title("HBA")
		# ToDo: implement functionality to switch themes - but not using ttk widgets if possible
		self.window["bg"] = self.bgc
		self.window.rowconfigure(2, weight=1)
		self.window.columnconfigure(0, weight=1)
		# List with all UI elements
		self.uiElements = []
		# List with the grid parameters of all UI elements
		self.uiGridParams = []
		
		# Create label for version number
		self.vLabel = tk.Label(master=self.window, text="HBA by Lukas Freudenberg v0.1", bg=self.bgc, fg=self.fgc)
		self.uiElements.append(self.vLabel)
		self.uiGridParams.append([0, 0, 1, 1, "NESW"])
		# Create frame for genaral controls
		self.controlFrame = tk.Frame(master=self.window, bg=self.bgc)
		self.uiElements.append(self.controlFrame)
		self.uiGridParams.append([1, 0, 1, 2, "NESW"])
		self.controlFrame.columnconfigure(3, weight=1)
		# Create button for loading armour definitions
		self.loadButton = tk.Button(master=self.controlFrame, bg=self.bgc, text=u"\U0001F4C2", font=(self.font, self.cfsize))
		self.uiElements.append(self.loadButton)
		self.uiGridParams.append([0, 0, 1, 1, "NESW"])
		self.loadButton.bind("<Button-1>", lambda event: self.loadArmourDefinitions(armour=None))
		# Create button for loading a full configuration
		self.loadConfigButton = tk.Button(master=self.controlFrame, bg=self.bgc, text=u"\U0001F4C2", font=(self.font, self.cfsize))
		self.uiElements.append(self.loadConfigButton)
		self.uiGridParams.append([0, 1, 1, 1, "NESW"])
		self.loadConfigButton.bind("<Button-1>", lambda event: self.loadConfiguration(configfile=None))
		# Create button for saving player character configuration
		self.saveButton = tk.Button(master=self.controlFrame, bg=self.bgc, text=u"\U0001F4BE", font=(self.font, self.cfsize))
		self.uiElements.append(self.saveButton)
		self.uiGridParams.append([0, 2, 1, 1, "NESW"])
		self.saveButton.bind("<Button-1>", lambda event: self.saveSettings())
		# Create spacer
		self.spacerLabel = tk.Label(master=self.window, bg=self.bgc)
		self.uiElements.append(self.spacerLabel)
		self.uiGridParams.append([0, 3, 1, 1, "NESW"])
		
		# Array that holds the loaded armour definitions
		self.loadedArmourDefinitions = [] 
		# Load armour definitions
		self.loadArmourDefinitions()
		
		# Array that holds the characters
		self.characters = []
		
		# Create scrollable canvas
		canvas = tk.Canvas(self.window, bg=self.bgc)
		canvas.grid(row=2, column=0, sticky="NESW")
		# Create scrollbar
		scroller = tk.Scrollbar(self.window, width=50, command=canvas.yview)
		scroller.grid(row=2, column=1, sticky="NESW")
		canvas.config(yscrollcommand=scroller.set)
		# Create window to scroll inside the canvas
		self.scrollFrame = tk.Frame(canvas, bg=self.bgc)
		self.scrollFrame.columnconfigure(0, weight=1)
		scrollFrameID = canvas.create_window((0, 0), window=self.scrollFrame, anchor="nw")
		# Update scroll area automatically
		self.scrollFrame.bind("<Configure>", lambda event: canvas.config(scrollregion=canvas.bbox("all")))
		canvas.bind("<Configure>", lambda event: self.updateFrame(canvas, scrollFrameID))
		# Set up scrolling binds
		# Mouse wheel scrolling
		canvas.bind_all("<MouseWheel>", lambda event: self.scrollMouse(canvas))
		# Arrow key scrolling
		canvas.bind_all("<Up>", lambda event: canvas.yview_scroll(-1, 'units'))
		canvas.bind_all("<Down>", lambda event: canvas.yview_scroll(1, "units"))
		# Touchpad scrolling (only works on Linux)
		self.window.bind('<Button-4>', lambda event: canvas.yview_scroll(-1, 'units'))
		self.window.bind('<Button-5>', lambda event: canvas.yview_scroll(1, 'units'))
        
		# Create button to add a character
		self.addCharacterButton = tk.Button(master=self.scrollFrame, text=u"\U0000002B", bg=self.bgc, fg=self.fgc, font=(self.font, self.cfsize))
		self.uiElements.append(self.addCharacterButton)
		self.uiGridParams.append([0, 0, 1, 1, "NESW"])
		self.addCharacterButton.grid(row=0, column=0, sticky="NESW")
		self.addCharacterButton.bind("<Button-1>", lambda event: self.addCharacter())
		
		# Display the widgets
		L.buildUI(self.uiElements, self.uiGridParams)
		# Maximize the window
		self.window.attributes("-zoomed", True)
		# Add event for closing the window
		self.window.protocol("WM_DELETE_WINDOW", self.quit)
		
		# Execute mainloop of the window
		self.window.mainloop()
	
	# Loads the armour definitions from a file.
	# The user can select a file or the default definitions will be used.
	# Example for a definitions file:
	#	# This line is a comment and will be ignored when loading the file.
	#	
	#	# Name of the armour type (must be unique)
	#	Leather
	#	# Reduction of piercing damage
	#		piercing: 1
	#	# Reduction of slashing damage
	#		slashing: 2
	#	# Reduction of bludgeoning damage
	#		bludgeoning: 1
	#	# Reduction of damage from spells that require an attack roll
	#		toHitSpells: 2
	#	
	#	Chainmail
	#		piercing: 2
	#		slashing: 5
	#		bludgeoning: 2
	#		toHitSpells: 3
	# 
	# This file defines two armour types: "Leather" and "Chainmail".
	# The "Leather" armour reduces piercing damage by 1, slashing damage by 2,
	# bludgeoning damage by 1 and damage from spells that require an attack roll (like Firebolt) by 2.
	# 
	# @param armour The path to the armour file. By default, the file for the default armour definitions will be used.
	def loadArmourDefinitions(self, armour="./default.hba", event=None):
		# Check whether to load default armour
		if armour == "./default.hba":
			# Check if default armour file exists; if not, create it
			if not os.path.exists(armour):
				L.pln("Default armour definitions don't exist.")
				default = open(armour, "w")
				default.writelines([
					"# This file defines different armour types. The syntax is as follows:\n"
					"# \n"
					"# NAME OF ARMOUR (must be unique)\n"
					"# 	piercing: NUMERIC REDUCTION VALUE\n"
					"# 	slashing: NUMERIC REDUCTION VALUE\n"
					"# 	bludgeoning: NUMERIC REDUCTION VALUE\n"
					"# 	toHitSpells: NUMERIC REDUCTION VALUE\n"
				])
				default.close()
		# Check if a path was provided
		elif armour == None:
			armour = tk.filedialog.askopenfilename(filetypes=[("Homebrew Armour files", "*.hba")])
			# If no armour definitions file was selected, don't load any
			if armour == "" or armour == ():
				L.pln("No armour file selected.")
				return
		else:
			# Check for correct data format
			if not isinstance(armour, str):
				L.pln("Path for armour file must be a string.")
				return
			# Check if path exists
			if not os.path.exists(armour):
				L.pln("Armour file: \"", armour, "\" doesn't exist.")
				return
		# Set the path for the current armour file
		self.armour = armour
		# Open the armour file
		armour = open(armour, "r")
		# Current index in the loaded armour array - this starts at -1 for looping reasons
		armourIndex = -1
		# Load armour definitions
		for line in armour.readlines():
			# Ignore the line if it is a comment (first character being "#") or empty
			if line[0] == "#" or line[0] == "\n":
				continue
			# Check if line declares piercing reduction
			elif len(line) > 11 and line[:11] == "	piercing: ":
				# check if an armour type has been given
				if armourIndex >= 0:
					piercing = line[11:-1]
					try:
						piercing = int(piercing)
						if piercing < 0:
							L.pln("Value for piercing must be a non-negative integer.")
						else:
							# load value into array
							self.loadedArmourDefinitions[armourIndex][1] = piercing
					except ValueError:
						L.pln("Value for piercing must be a non-negative integer.")
				else:
					L.pln("You must give an armour type a name before defining its stats.")
			# Check if line declares slashing reduction
			elif len(line) > 11 and line[:11] == "	slashing: ":
				# check if an armour type has been given
				if armourIndex >= 0:
					slashing = line[11:-1]
					try:
						slashing = int(slashing)
						if slashing < 0:
							L.pln("Value for slashing must be a non-negative integer.")
						else:
							# load value into array
							self.loadedArmourDefinitions[armourIndex][2] = slashing
					except ValueError:
						L.pln("Value for slashing must be a non-negative integer.")
				else:
					L.pln("You must give an armour type a name before defining its stats.")
			# Check if line declares bludgeoning reduction
			elif len(line) > 14 and line[:14] == "	bludgeoning: ":
				# check if an armour type has been given
				if armourIndex >= 0:
					bludgeoning = line[14:-1]
					try:
						bludgeoning = int(bludgeoning)
						if bludgeoning < 0:
							L.pln("Value for bludgeoning must be a non-negative integer.")
						else:
							# load value into array
							self.loadedArmourDefinitions[armourIndex][3] = bludgeoning
					except ValueError:
						L.pln("Value for bludgeoning must be a non-negative integer.")
				else:
					L.pln("You must give an armour type a name before defining its stats.")
			# Check if line declares toHitSpells reduction
			elif len(line) > 14 and line[:14] == "	toHitSpells: ":
				# check if an armour type has been given
				if armourIndex >= 0:
					toHitSpells = line[14:-1]
					try:
						toHitSpells = int(toHitSpells)
						if toHitSpells < 0:
							L.pln("Value for toHitSpells must be a non-negative integer.")
						else:
							# load value into array
							self.loadedArmourDefinitions[armourIndex][4] = toHitSpells
					except ValueError:
						L.pln("Value for toHitSpells must be a non-negative integer.")
				else:
					L.pln("You must give an armour type a name before defining its stats.")
			# Otherwise the line gives the name of an armour type that will be defined by the following lines
			else:
				# increment index
				armourIndex += 1
				# Armour name is the entire line (minus newline character)
				armourName = line[:-1]
				# Add armour with empty stats to the loaded definitions
				self.loadedArmourDefinitions.append([armourName, 0, 0, 0, 0])
			
		# Close armour definitions file
		armour.close()
		
		L.pln("Armour definitions loaded.")
	
	# Creates a new character and all its controls.
	# 
	# @param name The name of the character to add.
	# @return the character label used for loading a character from a file.
	def addCharacter(self, name=None, event=None):
		# Get index of the new character
		characterIndex = len(self.characters)
		# Create frame for the character
		characterFrame = tk.Frame(master=self.scrollFrame, bg=self.bgc)
		# Maybe this is bad - there should be no need to rebuild the UI and this leads to difficulties when moving players around
		self.uiElements.append(characterFrame)
		self.uiGridParams.append([characterIndex, 0, 1, 1, "NESW"])
		characterFrame.grid(row=characterIndex, column=0, sticky="NESW")
		# This needs to fit whatever I want to be the scalable UI-element. It definetely has to exist, if nothing else then for the character name
		#characterFrame.columnconfigure(3, weight=1)
		# Create button to remove the character
		removeButton = tk.Button(master=characterFrame, text=u"\U00002716", bg=self.rbc, fg=self.rbtc, font=(self.font, self.rbfsize))
		self.uiElements.append(removeButton)
		self.uiGridParams.append([0, 0, 1, 1, "WE"])
		removeButton.bind("<Button-1>", lambda event: self.removeCharacter(name, characterFrame))
		removeButton.grid(row=0, column=0, sticky="NESW")
		# If no name was given, generate one
		if name == None:
			name = "character " + str(characterIndex + 1)
		# Add the character to the global character list
		self.characters.append([name, [], [], [], [], [], []])
		# Create character label
		characterLabel = tk.Label(master=characterFrame, bg=self.bgc, fg=self.fgc, text=name, font=(self.font, self.glfsize), anchor="w")
		self.uiElements.append(characterLabel)
		self.uiGridParams.append([0, 1, 1, 6, "NESW"])
		characterLabel.bind("<Button-1>", lambda event: self.loadCharacter(characterLabel))
		characterLabel.grid(row=0, column=1, columnspan=6, sticky="NESW")
		# Create label for attack input field
		attackLabel = tk.Label(master=characterFrame, bg=self.bgc, fg=self.fgc, text="ATK", font=(self.font, self.rdlfsize), anchor="w")
		self.uiElements.append(attackLabel)
		self.uiGridParams.append([1, 0, 1, 1, "NESW"])
		attackLabel.grid(row=1, column=0, sticky="NESW")
		# Register validation function for integer input
		vcmd = self.window.register(validateIntegerInput)
		# Create input field for the attack roll
		attackInput = tk.Entry(master=characterFrame, bg=self.bgc, fg=self.fgc, font=(self.font, self.rdlfsize), width=3, validate="key", validatecommand=(vcmd, "%P"))
		self.uiElements.append(attackInput)
		self.uiGridParams.append([2, 0, 1, 1, "NESW"])
		attackInput.grid(row=2, column=0, sticky="NESW")
		# Create label for damage input field
		damageLabel = tk.Label(master=characterFrame, bg=self.bgc, fg=self.fgc, text="DMG", font=(self.font, self.rdlfsize), anchor="w")
		self.uiElements.append(damageLabel)
		self.uiGridParams.append([1, 1, 1, 1, "NESW"])
		damageLabel.grid(row=1, column=1, sticky="NESW")
		# Create input field for the damage total
		damageInput = tk.Entry(master=characterFrame, bg=self.bgc, fg=self.fgc, font=(self.font, self.rdlfsize), width=4, validate="key", validatecommand=(vcmd, "%P"))
		self.uiElements.append(damageInput)
		self.uiGridParams.append([2, 1, 1, 1, "NESW"])
		damageInput.grid(row=2, column=1, sticky="NESW")
		# Create button for calculating piercing damage: 🏹 (1F3F9)
		piercingButton = tk.Button(master=characterFrame, text=u"\U0001F3F9", fg=self.fgc, bg=self.bgc, font=(self.font, self.dbfsize))
		self.uiElements.append(piercingButton)
		self.uiGridParams.append([1, 2, 2, 1, "NESW"])
		piercingButton.grid(row=1, column=2, rowspan=2, sticky="NESW")
		# Create button for calculating slashing damage: 🪓 (1FA93)
		slashingButton = tk.Button(master=characterFrame, text=u"\U0001FA93", fg=self.fgc, bg=self.bgc, font=(self.font, self.dbfsize))
		self.uiElements.append(slashingButton)
		self.uiGridParams.append([1, 3, 2, 1, "NESW"])
		slashingButton.grid(row=1, column=3, rowspan=2, sticky="NESW")
		# Create button for calculating bludgeoning damage: 🔨 (1F528)
		bludgeoningButton = tk.Button(master=characterFrame, text=u"\U0001F528", fg=self.fgc, bg=self.bgc, font=(self.font, self.dbfsize))
		self.uiElements.append(bludgeoningButton)
		self.uiGridParams.append([1, 4, 2, 1, "NESW"])
		bludgeoningButton.grid(row=1, column=4, rowspan=2, sticky="NESW")
		# Create button for calculating damage from spells that require an attack roll: 🪄 (1FA84)
		spellButton = tk.Button(master=characterFrame, text=u"\U0001FA84", fg=self.fgc, bg=self.bgc, font=(self.font, self.dbfsize))
		self.uiElements.append(spellButton)
		self.uiGridParams.append([1, 5, 2, 1, "NESW"])
		spellButton.grid(row=1, column=5, rowspan=2, sticky="NESW")
		# Create label for reduced damage title
		reducedTitleLabel = tk.Label(master=characterFrame, bg=self.bgc, fg=self.fgc, text="Reduced DMG", font=(self.font, self.rdlfsize), anchor="w")
		self.uiElements.append(reducedTitleLabel)
		self.uiGridParams.append([1, 6, 1, 1, "NESW"])
		reducedTitleLabel.grid(row=1, column=6, sticky="NESW")
		# Create label that will display the reduced damage
		reducedDamageLabel = tk.Label(master=characterFrame, bg=self.bgc, fg=self.fgc, text="0", font=(self.font, self.rdlfsize), anchor="w")
		self.uiElements.append(reducedDamageLabel)
		self.uiGridParams.append([2, 6, 1, 1, "NESW"])
		reducedDamageLabel.grid(row=2, column=6, sticky="NESW")
		# Bind buttons to refresh label functions
		piercingButton.bind("<Button-1>", lambda event: self.calculateDamage(characterLabel, attackInput, damageInput, "piercing", reducedDamageLabel))
		slashingButton.bind("<Button-1>", lambda event: self.calculateDamage(characterLabel, attackInput, damageInput, "slashing", reducedDamageLabel))
		bludgeoningButton.bind("<Button-1>", lambda event: self.calculateDamage(characterLabel, attackInput, damageInput, "bludgeoning", reducedDamageLabel))
		spellButton.bind("<Button-1>", lambda event: self.calculateDamage(characterLabel, attackInput, damageInput, "toHitSpells", reducedDamageLabel))
		
		# Update window to get correct size for the scale
		self.window.update_idletasks()
		
		# Create separator between this character and next element 
		sepLabel = tk.Label(master=characterFrame, bg=self.bgc)
		self.uiElements.append(sepLabel)
		self.uiGridParams.append([3, 0, 1, 7, "NESW"])
		sepLabel.grid(row=3, column=0, columnspan=7, sticky="NESW")
		# Move button to add a new character
		self.uiGridParams[self.uiElements.index(self.addCharacterButton)] = [characterIndex+1, 0, 1, 1, "NESW"]
		self.addCharacterButton.grid(row=characterIndex+1, column=0, sticky="NESW")
		
		return characterLabel
	
	# Loads a character from a configuration file.
	# 
	# @param frame The frame of the character to load the configuration into.
	# @param character The path to the character file. If no path is given, the user will be prompted for a file dialogue.
	def loadCharacter(self, characterLabel, character=None, event=None):
		# Check if a path was provided
		if character == None:
			character = tk.filedialog.askopenfilename(filetypes=[("Character files", "*.char")])
			# If no character file was selected, don't load any
			if character == "" or character == ():
				L.pln("No character file selected.")
				return
		else:
			# Check for correct data format
			if not isinstance(character, str):
				L.pln("Path for character file must be a string.")
				return
			# Check if path exists
			if not os.path.exists(character):
				L.pln("Character file: \"", character, "\" doesn't exist.")
				return
		# Get old character name from label
		characterName = characterLabel.cget("text")
		# Calculate character index in global array
		characterIndex = indexInList(self.characters, characterName)
		# Remove any old information the character may have had before (except the name)
		for index, _ in enumerate(self.characters[characterIndex]):
			self.characters[characterIndex][index] = []
		self.characters[characterIndex][0] = characterName
		# Open the character file
		character = open(character, "r")
		# Character name as read from file
		characterName = None
		# Current armour slot index
		armourSlotIndex = None
		# Load character definition
		for line in character.readlines():
			# Ignore the line if it is a comment (first character being "#") or empty
			if line[0] == "#" or line[0] == "\n":
				continue
			# Check if line contains the character name
			elif len(line) > 5 and line[:5] == "name=":
				# Set character name
				characterName = line[5:-1]
				# Update global array
				self.characters[characterIndex][0] = characterName
				# Update label
				characterLabel.config(text=characterName)
			# Check if line declares footwear section
			elif len(line) > 4 and line[:4] == "feet":
				armourSlotIndex = 1
			# Check if line declares legwear section
			elif len(line) > 4 and line[:4] == "legs":
				armourSlotIndex = 2
			# Check if line declares main bodywear section
			elif len(line) > 5 and line[:5] == "torso":
				armourSlotIndex = 3
			# Check if line declares armguard section
			elif len(line) > 4 and line[:4] == "arms":
				armourSlotIndex = 4
			# Check if line declares glove section
			elif len(line) > 5 and line[:5] == "hands":
				armourSlotIndex = 5
			# Check if line declares headwear section
			elif len(line) > 4 and line[:4] == "head":
				armourSlotIndex = 6
			# Check if line declares an armour item
			elif len(line) > 2 and line[0] == "	":
				# Check if the armour slot has been given
				if armourSlotIndex >= 1:
					self.characters[characterIndex][armourSlotIndex].append(line[1:-1])
				else:
					L.pln("You must specify an armour slot before listing equipped items.")
			else:
				# Invalid syntax, line will be skipped
				L.pln(line[:-1], " has an invalid syntax and will not be processed.")
				continue
			
		# Close character file
		character.close()
		
		L.pln(characterName, " loaded.")
	
	# Loads a configuration for the app from a file.
	# 
	# @param configfile The path to the configuration file. If no path is given, the user will be prompted for a file dialogue.
	def loadConfiguration(self, configfile=None, event=None):
		# Check if a path was provided
		if configfile == None:
			configfile = tk.filedialog.askopenfilename(filetypes=[("HBA configuration files", "*.hacfg")])
			# If no configuration file was selected, don't load any
			if configfile == "" or configfile == ():
				L.pln("No configuration file selected.")
				return
		else:
			# Check for correct data format
			if not isinstance(configfile, str):
				L.pln("Path for configuration file must be a string.")
				return
			# Check if path exists
			if not os.path.exists(configfile):
				L.pln("Configuration file: \"", configfile, "\" doesn't exist.")
				return
		# Open the configuration file
		configfile = open(configfile, "r")
		# Load app configuration
		for line in configfile.readlines():
			# Ignore the line if it is a comment (first character being "#") or empty
			if line[0] == "#" or line[0] == "\n":
				continue
			# Check if line defines an armour definitions file
			elif len(line) > 7 and line[:7] == "armour=":
				# Load armour definitions file
				self.loadArmourDefinitions(armour=line[7:-1])
			elif len(line) > 10 and line[:10] == "character=":
				# Create character
				charLabel = self.addCharacter()
				# Load character configuration
				self.loadCharacter(charLabel, line[10:-1])
			else:
				# Invalid syntax, line will be skipped
				L.pln(line[:-1], " has an invalid syntax and will not be processed.")
				continue
	
	# Updates the scroll frame of a scene to match the size of the canvas.
	# 
	# @param canvas The canvas, that the frame lives in.
	# @param frameID ID of the frame window.
	def updateFrame(self, canvas, frameID, event=None):
		canvas.itemconfig(frameID, width=canvas.winfo_width())
	
	# Scrolls the scene with the mouse wheel.
	# 
	# @param canvas The canvas to scroll.
	def scrollMouse(self, canvas, event=None):
		canvas.yview_scroll(int(-1*(event.delta/120)), "units")
		L.pln(canvas.winfo_master())
	
	# Calculates the reduced damage.
	# 
	# @param characterLabel Label with the name of the character whose stats to reference.
	# @param attackInput Input field for the attack roll.
	# @param damageInput Input field for the damage roll.
	# @param damageType Type of the damage: "piercing", "slashing", "bludgeoning" or "toHitSpells".
	# @param reducedDamageLabel Label to display the calculated reduced damage.
	def calculateDamage(self, characterLabel, attackInput, damageInput, damageType, reducedDamageLabel, event=None):
		# Determine hit target
		target = None
		targetIndex = None
		targetDigit = int(attackInput.get()) % 10
		if 0 == targetDigit:
			target = "feet"
			targetIndex = 1
		elif (1 <= targetDigit) and (2 >= targetDigit):
			target = "legs"
			targetIndex = 2
		elif (3 <= targetDigit) and (5 >= targetDigit):
			target = "torso"
			targetIndex = 3
		elif 6 == targetDigit:
			target = "arms"
			targetIndex = 4
		elif 7 == targetDigit:
			target = "hands"
			targetIndex = 5
		elif (8 <= targetDigit) and (9 >= targetDigit):
			target = "head"
			targetIndex = 6
		else:
			# This should be impossible
			L.pln("Error: hit target ", targetDigit, " is undefined.")
		# Get character name from label
		characterName = characterLabel.cget("text")
		L.pln(characterName, " is hit on their ", target, ".")
		# Get character armour for calculated target
		characterIndex = indexInList(self.characters, characterName)
		armour = self.characters[characterIndex][targetIndex]
		# Tracks the reduced damage
		reducedDamage = int(damageInput.get())
		# Iterate over all armour layers
		for armourLayer in armour:
			# find armour layer in definitions
			armourIndex = indexInList(self.loadedArmourDefinitions, armourLayer)
			if None == armourIndex:
				L.pln("Error: ", characterName, " is wearing undefined armour: ", armourLayer)
			else:
				damageTypeIndex = None
				if "piercing" == damageType:
					damageTypeIndex = 1
				elif "slashing" == damageType:
					damageTypeIndex = 2
				elif "bludgeoning" == damageType:
					damageTypeIndex = 3
				elif "toHitSpells" == damageType:
					damageTypeIndex = 4
				else:
					# This should never happen.
					L.pln("Error: Damage type ", damageType, " is undefined.")
				# Pull value from loaded values
				reductionValue = self.loadedArmourDefinitions[armourIndex][damageTypeIndex]
				L.pln(armourLayer, " reduces ", damageType, " damage by ", reductionValue, ".")
				# Subtract from damage total
				reducedDamage -= reductionValue
		# Damage can't be negative
		if 0 > reducedDamage:
			reducedDamage = 0
		# Update label
		reducedDamageLabel.config(text=reducedDamage)
	
	# Callback for quitting the program
	def quit(self, event=None):
		#for scene in self.players:
		#	for player in scene:
		#		player.terminate()
		#time.sleep(0.5)
		#L.pln(threading.enumerate())
		self.window.destroy()

# Initialize the gui
gui = HBA()
