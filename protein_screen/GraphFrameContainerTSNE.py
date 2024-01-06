from PyQt5.QtWidgets import QVBoxLayout, QFrame
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from sklearn.manifold import TSNE
import time

from protein_screen import GlobalObject


class GraphFrameContainerTSNE(QFrame):

    # constructor
    def __init__(self, parent=None):
        super(GraphFrameContainerTSNE, self).__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that
        # displays the 'figure' it takes the
        # 'figure' instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # creating a Vertical Box layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # adding toolbar to the layout
        layout.addWidget(self.toolbar)

        # adding canvas to the layout
        layout.addWidget(self.canvas)

        # setting layout to the main window
        self.setLayout(layout)

        # Add Event Listener for Emitted Object
        GlobalObject().add_event_listener("PLOT_TSNE", self.plot)

    # action called by the push button
    def plot(self):
        data = GlobalObject().data_frame
        num_components = GlobalObject().num_components
        verbose = GlobalObject().verbose
        perplexity = GlobalObject().perplexity
        num_iterations = GlobalObject().num_iterations
        if data is None:
            return
        original_data = data.copy()
        data = data.drop(columns=['Areax', 'AreaY', 'LocalX', 'LocalY', 'GlobX', 'GlobY'])
        time_start = time.time()
        print("Components", num_components, "Verbose", verbose, "Perplexity", perplexity, "Num_iterations", num_iterations)
        tsne = TSNE(n_components=num_components, verbose=verbose, perplexity=perplexity, n_iter=num_iterations)
        tsne_results = tsne.fit_transform(data)

        print('t-SNE done! Time elapsed: {} seconds'.format(time.time() - time_start))
        data['tsne-2d-one'] = tsne_results[:, 0]
        data['tsne-2d-two'] = tsne_results[:, 1]
        data['AreaX'] = original_data['Areax']
        # clearing old figure
        self.figure.clear()

        # create an axis
        ax = self.figure.add_subplot(111)

        ax.scatter(
            x="tsne-2d-one", y="tsne-2d-two",
            data=data,
            alpha=0.3
        )

        # refresh canvas
        self.canvas.draw()
