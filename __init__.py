# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2008-2023 NV Access Limited, Babbage B.V, Bram Duvigneau
# Later modified to use pybrlapi according to GNU GPL rules
# Copyright (C) 2025 by Dalen Bernaca

"""
This is just a bit boosted brltty driver.
"""

import os
import time
import wx
import braille
from logHandler import log
import inputCore
from typing import List
try:
	from . import pybrlapi as brlapi
except ImportError:
	brlapi = None

class BrailleDisplayDriver(braille.BrailleDisplayDriver):
	"""brltty braille display driver.
	"""
	name = "brltty2"
	description = "brltty2"
	isThreadSafe = True

	# Type info for auto property: _get_brlapi_pipes
	brlapi_pipes: List[str]

	@classmethod
	def _get_brlapi_pipes(cls) -> List[str]:
		"""Get the BrlAPI named pipes

		Every BRLTTY instance with the BrlAPI enabled will have it's own named pipe to accept API connections.
		The brlapi.Connection constructor takes either a `host:port` argument or just `:port`.
		If only a port is given, this corresponds to the number at the end of the named pipe.
		"""
		return [pipe.name for pipe in os.scandir("//./pipe/") if pipe.name.startswith(BRLAPI_NAMED_PIPE_PREFIX)]

	@classmethod
	def check(cls):
		if not bool(brlapi):
			return False
		return True

	def __init__(self):
		super().__init__()
		self._conn = brlapi.Client("192.168.1.100", auth_callback=lambda m: "nonsense\n", key_callback=self._handleKeyPresses)
		self._conn.connect()
		self._conn.enterTTYMode()
		# BRLTTY simulates key presses for braille typing keys, so let BRLTTY handle them.
		# NVDA may eventually implement this itself, but there's no reason to deny BRLTTY users this functionality in the meantime.
		#self._conn.ignoreKeys(brlapi.rangeType_type, (brlapi.KEY_TYPE_SYM,))

	def terminate(self):
		super().terminate()
		try:
			# Give BRLTTY a chance to write the last piece of data to the display.
			time.sleep(0.05)
			self._conn.leaveTTYMode()
			self._conn.close()
		except:
			pass

	def _get_displaySize (self):
		self.displaySize = ds = self._conn.getDisplaySize()
		return ds

	def _get_numCells(self):
		self.numCells = nc = self.displaySize[0]
		return nc

	def _get_numRows(self):
		self.numRows = nr = self.displaySize[1]
		return nr

	def display (self, cells: List[int]):
		self._conn.writeDots(bytes(cells))

	def _get_driverName(self):
		m = "_".join(self._conn.getModelIdentifier().split())
		self.driverName = dn = self._conn.getDriverName()+("_"+m if m else "")
		return dn

	def _handleKeyPresses(self, key):
		try:
			key = key.expandKeyCode()
		except:
			return
		wx.CallAfter(self._onKeyPress, key)

	def _onKeyPress(self, key):
		keyType = key["type"]
		if keyType == "CMD":
			command = key["command"]
			argument = key["argument"]
			try:
				inputCore.manager.executeGesture(
					InputGesture(self.driverName, command, argument)
				)
			except inputCore.NoInputGestureAction:
				pass

	gestureMap = inputCore.GlobalGestureMap({
		"globalCommands.GlobalCommands": {
			"braille_scrollBack": (f"br({name}):fwinlt",),
			"braille_scrollForward": (f"br({name}):fwinrt",),
			"braille_previousLine": (f"br({name}):lnup",),
			"braille_nextLine": (f"br({name}):lndn",),
			"braille_routeTo": (f"br({name}):route",),
			"toggleInputHelp": (f"brl({name}):learn"),
			"showGui": (f"brl({name}):prefmenu",),
			"revertConfiguration": (f"brl({name}):prefload",),
			"saveConfiguration": (f"brl({name}):prefsave",),
			"dateTime": (f"brl({name}):time",),
			"review_currentLine": (f"brl({name}):say_line",),
			"review_sayAll": (f"brl({name}):say_below",),
		}
	})

class InputGesture(braille.BrailleDisplayGesture):

	source = BrailleDisplayDriver.name

	def __init__(self, model, command, argument):
		super().__init__()
		self.model = model
		self.id = command.lower()
		if command == "ROUTE":
			self.routingIndex = argument
