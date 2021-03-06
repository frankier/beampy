# -*- coding: utf-8 -*-
"""
Created on Fri May 22 18:28:59 2015
@author: hugo
"""
from beampy.statics.default_theme import THEME
import sys
from distutils.spawn import find_executable
from cache import cache_slides
#Auto change path
import os
import sys
bppath = os.path.dirname(__file__) + '/'
basename = os.path.basename(__file__)
script_file_name = os.path.basename(sys.argv[0]).split('.')[0]

class document():
    """
       Main function to define the document style etc...
    """

    __version__ = 0.3
    #Global variables to sotre data
    _contents = {}
    _global_counter = {}
    _width = 0
    _height = 0
    _guide = False
    _text_box = False
    _optimize_svg = True
    _output_format = 'html5'
    _theme = THEME
    _cache = None
    _pdf_animations = False
    _resize_raster = True

    #Define path to external commands (see default THEME file)
    _external_cmd = {}

    def __init__(self, **kwargs):

        """
            Create document to store slides
            options (see THEME)
            -------
            - width[800]: with of slides
            - height[600]: height of slides
            - guide[False]: Draw guide lines on slides to test alignements
            - text_box[False]: Draw box on slide elements to test width and height detection of elements (usefull to debug placement)
            - optimize[True]: Optimize svg using scour python script. This reduce the size but increase compilation time
            - cache[True]: Use cache system to not compile slides each times if nothing changed!
            - resize_raster[True]: Resize raster images (inside svg and for jpeg/png figures)
            - theme: Define the path to your personal THEME dictionnary
        """

		#reset if their is old variables
        self.reset()
        #A document is a dictionnary that contains all the slides
        self.data = self._contents
        #To store different counters
        self.global_counter = self._global_counter

        #Check if we want to load a new theme
        if 'theme' in kwargs:
            theme = kwargs['theme']
            try :
                new_theme = self.dict_deep_update( document._theme, __import__( theme.split('.')[0] ).THEME )
                self.theme =  new_theme
                document._theme = new_theme

            except ImportError:
                print("No slide theme '" + theme + "', returning to default theme.")
                sys.exit(0)


        #Load document options from THEME
        self.set_options(kwargs)

        #Load external tools
        self.link_external_programs()

        #Print the header message
        print("="*20 + " BEAMPY START " + "="*20)

    def set_options(self, input_dict):
        #Get document option from THEME
        default_options = self._theme['document']

        good_values = {}
        for key, value in input_dict.items():
            if key in default_options:
                good_values[key] = value
            else:
                print('%s is not a valid argument for document'%key)
                print('valid arguments')
                print(default_options)
                sys.exit(1)

        #Update default if not in input
        for key, value in default_options.items():
            if key not in good_values:
                good_values[key] = value

        #Set size etc...
        document._width = good_values['width']
        document._height = good_values['height']
        document._guide = good_values['guide']
        document._text_box = good_values['text_box']
        document._cache = good_values['cache']
        document._optimize_svg = good_values['optimize']
        document._resize_raster = good_values['resize_raster']
        document._output_format = good_values['format']
        if document._cache == False:
            document._cache = None
        else:
            cache_file = './.beampy_cache_%s_%s.pklz'%(script_file_name, document._output_format)
            print("\nChache file to %s"%(cache_file))
            document._cache = cache_slides(cache_file, self)

        self.options = good_values

    def reset(self):
        document._contents = {}
        document._global_counter = {}
        document._width = 0
        document._height = 0
        document._guide = False
        document._text_box = False
        document._theme = THEME
        document._cache = None
        document._external_cmd = {}
        document._resize_raster = True
        document._output_format = 'html5'

    def dict_deep_update( self, original, update ):

        """
        Recursively update a dict.
        Subdict's won't be overwritten but also updated.
        from http://stackoverflow.com/questions/38987/how-can-i-merge-two-python-dictionaries-in-a-single-expression/44512#44512
        """

        for key, value in original.iteritems():
            if not key in update:
                update[key] = value
            elif isinstance(value, dict):
                self.dict_deep_update( value, update[key] )
        return update

    def link_external_programs(self):
        #Function to link [if THEME['document']['external'] = 'auto'
        #and check external if programs exist

        #Loop over options
        missing = False
        for progname, cmd in self.options['external_app'].items():
            if cmd == 'auto':

                #Special case of video_encoder (ffmpeg or avconv)
                if progname == 'video_encoder':
                    find_ffmpeg = find_executable('ffmpeg')
                    find_avconv = find_executable('avconv')
                    if find_ffmpeg != None:
                        document._external_cmd[progname] = find_ffmpeg
                    elif find_avconv != None:
                        document._external_cmd[progname] = find_avconv
                    else:
                        missing = True
                else:
                    find_app = find_executable( progname )
                    if find_app != None:
                        document._external_cmd[progname] = find_app
                    else:
                        missing = True

            else:
                document._external_cmd[progname] = cmd

            if missing:
                if progname == 'video':
                    name = 'ffmpeg or avconv'
                else:
                    name = progname

                print('Missing external tool: %s, please install it before running Beampy'%name)
                #sys.exit(1)

        outprint = '\n'.join(['%s:%s'%(k, v) for k, v in document._external_cmd.items()])
        print('Linked external programs\n%s'%outprint)
