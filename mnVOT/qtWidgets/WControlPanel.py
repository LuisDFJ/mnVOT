from PyQt5 import QtWidgets, QtCore, QtGui
from pygrabber.dshow_graph import FilterGraph
import os


class WControlPanel( QtWidgets.QWidget ):
    def __init__(self, parent = None) -> None:
        super( QtWidgets.QWidget, self ).__init__( parent = parent )
        self._setup()
        self.hide_browse()
        self.setMaximumSize( 350, 700 )
        self.set_callbacks()
        self.rec_file = ''
        self.live_idx = 0
        self.nodes    = []
        self.lines    = []

    def hide_browse( self, flag = True ):
        if flag:
            self.liveflag = True
            self.video_browse.hide()
            self.video_label.hide()
            self.video_wcam.show()
        else:
            self.liveflag = False
            self.video_browse.show()
            self.video_label.show()
            self.video_wcam.hide()

    def set_callbacks( self ):
        self.mode.currentTextChanged.connect( self._mode_callback )
        self.video_wcam.currentIndexChanged.connect( self._live_source_callback )
        self.video_browse.clicked.connect( self._browse_callback )
        self.node_add.clicked.connect( self._add_callback )
        self.node_del.clicked.connect( self._del_callback )
        self.node_mat.clicked.connect( self._mat_callback )
        self.line_del.clicked.connect( self._del_mat_callback )

    def _update_node_list( self ):
        self.node_list.clear()
        for i, node in enumerate( self.nodes ):
            self.node_list.addItem( "{}-{}".format( i + 1, node ) )

    def _add_callback( self ):
        nodename = self.node_entry.text()
        self.node_entry.setText( "" )
        if nodename and nodename not in self.nodes:
            self.nodes.append( nodename )
            self._update_node_list()

    def _del_callback( self ):
        idx = [ i.row() for i in self.node_list.selectedIndexes() ]
        if len( idx ):
            self.nodes = [ i for j, i in enumerate( self.nodes ) if j not in idx ]
            self._update_node_list()

    def _update_line_list( self ):
        self.line_list.clear()
        for line in self.lines:
            self.line_list.addItem( "({}, {})".format( *line ) )

    def _mat_callback( self ):
        idx = [ i.row() + 1 for i in self.node_list.selectedIndexes() ]
        if len( idx ) == 2:
            idx.sort()
            idx = tuple( idx )
            if idx not in self.lines:
                self.lines.append( idx )
                self._update_line_list()
    
    def _del_mat_callback( self ):
        idx = [ i.row() for i in self.line_list.selectedIndexes() ]
        if len( idx ):
            self.lines = [ i for j, i in enumerate( self.lines ) if j not in idx ]
            self._update_line_list()

    def _browse_callback( self ):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName( self,
        "Select Video",
        ".",
        "Video Files (*.mp4 *.mov *.wmv *.avi *.flv)" )
        self.video_label.setText( os.path.basename( filename ) )
        self.rec_file = filename

    def _mode_callback( self, t : str ):
        if t == 'Video File':
            self.hide_browse( False )
        else: 
            self.hide_browse( True )

    def _live_source_callback( self, i : int ):
        self.live_idx = i

    def _setup( self ):
        aflag = QtCore.Qt.AlignmentFlag
        sflag = QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection
        mlayout = QtWidgets.QGridLayout()
        vlayout = QtWidgets.QVBoxLayout()

        # Mode Selection
        self.mode = QtWidgets.QComboBox( self )
        self.mode.addItems( 
            [ "Live", "Video File" ]
        )
        self.video_label = QtWidgets.QLabel( "" )
        self.video_browse = QtWidgets.QPushButton( "Browse" )
        self.video_wcam = QtWidgets.QComboBox()
        mlayout.addWidget( QtWidgets.QLabel( "Select Mode" ), 0, 0 )
        mlayout.addWidget( self.mode, 0, 1 )
        mlayout.addWidget( self.video_label, 0, 2 )
        mlayout.addWidget( self.video_browse, 0, 3 )
        mlayout.addWidget( self.video_wcam, 0, 2, 1, 2 )
        self._available_cameras()
        # Add Node
        self.node_entry = QtWidgets.QLineEdit()
        self.node_entry.setMaxLength( 5 )
        self.node_add = QtWidgets.QPushButton()
        self.node_add.setText( "Add" )
        mlayout.addWidget( QtWidgets.QLabel( "Node Name" ), 1, 0 )
        mlayout.addWidget( self.node_entry, 1, 1 )
        mlayout.addWidget( self.node_add, 1, 2 )

        # Nodes List
        self.node_list = QtWidgets.QListWidget()
        self.node_list.setSelectionMode( sflag )
        self.line_list = QtWidgets.QListWidget()
        self.line_list.setSelectionMode( sflag )
        self.node_mat = QtWidgets.QPushButton()
        self.node_mat.setText( "Match" )
        self.node_del = QtWidgets.QPushButton()
        self.node_del.setText( "Delete" )
        self.line_del = QtWidgets.QPushButton()
        self.line_del.setText( "Delete" )
        mlayout.addWidget( QtWidgets.QLabel( "Nodes List" ), 2, 0, alignment=aflag.AlignBottom | aflag.AlignLeft )
        mlayout.addWidget( QtWidgets.QLabel( "Lines List" ), 2, 2, alignment=aflag.AlignBottom | aflag.AlignLeft )
        mlayout.addWidget( self.node_list, 3,0, 5, 2 )
        mlayout.addWidget( self.line_list, 3,2, 5, 2 )
        mlayout.addWidget( self.node_mat, 8, 0 )
        mlayout.addWidget( self.node_del, 8, 1 )
        mlayout.addWidget( self.line_del, 8, 3 )

        # Start/Stop
        self.start = QtWidgets.QPushButton()
        self.start.setText( "Start" )
        self.stop = QtWidgets.QPushButton()
        self.stop.setText( "Stop" )
        mlayout.addWidget( self.start, 9, 0, 1, 2 )
        mlayout.addWidget( self.stop, 9, 2, 1, 2 )

        vlayout.addLayout( mlayout )
        vlayout.addStretch( 2 )
        self.setLayout( vlayout )

    def _available_cameras( self ):
        devices = FilterGraph().get_input_devices()
        self.video_wcam.addItems( devices )
        