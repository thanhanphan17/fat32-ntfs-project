# Import fat32 and ntfs modules
from fat32.directory import *

from ntfs.directory.root import *
from ntfs.pbs.pbs import *
from ntfs.mft.mft import *

# Import modules working with os
import win32api
import os

# Import Tkinter
import tkinter
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import Frame, Label, Entry
from tkinter import Tk, Text, TOP, BOTH, X, N, LEFT, scrolledtext, messagebox

# Import PIL working with images
from PIL import Image, ImageTk

# Define colors
WHITE = '#FFFFFF'
BLACK = '#000000'
DARK = '#4D455D'
PINK = '#FF7483'
PURPLE = '#7F74B9'
LIGHT = '#F5E9CF'
LIGHT_BLUE = '#E9EFFF'
BLUE = '#0052C0'
YELLOW = '#FFCC8A'

# Define apps to open file
getApp = {
    ".doc": "Microsoft Word",
    ".docx": "Microsoft Word",
    ".pdf": "Adobe Reader, Microsoft Edge,...",
    ".tex": "LaTeX",
    ".xls": "Microsoft Excel",
    ".xlsx": "Microsoft Excel",
    ".ppt": "Microsoft PowerPoint",
    ".pptx": "Microsoft PowerPoint",
    ".bmp": "Microsoft Photos",
    ".png": "Microsoft Photos",
    ".jpeg": "Microsoft Photos",
    ".jpg": "Microsoft Photos",
    ".mp3": "Window Media Player",
    ".wav": "Window Media Player",
    ".psd": "Adobe Photoshop",
    ".mp4": "Microsoft Movies & TV, Window Media Player,...",
    ".avi": "Microsoft Movies & TV, Window Media Player,...",
    ".mov": "Microsoft Movies & TV, Window Media Player,...",
    ".rar": "Rar, 7-zip,...",
    ".7z": "Rar,7-Zip,...",
    ".zip": "Rar,7-Zip,...",
    ".exe": "Command prompt",
    ".html": "Microsoft Edge",
    ".htm": "Microsoft Edge"
}
