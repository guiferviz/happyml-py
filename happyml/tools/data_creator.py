
import numpy as np
from matplotlib import pyplot as plt

from happyml import plot
from happyml.datasets import DataSet


class DataSetCreator(object):

    """Create simple datasets clicking on a plot.

    This class manage *matplotlib* events and store all points in a
    :attr:`happyml.datasets.DataSet` object.

    **Instructions for use**:

        Use the **left button** to create points of class 0 and
        the **right button** to create points of class 1.
        Use the **wheel button** to delete a point.

        You can create points of more classes (maximun 10 classes)
        if you press the **number keys 0-9** and after that you click
        with any mouse button. Onces you press a key number, all the
        points created with the mouse will be of this class unless you
        press another key.

        If all the points you create are of the same class, it will be
        considered that it is a regression dataset, i.e., one input feature
        and one output real number. Avoid this behaviour setting the kwarg
        'no_regression' to True.

    Example:
        .. code-block:: python

            creator = DataSetCreator()
            creator.show()  # show interactive plot and wait until close
            dataset = creator.get_dataset()  # obtain DataSet object

    """

    def __init__(self, **args):
        # Make a void plot window.
        options = {
            "limits": args["limits"],
            "grid": True,
            "scaled": not args["no_scaled"],
            "return_all": True,
        }
        if args['dataset']:
            dataset = args['dataset']
            if dataset.get_N() > 0 and dataset.get_k() == 1:
                scatters = plot.dataset(dataset, **options)
        else:
            scatters = plot.dataset(DataSet(), dtype="multiclass", **options)

        # Connect matplotlib event handlers.
        fig = plt.gcf()
        fig.canvas.mpl_connect('button_press_event', self._onclick)
        fig.canvas.mpl_connect('close_event', self._onclose)
        fig.canvas.mpl_connect('key_press_event', self._onkeydown)
        fig.canvas.mpl_connect('pick_event', self._onpick)

        # Save important fields.
        self._selected_class = None
        self._scatters = scatters
        self.save_plot = args['save_plot'] or False
        self.no_regression = args['no_regression'] or False
        self.ones = args.get('ones') or False
        self.binary = args.get('binary') or self.ones


    def get_dataset(self):
        """Get the dataset object associated to the current plot.

        Returns:
            dataset (:attr:`happyml.datasets.DataSet`).

        Raises:
            ValueError: if binary flag is activated but more than 2
                2 classes were found.

        """
        # Join scatters points on a list.
        data = self.get_data_array()
        # Construct dataset object.
        dataset = DataSet()
        if data.shape[0] > 0:
            # Check if is a classification or regression dataset.
            classes = np.unique(data[:, 0])  # The sorted unique classes
            if len(classes) == 1 and not self.no_regression and not self.binary:
                # If only one class it is regression data.
                dataset.X = data[:, 1].reshape(-1, 1)
                dataset.Y = data[:, 2].reshape(-1, 1)
            else:
                dataset.X = data[:, 1:3]
                dataset.Y = data[:, 0].reshape(-1, 1)

            if self.binary:
                if len(classes) <= 2:
                    if self.ones:
                        dataset.Y[dataset.Y == classes[0]] = -1
                        if len(classes) == 2:
                            dataset.Y[dataset.Y == classes[1]] = 1
                else:
                    raise ValueError("You are suposed to create a binary dataset "
                        "but more than 2 classed were found.")

        return dataset

    def get_data_array(self):
        """Return an numpy array with all the data in the plot.

        This method does not check if the data meets all the required
        properties (like no regression, binary, ...).

        Returns:
            data (numpy.ndarray): The first column is the target value.

        """
        data = []
        for i, s in enumerate(self._scatters):
            for x1, x2 in s.get_offsets():
                data += [[i, x1, x2]]

        return np.array(data)

    def show(self):
        """Show interactive plot and wait until close."""
        plt.show()

    def _onkeydown(self, event):
        key = ord(event.key[0]) - ord('0')
        if 0 <= key <= 9:
            self._selected_class = key

    def _onclick(self, event):
        button = 0 if event.button == 1 else \
                 1 if event.button == 3 else None
        x, y = event.xdata, event.ydata
        # If not wheel button (if not delete) and clicked inside
        # the axes (coordinates are not nan).
        if button is not None and (x is not None and y is not None):
            class_number = self._selected_class if self._selected_class \
                           else button
            self._add_point(class_number, [x, y])
            plt.draw()

    def _onclose(self, event):
        """Called when the plot is closed.

        Save an image of the dataset plot before exit.

        """
        if self.save_plot:
            plt.savefig(self.save_plot)

    def _onpick(self, event):
        # If picket using wheel
        if event.mouseevent.button == 2:
            self._remove_point(event.artist, event.ind)
            plt.draw()

    def _add_point(self, class_number, point):
        """Add point to the given class."""
        scatter = self._scatters[class_number]
        points = scatter.get_offsets()
        points = np.append(points, point[0:2])
        scatter.set_offsets(points)

    def _remove_point(self, scatter, point_idx):
        """Remove point for the given scatter plot."""
        points = scatter.get_offsets()
        points = np.delete(points, point_idx, axis=0)
        scatter.set_offsets(points)
